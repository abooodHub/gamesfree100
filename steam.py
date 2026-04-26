from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
import datetime
import queue
import time
import json
import os
import pytz
import bs4
from bs4 import Tag
import re
from typing import Optional, Tuple
import threading

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

# لتقليل احتمال حظر Steam أثناء جلب صفحات الألعاب
STORE_PAGE_SEMAPHORE = threading.Semaphore(2)

def parse_end_date_text(text: str) -> Optional[str]:
    try:
        t = text.lower()

        # 1) صيغة تاريخية مثل:
        # "Offer ends 26 March"
        # "Offer ends March 26"
        # "Offer ends 26 March at 3pm"
        # "Offer ends 26 March at 3:00pm"
        # "Offer ends 26 March 2026 at 3:00pm"
        m = re.search(
            r'(\d{1,2})\s+([a-z]+)\s*,?\s*(\d{4})?'
            r'(?:\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?)?',
            t
        )

        # بديل: "March 26"
        if not m:
            m = re.search(
                r'([a-z]+)\s+(\d{1,2})\s*,?\s*(\d{4})?'
                r'(?:\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?)?',
                t
            )

        if m:
            # لو النمط الأول: (day, month, year, hour, minute, am/pm)
            # في النمط الثاني: (month, day, year, hour, minute, am/pm)
            if (m.group(1) or '').isdigit():
                d = int(m.group(1))
                mon_str = m.group(2)
                y_str = m.group(3)
                hh = m.group(4)
                mm = m.group(5)
                ampm = m.group(6)
            else:
                mon_str = m.group(1)
                d = int(m.group(2))
                y_str = m.group(3)
                hh = m.group(4)
                mm = m.group(5)
                ampm = m.group(6)

            mon = MONTHS.get(mon_str)
            if not mon:
                return None

            now = datetime.datetime.now()
            y = int(y_str) if y_str else now.year

            # إذا لم توجد سنة: خمنها كسنة مستقبلية
            if not y_str:
                try:
                    probe = datetime.datetime(y, mon, d)
                    if probe < now:
                        y += 1
                except Exception:
                    pass

            h = int(hh) if hh else 0
            mi = int(mm) if mm else 0

            # تحويل AM/PM إلى 24 ساعة
            if ampm:
                ampm = ampm.lower()
                if ampm == 'pm' and h < 12:
                    h += 12
                if ampm == 'am' and h == 12:
                    h = 0

            dt = datetime.datetime(y, mon, d, h, mi)
            return dt.strftime('%Y-%m-%d %H:%M:%S')

        # 2) صيغة نسبية مثل: "Offer ends in 1 day 3 hours"
        if 'ends in' in t:
            now = datetime.datetime.now()
            days = 0
            hours = 0
            minutes = 0

            md = re.search(r'(\d+)\s+day', t)
            if md:
                days = int(md.group(1))
            mh = re.search(r'(\d+)\s+hour', t)
            if mh:
                hours = int(mh.group(1))
            mi_m = re.search(r'(\d+)\s+minute', t)
            if mi_m:
                minutes = int(mi_m.group(1))

            if days or hours or minutes:
                dt = now + datetime.timedelta(days=days, hours=hours, minutes=minutes)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

        return None
    except Exception:
        return None

def get_end_date_from_store_page(url: str) -> Optional[str]:
    try:
        from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

        # إجبار اللغة إلى الإنجليزية لتفادي اختلاف نص "Offer ends"
        parsed = urlparse(url)
        qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
        qs.setdefault('l', 'english')
        qs.setdefault('cc', 'us')
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(qs), parsed.fragment))

        # ملاحظة: لا نشارك Session بين Threads (requests.Session ليست thread-safe غالباً)
        sess = requests.Session()
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retries)
            sess.mount('http://', adapter)
            sess.mount('https://', adapter)
        except Exception:
            pass
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://store.steampowered.com/'
        }

        # Steam قد يحدّ الطلبات؛ أعد المحاولة عدة مرات
        for attempt in range(5):
            try:
                STORE_PAGE_SEMAPHORE.acquire()
                try:
                    resp = sess.get(url, headers=headers, timeout=25)
                finally:
                    STORE_PAGE_SEMAPHORE.release()

                # تعامل صريح مع 429 لتقليل فشل الاستخراج
                status_code = getattr(resp, "status_code", None)
                if status_code == 429:
                    time.sleep(10.0 + attempt * 6.0)
                    continue
                if status_code is None or status_code >= 400:
                    time.sleep(3.0 + attempt * 2.5)
                    continue

                html = resp.text or ""

                # 1) محاولة قراءة timestamp من JSON داخل الصفحة
                m = re.search(r'"discount_expiration"\s*:\s*(\d+)', html)
                if m:
                    ts = int(m.group(1))
                    # قد تكون بالms
                    if ts > 10**12:
                        ts = ts / 1000
                    dt = datetime.datetime.utcfromtimestamp(ts)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')

                # 2) بديل: قراءة نص "Offer ends ..."
                m2 = re.search(r'Offer\s+ends[^<]{0,120}', html, re.IGNORECASE)
                if m2:
                    return parse_end_date_text(m2.group(0))

                return None
            except Exception as e:
                # 429 غالباً يعني تقييد؛ انتظر أطول
                status_code = getattr(getattr(e, "response", None), "status_code", None)
                if status_code == 429:
                    time.sleep(10.0 + attempt * 6.0)
                else:
                    time.sleep(3.0 + attempt * 2.5)
                continue

    except Exception:
        return None
    return None

# جلسة HTTP مشتركة مع آلية إعادة المحاولة لتحسين الأداء والموثوقية
SESSION: Optional[requests.Session] = None

def make_session() -> requests.Session:
    """تهيئة جلسة HTTP مشتركة مع معادلات إعادة المحاولة والاتصال المستمر
    - تقلل من تكلفة إنشاء اتصال لكل طلب
    - تضيف إعادة محاولات تلقائية على الأخطاء المؤقتة
    """
    global SESSION
    if SESSION:
        return SESSION
    sess = requests.Session()
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        sess.mount('http://', adapter)
        sess.mount('https://', adapter)
    except Exception:
        pass
    SESSION = sess
    return sess

# عناوين البحث في Steam
SPECIALS_URL       = "https://store.steampowered.com/search/results/?query&specials=1&maxdiscount=100&start={pos}&count=100&infinite=1"
FREE_TEMPORARY_URL = "https://store.steampowered.com/search/results/?query&specials=1&maxprice=free&start={pos}&count=100&infinite=1"
HIGH_DISCOUNT_URL  = "https://store.steampowered.com/search/results/?query&specials=1&min_discount=90&start={pos}&count=100&infinite=1"
ALL_GAMES_URL      = "https://store.steampowered.com/search/results/?query&start={pos}&count=100&infinite=1"
FREE_TO_PLAY_URL   = "https://store.steampowered.com/search/results/?maxprice=free&start={pos}&count=100&infinite=1"
BIG_DISCOUNT_URL   = "https://store.steampowered.com/search/results/?specials=1&min_discount=75&start={pos}&count=100&infinite=1"
THREAD_CNT = 8

free_list = queue.Queue()
discounted_games_list = queue.Queue()  # قائمة منفصلة للألعاب المخصومة

def fetch_Steam_json_response(url: str) -> dict:
    """جلب استجابة JSON من واجهة Steam
    - يستخدم جلسة HTTP مشتركة
    - يعيد قاموس JSON للنتائج
    """
    sess = make_session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://store.steampowered.com/',
        'Cache-Control': 'no-cache',
    }
    for _ in range(3):
        try:
            resp = sess.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"خطأ في جلب البيانات: {e}")
            time.sleep(2)
    return {}

def extract_price_info(discount_block: Tag) -> Tuple[str, str, str, Optional[str]]:
    """استخراج معلومات السعر من كتلة الخصم
    يعيد: (السعر الأصلي، السعر بعد الخصم، نسبة الخصم، تاريخ الانتهاء إن وُجد)
    """
    old_price = ""
    new_price = "$0.00"
    discount_percent = ""
    end_date: Optional[str] = None

    try:
        discount_value = discount_block.get("data-discount", "")
        if discount_value:
            discount_percent = f"{discount_value}%"

        original_price_elem = discount_block.find(name="div", attrs={"class": "discount_original_price"})
        if original_price_elem:
            old_price = original_price_elem.get_text(strip=True)

        final_price_elem = discount_block.find(name="div", attrs={"class": "discount_final_price"})
        if final_price_elem:
            new_price = final_price_elem.get_text(strip=True)

        norm = new_price.strip().lower()
        if norm in {'0', '0.00', 'free', 'مجاني', '0.00 sr', '0.00 usd'}:
            new_price = "$0.00"

        try:
            end_date_elem = discount_block.find(name="div", attrs={"class": "discount_end_date"})
            if end_date_elem:
                parsed = parse_end_date_text(end_date_elem.get_text(strip=True))
                end_date = parsed if parsed else None
        except Exception:
            pass

    except Exception as e:
        print(f"خطأ في استخراج معلومات السعر: {e}")

    return old_price, new_price, discount_percent, end_date

def get_free_goods(start: int, append_list: bool = False,
                   use_specials_url: bool = False,
                   use_free_temporary: bool = False,
                   use_high_discount: bool = False,
                   use_all_games: bool = False,
                   use_free_to_play: bool = False,
                   use_big_discount: bool = False) -> int:
    """استخراج الألعاب المجانية/المخصومة من نتائج Steam
    - start: رقم البداية للصفحة
    - append_list: إضافة النتائج إلى قوائم التخزين المشتركة
    - أعلام التحكم لاختيار نوع البحث
    يعيد: عدد العناصر المستخرجة
    """
    global free_list, discounted_games_list
    retry_time = 3

    while retry_time >= 0:
        try:
            if use_free_to_play:
                url = FREE_TO_PLAY_URL
            elif use_big_discount:
                url = BIG_DISCOUNT_URL
            elif use_all_games:
                url = ALL_GAMES_URL
            elif use_high_discount:
                url = HIGH_DISCOUNT_URL
            elif use_free_temporary:
                url = FREE_TEMPORARY_URL
            else:
                url = SPECIALS_URL

            response_json = fetch_Steam_json_response(url.format(pos=start))
            
            goods_html = response_json.get("results_html", "")
            if not goods_html:
                print(f"لا توجد نتائج HTML في الاستجابة")
                return 0
                
            page_parser = bs4.BeautifulSoup(goods_html, "html.parser")
            
            # البحث عن جميع عناصر الألعاب
            all_games = page_parser.find_all(name = "a", attrs = {"class":"search_result_row"})
            sub_free_list = []
            sub_discounted_list = []
            
            for game in all_games:
                try:
                    # الحصول على اسم اللعبة
                    title_elem = game.find(name = "span", attrs = {"class":"title"})
                    if not title_elem:
                        continue
                    game_name = title_elem.get_text().strip()
                    game_url = game.get("href", "")
                    
                    # البحث عن السعر أو الخصم 100%
                    is_free = False
                    is_discounted = False
                    old_price = ""
                    new_price = "مجاني"
                    discount_percent = ""
                    
                    # التحقق من الخصم 100% أولاً
                    discount_block = game.find(name = "div", attrs = {"class":"search_discount_block", "data-discount":"100"})
                    if discount_block:
                        is_free = True
                        is_discounted = True
                        old_price, new_price, discount_percent, end_date = extract_price_info(discount_block)
                        if not end_date and game_url:
                            end_date = get_end_date_from_store_page(game_url)
                    
                    # البحث عن ألعاب بخصم 100% في العروض الخاصة
                    if (use_specials_url or use_free_temporary or use_high_discount or use_all_games or use_big_discount) and not is_discounted:
                        # البحث عن أي خصم في العروض الخاصة
                        discount_blocks = game.find_all(name = "div", attrs = {"class":"search_discount_block"})
                        for discount_block in discount_blocks:
                            discount_value = discount_block.get("data-discount", "")
                            if discount_value:
                                discount_num = int(discount_value) if discount_value.isdigit() else 0
                                # قبول الخصومات الكبيرة (75%+ للخصومات الكبيرة، 90%+ للعالية، 100% للمؤقتة)
                                if ((use_big_discount and discount_num >= 75) or 
                                    (use_high_discount and discount_num >= 90) or 
                                    (discount_num == 100)):
                                    is_free = True
                                    is_discounted = True
                                    old_price, new_price, discount_percent, end_date = extract_price_info(discount_block)
                                    # نحتاج تاريخ انتهاء الخصم فعلياً فقط لخصم 100%
                                    # لتقليل عدد طلبات صفحات Steam وتفادي 429
                                    if not end_date and game_url and discount_num == 100:
                                        end_date = get_end_date_from_store_page(game_url)
                                    break
                    
                    # التحقق من السعر = 0 أو مجاني (للألعاب المجانية الأصلية)
                    if not is_discounted:
                        price_elem = game.find(name = "div", attrs = {"class":"search_price"})
                        if price_elem:
                            price_text = price_elem.get_text().strip().lower()
                            if "free" in price_text or price_text == "0" or price_text == "مجاني":
                                is_free = True
                                new_price = "مجاني"
                                old_price = ""
                        
                        # التحقق من data-price-final="0"
                        price_block = game.find(name = "div", attrs = {"data-price-final":"0"})
                        if price_block:
                            is_free = True
                    
                    # التحقق من أن اللعبة ليست DLC أو محتوى إضافي
                    if game_name and game_url and is_free:
                        # تجنب المحتوى الإضافي والدوالين
                        if not any(keyword in game_name.lower() for keyword in ['dlc', 'pack', 'bundle', 'expansion', 'season pass']):
                            if is_discounted:
                                # لعبة مخصومة 100%
                                sub_discounted_list.append([game_name, game_url, old_price, new_price, discount_percent, end_date])
                            else:
                                # لعبة مجانية أصلية
                                sub_free_list.append([game_name, game_url, old_price, new_price])
                        
                except Exception as e:
                    print(f"خطأ في معالجة لعبة: {e}")
                    continue

            if append_list:
                for sub_free in sub_free_list:
                    free_list.put(sub_free)
                for sub_discounted in sub_discounted_list:
                    discounted_games_list.put(sub_discounted)

            return len(sub_free_list) + len(sub_discounted_list)
            
        except Exception as e:
            print(f"get_free_goods: خطأ في start = {start}, المحاولات المتبقية {retry_time}")
            print(e)
            retry_time -= 1
            
    print(f"get_free_goods: فشل في start = {start}")
    return 0

def is_game_expired(game):
    """
    التحقق من انتهاء صلاحية اللعبة بناءً على تاريخ الانتهاء المخزّن
    Check if a game's discount period has expired based on stored end_date
    """
    try:
        end_date = None

        # للألعاب المخصومة: game[7] يحتوي على تاريخ الانتهاء
        if len(game) > 7 and game[7] and str(game[7]) not in ('null', 'None', ''):
            end_date = game[7]
        # للألعاب القديمة ذات البنية المختلفة: game[5]
        elif len(game) > 5 and game[5] and isinstance(game[5], str) and '-' in game[5]:
            end_date = game[5]

        if not end_date:
            return False

        end_datetime = None
        if isinstance(end_date, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    end_datetime = datetime.datetime.strptime(end_date, fmt)
                    break
                except Exception:
                    pass

        if not end_datetime:
            return False

        is_expired = end_datetime <= datetime.datetime.now()
        if is_expired:
            print(f"⏰ اللعبة منتهية (تاريخ): {game[0]} (انتهت في {end_date})")
        return is_expired

    except Exception as e:
        print(f"خطأ في التحقق من انتهاء اللعبة: {e}")
        return False


def verify_discount_still_active_via_api(appid: str, game_name: str) -> bool:
    """
    يتحقق عبر Steam storefront API إذا كانت اللعبة لا تزال بخصم فعلي.
    يُستخدم للألعاب القديمة (من الملف السابق) التي لم تظهر في نتائج Steam الجديدة.
    يعيد True إذا كانت اللعبة لا تزال مخصومة بشكل فعلي، False إذا انتهى خصمها.
    """
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=english"
        sess = make_session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        for attempt in range(3):
            try:
                resp = sess.get(url, headers=headers, timeout=15)
                if resp.status_code == 429:
                    time.sleep(8.0 + attempt * 5.0)
                    continue
                resp.raise_for_status()
                data = resp.json()
                app_data = data.get(str(appid), {})
                if not app_data.get('success'):
                    # التطبيق غير موجود أو لم ترجع بيانات صالحة → اعتبره منتهياً
                    print(f"⚠️ لا توجد بيانات من API للعبة: {game_name} (appid={appid})")
                    return False
                price_info = app_data.get('data', {}).get('price_overview', {})
                if not price_info:
                    # لعبة مجانية أصلاً (Free to Play) → تعتبر نشطة دائماً
                    is_free = app_data.get('data', {}).get('is_free', False)
                    return bool(is_free)
                discount_percent = price_info.get('discount_percent', 0)
                final_price = price_info.get('final', 0)
                # لا تزال مخصومة إذا كانت نسبة الخصم > 0 والسعر النهائي = 0
                still_active = (discount_percent > 0 and final_price == 0)
                if not still_active:
                    print(f"🚫 انتهى خصم اللعبة: {game_name} (discount={discount_percent}%, price={final_price})")
                else:
                    print(f"✅ خصم لا يزال نشطاً: {game_name} (discount={discount_percent}%)")
                return still_active
            except Exception as e:
                time.sleep(3.0 + attempt * 2.0)
                continue
        # لو فشلت كل المحاولات، نحتاط ونزيل اللعبة
        print(f"⚠️ فشل التحقق من API للعبة: {game_name} → ستُحذف احتياطاً")
        return False
    except Exception as e:
        print(f"خطأ في verify_discount_still_active_via_api: {e}")
        return False


def clean_expired_games(games_list):
    """
    تنظيف قائمة الألعاب من الألعاب المنتهية بناءً على تاريخ الانتهاء المخزّن
    Clean the games list from expired games based on stored end_date
    """
    if not games_list:
        return []

    cleaned_games = []
    expired_count = 0

    for game in games_list:
        if not is_game_expired(game):
            cleaned_games.append(game)
        else:
            expired_count += 1

    if expired_count > 0:
        print(f"🗑️ تم إزالة {expired_count} لعبة منتهية من القائمة")

    return cleaned_games

print("🎮 بدء جلب الألعاب المجانية والمخصومة من Steam...")
print("=" * 60)

# جلب الألعاب المجانية الأصلية (Free to Play)
print("🔍 البحث في الألعاب المجانية الأصلية...")
free_to_play_count = get_free_goods(0, True, False, False, False, False, True, False)
print(f"عدد الألعاب المجانية الأصلية: {free_to_play_count}")

# جلب المزيد من الألعاب المجانية
if free_to_play_count > 0:
    threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
    futures = [threads.submit(get_free_goods, index, True, False, False, False, False, True, False) for index in range(100, 1000, 100)]
    wait(futures, return_when=ALL_COMPLETED)
    print("✅ تم البحث في 1000 لعبة مجانية أصلية")

# جلب ألعاب بخصم 100% من العروض الخاصة
print("\n🔍 البحث في العروض الخاصة للألعاب بخصم 100%...")
specials_count = get_free_goods(0, True, True, False, False, False, False, False)
print(f"عدد ألعاب بخصم 100% من العروض الخاصة: {specials_count}")

# جلب المزيد من العروض الخاصة
threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
futures = [threads.submit(get_free_goods, index, True, True, False, False, False, False, False) for index in range(100, 1500, 100)]
wait(futures, return_when=ALL_COMPLETED)
print("✅ تم البحث في 1500 لعبة من العروض الخاصة")

# جلب ألعاب بخصومات كبيرة (75%+)
print("\n🔍 البحث عن الألعاب بخصومات كبيرة (75%+)...")
big_discount_count = get_free_goods(0, True, False, False, False, False, False, True)
print(f"عدد ألعاب بخصومات كبيرة: {big_discount_count}")

# جلب المزيد من الخصومات الكبيرة
threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
futures = [threads.submit(get_free_goods, index, True, False, False, False, False, False, True) for index in range(100, 1000, 100)]
wait(futures, return_when=ALL_COMPLETED)
print("✅ تم البحث في 1000 لعبة بخصومات كبيرة")

# جلب ألعاب مجانية مؤقتاً (خصم 100%)
print("\n🔍 البحث عن الألعاب المجانية المؤقتة (خصم 100%)...")
temporary_free_count = get_free_goods(0, True, False, True, False, False, False, False)
print(f"عدد ألعاب مجانية مؤقتاً: {temporary_free_count}")

# جلب ألعاب بخصومات عالية (90%+)
print("\n🔍 البحث عن الألعاب بخصومات عالية (90%+)...")
high_discount_count = get_free_goods(0, True, False, False, True, False, False, False)
print(f"عدد ألعاب بخصومات عالية: {high_discount_count}")

# جلب ألعاب بخصم 100% من جميع الألعاب
print("\n🔍 البحث عن ألعاب بخصم 100% من جميع الألعاب...")
all_games_count = get_free_goods(0, True, False, False, False, True, False, False)
print(f"عدد ألعاب بخصم 100% من جميع الألعاب: {all_games_count}")

# جلب المزيد من الألعاب بخصم 100%
threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
futures = [threads.submit(get_free_goods, index, True, False, False, False, True, False, False) for index in range(100, 2000, 100)]
wait(futures, return_when=ALL_COMPLETED)
print("✅ تم البحث في 2000 لعبة للعثور على خصومات 100%")

# معالجة النتائج وإزالة التكرار
print("\n🔄 معالجة النتائج وإزالة التكرار...")

final_free_list = []
final_discounted_list = []
free_appids = set()  # استخدام app IDs بدلاً من URLs
discounted_appids = set()

def extract_appid_from_url(url):
    """استخراج app ID من رابط Steam"""
    try:
        match = re.search(r'/app/(\d+)/', url)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None

# معالجة الألعاب المجانية الأصلية
free_count = 0
while not free_list.empty():
    free_item = free_list.get()
    game_name = free_item[0]
    game_url = free_item[1]
    old_price = free_item[2] if len(free_item) > 2 else ""
    new_price = free_item[3] if len(free_item) > 3 else "مجاني"
    
    appid = extract_appid_from_url(game_url)
    
    # التحقق من التكرار بناءً على app ID
    if appid and appid not in free_appids:
        free_appids.add(appid)
        header_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
        capsule_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg"
            
        final_free_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price])
        free_count += 1
    elif not appid and game_url not in [item[1] for item in final_free_list]:
        # للألعاب التي لا تحتوي على app ID صالح
        header_url = capsule_url = "https://via.placeholder.com/300x150/222/fff?text=Steam"
        final_free_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price])
        free_count += 1

print(f"✅ تم معالجة {free_count} لعبة مجانية فريدة")

# معالجة الألعاب المخصومة
discounted_count = 0
while not discounted_games_list.empty():
    discounted_item = discounted_games_list.get()
    game_name = discounted_item[0]
    game_url = discounted_item[1]
    old_price = discounted_item[2] if len(discounted_item) > 2 else ""
    new_price = discounted_item[3] if len(discounted_item) > 3 else "$0.00"
    discount_percent = discounted_item[4] if len(discounted_item) > 4 else "100%"
    
    appid = extract_appid_from_url(game_url)
    
    # التحقق من التكرار بناءً على app ID
    if appid and appid not in discounted_appids:
        discounted_appids.add(appid)
        header_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
        capsule_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg"
        
        # إضافة تاريخ انتهاء الخصم (إذا كان متوفراً)
        end_date = discounted_item[5] if len(discounted_item) > 5 else None
            
        final_discounted_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price, discount_percent, end_date])
        discounted_count += 1
    elif not appid and game_url not in [item[1] for item in final_discounted_list]:
        # للألعاب التي لا تحتوي على app ID صالح
        header_url = capsule_url = "https://via.placeholder.com/300x150/222/fff?text=Steam"
        
        # إضافة تاريخ انتهاء الخصم (إذا كان متوفراً)
        end_date = discounted_item[5] if len(discounted_item) > 5 else None
        
        final_discounted_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price, discount_percent, end_date])
        discounted_count += 1

print(f"✅ تم معالجة {discounted_count} لعبة مخصومة فريدة")

# إزالة التكرار بين القوائم (إذا كانت لعبة موجودة في كلا القائمتين)
print("🔄 إزالة التكرار بين الألعاب المجانية والمخصومة...")
final_free_filtered = []
for free_game in final_free_list:
    free_appid = extract_appid_from_url(free_game[1])
    if free_appid not in discounted_appids:
        final_free_filtered.append(free_game)

final_free_list = final_free_filtered
print(f"✅ تم تنظيف {len(final_free_list)} لعبة مجانية نهائية")

print(f"\n📊 النتائج النهائية:")
print(f"🎮 الألعاب المجانية الأصلية: {len(final_free_list)}")
print(f"💰 الألعاب المخصومة: {len(final_discounted_list)}")
print(f"📈 إجمالي الألعاب: {len(final_free_list) + len(final_discounted_list)}")

if len(final_free_list) == 0 and len(final_discounted_list) == 0:
    print("⚠️ تحذير: لم يتم العثور على أي ألعاب مجانية أو مخصومة.")

# قراءة البيانات الموجودة للمقارنة
existing_free_games = []
existing_discounted_games = []
try:
    if os.path.exists("free_goods_detail.json"):
        with open("free_goods_detail.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            existing_free_games = data.get("free_games", [])
            existing_discounted_games = data.get("discounted_games", [])
            print(f"✅ تم تحميل {len(existing_free_games)} مجانية + {len(existing_discounted_games)} مخصومة من الملف السابق")
except Exception as e:
    print(f"⚠️ لم يتم العثور على بيانات سابقة: {e}")

# استخراج appids الجديدة (من السكان الحالي)
new_free_appids = set()
for game in final_free_list:
    if len(game) > 1:
        appid = extract_appid_from_url(game[1])
        if appid:
            new_free_appids.add(appid)

new_discounted_appids = set()
for game in final_discounted_list:
    if len(game) > 1:
        appid = extract_appid_from_url(game[1])
        if appid:
            new_discounted_appids.add(appid)

all_new_appids = new_free_appids | new_discounted_appids

# البيانات الجديدة هي الأساس
merged_free_games = list(final_free_list)
merged_discounted_games = list(final_discounted_list)

# الألعاب القديمة غير الموجودة في السكان الجديد:
# - المجانية الأصلية → تُضاف مباشرة
# - المخصومة → تُفحص عبر API، إن انتهى خصمها تُحذف

kept_old_free = 0
removed_old_free = 0
for game in existing_free_games:
    if len(game) > 1:
        appid = extract_appid_from_url(game[1])
        if appid and appid not in all_new_appids:
            # الألعاب المجانية الأصلية (بدون end_date) تُضاف مباشرة
            # الألعاب بتاريخ انتهاء تُفحص أولاً
            has_end_date = (
                (len(game) > 7 and game[7] and str(game[7]) not in ('null', 'None', '')) or
                (len(game) > 5 and game[5] and isinstance(game[5], str) and '-' in game[5])
            )
            if has_end_date and is_game_expired(game):
                # منتهية بالتاريخ → احذفها
                removed_old_free += 1
                continue
            merged_free_games.append(game)
            all_new_appids.add(appid)
            kept_old_free += 1
        elif not appid and game[1] not in [g[1] for g in merged_free_games]:
            merged_free_games.append(game)
            kept_old_free += 1

kept_old_discounted = 0
removed_old_discounted = 0
print("\n🔎 التحقق من الألعاب المخصومة القديمة عبر Steam API...")
for game in existing_discounted_games:
    if len(game) > 1:
        appid = extract_appid_from_url(game[1])
        if appid and appid not in all_new_appids:
            # أولاً: فحص تاريخ الانتهاء المخزّن
            if is_game_expired(game):
                removed_old_discounted += 1
                continue
            # ثانياً: تأكيد عبر Steam API (لأن الخصم قد ينتهي بدون تاريخ مخزّن)
            if verify_discount_still_active_via_api(appid, game[0]):
                merged_discounted_games.append(game)
                all_new_appids.add(appid)
                kept_old_discounted += 1
            else:
                removed_old_discounted += 1
                print(f"🗑️ حُذفت (انتهى خصمها): {game[0]}")
        elif not appid and game[1] not in [g[1] for g in merged_discounted_games]:
            merged_discounted_games.append(game)
            kept_old_discounted += 1

print(f"✅ البيانات الجديدة: {len(final_free_list)} مجانية + {len(final_discounted_list)} مخصومة")
print(f"✅ تم الاحتفاظ بـ {kept_old_free} مجانية قديمة + {kept_old_discounted} مخصومة قديمة")
print(f"🗑️ تم حذف {removed_old_free} مجانية قديمة منتهية + {removed_old_discounted} مخصومة قديمة منتهية")

# تنظيف الألعاب المنتهية من القوائم النهائية
print("\n🔍 فحص وتنظيف الألعاب المنتهية...")
merged_free_games = clean_expired_games(merged_free_games)
merged_discounted_games = clean_expired_games(merged_discounted_games)

# حفظ البيانات النهائية
print("\n💾 حفظ البيانات في ملف JSON...")
with open("free_goods_detail.json", "w", encoding="utf-8") as fp:
    json.dump({
        "total_count": len(merged_free_games) + len(merged_discounted_games),
        "free_games": merged_free_games,
        "discounted_games": merged_discounted_games,
        "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M:%S')
    }, fp, ensure_ascii=False, indent=2)

print("✅ تم حفظ البيانات بنجاح في ملف free_goods_detail.json")
print(f"\n🎉 تم الانتهاء من جلب الألعاب!")
print(f"🎮 إجمالي الألعاب المجانية: {len(merged_free_games)}")
print(f"💰 إجمالي الألعاب المخصومة: {len(merged_discounted_games)}")
print(f"📈 إجمالي جميع الألعاب: {len(merged_free_games) + len(merged_discounted_games)}")
print(f"⏰ وقت التحديث: {datetime.datetime.now(tz=pytz.timezone('Asia/Riyadh')).strftime('%Y-%m-%d %H:%M:%S')}")
