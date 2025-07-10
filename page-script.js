// ======================================
// Additional Pages Script - سكريبت الصفحات الإضافية
// Language Support and Interactions
// ======================================

let lang = 'ar';

// --- تبديل اللغة ---
function initLanguageToggle() {
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.addEventListener('click', function() {
            lang = lang === 'ar' ? 'en' : 'ar';
            
            // تحديث اتجاه الصفحة
            document.documentElement.lang = lang;
            document.body.dir = lang === 'ar' ? 'rtl' : 'ltr';
            
            // تحديث زر اللغة
            this.textContent = lang === 'ar' ? 'EN' : 'AR';
            
            // تحديث محتوى الصفحة
            updatePageContent();
        });
    }
}

// --- تحديث محتوى الصفحة ---
function updatePageContent() {
    // تحديث العناصر ذات البيانات متعددة اللغات
    document.querySelectorAll('[data-ar][data-en]').forEach(element => {
        // التحقق إذا كان العنصر يحتوي على أيقونات (img tags)
        if (element.querySelector('img') || element.innerHTML.includes('<img')) {
            // حفظ الأيقونات الموجودة
            const images = element.querySelectorAll('img');
            const imageHTML = Array.from(images).map(img => img.outerHTML).join(' ');
            
            // تحديث النص مع الحفاظ على الأيقونات
            const newText = lang === 'ar' ? element.getAttribute('data-ar') : element.getAttribute('data-en');
            
            // إذا كان النص يحتوي على اسم المتجر، نضع الأيقونة قبل النص
            if (imageHTML) {
                element.innerHTML = `${imageHTML} ${newText}`;
            } else {
                element.textContent = newText;
            }
        } else {
            // العناصر التي لا تحتوي على أيقونات
            if (lang === 'ar') {
                element.textContent = element.getAttribute('data-ar');
            } else {
                element.textContent = element.getAttribute('data-en');
            }
        }
    });
    
    // تحديث placeholders في النماذج
    document.querySelectorAll('[data-ar-placeholder][data-en-placeholder]').forEach(element => {
        if (lang === 'ar') {
            element.placeholder = element.getAttribute('data-ar-placeholder');
        } else {
            element.placeholder = element.getAttribute('data-en-placeholder');
        }
    });
    
    // تحديث options في select elements
    document.querySelectorAll('option[data-ar][data-en]').forEach(element => {
        if (lang === 'ar') {
            element.textContent = element.getAttribute('data-ar');
        } else {
            element.textContent = element.getAttribute('data-en');
        }
    });
    
    // تحديث عنوان الصفحة
    updatePageTitle();
}

// --- تحديث عنوان الصفحة ---
function updatePageTitle() {
    const currentPath = window.location.pathname.toLowerCase();
    let newTitle = '';
    
    if (currentPath.includes('about')) {
        newTitle = lang === 'ar' 
            ? '🎮 عن الموقع | About Us - Games100'
            : '🎮 About Us | عن الموقع - Games100';
    } else if (currentPath.includes('privacy')) {
        newTitle = lang === 'ar'
            ? '🎮 سياسة الخصوصية | Privacy Policy - Games100'
            : '🎮 Privacy Policy | سياسة الخصوصية - Games100';
    } else if (currentPath.includes('terms')) {
        newTitle = lang === 'ar'
            ? '🎮 شروط الاستخدام | Terms of Use - Games100'
            : '🎮 Terms of Use | شروط الاستخدام - Games100';
    } else if (currentPath.includes('contact')) {
        newTitle = lang === 'ar'
            ? '🎮 تمويل بنا | Contact Us - Games100'
            : '🎮 Contact Us | تمويل بنا - Games100';
    } else if (currentPath.includes('sitemap')) {
        newTitle = lang === 'ar'
            ? '🎮 خريطة الموقع | Sitemap - Games100'
            : '🎮 Sitemap | خريطة الموقع - Games100';
    }
    
    if (newTitle) {
        document.title = newTitle;
    }
}

// --- تأثيرات التفاعل ---
function initInteractionEffects() {
    // تأثير الحوامة على البطاقات
    const contentSections = document.querySelectorAll('.content-section');
    contentSections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // تأثير الحوامة على بطاقات الإحصائيات
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) rotate(1deg)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) rotate(0deg)';
        });
    });
    
    // تأثير التمرير السلس للعناصر
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // تطبيق تأثير التمرير على العناصر
    contentSections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

// --- التحقق من صحة النموذج ---
function initFormValidation() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            // التحقق من الحقول المطلوبة
            if (!name || !email || !message) {
                showNotification(
                    lang === 'ar' ? 'يرجى ملء جميع الحقول المطلوبة' : 'Please fill in all required fields',
                    'error'
                );
                return;
            }
            
            // التحقق من صحة البريد الإلكتروني
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showNotification(
                    lang === 'ar' ? 'يرجى إدخال بريد إلكتروني صحيح' : 'Please enter a valid email address',
                    'error'
                );
                return;
            }
            
            // محاكاة إرسال النموذج
            const submitBtn = contactForm.querySelector('.form-submit');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = lang === 'ar' ? 'جاري الإرسال...' : 'Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                showNotification(
                    lang === 'ar' ? 'تم إرسال رسالتك بنجاح!' : 'Your message has been sent successfully!',
                    'success'
                );
                
                contactForm.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
}

// --- عرض الإشعارات ---
function showNotification(message, type = 'info') {
    // إزالة الإشعارات السابقة
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // إنشاء الإشعار الجديد
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;
    
    // أنماط الإشعار
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        ${lang === 'ar' ? 'right' : 'left'}: 20px;
        background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : 'var(--accent2)'};
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transform: translateY(-100px);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // تأثير الظهور
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
    }, 100);
    
    // إزالة الإشعار بعد 5 ثوانٍ
    setTimeout(() => {
        notification.style.transform = 'translateY(-100px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

// --- إعدادات التمرير السلس ---
function initSmoothScrolling() {
    // التمرير السلس للروابط الداخلية
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// --- تحديث التوقيت المحلي ---
function updateLocalTime() {
    const timeElements = document.querySelectorAll('.local-time');
    timeElements.forEach(element => {
        const now = new Date();
        const timeString = now.toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        element.textContent = timeString;
    });
}

// --- التهيئة الرئيسية ---
function initPage() {
    initLanguageToggle();
    initInteractionEffects();
    initFormValidation();
    initSmoothScrolling();
    updateLocalTime();
    
    // تحديث المحتوى الأولي
    updatePageContent();
    
    // تحديث الوقت كل دقيقة
    setInterval(updateLocalTime, 60000);
}

// --- تشغيل التطبيق عند تحميل الصفحة ---
document.addEventListener('DOMContentLoaded', initPage);

// --- معالجة الأخطاء ---
window.addEventListener('error', function(event) {
    console.error('Page error:', event.error);
});

// --- دعم التنقل بلوحة المفاتيح ---
document.addEventListener('keydown', function(e) {
    // التنقل السريع بين الأقسام باستخدام أرقام لوحة المفاتيح
    if (e.altKey && e.key >= '1' && e.key <= '9') {
        const sections = document.querySelectorAll('.content-section');
        const index = parseInt(e.key) - 1;
        if (sections[index]) {
            sections[index].scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// --- دعم وضع الطباعة ---
window.addEventListener('beforeprint', function() {
    // إخفاء العناصر غير المرغوب فيها عند الطباعة
    document.querySelectorAll('.lang-btn, .home-btn').forEach(element => {
        element.style.display = 'none';
    });
});

window.addEventListener('afterprint', function() {
    // إظهار العناصر بعد الطباعة
    document.querySelectorAll('.lang-btn, .home-btn').forEach(element => {
        element.style.display = '';
    });
}); 