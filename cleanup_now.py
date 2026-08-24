"""
سكريبت تنظيف فوري - يحذف الألعاب المنتهية من free_goods_detail.json
يفحص كل لعبة مخصومة عبر Steam API ويحذف ما انتهى خصمه
"""
import json, re, time, datetime, sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.stdout.reconfigure(encoding='utf-8')

def make_session():
    sess = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    sess.mount('https://', HTTPAdapter(max_retries=retries))
    return sess

ACTIVE = "active"
EXPIRED = "expired"
UNKNOWN = "unknown"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def extract_appid(url):
    m = re.search(r'/app/(\d+)/', url or '')
    return m.group(1) if m else None

def is_date_expired(end_date):
    if not end_date or str(end_date) in ('null', 'None', ''):
        return False
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(str(end_date), fmt) <= datetime.datetime.now()
        except:
            pass
    return False

def check_steam_discount(appid, name):
    """يعيد ACTIVE أو EXPIRED أو UNKNOWN عند تعذر التحقق."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=english"
    session = make_session()
    for attempt in range(3):
        try:
            r = session.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                time.sleep(10 + attempt * 5)
                continue
            r.raise_for_status()
            data = r.json().get(str(appid), {})
            if not data.get('success'):
                print(f"  ⚠️ استجابة غير حاسمة: {name} → سيبقى العرض")
                return UNKNOWN
            app = data.get('data', {})
            if app.get('is_free'):
                return ACTIVE
            price = app.get('price_overview', {})
            if not price:
                return EXPIRED
            still = price.get('discount_percent', 0) > 0 and price.get('final', 1) == 0
            if not still:
                print(f"  🗑️ انتهى خصمها: {name} (discount={price.get('discount_percent',0)}%, price={price.get('final',0)})")
            return ACTIVE if still else EXPIRED
        except Exception:
            time.sleep(3 + attempt * 2)
    print(f"  ⚠️ فشل فحص API: {name} → سيبقى العرض حتى تحقق ناجح")
    return UNKNOWN

# ── تحميل الملف ──────────────────────────────────────────────
print("=" * 55)
print("🔧 تنظيف free_goods_detail.json")
print("=" * 55)

with open('free_goods_detail.json', encoding='utf-8-sig') as f:
    data = json.load(f)

free_games       = data.get('free_games', [])
discounted_games = data.get('discounted_games', [])

print(f"الحالة قبل التنظيف:")
print(f"  مجانية     : {len(free_games)}")
print(f"  مخصومة     : {len(discounted_games)}")

# ── 1) تنظيف المجانية بالتاريخ فقط (لا نحتاج API) ──────────
cleaned_free = []
removed_free = 0
for g in free_games:
    end = g[7] if len(g) > 7 else None
    if is_date_expired(end):
        print(f"  ⏰ منتهية (تاريخ): {g[0]}")
        removed_free += 1
    else:
        cleaned_free.append(g)

print(f"\nالمجانية: حُذف {removed_free} منتهية بالتاريخ، تبقّى {len(cleaned_free)}")

# ── 2) تنظيف المخصومة: تاريخ أولاً، ثم API للباقي ──────────
print(f"\n🔎 فحص {len(discounted_games)} لعبة مخصومة...")

# المرحلة أ: حذف ما له تاريخ منتهٍ فوراً
needs_api   = []
cleaned_dis = []
removed_dis = 0

for g in discounted_games:
    end = g[7] if len(g) > 7 else None
    if is_date_expired(end):
        print(f"  ⏰ منتهية (تاريخ): {g[0]}")
        removed_dis += 1
    else:
        needs_api.append(g)

print(f"  بعد فحص التاريخ: حُذف {removed_dis}، يحتاج API: {len(needs_api)}")

# المرحلة ب: فحص الباقي عبر Steam API بـ threads
print(f"\n  📡 فحص {len(needs_api)} لعبة عبر Steam API (قد يستغرق دقائق)...")

def worker(g):
    appid = extract_appid(g[1])
    if not appid:
        return (g, UNKNOWN)  # بدون appid لا نحذف دون تحقق حاسم
    return (g, check_steam_discount(appid, g[0]))

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(worker, g): g for g in needs_api}
    done = 0
    for future in as_completed(futures):
        game, verification = future.result()
        done += 1
        if verification != EXPIRED:
            cleaned_dis.append(game)
        else:
            removed_dis += 1
        if done % 50 == 0:
            print(f"    تقدم: {done}/{len(needs_api)} ...")

print(f"\nالمخصومة: حُذف {removed_dis} منتهية، تبقّى {len(cleaned_dis)}")

# ── 3) حفظ الملف المنظف ─────────────────────────────────────
data['free_games']       = cleaned_free
data['discounted_games'] = cleaned_dis
data['total_count']      = len(cleaned_free) + len(cleaned_dis)
data['update_time']      = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

target_path = os.path.abspath('free_goods_detail.json')
with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=os.path.dirname(target_path), delete=False) as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.flush()
    os.fsync(f.fileno())
    temp_path = f.name
os.replace(temp_path, target_path)

print("\n" + "=" * 55)
print("✅ تم حفظ free_goods_detail.json")
print(f"  مجانية  : {len(cleaned_free)}")
print(f"  مخصومة  : {len(cleaned_dis)}")
print(f"  الإجمالي: {data['total_count']}")
print(f"  حُذف    : {removed_free + removed_dis} لعبة منتهية")
print("=" * 55)
