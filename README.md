# 🎮 Games100 - ألعاب مجانية من جميع المتاجر العالمية

موقع متخصص في عرض الألعاب المجانية وأقوى العروض من جميع المتاجر العالمية في مكان واحد.



## 🎯 المتاجر المدعومة

| المتجر | الحالة | التحديث |
|--------|--------|---------|
| 🎮 Steam | ✅ يعمل | كل 6 ساعات |
| 🎮 Epic Games | ✅ يعمل | كل 6 ساعات |
| 🎮 GOG | ✅ يعمل | كل 6 ساعات |
## 🚀 التقنيات المستخدمة

## 🔧 التثبيت والتشغيل

### المتطلبات
```bash
Python 3.10+
pip install -r requirements.txt
```

### تشغيل محلي
```bash
# تشغيل السكريبتات
python balash.py
python epic_balash.py
python gog_balash.py

# تشغيل خادم محلي
python -m http.server 8000
```

## 📁 هيكل المشروع

```
gamesfree100/
├── index.html              # الصفحة الرئيسية
├── sitemap.html            # خريطة الموقع
├── styles.css              # التصميم الرئيسي
├── styles.v2.css           # تحسينات واجهة إضافية
├── script.js               # الوظائف الرئيسية
├── balash.py               # سكريبت Steam
├── epic_balash.py          # سكريبت Epic
├── gog_balash.py           # سكريبت GOG
├── free_goods_detail.json  # بيانات Steam
├── epic_goods_detail.json  # بيانات Epic
├── gog_goods_detail.json   # بيانات GOG
├── icons/                  # أيقونات المتاجر
├── .github/workflows/      # GitHub Actions
├── robots.txt              # إعدادات SEO
├── sitemap.xml             # خريطة الموقع
├── web.config              # تهيئة الخادم وHeaders
└── README.md               # هذا الملف
```

## 🔄 التحديث التلقائي

الموقع يستخدم GitHub Actions للتحديث التلقائي:

- **الجدولة**: كل 6 ساعات
- **التحديث**: الألعاب المجانية والتوقي
## 🌐 الروابط

- **الموقع الرسمي**: [https://gamesfree100.online](https://gamesfree100.online)
- **GitHub Repository**: [https://github.com/abooodHub/gamesfree100](https://github.com/abooodHub/gamesfree100)

## 📞 التواصل

- **المطور**: Games100 
- **البريد الإلكتروني**: [contact@gamesfree100.online](mailto:contact@gamesfree100.online)
- **GitHub**: [@abooodHub](https://github.com/abooodHub)

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف [LICENSE](LICENSE) للتفاصيل.




