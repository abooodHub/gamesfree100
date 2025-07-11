from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
import datetime
import queue
import time
import json
import pytz
import bs4
from bs4 import Tag
<<<<<<< HEAD
import re

# تحديث URL للبحث عن ألعاب مجانية بدلاً من العروض الخاصة فقط
# البحث عن ألعاب بسعر 0 أو ألعاب Free to Play
API_URL_TEMPLATE = "https://store.steampowered.com/search/results/?query&maxprice=free&category1=998&os=win&supportedlang=english&start={pos}&count=100&infinite=1"
# URL بديل للبحث عن ألعاب بخصومات 100%
SPECIALS_URL = "https://store.steampowered.com/search/results/?query&specials=1&maxdiscount=100&start={pos}&count=100&infinite=1"
# URL جديد للبحث عن ألعاب مجانية مؤقتاً
FREE_TEMPORARY_URL = "https://store.steampowered.com/search/results/?query&specials=1&maxprice=free&start={pos}&count=100&infinite=1"
# URL للبحث عن ألعاب بخصومات عالية
HIGH_DISCOUNT_URL = "https://store.steampowered.com/search/results/?query&specials=1&min_discount=90&start={pos}&count=100&infinite=1"
# URL للبحث في جميع الألعاب
ALL_GAMES_URL = "https://store.steampowered.com/search/results/?query&start={pos}&count=100&infinite=1"
THREAD_CNT = 8

free_list = queue.Queue()
discounted_games_list = queue.Queue()  # قائمة منفصلة للألعاب المخصومة
=======

API_URL_TEMPLATE = "https://store.steampowered.com/search/results/?query&specials=1&maxdiscount=100&start={pos}&count=100&infinite=1"
THREAD_CNT = 8

free_list = queue.Queue()
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91

def fetch_Steam_json_response(url):
    ''' Fetch json response from Steam API
    URL:            Steam WebAPI url

    return:         json content
    '''
    while True:
        try:
<<<<<<< HEAD
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
            with requests.get(url, headers=headers, timeout = 15) as response:
                ret_json = response.json()
            return ret_json
        except Exception as e:
            print(f"خطأ في جلب البيانات: {e}")
            time.sleep(5)
            continue

def extract_price_info(discount_block):
    """استخراج معلومات السعر من كتلة الخصم"""
    old_price = ""
    new_price = "$0.00"
    discount_percent = ""
    
    try:
        # الحصول على نسبة الخصم
        discount_value = discount_block.get("data-discount", "")
        if discount_value:
            discount_percent = f"{discount_value}%"
        
        # الحصول على السعر الأصلي
        original_price_elem = discount_block.find(name = "div", attrs = {"class":"discount_original_price"})
        if original_price_elem:
            old_price = original_price_elem.get_text().strip()
        
        # الحصول على السعر الجديد
        final_price_elem = discount_block.find(name = "div", attrs = {"class":"discount_final_price"})
        if final_price_elem:
            new_price = final_price_elem.get_text().strip()
        
        # التحقق من أن السعر الجديد هو 0 أو مجاني
        if new_price.lower() in ['0', '0.00', 'free', 'مجاني', '0.00 sr', '0.00 usd']:
            new_price = "$0.00"
            
    except Exception as e:
        print(f"خطأ في استخراج معلومات السعر: {e}")
    
    return old_price, new_price, discount_percent

def get_free_goods(start, append_list = False, use_specials_url=False, use_free_temporary=False, use_high_discount=False, use_all_games=False):
    ''' Extract free games from Steam search results
    start:          start page index
    append_list:    if to append new found free goods to final list
    use_specials_url: if True, search for 100% discount games
    use_free_temporary: if True, search for temporary free games
    use_high_discount: if True, search for high discount games
    use_all_games: if True, search in all games
=======
            with requests.get(url, timeout = 5) as response:
                ret_json = response.json()
            return ret_json
        except Exception as e:
            print(e)
            time.sleep(10)
            continue

def get_free_goods(start, append_list = False):
    ''' Extract 100%-discount goods list in a list of 100 products
    start:          start page index
    append_list:    if to append new found free goods to final list
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91

    return:         goods_count
    '''

<<<<<<< HEAD
    global free_list, discounted_games_list
    retry_time = 3

    while retry_time >= 0:
        try:
            # اختيار URL بناءً على نوع البحث
            if use_all_games:
                url = ALL_GAMES_URL
            elif use_high_discount:
                url = HIGH_DISCOUNT_URL
            elif use_free_temporary:
                url = FREE_TEMPORARY_URL
            elif use_specials_url:
                url = SPECIALS_URL
            else:
                url = API_URL_TEMPLATE
                
            response_json = fetch_Steam_json_response(url.format(pos = start))
            
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
                        old_price, new_price, discount_percent = extract_price_info(discount_block)
                    
                    # البحث عن ألعاب بخصم 100% في العروض الخاصة
                    if (use_specials_url or use_free_temporary or use_high_discount or use_all_games) and not is_discounted:
                        # البحث عن أي خصم في العروض الخاصة
                        discount_blocks = game.find_all(name = "div", attrs = {"class":"search_discount_block"})
                        for discount_block in discount_blocks:
                            discount_value = discount_block.get("data-discount", "")
                            if discount_value == "100":
                                is_free = True
                                is_discounted = True
                                old_price, new_price, discount_percent = extract_price_info(discount_block)
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
                                sub_discounted_list.append([game_name, game_url, old_price, new_price, discount_percent])
                            else:
                                # لعبة مجانية أصلية
                                sub_free_list.append([game_name, game_url, old_price, new_price])
                        
                except Exception as e:
                    print(f"خطأ في معالجة لعبة: {e}")
                    continue
=======
    global free_list
    retry_time = 3

    while retry_time >= 0:
        response_json = fetch_Steam_json_response(API_URL_TEMPLATE.format(pos = start))
        try:
            goods_html = response_json["results_html"]
            page_parser = bs4.BeautifulSoup(goods_html, "html.parser")
            # كل العناصر التي عليها خصم 100%
            full_discounts_div = page_parser.find_all(name = "div", attrs = {"class":"search_discount_block", "data-discount":"100"})
            sub_free_list = [
                [
                    div.parent.parent.parent.parent.find(name = "span", attrs = {"class":"title"}).get_text(),
                    div.parent.parent.parent.parent.get("href"),
                ] for div in full_discounts_div
            ]
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91

            if append_list:
                for sub_free in sub_free_list:
                    free_list.put(sub_free)
<<<<<<< HEAD
                for sub_discounted in sub_discounted_list:
                    discounted_games_list.put(sub_discounted)

            return len(sub_free_list) + len(sub_discounted_list)
            
        except Exception as e:
            print(f"get_free_goods: خطأ في start = {start}, المحاولات المتبقية {retry_time}")
            print(e)
            retry_time -= 1
            
    print(f"get_free_goods: فشل في start = {start}")
    return 0

print("🎮 بدء جلب الألعاب المخصومة من Steam...")
print("=" * 50)

# جلب ألعاب بخصم 100% من العروض الخاصة
print("🔍 البحث في العروض الخاصة للألعاب بخصم 100%...")
specials_count = get_free_goods(0, True, True, False, False, False)
print(f"عدد ألعاب بخصم 100% من العروض الخاصة: {specials_count}")

# جلب المزيد من العروض الخاصة
if specials_count > 0:
    threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
    futures = [threads.submit(get_free_goods, index, True, True, False, False, False) for index in range(100, 1000, 100)]
    wait(futures, return_when=ALL_COMPLETED)
    print("✅ تم البحث في 1000 لعبة من العروض الخاصة")

# جلب ألعاب مجانية مؤقتاً (خصم 100%)
print("\n🔍 البحث عن الألعاب المجانية المؤقتة (خصم 100%)...")
temporary_free_count = get_free_goods(0, True, False, True, False, False)
print(f"عدد ألعاب مجانية مؤقتاً: {temporary_free_count}")

# جلب ألعاب بخصومات عالية (90%+)
print("\n🔍 البحث عن الألعاب بخصومات عالية (90%+)...")
high_discount_count = get_free_goods(0, True, False, False, True, False)
print(f"عدد ألعاب بخصومات عالية: {high_discount_count}")

# جلب ألعاب بخصم 100% من جميع الألعاب
print("\n🔍 البحث عن ألعاب بخصم 100% من جميع الألعاب...")
all_games_count = get_free_goods(0, True, False, False, False, True)
print(f"عدد ألعاب بخصم 100% من جميع الألعاب: {all_games_count}")

# جلب المزيد من الألعاب بخصم 100%
if all_games_count > 0:
    threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
    futures = [threads.submit(get_free_goods, index, True, False, False, False, True) for index in range(100, 2000, 100)]
    wait(futures, return_when=ALL_COMPLETED)
    print("✅ تم البحث في 2000 لعبة للعثور على خصومات 100%")

# معالجة النتائج وإزالة التكرار
print("\n🔄 معالجة النتائج وإزالة التكرار...")

final_discounted_list = []
discounted_urls = set()

=======

            return len(sub_free_list)
        except Exception as e:
            print("get_free_goods: error on start = %d, remain retry %d time(s)" % (start, retry_time))
            print(e)
            retry_time -= 1
    print("get_free_goods: error on start = %d, throw" % (start))

    return 0

print("بدء جلب الصفحة الأولى...")
tryget_first_page = get_free_goods(0)
print(f"عدد العناصر في الصفحة الأولى: {tryget_first_page}")
total_count = tryget_first_page

# جلب HTML الصفحة الأولى وحفظه للمعاينة
try:
    import requests
    resp = requests.get(API_URL_TEMPLATE.format(pos=0), timeout=10)
    if resp.ok:
        data = resp.json()
        with open("debug_steam.html", "w", encoding="utf-8") as f:
            f.write(data.get("results_html", ""))
        print("تم حفظ HTML الصفحة الأولى في debug_steam.html")
except Exception as e:
    print(f"تعذر حفظ HTML الصفحة الأولى: {e}")

print("بدء جلب باقي الصفحات...")
threads = ThreadPoolExecutor(max_workers = THREAD_CNT)
futures = [threads.submit(get_free_goods, index, True) for index in range(0, total_count, 100)]
wait(futures, return_when=ALL_COMPLETED)
print("انتهى جلب جميع الصفحات.")

# Process free list
final_free_list = []
free_names = set()
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91
def extract_appid_from_url(url):
    # رابط اللعبة يكون بهذا الشكل: https://store.steampowered.com/app/582660/Black_Desert/
    try:
        parts = url.split('/')
        idx = parts.index('app')
        appid = parts[idx+1]
        if appid.isdigit():
            return appid
    except Exception:
        pass
    return ''
<<<<<<< HEAD

# معالجة الألعاب المخصومة 100% فقط
discounted_count = 0
while not discounted_games_list.empty():
    discounted_item = discounted_games_list.get()
    game_name = discounted_item[0]
    game_url = discounted_item[1]
    old_price = discounted_item[2] if len(discounted_item) > 2 else ""
    new_price = discounted_item[3] if len(discounted_item) > 3 else "$0.00"
    discount_percent = discounted_item[4] if len(discounted_item) > 4 else "100%"
    
    if game_url not in discounted_urls:
        discounted_urls.add(game_url)
=======
while not free_list.empty():
    free_item = free_list.get()
    game_name = free_item[0]
    game_url = free_item[1]
    if game_name not in free_names:
        free_names.add(game_name)
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91
        appid = extract_appid_from_url(game_url)
        if appid:
            header_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            capsule_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg"
        else:
            header_url = capsule_url = "https://via.placeholder.com/300x150/222/fff?text=Steam"
<<<<<<< HEAD
            
        final_discounted_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price, discount_percent])
        discounted_count += 1

print(f"✅ تم معالجة {discounted_count} لعبة مخصومة فريدة")

print(f"\n📊 النتائج النهائية:")
print(f"💰 الألعاب بخصم 100%: {len(final_discounted_list)}")

# عرض بعض الأمثلة على الألعاب المخصومة
if len(final_discounted_list) > 0:
    print(f"\n🎯 أمثلة على الألعاب بخصم 100%:")
    for i, game in enumerate(final_discounted_list[:5]):
        print(f"  {i+1}. {game[0]}")
        print(f"     السعر الأصلي: {game[4]} → السعر الجديد: {game[5]}")
        print(f"     الخصم: {game[6] if len(game) > 6 else '100%'}")
        print()

if len(final_discounted_list) == 0:
    print("⚠️ تحذير: لم يتم العثور على أي ألعاب مخصومة 100%.")
    print("🔍 هذا طبيعي لأن Steam لا يعرض دائماً الألعاب المخصومة 100% في نفس الوقت.")

# حفظ البيانات
print("\n💾 حفظ البيانات في ملف JSON...")
with open("free_goods_detail.json", "w", encoding="utf-8") as fp:
    json.dump({
        "total_count": len(final_discounted_list),
        "free_games": [],  # قائمة فارغة لأننا نركز على الألعاب المخصومة فقط
        "discounted_games": final_discounted_list,
        "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S')
    }, fp, ensure_ascii=False, indent=2)
    
print("✅ تم حفظ البيانات بنجاح في ملف free_goods_detail.json")
print(f"\n🎉 تم الانتهاء من جلب الألعاب المخصومة!")
print(f"💰 الألعاب بخصم 100%: {len(final_discounted_list)}")
print(f"⏰ وقت التحديث: {datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")
=======
        # جلب السعر من HTML الصفحة الأولى (أو من free_item إذا أضفتها هناك)
        # سنعيد تحليل debug_steam.html للبحث عن السعر
        old_price = new_price = ''
        try:
            with open('debug_steam.html', encoding='utf-8') as f:
                soup = bs4.BeautifulSoup(f.read(), 'html.parser')
                card = soup.find('a', href=game_url)
                if isinstance(card, Tag):
                    price_block = None
                    for div in card.find_all('div'):
                        if 'search_price' in div.get('class', []):
                            price_block = div
                            break
                    if price_block:
                        prices = price_block.get_text(strip=True).split('₩')
                        if len(prices) == 2:
                            old_price = prices[0].strip()
                            new_price = prices[1].strip()
                        else:
                            old_price = price_block.get_text(strip=True)
                            new_price = '0'
        except Exception:
            pass
        final_free_list.append([game_name, game_url, header_url, capsule_url, old_price, new_price])

print(f"عدد العناصر النهائية: {len(final_free_list)}")
if len(final_free_list) == 0:
    print("تحذير: لم يتم العثور على أي عناصر مجانية. قد يكون السبب عدم وجود عروض مجانية حالياً أو تغيّر شكل صفحة Steam.")

with open("free_goods_detail.json", "w") as fp:
    json.dump({
        "total_count": len(final_free_list),
        "free_list": final_free_list,
        "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S')
    }, fp)
print(f"تم تحديث قائمة العناصر المجانية بنجاح! عدد العناصر: {len(final_free_list)}")
>>>>>>> d75e3dd50d01477b9160d2bec409a1df28571f91
