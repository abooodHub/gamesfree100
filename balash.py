from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
import datetime
import queue
import time
import json
import pytz
import bs4
from bs4 import Tag

API_URL_TEMPLATE = "https://store.steampowered.com/search/results/?query&specials=1&maxdiscount=100&start={pos}&count=100&infinite=1"
THREAD_CNT = 8

free_list = queue.Queue()

def fetch_Steam_json_response(url):
    ''' Fetch json response from Steam API
    URL:            Steam WebAPI url

    return:         json content
    '''
    while True:
        try:
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

    return:         goods_count
    '''

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

            if append_list:
                for sub_free in sub_free_list:
                    free_list.put(sub_free)

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
while not free_list.empty():
    free_item = free_list.get()
    game_name = free_item[0]
    game_url = free_item[1]
    if game_name not in free_names:
        free_names.add(game_name)
        appid = extract_appid_from_url(game_url)
        if appid:
            header_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            capsule_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg"
        else:
            header_url = capsule_url = "https://via.placeholder.com/300x150/222/fff?text=Steam"
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