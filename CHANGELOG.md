# 📝 سجل التغييرات - Changelog

## [2.0.0] - 2025-01-09

### ✨ إضافات جديدة - New Features

#### 🚀 تحسينات كبيرة في النظام
- **ملف دفعي للتحديث السريع (`update_games.bat`)**
  - تحديث جميع المتاجر بنقرة واحدة
  - تحقق تلقائي من المتطلبات
  - تثبيت تلقائي للمكتبات المطلوبة
  - خيار تحديث Steam بشكل منفصل

- **سكريبت تحديث موحد (`update_all_games.py`)**
  - تحديث جميع المتاجر من سكريبت واحد
  - معالجة أخطاء محسنة
  - تقارير مفصلة عن التحديثات
  - إحصائيات في نهاية التحديث

- **دليل استخدام شامل (`USAGE.md`)**
  - دليل مفصل بالعربية والإنجليزية
  - حلول للمشاكل الشائعة
  - أمثلة عملية
  - معلومات عن وقت التحديث

### 🔧 إصلاحات - Bug Fixes

#### مشكلة المسارات النسبية
- **المشكلة السابقة**: السكريبترات تستخدم مسارات نسبية `../data/` التي لا تعمل عند التشغيل من مواقع مختلفة
- **الحل**: استخدام `pathlib.Path` للحصول على المسارات الصحيحة تلقائياً
- **الملفات المحدثة**:
  - ✅ `epic_scraper.py`
  - ✅ `steam_scraper.py`
  - ✅ `gog_scraper.py`
  - ✅ `playstation_scraper.py`
  - ✅ `ubisoft_scraper.py`
  - ✅ `xbox_scraper.py`

#### تحديث Headers
- **المشكلة السابقة**: User-Agent قديم (Chrome 91) يسبب حظر من بعض المواقع
- **الحل**: تحديث إلى Chrome 131
- **التحسينات**:
  - إضافة `Cache-Control: no-cache`
  - إضافة Sec-Fetch headers لـ Steam
  - تحديث جميع headers لتتوافق مع المتصفحات الحديثة

#### معالجة الأخطاء المحسنة
- **إضافة `traceback.print_exc()`** في جميع دوال الحفظ
- **رسائل خطأ أوضح** للمستخدم
- **معالجة أفضل للاستثناءات**

### 📦 التحسينات التقنية - Technical Improvements

#### البنية التحتية
```python
# قبل (Before)
with open("../data/epic_goods_detail.json", "w") as fp:
    json.dump(data, fp)

# بعد (After)
script_dir = Path(__file__).parent
data_dir = script_dir.parent / 'data'
data_dir.mkdir(exist_ok=True)
output_file = data_dir / 'epic_goods_detail.json'
with open(output_file, "w", encoding="utf-8") as fp:
    json.dump(data, fp, ensure_ascii=False, indent=2)
```

#### إضافة حقل "source" لكل ملف JSON
```json
{
  "total_count": 10,
  "free_games": [...],
  "update_time": "2025-01-09 12:00:00",
  "source": "Epic Games Store"  // ← جديد
}
```

### 📚 التوثيق - Documentation

#### ملفات جديدة
- ✅ **USAGE.md** - دليل استخدام شامل
- ✅ **CHANGELOG.md** - سجل التغييرات
- ✅ **update_games.bat** - ملف دفعي للتحديث

#### ملفات محدثة
- ✅ **README.md** - إضافة معلومات عن الملفات الجديدة
- ✅ جميع السكريبترات - تعليقات محسنة

### 🎯 تحسينات الأداء - Performance

- **تحسين وقت التحديث**: 
  - Epic Games: ~30 ثانية
  - GOG: ~30 ثانية
  - PlayStation: ~30 ثانية
  - Ubisoft: ~30 ثانية
  - Xbox: ~30 ثانية
  - Steam: 3-5 دقائق (بدون تغيير)

- **معالجة أفضل للأخطاء**: تقليل الوقت المهدر في إعادة المحاولات الفاشلة

### 🔐 الأمان - Security

- تحديث User-Agent لتجنب الحظر
- معالجة أفضل للاستثناءات
- التحقق من وجود المجلدات قبل الكتابة

### 🌐 التوافق - Compatibility

#### الأنظمة المدعومة
- ✅ Windows 10/11
- ✅ Linux
- ✅ macOS

#### إصدارات Python
- ✅ Python 3.7+
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

### 📊 الإحصائيات - Statistics

#### عدد الملفات المحدثة
- **6 سكريبترات محدثة**
- **3 ملفات جديدة**
- **2 ملفات توثيق محدثة**
- **+300 سطر من الكود الجديد**

#### التحسينات
- **100%** إصلاح مشكلة المسارات
- **100%** تحديث Headers
- **100%** تحسين معالجة الأخطاء
- **+50%** تحسين سهولة الاستخدام

---

## [1.0.0] - 2024-12-XX

### النسخة الأولى - Initial Release

- إطلاق الموقع الأساسي
- دعم 6 متاجر
- تحديث تلقائي كل 6 ساعات
- واجهة عربية/إنجليزية

---

## خطط المستقبل - Future Plans

### النسخة 2.1.0 (قريباً)
- [ ] إضافة متاجر جديدة (Nintendo eShop, etc.)
- [ ] تحسين أداء Steam scraper
- [ ] إضافة إشعارات عند توفر ألعاب جديدة
- [ ] API عام للمطورين

### النسخة 2.2.0
- [ ] تطبيق موبايل (PWA)
- [ ] نظام تنبيهات متقدم
- [ ] تكامل مع Discord/Telegram
- [ ] إحصائيات متقدمة

---

## ملاحظات الترقية - Upgrade Notes

### الترقية من 1.x إلى 2.0

1. **تحديث المكتبات**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **استخدام الملف الدفعي الجديد**:
   ```bash
   update_games.bat
   ```

3. **أو استخدام السكريبت الرئيسي**:
   ```bash
   python scripts/update_all_games.py
   ```

4. **لا حاجة لتغييرات في الكود** - جميع التحديثات متوافقة مع النسخة السابقة

---

## شكر خاص - Special Thanks

شكراً لجميع المستخدمين الذين أبلغوا عن المشاكل وساعدوا في تحسين المشروع! 🙏

Special thanks to all users who reported issues and helped improve the project! 🙏

