// ======================================
// Error Pages Script - سكريبت صفحات الخطأ
// Language Support and Interactions
// ======================================

let lang = 'ar';

// ترجمات صفحات الخطأ
const errorTranslations = {
    ar: {
        // 404 Page
        404: {
            title: 'الصفحة غير موجودة',
            message: 'عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها إلى موقع آخر.',
            homeBtn: 'العودة للرئيسية',
            backBtn: 'العودة للخلف',
            suggestionsTitle: 'يمكنك أيضاً:',
            suggestions: [
                'تصفح الألعاب المجانية الجديدة',
                'استكشاف ألعاب Steam المجانية', 
                'اكتشاف عروض Epic Games',
                'تصفح مكتبة GOG'
            ]
        },
        // 500 Page
        500: {
            title: 'خطأ في الخادم',
            message: 'عذراً، حدث خطأ داخلي في الخادم. نحن نعمل على حل هذه المشكلة في أسرع وقت ممكن.',
            homeBtn: 'العودة للرئيسية',
            refreshBtn: 'إعادة المحاولة',
            suggestionsTitle: 'إذا استمرت المشكلة:',
            suggestions: [
                'تأكد من اتصالك بالإنترنت',
                'حاول تحديث الصفحة بعد بضع دقائق',
                'امسح ذاكرة التخزين المؤقت للمتصفح',
                'عد إلى الصفحة الرئيسية'
            ]
        },
        // General Error Page
        general: {
            title: 'حدث خطأ غير متوقع',
            message: 'عذراً، حدث خطأ غير متوقع أثناء تحميل الصفحة. يرجى المحاولة مرة أخرى.',
            homeBtn: 'العودة للرئيسية',
            refreshBtn: 'إعادة المحاولة',
            backBtn: 'العودة للخلف',
            suggestionsTitle: 'نصائح لحل المشكلة:',
            suggestions: [
                'تأكد من اتصالك بالإنترنت',
                'حاول إعادة تحميل الصفحة',
                'امسح ذاكرة التخزين المؤقت',
                'جرب استخدام متصفح آخر',
                'عد إلى الصفحة الرئيسية'
            ]
        }
    },
    en: {
        // 404 Page
        404: {
            title: 'Page Not Found',
            message: 'Sorry, the page you are looking for does not exist or has been moved to another location.',
            homeBtn: 'Back to Home',
            backBtn: 'Go Back',
            suggestionsTitle: 'You can also:',
            suggestions: [
                'Browse new free games',
                'Explore free Steam games',
                'Discover Epic Games offers',
                'Browse GOG library'
            ]
        },
        // 500 Page
        500: {
            title: 'Server Error',
            message: 'Sorry, an internal server error occurred. We are working to resolve this issue as quickly as possible.',
            homeBtn: 'Back to Home',
            refreshBtn: 'Try Again',
            suggestionsTitle: 'If the problem persists:',
            suggestions: [
                'Check your internet connection',
                'Try refreshing the page after a few minutes',
                'Clear your browser cache',
                'Return to the home page'
            ]
        },
        // General Error Page
        general: {
            title: 'An Unexpected Error Occurred',
            message: 'Sorry, an unexpected error occurred while loading the page. Please try again.',
            homeBtn: 'Back to Home',
            refreshBtn: 'Try Again',
            backBtn: 'Go Back',
            suggestionsTitle: 'Tips to resolve the issue:',
            suggestions: [
                'Check your internet connection',
                'Try refreshing the page',
                'Clear browser cache',
                'Try using another browser',
                'Return to the home page'
            ]
        }
    }
};

// تحديد نوع صفحة الخطأ بناءً على العنوان
function getErrorType() {
    const title = document.title;
    if (title.includes('404')) return '404';
    if (title.includes('500')) return '500';
    return 'general';
}

// تحديث محتوى الصفحة بناءً على اللغة
function updatePageContent() {
    const errorType = getErrorType();
    const translations = errorTranslations[lang][errorType];
    
    // تحديث النصوص الأساسية
    const errorTitle = document.getElementById('errorTitle');
    const errorMessage = document.getElementById('errorMessage');
    const suggestionsTitle = document.getElementById('suggestionsTitle');
    
    if (errorTitle) errorTitle.textContent = translations.title;
    if (errorMessage) errorMessage.textContent = translations.message;
    if (suggestionsTitle) suggestionsTitle.textContent = translations.suggestionsTitle;
    
    // تحديث الأزرار
    const homeBtn = document.getElementById('homeBtn');
    const backBtn = document.getElementById('backBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    if (homeBtn) homeBtn.textContent = translations.homeBtn;
    if (backBtn && translations.backBtn) backBtn.textContent = translations.backBtn;
    if (refreshBtn && translations.refreshBtn) refreshBtn.textContent = translations.refreshBtn;
    
    // تحديث قائمة الاقتراحات
    const suggestionsList = document.getElementById('suggestionsList');
    if (suggestionsList && translations.suggestions) {
        suggestionsList.innerHTML = '';
        translations.suggestions.forEach((suggestion, index) => {
            const li = document.createElement('li');
            
            // إضافة روابط للاقتراحات التي تحتوي على روابط
            if (index === 0 && errorType === '404') {
                li.innerHTML = `<a href="/">${suggestion}</a>`;
            } else if (index === 1 && errorType === '404') {
                li.innerHTML = `<a href="/#steam">${suggestion}</a>`;
            } else if (index === 2 && errorType === '404') {
                li.innerHTML = `<a href="/#epic">${suggestion}</a>`;
            } else if (index === 3 && errorType === '404') {
                li.innerHTML = `<a href="/#gog">${suggestion}</a>`;
            } else if ((index === 3 && errorType === '500') || (index === 4 && errorType === 'general')) {
                li.innerHTML = `<a href="/">${suggestion}</a>`;
            } else {
                li.textContent = suggestion;
            }
            
            suggestionsList.appendChild(li);
        });
    }
    
    // تحديث عنوان الصفحة
    const pageTitle = document.querySelector('title');
    if (pageTitle) {
        if (errorType === '404') {
            pageTitle.textContent = lang === 'ar' 
                ? '🎮 404 - الصفحة غير موجودة | Page Not Found - Games100'
                : '🎮 404 - Page Not Found | الصفحة غير موجودة - Games100';
        } else if (errorType === '500') {
            pageTitle.textContent = lang === 'ar'
                ? '🎮 500 - خطأ في الخادم | Server Error - Games100'
                : '🎮 500 - Server Error | خطأ في الخادم - Games100';
        } else {
            pageTitle.textContent = lang === 'ar'
                ? '🎮 خطأ | Error - Games100'
                : '🎮 Error | خطأ - Games100';
        }
    }
}

// تبديل اللغة
function toggleLanguage() {
    lang = lang === 'ar' ? 'en' : 'ar';
    
    // تحديث اتجاه الصفحة
    document.documentElement.lang = lang;
    document.body.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // تحديث زر اللغة
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.textContent = lang === 'ar' ? 'EN' : 'AR';
    }
    
    // تحديث الشعار
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.textContent = '🎮 Games100';
    }
    
    // تحديث محتوى الصفحة
    updatePageContent();
    
    // تحديث تذييل الصفحة
    updateFooter();
}

// تحديث تذييل الصفحة
function updateFooter() {
    const footerContent = document.querySelector('.footer-content');
    if (footerContent) {
        if (lang === 'ar') {
            footerContent.innerHTML = `
                <p>جميع الحقوق محفوظة &copy; 2024 | <a href="/">Games100</a></p>
                <p>موقع متخصص في عرض الألعاب المجانية من Steam, Epic, GOG, Ubisoft, PlayStation, Xbox</p>
            `;
        } else {
            footerContent.innerHTML = `
                <p>All rights reserved &copy; 2024 | <a href="/">Games100</a></p>
                <p>Specialized website for displaying free games from Steam, Epic, GOG, Ubisoft, PlayStation, Xbox</p>
            `;
        }
    }
}

// تهيئة صفحة الخطأ
function initErrorPage() {
    // إعداد زر تبديل اللغة
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.addEventListener('click', toggleLanguage);
    }
    
    // تحديث المحتوى الأولي
    updatePageContent();
    updateFooter();
    
    // إضافة تأثيرات التفاعل
    addInteractionEffects();
    
    // إعداد الأزرار
    setupButtons();
}

// إضافة تأثيرات التفاعل
function addInteractionEffects() {
    // تأثير الحوامة على الأزرار
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// إعداد وظائف الأزرار
function setupButtons() {
    // زر العودة للخلف
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = '/';
            }
        });
    }
    
    // زر إعادة المحاولة
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // إضافة تأثير تحميل
            this.innerHTML = '<div class="error-loading"></div>';
            this.disabled = true;
            
            // إعادة تحميل الصفحة بعد ثانية
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
}

// تشغيل التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', initErrorPage);

// معالجة الأخطاء العامة
window.addEventListener('error', function(event) {
    console.error('Error occurred:', event.error);
});

// معالجة الأخطاء غير المعالجة
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// حفظ نوع الخطأ في Local Storage للمتابعة
function logError(errorType, details = {}) {
    try {
        const errorLog = {
            type: errorType,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            details: details
        };
        
        localStorage.setItem('lastError', JSON.stringify(errorLog));
    } catch (e) {
        console.warn('Could not save error log:', e);
    }
} 