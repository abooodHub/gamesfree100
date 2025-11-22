// --- بيانات المتاجر ---
let gamesData = {
    steam: null, epic: null, gog: null
};
let allGames = [];
let lang = 'ar';
let tab = 'all';
let theme = localStorage.getItem('games100_theme') || 'dark';
const themes = ['dark', 'light', 'ocean', 'violet'];
let countdownId = null;


const storeNames = {
    ar: {
        steam: 'ستيم',
        epic: 'إيبك',
        gog: 'جوج',
        all: 'الكل',
        shop: 'رابط الشراء',
        old: 'السعر الأصلي',
        new: 'السعر بعد الخصم',
        update: 'آخر تحديث',
        noGames: 'لا توجد ألعاب مجانية حالياً',
        percent: 'خصم',
        newGame: 'جديد',
        newGamesFound: 'تم العثور على ألعاب مجانية جديدة!',
        notificationsEnabled: 'تم تفعيل التنبيهات',
        notificationsDisabled: 'تم إيقاف التنبيهات',
        viewNewGames: 'عرض الألعاب الجديدة',
        markAllSeen: 'وضع علامة كمشاهد',
        notifications: 'التنبيهات',
        endsIn: 'ينتهي في',
        daysLeft: 'يوم متبقي',
        hoursLeft: 'ساعة متبقية',
        endingSoon: 'ينتهي قريباً'
    },
    en: {
        steam: 'Steam',
        epic: 'Epic',
        gog: 'GOG',
        all: 'All',
        shop: 'Shop Link',
        old: 'Old Price',
        new: 'New Price',
        update: 'Last Update',
        noGames: 'No free games found',
        percent: 'OFF',
        newGame: 'New',
        newGamesFound: 'New free games found!',
        notificationsEnabled: 'Notifications enabled',
        notificationsDisabled: 'Notifications disabled',
        viewNewGames: 'View New Games',
        markAllSeen: 'Mark All as Seen',
        notifications: 'Notifications',
        endsIn: 'Ends in',
        daysLeft: 'days left',
        hoursLeft: 'hours left',
        endingSoon: 'Ending soon'
    }
};


function showNotificationPanel() {
    return;
}


// --- تحميل البيانات ---
function fetchAllData() {
    const files = [
        ['steam', 'free_goods_detail.json'],
        ['epic', 'epic_goods_detail.json'],
        ['gog', 'gog_goods_detail.json']
    ];

    let loaded = 0;
    const totalFiles = files.length;

    // إظهار حالة التحميل
    showLoading();

    files.forEach(([key, file]) => {
        // إضافة timestamp لتجنب cache المتصفح
        const cacheBuster = '?t=' + Date.now();
        fetch(file + cacheBuster)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                let data = {};
                try {
                    if (text && text.trim().length) {
                        data = JSON.parse(text);
                    }
                } catch (e) {
                    data = {};
                }
                return data;
            })
            .then(data => {
                gamesData[key] = data;
                loaded++;
                console.log(`تم تحميل ${key}: ${file}`);
                if (loaded === totalFiles) {
                    mergeAllGames();
                    renderGames();
                    updateBar();
                    startUpdateCountdown();
                    updateHomeCount();
                    hideLoading();

                }
            })
            .catch(error => {
                console.error(`Error loading ${file}:`, error);
                loaded++;
                if (loaded === totalFiles) {
                    mergeAllGames();
                    renderGames();
                    updateBar();
                    startUpdateCountdown();
                    updateHomeCount();
                    hideLoading();
                }
            });
    });

    // إعداد auto-refresh للبيانات كل 6 ساعات
    setupAutoRefresh();
}

// آلية auto-refresh للبيانات
function setupAutoRefresh() {
    // تحديث البيانات كل 6 ساعات (6 * 60 * 60 * 1000 = 21600000 ms)
    const refreshInterval = 6 * 60 * 60 * 1000;

    setInterval(() => {
        console.log('🔄 تحديث تلقائي للبيانات...');
        fetchAllData();
    }, refreshInterval);

    console.log('✅ تم تفعيل التحديث التلقائي كل 6 ساعات');
}


function mergeAllGames() {
    allGames = [];
    Object.keys(gamesData).forEach(key => {
        const d = gamesData[key];
        if (!d) return;
        const add = (g) => { allGames.push({ ...g, _store: key }); };

        // خصومات 100% فقط من جميع المتاجر
        if (Array.isArray(d.discounted_games)) {
            d.discounted_games.forEach(g => {
                const discount = g[6];
                if (discount && discount.includes('100%')) add(g);
            });
        }
        if (Array.isArray(d.discounted_list)) {
            d.discounted_list.forEach(g => {
                const discount = g[6];
                if (discount && discount.includes('100%')) add(g);
            });
        }

        // Epic فقط: خصم 100% من free_games/free_list مع استبعاد Coming Soon و"مجاني دائماً"
        if (key !== 'steam') {
            if (Array.isArray(d.free_games)) {
                d.free_games.forEach(g => {
                    const t = g[6];
                    if (t && t.includes('100%') && !t.includes('Coming Soon') && !t.includes('مجاني دائماً')) add(g);
                });
            }
            if (Array.isArray(d.free_list)) {
                d.free_list.forEach(g => {
                    const t = g[6];
                    if (t && t.includes('100%') && !t.includes('Coming Soon') && !t.includes('مجاني دائماً')) add(g);
                });
            }
        }
        // Steam: تجاهل free_games/free_list لأنها ليست خصم 100%
    });
    console.log(`تم دمج ${allGames.length} لعبة (خصم 100% فقط)`);
}

// --- عرض الألعاب ---
function renderGames() {
    let grid = document.getElementById('gamesGrid');
    grid.innerHTML = '';

    let list = [];
    if (tab === 'all') {
        list = allGames;
    } else {
        list = allGames.filter(g => g._store === tab);
    }

    console.log(`عرض ${list.length} لعبة للتبويب: ${tab}`);

    if (!list.length) {
        grid.innerHTML = `<div class="no-games">${storeNames[lang].noGames}</div>`;
        return;
    }

    list.forEach(game => {
        const card = gameCard(game);
        grid.appendChild(card);
    });
}

function gameCard(game) {

    let img = '';
    if (game._store === 'steam') {
        let header = game[2];
        let capsule = game[3];
        img = `<img src="${header}" class="game-thumb" alt="${game[0]}" loading="lazy" onerror="if(this.src!==this.getAttribute('data-capsule')){this.src=this.getAttribute('data-capsule');}else{this.onerror=null;this.src='https://via.placeholder.com/300x150/222/fff?text=Steam';}" data-capsule="${capsule}">`;
    } else if (game[2] && game[2].startsWith('http')) {
        img = `<img src="${game[2]}" class="game-thumb" alt="${game[0]}" loading="lazy" onerror="this.onerror=null;this.src='https://via.placeholder.com/120x120/222/fff?text=No+Image';">`;
    } else {
        img = `<div class="game-thumb"></div>`;
    }

    let store = '';
    if (game._store) {
        let iconPath = '';
        switch (game._store) {
            case 'steam': iconPath = 'icons/steam.svg'; break;
            case 'epic': iconPath = 'icons/Epic.svg'; break;
            case 'gog': iconPath = 'icons/gog.svg'; break;
            default: iconPath = '';
        }
        store = `<div class="store-badge" style="display: flex; align-items: center; gap: 6px;">
            ${iconPath ? `<img src='${iconPath}' class='card-store-icon' alt='${game._store}'>` : ''}
            <span>${storeNames[lang][game._store] || game._store}</span>
        </div>`;
    }

    let discount = '';
    // التحقق من الخصم في البنية الجديدة (game[6] للخصم)
    if (game[6] && (game[6].includes('خصم') || game[6].includes('OFF') || game[6].includes('%') || game[6].includes('Coming Soon'))) {
        discount = `<div class="discount-badge">${game[6]}</div>`;
    } else if (game[4] && (game[4].includes('خصم') || game[4].includes('OFF') || game[4].includes('Coming Soon'))) {
        discount = `<div class="discount-badge">${game[4]}</div>`;
    }

    // دالة مساعدة للتحقق من أن النص هو سعر وليس تاريخ
    function isValidPrice(val) {
        if (!val) return false;
        if (typeof val !== 'string') val = String(val);
        // إذا كان يحتوي على تاريخ أو وقت
        if (val.match(/\d{2}:\d{2}:\d{2}/) || val.match(/\d{4}-\d{2}-\d{2}/)) return false;
        // إذا كان يحتوي على أرقام أو كلمة مجاني أو $ أو SR
        if (val.match(/\d/) || val.includes('مجاني') || val.includes('$') || val.includes('SR') || val.toLowerCase().includes('free')) return true;
        return false;
    }
    let priceRow = '';
    let priceInfo = '';

    // للبنية الجديدة: game[4] = السعر القديم، game[5] = السعر الجديد
    if (isValidPrice(game[4]) && isValidPrice(game[5]) && game[4] !== game[5]) {
        priceRow = `
            <div class="price-row">
                <span class="old-price">${game[4]}</span>
                <span class="new-price">${game[5]}</span>
            </div>
        `;
        priceInfo = `
            <div class="price-info">
                <span class="price-label" data-ar="السعر الأصلي" data-en="Original Price">السعر الأصلي:</span>
                <span class="price-value old">${game[4]}</span>
                <span class="price-label" data-ar="السعر بعد الخصم" data-en="Discounted Price">السعر بعد الخصم:</span>
                <span class="price-value new">${game[5]}</span>
            </div>
        `;
    } else if (isValidPrice(game[5]) && isValidPrice(game[6]) && game[5] !== game[6]) {
        // للبنية القديمة
        priceRow = `
            <div class="price-row">
                <span class="old-price">${game[5]}</span>
                <span class="new-price">${game[6]}</span>
            </div>
        `;
        priceInfo = `
            <div class="price-info">
                <span class="price-label" data-ar="السعر الأصلي" data-en="Original Price">السعر الأصلي:</span>
                <span class="price-value old">${game[5]}</span>
                <span class="price-label" data-ar="السعر بعد الخصم" data-en="Discounted Price">السعر بعد الخصم:</span>
                <span class="price-value new">${game[6]}</span>
            </div>
        `;
    } else if (isValidPrice(game[4]) || isValidPrice(game[5])) {
        // عرض السعر الحالي فقط إذا كان متوفراً
        const currentPrice = isValidPrice(game[5]) ? game[5] : game[4];
        priceInfo = `
            <div class="price-info">
                <span class="price-label" data-ar="السعر الحالي" data-en="Current Price">السعر الحالي:</span>
                <span class="price-value current">${currentPrice}</span>
            </div>
        `;
    }

    // إضافة عرض تاريخ انتهاء الخصم
    let endDateInfo = '';

    // البحث عن تاريخ الانتهاء في مواقع مختلفة من المصفوفة
    let endDate = null;

    // Epic Games: game[7]
    if (game[7] && game[7] !== 'null' && game[7] !== 'None') {
        endDate = game[7];
    }
    else if (game[4] && game[4] !== 'null' && game[4] !== 'None' && typeof game[4] === 'string' && game[4].includes('-')) {
        endDate = game[4];
    }
    // Steam: game[6] (إذا كان تاريخ)
    else if (game[6] && game[6] !== 'null' && game[6] !== 'None' && typeof game[6] === 'string' && game[6].includes('-')) {
        endDate = game[6];
    }

    if (endDate) {
        try {
            const endDateObj = new Date(endDate);
            const now = new Date();
            const timeLeft = endDateObj - now;
            if (timeLeft > 0) {
                const days = Math.ceil(timeLeft / (1000 * 60 * 60 * 24));
                const timeText = days > 0 ? `${days} ${storeNames[lang].daysLeft}` : storeNames[lang].endingSoon;
                endDateInfo = `
                    <div class="end-date-info">
                        <span class="end-date-label" data-ar="${storeNames.ar.endsIn}" data-en="${storeNames.en.endsIn}">${storeNames[lang].endsIn}:</span>
                        <span class="end-date-value">${timeText}</span>
                    </div>
                `;
            }
        } catch (e) {
            console.log('خطأ في تحليل تاريخ الانتهاء:', e);
        }
    }

    return htmlToElement(`
        <div class="game-card fade-in" style="position: relative;">
            ${store}
            ${discount}
            ${img}
            <div class="game-title">${escapeHtml(game[0])}</div>
            ${priceInfo}
            ${priceRow}
            ${endDateInfo}
            <a href="${game[1]}" class="btn-shop" target="_blank" rel="noopener noreferrer">
                ${storeNames[lang].shop}
            </a>
        </div>
    `);
}


function htmlToElement(html) {
    let template = document.createElement('template');
    template.innerHTML = html.trim();
    return template.content.firstChild;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// --- تحديث شريط التحديث ---
function updateBar() {
    let times = Object.values(gamesData)
        .map(d => d && d.update_time)
        .filter(Boolean);

    let last = times.sort().reverse()[0] || '';
    const bar = document.getElementById('updateBar');
    if (!bar) return;
    bar.innerHTML = `${storeNames[lang].update}: ${last} • ${lang === 'ar' ? 'التحديث القادم خلال' : 'Next update in'}: <span id="nextUpdateCountdown">--:--:--</span>`;
}

function parseUpdateTime(str) {
    if (!str || typeof str !== 'string') return null;
    const m = str.match(/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/);
    if (!m) return null;
    const y = parseInt(m[1], 10), mo = parseInt(m[2], 10) - 1, d = parseInt(m[3], 10), h = parseInt(m[4], 10), mi = parseInt(m[5], 10), s = parseInt(m[6], 10);
    return new Date(y, mo, d, h, mi, s);
}

function startUpdateCountdown() {
    if (countdownId) {
        clearInterval(countdownId);
        countdownId = null;
    }
    const times = Object.values(gamesData)
        .map(d => d && d.update_time)
        .filter(Boolean);
    const lastStr = times.sort().reverse()[0] || '';
    const lastDate = parseUpdateTime(lastStr) || new Date();
    const period = 6 * 60 * 60 * 1000;
    countdownId = setInterval(() => {
        const el = document.getElementById('nextUpdateCountdown');
        if (!el) return;
        const now = new Date();
        let diff = period - ((now - lastDate) % period);
        if (diff <= 0 || isNaN(diff)) diff = period;
        const hh = Math.floor(diff / 3600000);
        const mm = Math.floor((diff % 3600000) / 60000);
        const ss = Math.floor((diff % 60000) / 1000);
        const pad = n => String(n).padStart(2, '0');
        el.textContent = `${pad(hh)}:${pad(mm)}:${pad(ss)}`;
    }, 1000);
}

// --- حالات التحميل ---
function showLoading() {
    const grid = document.getElementById('gamesGrid');
    grid.innerHTML = `
        <div class="no-games">
            <div class="loading"></div>
            <div>جاري تحميل البيانات...</div>
        </div>
    `;
}

function hideLoading() {
    // سيتم استبدالها بـ renderGames()
}

// --- التبويبات ---
function initTabs() {
    document.querySelectorAll('.tab').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab').forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
                b.setAttribute('tabindex', '-1');
            });
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');
            this.setAttribute('tabindex', '0');
            tab = this.getAttribute('data-tab');
            renderGames();
            this.focus();
        });
    });
}

// --- تحديث التبويبات مع الأيقونات ---
function updateTabs() {
    document.querySelectorAll('.tab').forEach(btn => {
        const t = btn.getAttribute('data-tab');
        let iconPath = '';
        switch (t) {
            case 'steam': iconPath = 'icons/steam.svg'; break;
            case 'epic': iconPath = 'icons/Epic.svg'; break;
            case 'gog': iconPath = 'icons/gog.svg'; break;
            default: iconPath = '';
        }
        const label = storeNames[lang][t] || t;
        btn.innerHTML = iconPath ? `<img src="${iconPath}" class="tab-icon" style="width:20px;vertical-align:middle;margin-${lang === 'ar' ? 'left' : 'right'}:8px;">${label}` : label;
    });
}

// --- تبديل اللغة ---
function initLanguageToggle() {
    const langBtn = document.getElementById('langBtn');
    if (!langBtn) return;

    // تحديث حالة الزر الأولية
    updateLanguageButtonState();

    langBtn.addEventListener('click', function () {
        // تغيير اللغة
        lang = (lang === 'ar') ? 'en' : 'ar';

        // تحديث localStorage
        localStorage.setItem('games100_language', lang);

        // تحديث الواجهة
        updateInterface();

        // إذا كان هناك نظام ترجمة متاح، استخدمه
        if (typeof switchLanguage === 'function') {
            switchLanguage(lang);
        }
    });
}

// تحديث حالة زر اللغة
function updateLanguageButtonState() {
    const langBtn = document.getElementById('langBtn');
    if (!langBtn) return;

    // تحميل اللغة المحفوظة
    const savedLang = localStorage.getItem('games100_language');
    if (savedLang) {
        lang = savedLang;
    }

    // تحديث نص الزر
    langBtn.textContent = lang === 'ar' ? 'EN' : 'AR';

    // تحديث الأنماط
    langBtn.style.cssText = `
        background: rgba(126, 214, 223, 0.2);
        border: 1px solid rgba(126, 214, 223, 0.4);
        border-radius: 12px;
        padding: 8px 16px;
        color: var(--text);
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    `;

    // تحديث اتجاه الصفحة
    document.body.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;

    // إذا كان هناك نظام ترجمة متاح، استخدمه
    if (typeof switchLanguage === 'function') {
        switchLanguage(lang);
    }
}

// تحديث واجهة الموقع بالكامل
function updateInterface() {
    applyTheme();
    // تحديث حالة زر اللغة
    updateLanguageButtonState();

    // تحديث الشعار
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.innerHTML = '🎮 Games100';
        logo.style.direction = 'ltr'; // دائماً من اليسار لليمين
    }

    // تحديث روابط Navigation
    updateNavigationLinks();

    // تحديث التبويبات
    document.querySelectorAll('.tab').forEach(btn => {
        const t = btn.getAttribute('data-tab');
        if (t && storeNames[lang][t]) {
            btn.textContent = storeNames[lang][t];

            // تحديث أنماط التبويبات
            btn.style.cssText = `
                transition: all 0.3s ease;
                ${lang === 'ar' ? 'font-family: "Tajawal", sans-serif;' : ''}
            `;
        }
    });
    // تحديث الأيقونات مع النصوص
    updateTabs();

    // تحديث محتوى التذييل
    updateFooterContent();

    // تحديث شريط التحديث
    updateBar();
    startUpdateCountdown();
    updateHomeCount();

    // تحديث الألعاب والبادجات
    const updateGamesAndBadges = () => {
        renderGames();
    };

    // تأخير قصير لضمان اكتمال التحديثات
    setTimeout(updateGamesAndBadges, 50);

    // تحديث إشعار ملفات تعريف الارتباط
    updateCookieBannerText();

    // إذا كان هناك نظام ترجمة متاح، استخدمه للصفحات الأخرى
    if (typeof switchLanguage === 'function' && (window.location.pathname.includes('guides.html') || window.location.pathname.includes('reviews.html'))) {
        switchLanguage(lang);
    }
}

function updateHomeCount() {
    const link = document.querySelector('.header-nav .nav-link[href="index.html"]');
    if (!link) return;
    const label = lang === 'ar' ? 'الرئيسية' : 'Home';
    const count = Array.isArray(allGames) ? allGames.length : 0;
    link.textContent = `🏠 ${label}${count ? ` (${count})` : ''}`;
}

// --- تحديث روابط Navigation ---
function updateNavigationLinks() {
    const navLinks = document.querySelectorAll('.header-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === 'index.html') {
            link.textContent = lang === 'ar' ? 'الرئيسية' : 'Home';
        }
    });
}

// --- تحديث محتوى التذييل ---
function updateFooterContent() {
    // تحديث العناصر ذات البيانات متعددة اللغات
    document.querySelectorAll('[data-ar][data-en]').forEach(element => {
        // تجاهل عناصر التحكم في التنبيهات
        if (element.hasAttribute('data-notification-control')) {
            return;
        }

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


}



// --- إدارة ملفات تعريف الارتباط ---
function initCookieConsent() {
    const banner = document.getElementById('cookieConsent');
    if (banner) {
        banner.style.display = 'none';
    }
}

function acceptCookies() {
    localStorage.setItem('cookieConsent', 'accepted');
    document.getElementById('cookieConsent').style.display = 'none';
    // تم قبول ملفات تعريف الارتباط
}

function rejectCookies() {
    localStorage.setItem('cookieConsent', 'rejected');
    document.getElementById('cookieConsent').style.display = 'none';
    // تم رفض ملفات تعريف الارتباط
}

function updateCookieBannerText() {
    const banner = document.getElementById('cookieConsent');
    if (!banner) return;

    const elements = banner.querySelectorAll('[data-ar]');
    elements.forEach(element => {
        if (lang === 'en') {
            element.textContent = element.getAttribute('data-en');
        } else {
            element.textContent = element.getAttribute('data-ar');
        }
    });
}

// --- تهيئة التطبيق ---
function initApp() {
    // تهيئة نظام اللغة
    initLanguageToggle();

    initThemeToggle();

    // تهيئة باقي المكونات
    initTabs();
    initCookieConsent();

    // تحديث الواجهة بالكامل
    updateInterface();

    // تحميل البيانات (فقط للصفحة الرئيسية)
    if (window.location.pathname.includes('index.html') || window.location.pathname === '/' || window.location.pathname === '') {
        fetchAllData();
    }
}

// --- تشغيل التطبيق عند تحميل الصفحة ---
document.addEventListener('DOMContentLoaded', initApp);

// --- Service Worker للتخزين المؤقت (اختياري) ---
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
function applyTheme() {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('themeBtn');
    if (btn) {
        let icon = '🌙';
        if (theme === 'light') icon = '☀️';
        else if (theme === 'ocean') icon = '🌊';
        else if (theme === 'violet') icon = '💜';
        btn.textContent = icon;
    }
}

function initThemeToggle() {
    applyTheme();
    const btn = document.getElementById('themeBtn');
    if (!btn) return;
    btn.addEventListener('click', function () {
        if (!themes.includes(theme)) theme = 'dark';
        const idx = themes.indexOf(theme);
        theme = themes[(idx + 1) % themes.length];
        localStorage.setItem('games100_theme', theme);
        applyTheme();
    });
}