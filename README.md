<div dir="rtl">

# 🎮 Games100 — ألعاب مجانية 100%

موقع يعرض الألعاب المجانية وعروض الخصم 100% من **Steam** و **Epic Games** ويتحدث تلقائياً كل 6 ساعات عبر GitHub Actions.

🌐 **الموقع**: [gamesfree100.online](https://gamesfree100.online)

---

## 🏗️ هيكل المشروع

```
gamesfree100/
├── index.html                  # الصفحة الرئيسية
├── styles.css                  # التصميم
├── script.js                   # منطق الواجهة (عرض، فلترة، حذف المنتهية)
│
├── steam.py                    # جلب ألعاب Steam + حذف المنتهية
├── epic.py                     # جلب ألعاب Epic + حذف المنتهية
├── update_timestamp.py         # تحديث وقت آخر تحديث
│
├── free_goods_detail.json      # بيانات Steam (يُحدَّث تلقائياً)
├── epic_goods_detail.json      # بيانات Epic (يُحدَّث تلقائياً)
├── update_timestamp.json       # وقت آخر تحديث
│
├── icons/                      # أيقونات Steam وEpic
├── .github/workflows/          # GitHub Actions
├── robots.txt                  # إعدادات SEO
├── sitemap.xml                 # خريطة الموقع لمحركات البحث
└── CNAME                       # نطاق مخصص
```

---

## 🔄 التحديث التلقائي

يعمل GitHub Actions كل 6 ساعات تلقائياً:

```
steam.py  →  يجلب الألعاب المجانية من Steam ويحذف المنتهية
epic.py   →  يجلب الألعاب المجانية من Epic ويحذف المنتهية
update_timestamp.py  →  يحدّث وقت آخر تحديث
git push  →  يرفع التغييرات للموقع
```

---

## 🖥️ تشغيل محلي

</div>

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل السكريبتات
python steam.py
python epic.py

# فتح الموقع محلياً
python -m http.server 8000
```

<div dir="rtl">

</div>
