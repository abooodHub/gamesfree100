# 🎮 دليل صفحات الخطأ - Error Pages Guide

## نظرة عامة | Overview

تم إنشاء صفحات الخطأ المخصصة لموقع Games100 بدعم كامل للغتين العربية والإنجليزية مع تصميم يتماشى مع هوية الموقع.

Custom error pages have been created for Games100 website with full Arabic and English language support and design that matches the site's identity.

## الملفات المنشأة | Created Files

### صفحات الخطأ | Error Pages
- `404.html` - صفحة غير موجودة | Page Not Found
- `500.html` - خطأ خادم داخلي | Internal Server Error  
- `error.html` - صفحة خطأ عامة | General Error Page

### ملفات التصميم والسكريبت | Style and Script Files
- `error-styles.css` - أنماط CSS خاصة بصفحات الخطأ
- `error-script.js` - JavaScript لوظائف صفحات الخطأ والترجمة

### ملفات التكوين | Configuration Files
- `.htaccess` - تكوين Apache لتوجيه الأخطاء والأمان
- `web.config` - تكوين IIS لتوجيه الأخطاء والأمان

## الميزات | Features

### 🌐 دعم متعدد اللغات | Multi-language Support
- تبديل فوري بين العربية والإنجليزية
- تغيير اتجاه النص تلقائياً (RTL/LTR)
- ترجمة كاملة لجميع النصوص والأزرار

### 🎨 تصميم متجاوب | Responsive Design
- متوافق مع جميع أحجام الشاشات
- استخدام منهجية BEM في CSS
- تأثيرات حركية سلسة
- تصميم يتماشى مع هوية الموقع الأساسي

### ⚡ أداء محسن | Optimized Performance
- CSS منفصل لتحسين التحميل
- JavaScript محسن للسرعة
- تخزين مؤقت ذكي للمتصفح
- ضغط الملفات تلقائياً

### 🔒 أمان محسن | Enhanced Security
- رؤوس أمان HTTP
- حماية من XSS
- منع تحميل الموقع في إطارات خارجية
- إخفاء الملفات الحساسة

## كيفية الاستخدام | How to Use

### 1. رفع الملفات | Upload Files
```bash
# رفع جميع الملفات إلى جذر الموقع
404.html
500.html
error.html
error-styles.css
error-script.js
.htaccess (للخوادم Apache)
web.config (للخوادم IIS)
```

### 2. التكوين التلقائي | Automatic Configuration
الخادم سيوجه الأخطاء تلقائياً:
- `404` → `404.html`
- `500` → `500.html`
- `502, 503, 403, 401` → `error.html`

### 3. التخصيص | Customization

#### تغيير النصوص | Change Text
عدل ملف `error-script.js` في قسم `errorTranslations`:

```javascript
const errorTranslations = {
    ar: {
        404: {
            title: 'عنوان مخصص',
            message: 'رسالة مخصصة...'
        }
    },
    en: {
        404: {
            title: 'Custom Title',
            message: 'Custom message...'
        }
    }
};
```

#### تغيير الألوان | Change Colors
عدل ملف `error-styles.css` أو `styles.css`:

```css
:root {
    --main-bg: #181c24;
    --card-bg: #232a36;
    --accent: #00b8d9;
    --accent2: #7ed6df;
    --text: #eaf6fb;
    --text2: #b2becd;
    --danger: #e74c3c;
    --success: #00b894;
}
```

## اختبار الصفحات | Testing Pages

### محلياً | Locally
```bash
# افتح الملفات مباشرة في المتصفح
file:///path/to/404.html
file:///path/to/500.html
file:///path/to/error.html
```

### على الخادم | On Server
```bash
# اختبار صفحة 404
https://yoursite.com/nonexistent-page

# محاكاة خطأ 500 (يحتاج تدخل الخادم)
# أو إنشاء ملف PHP مؤقت مع:
<?php http_response_code(500); ?>
```

## استكشاف الأخطاء | Troubleshooting

### المشاكل الشائعة | Common Issues

#### 1. صفحات الخطأ لا تعمل
```bash
# تأكد من وجود الملفات في المكان الصحيح
ls -la 404.html 500.html error.html

# تحقق من أذونات الملفات
chmod 644 *.html
chmod 644 .htaccess
```

#### 2. CSS لا يتحمل
```bash
# تأكد من مسار ملف CSS
<link rel="stylesheet" href="error-styles.css">

# تحقق من أذونات ملف CSS
chmod 644 error-styles.css
```

#### 3. JavaScript لا يعمل
```bash
# تأكد من مسار ملف JavaScript
<script src="error-script.js"></script>

# افتح Developer Tools وتحقق من الأخطاء
F12 > Console
```

## تحديثات مستقبلية | Future Updates

### إضافات مخططة | Planned Additions
- [ ] إضافة المزيد من أنواع الأخطاء
- [ ] تحسين الرسوم المتحركة
- [ ] إضافة خيارات تخصيص أكثر
- [ ] دعم لغات إضافية
- [ ] تتبع الأخطاء وإحصائيات

### تحسينات الأداء | Performance Improvements
- [ ] تحسين حجم الملفات
- [ ] ضغط الصور بشكل أفضل
- [ ] تحسين تخزين مؤقت أكثر ذكاءً

## الدعم | Support

### روابط مفيدة | Helpful Links
- [MDN - HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Apache .htaccess Guide](https://httpd.apache.org/docs/current/howto/htaccess.html)
- [IIS web.config Reference](https://docs.microsoft.com/en-us/iis/configuration/)

### الحصول على المساعدة | Getting Help
في حالة وجود مشاكل:
1. تحقق من أن الخادم يدعم `.htaccess` أو `web.config`
2. راجع سجلات الأخطاء في الخادم
3. تأكد من أن جميع الملفات تم رفعها بشكل صحيح
4. اختبر في متصفحات مختلفة

---

تم إنشاء هذا الدليل لمساعدتك في استخدام صفحات الخطأ المخصصة بفعالية. 
This guide was created to help you use custom error pages effectively.

**تاريخ الإنشاء | Created:** 2024
**الإصدار | Version:** 1.0
**التوافق | Compatibility:** جميع المتصفحات الحديثة | All modern browsers 