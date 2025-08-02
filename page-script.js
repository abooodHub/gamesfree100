// ======================================
// Additional Pages Script - سكريبت الصفحات الإضافية
// Language Support and Interactions
// ======================================

// --- نظام تغيير اللغة للصفحات الفرعية ---
let lang = 'ar';

// تحميل اللغة المحفوظة
const savedLang = localStorage.getItem('games100_language');
if (savedLang) {
    lang = savedLang;
}

// ترجمة النصوص
const translations = {
    ar: {
        home: 'الرئيسية',
        reviews: 'المراجعات',
        guides: 'الدليل',
        about: 'عن الموقع',
        guidesTitle: 'دليل الألعاب المجانية',
        guidesDescription: 'اكتشف عالم الألعاب المجانية من خلال دليلنا الشامل. نصائح، استراتيجيات، وأفضل الممارسات للاستمتاع بالألعاب المجانية.',
        reviewsTitle: 'مراجعات الألعاب المجانية',
        reviewsDescription: 'اكتشف أفضل الألعاب المجانية من خلال مراجعات شاملة ومفصلة. نحن نختبر كل لعبة بعناية لنقدم لك التوصيات الأفضل.',
        howToChoose: 'كيفية اختيار الألعاب المناسبة',
        howToChooseContent: 'اختيار اللعبة المناسبة أمر مهم للاستمتاع بالتجربة. إليك بعض النصائح:',
        gameType: 'حدد نوع الألعاب المفضل:',
        gameTypeDesc: 'هل تفضل ألعاب الحركة أم الاستراتيجية؟',
        systemRequirements: 'تحقق من متطلبات النظام:',
        systemRequirementsDesc: 'تأكد من توافق اللعبة مع جهازك',
        readReviews: 'اقرأ المراجعات:',
        readReviewsDesc: 'استفد من تجارب اللاعبين الآخرين',
        tryDemo: 'جرب النسخ التجريبية:',
        tryDemoDesc: 'اختبر اللعبة قبل التحميل الكامل',
        quickTips: 'نصائح سريعة:',
        startSimple: 'ابدأ بالألعاب البسيطة إذا كنت مبتدئاً',
        joinCommunity: 'انضم لمجتمعات اللاعبين للحصول على المساعدة',
        tryNewTypes: 'لا تتردد في تجربة أنواع جديدة من الألعاب',
        performanceTitle: 'تحسين أداء الألعاب',
        performanceContent: 'لتحسين أداء الألعاب على جهازك، اتبع هذه الخطوات:',
        closePrograms: 'إغلاق البرامج غير الضرورية:',
        closeProgramsDesc: 'حرر ذاكرة النظام',
        updateDrivers: 'تحديث تعريفات الرسومات:',
        updateDriversDesc: 'احصل على أحدث الإصدارات',
        bestForBeginners: 'أفضل الألعاب للمبتدئين',
        bestForBeginnersContent: 'إذا كنت جديداً في عالم الألعاب، إليك بعض التوصيات:',
        adventureGames: 'ألعاب المغامرة:',
        strategyGames: 'ألعاب الاستراتيجية:',
        advancedStrategies: 'استراتيجيات اللعب المتقدم',
        advancedStrategiesContent: 'لتحسين مهاراتك في الألعاب، اتبع هذه الاستراتيجيات:',
        skillImprovement: 'تحسين المهارات:',
        regularTraining: 'التدريب المنتظم:',
        regularTrainingDesc: 'خصص وقتاً يومياً للتدريب',
        errorAnalysis: 'تحليل الأخطاء:',
        errorAnalysisDesc: 'تعلم من أخطائك',
        watchPros: 'مشاهدة المحترفين:',
        watchProsDesc: 'استفد من تجارب اللاعبين المحترفين',
        communityInteraction: 'التواصل مع المجتمع:',
        communityInteractionDesc: 'انضم لمجموعات اللاعبين',
        competitionTips: 'نصائح للتنافس:',
        stayCalm: 'حافظ على هدوئك تحت الضغط',
        learnFromMatches: 'تعلم من كل مباراة',
        developStrategies: 'طور استراتيجياتك باستمرار',
        beSportsmanlike: 'كن رياضياً في الفوز والخسارة',
        usefulResources: 'موارد مفيدة',
        gameGuides: 'أدلة الألعاب',
        gameGuidesDesc: 'مجموعة شاملة من الأدلة والاستراتيجيات لأشهر الألعاب المجانية',
        exploreGuides: 'استكشف الأدلة',
        tutorialVideos: 'فيديوهات تعليمية',
        tutorialVideosDesc: 'مقاطع فيديو تعليمية تغطي أساسيات اللعب والتقنيات المتقدمة',
        watchVideos: 'شاهد الفيديوهات',
        playerCommunity: 'مجتمع اللاعبين',
        playerCommunityDesc: 'انضم لمجتمعنا النشط وشارك تجاربك مع لاعبين آخرين',
        joinCommunity: 'انضم للمجتمع',
        gameStats: 'إحصائيات الألعاب',
        gameStatsDesc: 'إحصائيات مفصلة عن الألعاب الأكثر شعبية والتوجهات الحالية',
        viewStats: 'عرض الإحصائيات',
        bestReviews: 'أفضل المراجعات',
        reviewCategories: 'تصنيفات المراجعات',
        actionGames: 'ألعاب الحركة',
        actionGamesDesc: 'مراجعات لأفضل ألعاب الحركة والقتال المجانية',
        strategyGamesReviews: 'ألعاب الاستراتيجية',
        strategyGamesReviewsDesc: 'تحليل شامل لألعاب الاستراتيجية والتخطيط',
        adventureGamesReviews: 'ألعاب المغامرة',
        adventureGamesReviewsDesc: 'اكتشف عوالم جديدة مع ألعاب المغامرة',
        sportsGames: 'ألعاب الرياضة',
        sportsGamesDesc: 'أفضل ألعاب الرياضة والمنافسة',
        playNow: 'العب الآن',
        features: 'المميزات:',
        cons: 'العيوب:',
        recommendation: 'التوصية:',
        excellentGame: 'لعبة ممتازة للمبتدئين والمحترفين على حد سواء. تستحق التجربة.',
        greatSimulation: 'لعبة رائعة لعشاق المحاكاة. النسخة المجانية جيدة للبداية.',
        highQualityGraphics: 'رسومات عالية الجودة',
        innovativeMechanics: 'آليات لعب مبتكرة',
        continuousUpdates: 'تحديثات مستمرة',
        activeCommunity: 'مجتمع نشط',
        completeCreativeFreedom: 'حرية إبداعية كاملة',
        beautifulGraphics: 'رسومات جميلة',
        richContent: 'محتوى غني',
        easyToPlay: 'سهولة اللعب',
        expensiveDLC: 'حزم إضافية باهظة',
        limitedBaseContent: 'محتوى محدود في النسخة الأساسية',
        uniqueBattleRoyale: 'لعبة Battle Royale مميزة من Respawn Entertainment. تتميز بآليات لعب مبتكرة وقدرات فريدة للشخصيات.',
        lifeSimulation: 'أشهر لعبة محاكاة الحياة. تتيح لك بناء منازل، إنشاء شخصيات، والعيش حياة افتراضية كاملة.',
        allRightsReserved: 'جميع الحقوق محفوظة © 2024 | Games100',
        guidesSubtitle: 'دليل الألعاب المجانية',
        guidesFooterDesc: 'دليل شامل للألعاب المجانية ونصائح مفيدة للاعبين',
        reviewsSubtitle: 'مراجعات الألعاب المجانية',
        reviewsFooterDesc: 'مراجعات شاملة للألعاب المجانية من جميع المتاجر العالمية'
    },
    en: {
        home: 'Home',
        reviews: 'Reviews',
        guides: 'Guides',
        about: 'About',
        guidesTitle: 'Free Games Guide',
        guidesDescription: 'Discover the world of free games through our comprehensive guide. Tips, strategies, and best practices for enjoying free games.',
        reviewsTitle: 'Free Game Reviews',
        reviewsDescription: 'Discover the best free games through comprehensive and detailed reviews. We carefully test each game to provide you with the best recommendations.',
        howToChoose: 'How to Choose Suitable Games',
        howToChooseContent: 'Choosing the right game is important for enjoying the experience. Here are some tips:',
        gameType: 'Determine your preferred game type:',
        gameTypeDesc: 'Do you prefer action games or strategy games?',
        systemRequirements: 'Check system requirements:',
        systemRequirementsDesc: 'Make sure the game is compatible with your device',
        readReviews: 'Read reviews:',
        readReviewsDesc: 'Benefit from other players\' experiences',
        tryDemo: 'Try demo versions:',
        tryDemoDesc: 'Test the game before full download',
        quickTips: 'Quick Tips:',
        startSimple: 'Start with simple games if you\'re a beginner',
        joinCommunity: 'Join player communities for help',
        tryNewTypes: 'Don\'t hesitate to try new types of games',
        performanceTitle: 'Improving Game Performance',
        performanceContent: 'To improve game performance on your device, follow these steps:',
        closePrograms: 'Close unnecessary programs:',
        closeProgramsDesc: 'Free up system memory',
        updateDrivers: 'Update graphics drivers:',
        updateDriversDesc: 'Get the latest versions',
        bestForBeginners: 'Best Games for Beginners',
        bestForBeginnersContent: 'If you\'re new to gaming, here are some recommendations:',
        adventureGames: 'Adventure Games:',
        strategyGames: 'Strategy Games:',
        advancedStrategies: 'Advanced Gaming Strategies',
        advancedStrategiesContent: 'To improve your gaming skills, follow these strategies:',
        skillImprovement: 'Skill Improvement:',
        regularTraining: 'Regular Training:',
        regularTrainingDesc: 'Set aside daily time for training',
        errorAnalysis: 'Error Analysis:',
        errorAnalysisDesc: 'Learn from your mistakes',
        watchPros: 'Watch Professionals:',
        watchProsDesc: 'Benefit from professional players\' experiences',
        communityInteraction: 'Community Interaction:',
        communityInteractionDesc: 'Join player groups',
        competitionTips: 'Competition Tips:',
        stayCalm: 'Stay calm under pressure',
        learnFromMatches: 'Learn from every match',
        developStrategies: 'Continuously develop your strategies',
        beSportsmanlike: 'Be sportsmanlike in victory and defeat',
        usefulResources: 'Useful Resources',
        gameGuides: 'Game Guides',
        gameGuidesDesc: 'Comprehensive collection of guides and strategies for the most popular free games',
        exploreGuides: 'Explore Guides',
        tutorialVideos: 'Tutorial Videos',
        tutorialVideosDesc: 'Educational videos covering gaming basics and advanced techniques',
        watchVideos: 'Watch Videos',
        playerCommunity: 'Player Community',
        playerCommunityDesc: 'Join our active community and share your experiences with other players',
        joinCommunity: 'Join Community',
        gameStats: 'Game Statistics',
        gameStatsDesc: 'Detailed statistics about the most popular games and current trends',
        viewStats: 'View Statistics',
        bestReviews: 'Best Reviews',
        reviewCategories: 'Review Categories',
        actionGames: 'Action Games',
        actionGamesDesc: 'Reviews of the best free action and fighting games',
        strategyGamesReviews: 'Strategy Games',
        strategyGamesReviewsDesc: 'Comprehensive analysis of strategy and planning games',
        adventureGamesReviews: 'Adventure Games',
        adventureGamesReviewsDesc: 'Discover new worlds with adventure games',
        sportsGames: 'Sports Games',
        sportsGamesDesc: 'Best sports and competition games',
        playNow: 'Play Now',
        features: 'Features:',
        cons: 'Cons:',
        recommendation: 'Recommendation:',
        excellentGame: 'Excellent game for both beginners and professionals. Worth trying.',
        greatSimulation: 'Great game for simulation lovers. The free version is good to start with.',
        highQualityGraphics: 'High quality graphics',
        innovativeMechanics: 'Innovative gameplay mechanics',
        continuousUpdates: 'Continuous updates',
        activeCommunity: 'Active community',
        completeCreativeFreedom: 'Complete creative freedom',
        beautifulGraphics: 'Beautiful graphics',
        richContent: 'Rich content',
        easyToPlay: 'Easy to play',
        expensiveDLC: 'Expensive DLC',
        limitedBaseContent: 'Limited content in base version',
        uniqueBattleRoyale: 'Unique Battle Royale game from Respawn Entertainment. Features innovative gameplay mechanics and unique character abilities.',
        lifeSimulation: 'The most famous life simulation game. Allows you to build houses, create characters, and live a complete virtual life.',
        allRightsReserved: 'All rights reserved © 2024 | Games100',
        guidesSubtitle: 'Free Games Guide',
        guidesFooterDesc: 'Comprehensive guide for free games and useful tips for players',
        reviewsSubtitle: 'Free Game Reviews',
        reviewsFooterDesc: 'Comprehensive reviews of free games from all major gaming stores'
    }
};

// دالة تحديث النصوص
function updateTexts() {
    // تحديث روابط Navigation
    const navLinks = document.querySelectorAll('.header-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            switch (href) {
                case 'index.html':
                    link.textContent = translations[lang].home;
                    break;
                case 'reviews.html':
                    link.textContent = translations[lang].reviews;
                    break;
                case 'guides.html':
                    link.textContent = translations[lang].guides;
                    break;
                case 'about.html':
                    link.textContent = translations[lang].about;
                    break;
            }
        }
    });

    // تحديث زر اللغة
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.textContent = lang === 'ar' ? 'EN' : 'AR';
    }

    // تحديث النصوص حسب الصفحة
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('guides.html')) {
        updateGuidesTexts();
    } else if (currentPage.includes('reviews.html')) {
        updateReviewsTexts();
    } else if (currentPage.includes('about.html')) {
        updateAboutTexts();
    }
}

// تحديث نصوص صفحة Guides
function updateGuidesTexts() {
    // العنوان الرئيسي
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.textContent = translations[lang].guidesTitle;
    }

    // الوصف
    const heroDescription = document.querySelector('.hero-description');
    if (heroDescription) {
        heroDescription.textContent = translations[lang].guidesDescription;
    }

    // تحديث جميع النصوص في الصفحة
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
}

// تحديث نصوص صفحة Reviews
function updateReviewsTexts() {
    // العنوان الرئيسي
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.textContent = translations[lang].reviewsTitle;
    }

    // الوصف
    const heroDescription = document.querySelector('.hero-description');
    if (heroDescription) {
        heroDescription.textContent = translations[lang].reviewsDescription;
    }

    // تحديث جميع النصوص في الصفحة
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
}

// تحديث نصوص صفحة About
function updateAboutTexts() {
    // تحديث جميع النصوص في الصفحة باستخدام data-ar و data-en
    const elements = document.querySelectorAll('[data-ar][data-en]');
    elements.forEach((element, index) => {
        // إضافة تأثير انتقالي
        element.style.opacity = '0.7';
        element.style.transform = 'translateY(5px)';
        
        setTimeout(() => {
            if (lang === 'ar') {
                element.textContent = element.getAttribute('data-ar');
            } else {
                element.textContent = element.getAttribute('data-en');
            }
            
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 50);
    });
    
    // تحديث عنوان الصفحة
    if (lang === 'ar') {
        document.title = 'عن الموقع - Games100';
    } else {
        document.title = 'About Us - Games100';
    }
}

// دالة تبديل اللغة
function initLanguageToggle() {
    const langBtn = document.getElementById('langBtn');
    if (!langBtn) return;

    // تحديث حالة الزر الأولية
    langBtn.textContent = lang === 'ar' ? 'EN' : 'AR';
    
    langBtn.addEventListener('click', function() {
        // تغيير اللغة
        lang = (lang === 'ar') ? 'en' : 'ar';
        
        // تحديث localStorage
        localStorage.setItem('games100_language', lang);
        
        // تحديث النصوص
        updateTexts();
        
        // تحديث اتجاه الصفحة
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
        document.documentElement.lang = lang;
    });
}

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحديث النصوص الأولية
    updateTexts();
    
    // تهيئة زر تغيير اللغة
    initLanguageToggle();
    
    // تحديث اتجاه الصفحة
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
});

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