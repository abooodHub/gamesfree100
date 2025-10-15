from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
import datetime
import queue
import time
import json
import pytz
import bs4
from bs4 import Tag
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
# URL للبحث في الألعاب المجانية فقط
FREE_TO_PLAY_URL = "https://store.steampowered.com/search/results/?maxprice=free&start={pos}&count=100&infinite=1"
# URL للبحث في الألعاب بخصومات كبيرة
BIG_DISCOUNT_URL = "https://store.steampowered.com/search/results/?specials=1&min_discount=75&start={pos}&count=100&infinite=1"
THREAD_CNT = 8

free_list = queue.Queue()
discounted_games_list = queue.Queue()  # قائمة منفصلة للألعاب المخصومة

def fetch_Steam_json_response(url):
    ''' Fetch json response from Steam API
    URL:            Steam WebAPI url

    return:         json content
    '''
    while True:
        try:
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
    end_date = None
    
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
        
        # محاولة الحصول على تاريخ انتهاء الخصم
        # Steam عادة لا يوفر تاريخ انتهاء مباشر، لكن يمكن البحث عنه في الصفحة
        try:
            # البحث عن عنصر يحتوي على تاريخ انتهاء الخصم
            end_date_elem = discount_block.find(name = "div", attrs = {"class": "discount_end_date"})
            if end_date_elem:
                end_date = end_date_elem.get_text().strip()
        except:
            pass
            
    except Exception as e:
        print(f"خطأ في استخراج معلومات السعر: {e}")
    
    return old_price, new_price, discount_percent, end_date

def get_free_goods(start, append_list = False, use_specials_url=False, use_free_temporary=False, use_high_discount=False, use_all_games=False, use_free_to_play=False, use_big_discount=False):
    ''' Extract free games from Steam search results
    start:          start page index
    append_list:    if to append new found free goods to final list
    use_specials_url: if True, search for 100% discount games
    use_free_temporary: if True, search for temporary free games
    use_high_discount: if True, search for high discount games
    use_all_games: if True, search in all games
    use_free_to_play: if True, search in free to play games
    use_big_discount: if True, search for big discounts (75%+)

    return:         goods_count
    '''
    global free_list, discounted_games_list
    retry_time = 3

    while retry_time >= 0:
        try:
            # اختيار URL بناءً على نوع البحث
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
                        old_price, new_price, discount_percent, end_date = extract_price_info(discount_block)
                    
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
        import re
        # البحث عن app ID في الرابط
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

# عرض بعض الأمثلة على الألعاب المخصومة
if len(final_discounted_list) > 0:
    print(f"\n🎯 أمثلة على الألعاب المخصومة:")
    for i, game in enumerate(final_discounted_list[:5]):
        print(f"  {i+1}. {game[0]}")
        print(f"     السعر الأصلي: {game[4]} → السعر الجديد: {game[5]}")
        print(f"     الخصم: {game[6] if len(game) > 6 else '100%'}")
        print()

if len(final_free_list) == 0 and len(final_discounted_list) == 0:
    print("⚠️ تحذير: لم يتم العثور على أي ألعاب مجانية أو مخصومة.")
    print("🔍 قد يكون السبب عدم وجود عروض حالياً أو تغيير في واجهة Steam.")

# حفظ البيانات
print("\n💾 حفظ البيانات في ملف JSON...")
with open("free_goods_detail.json", "w", encoding="utf-8") as fp:
    json.dump({
        "total_count": len(final_free_list) + len(final_discounted_list),
        "free_games": final_free_list,
        "discounted_games": final_discounted_list,
        "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S')
    }, fp, ensure_ascii=False, indent=2)
    
print("✅ تم حفظ البيانات بنجاح في ملف free_goods_detail.json")
print(f"\n🎉 تم الانتهاء من جلب الألعاب!")
print(f"🎮 الألعاب المجانية الأصلية: {len(final_free_list)}")
print(f"💰 الألعاب المخصومة: {len(final_discounted_list)}")
print(f"📈 إجمالي الألعاب: {len(final_free_list) + len(final_discounted_list)}")
print(f"⏰ وقت التحديث: {datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")
