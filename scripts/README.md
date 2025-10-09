# 🎮 Scripts - السكريبترات

## 📋 نظرة عامة - Overview

هذا المجلد يحتوي على جميع سكريبترات Python المستخدمة لجلب الألعاب المجانية من مختلف المتاجر.

This folder contains all Python scripts used to fetch free games from various stores.

---

## 📂 الملفات - Files

### 🚀 السكريبت الرئيسي - Main Script

#### `update_all_games.py`
**الوظيفة**: تحديث جميع المتاجر من سكريبت واحد  
**الاستخدام**:
```bash
python scripts/update_all_games.py
```
**المميزات**:
- ✅ تحديث جميع المتاجر (ماعدا Steam)
- ✅ معالجة أخطاء محسنة
- ✅ تقارير مفصلة
- ✅ إحصائيات في النهاية

---

### 🎮 سكريبترات المتاجر - Store Scrapers

#### `epic_scraper.py`
**المتجر**: Epic Games Store  
**الوظيفة**: جلب الألعاب المجانية من Epic Games  
**الاستخدام**:
```bash
python scripts/epic_scraper.py
```
**الوقت المتوقع**: ~30 ثانية  
**الملف الناتج**: `data/epic_goods_detail.json`

---

#### `steam_scraper.py`
**المتجر**: Steam Store  
**الوظيفة**: جلب الألعاب المجانية والمخصومة من Steam  
**الاستخدام**:
```bash
python scripts/steam_scraper.py
```
**الوقت المتوقع**: 3-5 دقائق  
**الملف الناتج**: `data/free_goods_detail.json`  
**ملاحظة**: يستخدم multi-threading لتسريع العملية

---

#### `gog_scraper.py`
**المتجر**: GOG Store  
**الوظيفة**: جلب الألعاب المجانية من GOG  
**الاستخدام**:
```bash
python scripts/gog_scraper.py
```
**الوقت المتوقع**: ~30 ثانية  
**الملف الناتج**: `data/gog_goods_detail.json`

---

#### `playstation_scraper.py`
**المتجر**: PlayStation Store  
**الوظيفة**: جلب الألعاب المجانية من PlayStation  
**الاستخدام**:
```bash
python scripts/playstation_scraper.py
```
**الوقت المتوقع**: ~30 ثانية  
**الملف الناتج**: `data/playstation_goods_detail.json`

---

#### `ubisoft_scraper.py`
**المتجر**: Ubisoft Connect  
**الوظيفة**: جلب الألعاب المجانية من Ubisoft  
**الاستخدام**:
```bash
python scripts/ubisoft_scraper.py
```
**الوقت المتوقع**: ~30 ثانية  
**الملف الناتج**: `data/ubisoft_goods_detail.json`

---

#### `xbox_scraper.py`
**المتجر**: Xbox Store  
**الوظيفة**: جلب الألعاب المجانية من Xbox  
**الاستخدام**:
```bash
python scripts/xbox_scraper.py
```
**الوقت المتوقع**: ~30 ثانية  
**الملف الناتج**: `data/xbox_goods_detail.json`

---

### 🛠️ سكريبترات مساعدة - Utility Scripts

#### `update_timestamps.py`
**الوظيفة**: تحديث الطوابع الزمنية في جميع ملفات JSON  
**الاستخدام**:
```bash
python scripts/update_timestamps.py
```
**الوقت المتوقع**: <5 ثواني  
**الملفات المحدثة**: جميع ملفات JSON في مجلد `data/`

---

## 🔧 المتطلبات - Requirements

### المكتبات المطلوبة
```
beautifulsoup4==4.11.1
bs4==0.0.1
pytz==2022.7
requests==2.31.0
```

### التثبيت
```bash
pip install -r requirements.txt
```

---

## 📊 بنية البيانات - Data Structure

### ملفات JSON الناتجة

#### Epic Games
```json
{
  "total_count": 2,
  "free_games": [...],
  "discounted_games": [...],
  "update_time": "2025-01-09 12:00:00",
  "source": "Epic Games Store"
}
```

#### Steam
```json
{
  "total_count": 100,
  "free_games": [...],
  "discounted_games": [...],
  "update_time": "2025-01-09 12:00:00",
  "source": "Steam Store"
}
```

#### GOG, PlayStation, Ubisoft, Xbox
```json
{
  "total_count": 10,
  "free_list": [...],
  "update_time": "2025-01-09 12:00:00",
  "source": "Store Name"
}
```

---

## 🎯 كيفية عمل السكريبترات - How Scripts Work

### 1. الاتصال بالموقع
```python
headers = {
    'User-Agent': 'Mozilla/5.0...',
    'Accept': 'application/json',
    ...
}
response = requests.get(url, headers=headers)
```

### 2. استخراج البيانات
```python
# Epic Games - JSON API
data = response.json()

# Steam - HTML Parsing
soup = BeautifulSoup(response.content, 'html.parser')
games = soup.find_all('a', class_='search_result_row')
```

### 3. معالجة البيانات
```python
for game in games:
    game_name = extract_name(game)
    game_url = extract_url(game)
    game_price = extract_price(game)
    ...
```

### 4. حفظ البيانات
```python
script_dir = Path(__file__).parent
data_dir = script_dir.parent / 'data'
output_file = data_dir / 'store_goods_detail.json'

with open(output_file, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, indent=2)
```

---

## 🔍 معالجة الأخطاء - Error Handling

جميع السكريبترات تتضمن:

1. **معالجة استثناءات الشبكة**
   ```python
   try:
       response = requests.get(url, timeout=30)
       response.raise_for_status()
   except requests.exceptions.RequestException as e:
       print(f"خطأ في الاتصال: {e}")
   ```

2. **معالجة أخطاء JSON**
   ```python
   try:
       data = json.loads(response.text)
   except json.JSONDecodeError as e:
       print(f"خطأ في تحليل JSON: {e}")
   ```

3. **Traceback مفصل**
   ```python
   except Exception as e:
       print(f"خطأ: {e}")
       import traceback
       traceback.print_exc()
   ```

---

## 🌐 APIs و URLs

### Epic Games
- API: `https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions`
- نوع البيانات: JSON
- التحديث: كل أسبوع

### Steam
- API: `https://store.steampowered.com/search/results/`
- نوع البيانات: HTML + JSON
- التحديث: يومي

### GOG
- URL: `https://www.gog.com/games?price=free`
- نوع البيانات: HTML
- التحديث: شهري

### PlayStation, Ubisoft, Xbox
- نوع البيانات: HTML
- التحديث: حسب العروض

---

## 📝 ملاحظات مهمة - Important Notes

1. **Steam يستغرق وقتاً أطول** لأنه يبحث في آلاف الألعاب
2. **Epic Games** يحدث قائمة الألعاب المجانية كل أسبوع (الخميس عادة)
3. **بعض المتاجر** قد لا تجد ألعاب مجانية في بعض الأوقات
4. **Headers محدثة** لتجنب الحظر من المواقع

---

## 🆘 حل المشاكل - Troubleshooting

### مشكلة: "لم يتم العثور على ألعاب"
**الحل**:
1. تحقق من الاتصال بالإنترنت
2. تحقق من الموقع الرسمي
3. أعد المحاولة لاحقاً

### مشكلة: "خطأ في حفظ البيانات"
**الحل**:
1. تحقق من صلاحيات الكتابة
2. تأكد من وجود مساحة كافية
3. تحقق من وجود مجلد `data/`

### مشكلة: "Timeout Error"
**الحل**:
1. زد قيمة timeout
2. تحقق من الاتصال بالإنترنت
3. استخدم VPN إذا لزم الأمر

---

## 🎉 نصائح للتطوير - Development Tips

### إضافة متجر جديد
1. أنشئ ملف `new_store_scraper.py`
2. استخدم نفس البنية الموجودة
3. أضف المتجر إلى `update_all_games.py`

### تحسين الأداء
- استخدم multi-threading للطلبات المتعددة
- قلل عدد الطلبات قدر الإمكان
- استخدم caching عند الإمكان

### اختبار السكريبترات
```bash
# اختبار سكريبت واحد
python scripts/epic_scraper.py

# اختبار جميع السكريبترات
python scripts/update_all_games.py
```

---

## 📚 مراجع - References

- [Requests Documentation](https://requests.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python pathlib](https://docs.python.org/3/library/pathlib.html)

---

**Made with ❤️ by Games100 Team**

