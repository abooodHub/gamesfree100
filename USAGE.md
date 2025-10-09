# 🎮 دليل الاستخدام - User Guide

## العربية

### 📋 المتطلبات

1. **Python 3.7 أو أحدث**
2. **المكتبات المطلوبة** (تثبت تلقائياً):
   - requests
   - beautifulsoup4
   - pytz

### 🚀 طريقة الاستخدام

#### الطريقة الأولى: استخدام الملف الدفعي (Windows)

1. انقر نقراً مزدوجاً على ملف `update_games.bat`
2. انتظر حتى يكتمل التحديث
3. سيطلب منك تحديث Steam (اختياري - يستغرق وقتاً أطول)

#### الطريقة الثانية: استخدام سطر الأوامر

```bash
# تثبيت المكتبات المطلوبة (مرة واحدة فقط)
pip install -r requirements.txt

# تحديث جميع المنصات (ماعدا Steam)
python scripts/update_all_games.py

# تحديث Steam فقط
python scripts/steam_scraper.py

# تحديث منصة معينة
python scripts/epic_scraper.py
python scripts/gog_scraper.py
python scripts/playstation_scraper.py
python scripts/ubisoft_scraper.py
python scripts/xbox_scraper.py
```

### 📂 الملفات الناتجة

بعد التحديث، ستجد الملفات التالية في مجلد `data/`:

- `epic_goods_detail.json` - ألعاب Epic Games المجانية
- `free_goods_detail.json` - ألعاب Steam المجانية
- `gog_goods_detail.json` - ألعاب GOG المجانية
- `playstation_goods_detail.json` - ألعاب PlayStation المجانية
- `ubisoft_goods_detail.json` - ألعاب Ubisoft المجانية
- `xbox_goods_detail.json` - ألعاب Xbox المجانية

### 🔧 حل المشاكل

#### المشكلة: "Python غير مثبت"
**الحل:** قم بتحميل وتثبيت Python من [python.org](https://www.python.org/)

#### المشكلة: "خطأ في تثبيت المكتبات"
**الحل:** 
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### المشكلة: "لم يتم العثور على ألعاب"
**الأسباب المحتملة:**
1. عدم وجود عروض مجانية حالياً
2. تغيير في API أو بنية الموقع
3. مشكلة في الاتصال بالإنترنت

**الحل:**
- تحقق من الاتصال بالإنترنت
- أعد المحاولة لاحقاً
- تحقق من الموقع الرسمي للمنصة

#### المشكلة: "خطأ في حفظ البيانات"
**الحل:**
- تحقق من وجود صلاحيات الكتابة في مجلد `data/`
- تأكد من وجود مساحة كافية على القرص

### 📊 معلومات إضافية

#### وقت التحديث
- **Epic Games**: ~30 ثانية
- **Steam**: 3-5 دقائق (بسبب البحث في آلاف الألعاب)
- **GOG**: ~30 ثانية
- **PlayStation**: ~30 ثانية
- **Ubisoft**: ~30 ثانية
- **Xbox**: ~30 ثانية

#### عدد الطلبات
- **Epic Games**: 2-3 طلبات
- **Steam**: ~20 طلب (متوازي)
- **GOG**: 1-2 طلب
- **PlayStation**: 1-3 طلبات
- **Ubisoft**: 1 طلب
- **Xbox**: 1-3 طلبات

---

## English

### 📋 Requirements

1. **Python 3.7 or newer**
2. **Required libraries** (installed automatically):
   - requests
   - beautifulsoup4
   - pytz

### 🚀 Usage

#### Method 1: Using Batch File (Windows)

1. Double-click on `update_games.bat`
2. Wait for the update to complete
3. You'll be asked to update Steam (optional - takes longer)

#### Method 2: Using Command Line

```bash
# Install required libraries (one time only)
pip install -r requirements.txt

# Update all platforms (except Steam)
python scripts/update_all_games.py

# Update Steam only
python scripts/steam_scraper.py

# Update specific platform
python scripts/epic_scraper.py
python scripts/gog_scraper.py
python scripts/playstation_scraper.py
python scripts/ubisoft_scraper.py
python scripts/xbox_scraper.py
```

### 📂 Output Files

After updating, you'll find the following files in the `data/` folder:

- `epic_goods_detail.json` - Epic Games free games
- `free_goods_detail.json` - Steam free games
- `gog_goods_detail.json` - GOG free games
- `playstation_goods_detail.json` - PlayStation free games
- `ubisoft_goods_detail.json` - Ubisoft free games
- `xbox_goods_detail.json` - Xbox free games

### 🔧 Troubleshooting

#### Problem: "Python not installed"
**Solution:** Download and install Python from [python.org](https://www.python.org/)

#### Problem: "Error installing libraries"
**Solution:** 
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Problem: "No games found"
**Possible causes:**
1. No free offers currently available
2. API or website structure changed
3. Internet connection issue

**Solution:**
- Check internet connection
- Try again later
- Check the official platform website

#### Problem: "Error saving data"
**Solution:**
- Check write permissions in `data/` folder
- Ensure sufficient disk space

### 📊 Additional Information

#### Update Time
- **Epic Games**: ~30 seconds
- **Steam**: 3-5 minutes (due to searching thousands of games)
- **GOG**: ~30 seconds
- **PlayStation**: ~30 seconds
- **Ubisoft**: ~30 seconds
- **Xbox**: ~30 seconds

#### Request Count
- **Epic Games**: 2-3 requests
- **Steam**: ~20 requests (parallel)
- **GOG**: 1-2 requests
- **PlayStation**: 1-3 requests
- **Ubisoft**: 1 request
- **Xbox**: 1-3 requests

---

## 🆘 Support - الدعم

إذا واجهت أي مشاكل، يرجى:
1. التحقق من هذا الدليل
2. التحقق من ملف `README.md`
3. فتح issue على GitHub

If you encounter any issues, please:
1. Check this guide
2. Check the `README.md` file
3. Open an issue on GitHub

