<div dir="rtl">

# 🎮 Games100 — ألعاب مجانية 100%

موقع ثابت مستضاف على GitHub Pages يعرض الألعاب المجانية وعروض الخصم 100% من Steam وEpic Games. تُحدّث البيانات آليًا كل 6 ساعات عبر GitHub Actions.

🌐 **الموقع:** [gamesfree100.online](https://gamesfree100.online)

## هيكل المشروع

```text
gamesfree100/
├── index.html                  # بنية الصفحة وبيانات SEO
├── styles.css                  # التصميم المتجاوب
├── script.js                   # العرض والفلترة واللغة والموافقة على التحليلات
├── deals.json                  # ملف العرض العام الصغير الذي تقرؤه الواجهة
├── build_public_feed.py        # يتحقق من المصادر ويبني deals.json
├── steam.py                    # جلب عروض Steam والتحقق منها
├── epic.py                     # جلب عروض Epic Games والتحقق منها
├── cleanup_now.py              # تنظيف يدوي محافظ للعروض المنتهية
├── update_timestamp.py         # ملخص حالة آخر محاولة تحديث
├── free_goods_detail.json      # بيانات Steam المصدرية
├── epic_goods_detail.json      # بيانات Epic المصدرية
├── update_timestamp.json       # حالة التحديث
├── tests/                      # اختبارات صحة البيانات والأمان والواجهة
├── icons/                      # أيقونات المتاجر
├── .github/workflows/          # التحديث الآلي والنشر عبر GitHub Pages
├── robots.txt
├── sitemap.xml
└── CNAME
```

الواجهة لا تحمّل ملفات المصادر الكبيرة؛ بل تقرأ `deals.json` فقط. يحتفظ البناء بالعروض الفعالة ذات الخصم 100%، ويتحقق من روابط HTTPS ونطاق المتجر وبنية البيانات قبل النشر.

## التحديث التلقائي

ينفذ سير GitHub Actions الخطوات التالية كل 6 ساعات أو يدويًا:

```text
فحص JavaScript
→ جلب Steam وEpic
→ بناء deals.json
→ بناء ملخص التحديث
→ تشغيل الاختبارات
→ رفع ملفات البيانات المتغيرة فقط
```

عند تعذر التحقق من متجر خارجي لا تُحذف العروض القديمة تلقائيًا لمجرد حدوث خطأ شبكة. تُكتب ملفات JSON بطريقة ذرّية لتقليل احتمال تلفها إذا انقطع التنفيذ.

لا ينشئ التحديث commit أو نشر GitHub Pages جديدًا إذا بقيت قائمة العروض كما هي؛ أوقات الفحص وحدها لا تُعد تغييرًا في الكتالوج. كما تُحذف سجلات Actions المكتملة الأقدم من 14 يومًا تلقائيًا مع بقاء سير العمل فعالًا.

## الاختبارات المستقلة

يعمل workflow باسم `Validate Project` عند Pull Requests وتغييرات الكود على `main`. يفحص JavaScript وPython وبنية البيانات دون تشغيل أدوات الجمع من المتاجر، لذلك يمكن اكتشاف أخطاء الكود قبل أن تؤثر في التحديث المجدول.

## التشغيل محليًا

</div>

```bash
python -m pip install -r requirements.txt
python build_public_feed.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m http.server 8000
```

<div dir="rtl">

ثم افتح `http://127.0.0.1:8000`. لا تفتح `index.html` مباشرة بنظام `file://` لأن المتصفح سيمنع جلب JSON في بعض البيئات.

## النشر

أي تعديل محلي لن يظهر على النطاق حتى يُرفع إلى الفرع الذي ينشره GitHub Pages. ملف `CNAME` يربط الإصدار المنشور بالنطاق المخصص.

</div>
