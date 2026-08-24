// بيانات المتاجر والحالة العامة
const gamesData = { steam: null, epic: null };
let allGames = [];
let lang = 'ar';
let tab = 'all';
let theme = safeStorageGet('games100_theme') || 'dark';
let hasLoadedData = false;
let refreshIntervalId = null;
let expiryIntervalId = null;
let countdownId = null;

const themes = ['dark', 'light', 'ocean', 'violet'];
const DATA_REFRESH_MS = 6 * 60 * 60 * 1000;
const EXPIRY_CHECK_MS = 60 * 1000;
const STEAM_MISSING_END_MAX_AGE_MS = 12 * 60 * 60 * 1000;
const ANALYTICS_ID = 'G-QXTT04YVZT';

const storeNames = {
    ar: {
        steam: 'ستيم', epic: 'إيبك', all: 'الكل',
        shop: 'رابط الحصول على العرض',
        shopFor: (title, store) => `احصل على ${title} من ${store}`,
        update: 'آخر تحديث', nextUpdate: 'التحديث القادم خلال',
        noGames: 'لا توجد ألعاب مجانية حالياً', loading: 'جاري تحميل العروض...',
        loadError: 'تعذر تحميل بيانات الألعاب. تحقق من الاتصال ثم حاول مجدداً.',
        partialError: stores => `تعذر تحديث: ${stores}. يتم عرض البيانات المتاحة.`,
        retry: 'إعادة المحاولة', endsIn: 'ينتهي خلال', daysLeft: 'يوم', hoursLeft: 'ساعة',
        currentPrice: 'السعر الحالي', originalPrice: 'السعر الأصلي', discountedPrice: 'السعر بعد الخصم',
        home: 'الرئيسية', skip: 'تخطي إلى قائمة الألعاب', theme: 'تغيير المظهر',
        language: 'Switch to English', gamesLabel: 'قائمة الألعاب المجانية',
        tabsLabel: 'تصفية حسب متجر الألعاب',
        consentText: 'نستخدم ملفات قياس اختيارية لتحسين الموقع. لن يتم تشغيل Google Analytics إلا بعد موافقتك.',
        accept: 'موافق', reject: 'رفض'
    },
    en: {
        steam: 'Steam', epic: 'Epic', all: 'All',
        shop: 'Get this offer',
        shopFor: (title, store) => `Get ${title} from ${store}`,
        update: 'Last update', nextUpdate: 'Next update in',
        noGames: 'No free games found', loading: 'Loading offers...',
        loadError: 'Could not load game data. Check your connection and try again.',
        partialError: stores => `Could not refresh: ${stores}. Showing available data.`,
        retry: 'Try again', endsIn: 'Ends in', daysLeft: 'days', hoursLeft: 'hours',
        currentPrice: 'Current price', originalPrice: 'Original price', discountedPrice: 'Discounted price',
        home: 'Home', skip: 'Skip to the games list', theme: 'Change theme',
        language: 'التبديل إلى العربية', gamesLabel: 'Free games list',
        tabsLabel: 'Filter by game store',
        consentText: 'We use optional measurement cookies to improve the site. Google Analytics will only load after you consent.',
        accept: 'Accept', reject: 'Reject'
    }
};

function safeStorageGet(key) {
    try { return localStorage.getItem(key); } catch { return null; }
}

function safeStorageSet(key, value) {
    try { localStorage.setItem(key, value); } catch { /* التخزين اختياري */ }
}

function loadInitialState() {
    const params = new URLSearchParams(window.location.search);
    const requestedLang = params.get('lang');
    const requestedTab = params.get('tab');
    const savedLang = safeStorageGet('games100_language');

    if (requestedLang === 'ar' || requestedLang === 'en') lang = requestedLang;
    else if (savedLang === 'ar' || savedLang === 'en') lang = savedLang;

    if (requestedTab === 'steam' || requestedTab === 'epic' || requestedTab === 'all') tab = requestedTab;
}

function syncUrlState() {
    const url = new URL(window.location.href);
    if (lang === 'ar') url.searchParams.delete('lang');
    else url.searchParams.set('lang', lang);
    if (tab === 'all') url.searchParams.delete('tab');
    else url.searchParams.set('tab', tab);
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
}

function createElement(tag, options = {}) {
    const element = document.createElement(tag);
    if (options.className) element.className = options.className;
    if (options.text !== undefined) element.textContent = String(options.text);
    if (options.attrs) {
        Object.entries(options.attrs).forEach(([name, value]) => {
            if (value !== null && value !== undefined) element.setAttribute(name, String(value));
        });
    }
    return element;
}

function safeHttpsUrl(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
        const url = new URL(value, window.location.origin);
        return url.protocol === 'https:' ? url.href : null;
    } catch { return null; }
}

function safeStoreUrl(value, store) {
    const allowedHosts = {
        steam: new Set(['store.steampowered.com']),
        epic: new Set(['store.epicgames.com'])
    };
    const safeUrl = safeHttpsUrl(value);
    if (!safeUrl || !allowedHosts[store]) return null;
    const url = new URL(safeUrl);
    return allowedHosts[store].has(url.hostname.toLowerCase()) ? url.href : null;
}

function parseDateTime(value, legacyOffset = 'Z') {
    if (!value || typeof value !== 'string') return null;
    const text = value.trim();
    let normalized = text;
    if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(text)) normalized = `${text.replace(' ', 'T')}${legacyOffset}`;
    else if (/^\d{4}-\d{2}-\d{2}$/.test(text)) normalized = `${text}T00:00:00${legacyOffset}`;
    const parsed = new Date(normalized);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function isGameExpired(game) {
    if (game.endAt) {
        const endDate = parseDateTime(game.endAt, 'Z');
        return endDate ? endDate.getTime() <= Date.now() : false;
    }
    if (game.store === 'steam' && game.discount.includes('100%')) {
        const updateTime = gamesData.steam && gamesData.steam.update_time;
        const updatedAt = parseDateTime(updateTime, '+03:00');
        if (updatedAt) return updatedAt.getTime() + STEAM_MISSING_END_MAX_AGE_MS <= Date.now();
    }
    return false;
}

function normalizePublicDeal(rawDeal) {
    if (!rawDeal || typeof rawDeal !== 'object') return null;
    if (!['steam', 'epic'].includes(rawDeal.store)) return null;
    const title = String(rawDeal.title || '').trim();
    const url = String(rawDeal.url || '').trim();
    if (!title || !safeStoreUrl(url, rawDeal.store)) return null;
    return {
        title,
        url,
        image: String(rawDeal.image || ''),
        capsule: String(rawDeal.fallback_image || ''),
        originalPrice: String(rawDeal.original_price || ''),
        currentPrice: String(rawDeal.current_price || ''),
        discount: String(rawDeal.discount_label || ''),
        endAt: rawDeal.end_at ? String(rawDeal.end_at) : null,
        store: rawDeal.store
    };
}

async function loadPublicFeed() {
    const response = await fetch('deals.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`deals.json: HTTP ${response.status}`);
    const data = await response.json();
    if (!data || data.schema_version !== 1 || !Array.isArray(data.deals) || !data.sources) {
        throw new Error('deals.json: invalid data schema');
    }
    return data;
}

async function fetchAllData() {
    const hadExistingData = hasLoadedData;
    setDataStatus('', 'info');
    if (!hadExistingData) showLoading();

    try {
        const feed = await loadPublicFeed();
        gamesData.steam = { update_time: feed.sources.steam && feed.sources.steam.last_success };
        gamesData.epic = { update_time: feed.sources.epic && feed.sources.epic.last_success };
        allGames = feed.deals
            .map(normalizePublicDeal)
            .filter(Boolean)
            .filter(game => !isGameExpired(game));
        hasLoadedData = true;
        renderGames();
        updateBar();
        startUpdateCountdown();
        updateHomeCount();
        setDataStatus('', 'info');
        if (!expiryIntervalId) setupExpiredGamesCheck();
    } catch (error) {
        console.error('Failed to load public deals feed:', error);
        if (!hadExistingData) {
            hasLoadedData = false;
            renderLoadError();
        }
        setDataStatus(storeNames[lang].loadError, 'error');
    }
}

function setupAutoRefresh() {
    if (refreshIntervalId) return;
    refreshIntervalId = window.setInterval(fetchAllData, DATA_REFRESH_MS);
}

function setupExpiredGamesCheck() {
    if (expiryIntervalId) return;
    expiryIntervalId = window.setInterval(() => {
        const previousCount = allGames.length;
        allGames = allGames.filter(game => !isGameExpired(game));
        if (allGames.length !== previousCount) {
            renderGames();
            updateHomeCount();
        }
    }, EXPIRY_CHECK_MS);
}

function setDataStatus(message, type) {
    const status = document.getElementById('dataStatus');
    if (!status) return;
    status.textContent = message;
    status.className = `data-status ${type || 'info'}`;
    status.hidden = !message;
}

function renderMessage(message, withRetry = false) {
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const wrapper = createElement('div', { className: 'no-games' });
    wrapper.appendChild(createElement('p', { text: message }));
    if (withRetry) {
        const retryButton = createElement('button', { className: 'retry-btn', text: storeNames[lang].retry, attrs: { type: 'button' } });
        retryButton.addEventListener('click', fetchAllData);
        wrapper.appendChild(retryButton);
    }
    grid.appendChild(wrapper);
}

function showLoading() {
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const wrapper = createElement('div', { className: 'no-games' });
    wrapper.appendChild(createElement('div', { className: 'loading', attrs: { 'aria-hidden': 'true' } }));
    wrapper.appendChild(createElement('p', { text: storeNames[lang].loading }));
    grid.appendChild(wrapper);
}

function renderLoadError() { renderMessage(storeNames[lang].loadError, true); }

function renderGames() {
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const visibleGames = tab === 'all' ? allGames : allGames.filter(game => game.store === tab);
    if (!visibleGames.length) {
        renderMessage(storeNames[lang].noGames);
        return;
    }
    const fragment = document.createDocumentFragment();
    visibleGames.forEach((game, index) => fragment.appendChild(gameCard(game, index)));
    grid.appendChild(fragment);
}

function createGameImage(game, isFirstCard) {
    const source = safeHttpsUrl(game.image);
    if (!source) return createElement('div', { className: 'game-thumb game-thumb-placeholder' });
    const image = createElement('img', {
        className: 'game-thumb',
        attrs: { src: source, alt: game.title, loading: isFirstCard ? 'eager' : 'lazy', decoding: 'async' }
    });
    if (isFirstCard) image.setAttribute('fetchpriority', 'high');
    const capsule = safeHttpsUrl(game.capsule);
    image.addEventListener('error', () => {
        if (capsule && image.src !== capsule) {
            image.src = capsule;
            return;
        }
        image.replaceWith(createElement('div', { className: 'game-thumb game-thumb-placeholder', attrs: { 'aria-label': game.title } }));
    });
    return image;
}

function appendPriceInfo(card, game) {
    const original = game.originalPrice.trim();
    const current = game.currentPrice.trim();
    if (!original && !current) return;
    const priceInfo = createElement('div', { className: 'price-info' });
    const appendPair = (label, value, valueClass) => {
        priceInfo.appendChild(createElement('span', { className: 'price-label', text: label }));
        priceInfo.appendChild(createElement('span', { className: `price-value ${valueClass}`, text: value }));
    };
    if (original && current && original !== current) {
        appendPair(storeNames[lang].originalPrice, original, 'old');
        appendPair(storeNames[lang].discountedPrice, current, 'new');
    } else appendPair(storeNames[lang].currentPrice, current || original, 'current');
    card.appendChild(priceInfo);
}

function appendEndDate(card, game) {
    const endDate = parseDateTime(game.endAt || '', 'Z');
    if (!endDate) return;
    const timeLeft = endDate.getTime() - Date.now();
    if (timeLeft <= 0) return;
    const hours = Math.max(1, Math.ceil(timeLeft / (60 * 60 * 1000)));
    const value = hours < 24 ? `${hours} ${storeNames[lang].hoursLeft}` : `${Math.ceil(hours / 24)} ${storeNames[lang].daysLeft}`;
    const wrapper = createElement('div', { className: 'end-date-info' });
    wrapper.appendChild(createElement('span', { className: 'end-date-label', text: `${storeNames[lang].endsIn}: ` }));
    wrapper.appendChild(createElement('span', { className: 'end-date-value', text: value }));
    card.appendChild(wrapper);
}

function gameCard(game, index) {
    const card = createElement('article', { className: 'game-card fade-in' });
    const storeBadge = createElement('div', { className: 'store-badge' });
    storeBadge.append(
        createElement('img', {
            className: 'card-store-icon',
            attrs: { src: game.store === 'steam' ? 'icons/steam.svg' : 'icons/Epic.svg', alt: '', 'aria-hidden': 'true' }
        }),
        createElement('span', { text: storeNames[lang][game.store] })
    );
    card.appendChild(storeBadge);
    if (game.discount) card.appendChild(createElement('div', { className: 'discount-badge', text: game.discount }));
    card.appendChild(createGameImage(game, index === 0));
    card.appendChild(createElement('h2', { className: 'game-title', text: game.title }));
    appendPriceInfo(card, game);
    appendEndDate(card, game);

    const shopUrl = safeStoreUrl(game.url, game.store);
    if (shopUrl) {
        const storeLabel = storeNames[lang][game.store];
        card.appendChild(createElement('a', {
            className: 'btn-shop', text: storeNames[lang].shop,
            attrs: { href: shopUrl, target: '_blank', rel: 'noopener noreferrer', 'aria-label': storeNames[lang].shopFor(game.title, storeLabel) }
        }));
    }
    return card;
}

function getLatestUpdateTime() {
    return Object.values(gamesData).map(data => data && data.update_time).filter(Boolean).sort().reverse()[0] || '';
}

function formatUpdateTime(value) {
    const date = parseDateTime(value, '+03:00');
    if (!date) return value;
    return new Intl.DateTimeFormat(lang === 'ar' ? 'ar-SA' : 'en', {
        dateStyle: 'medium',
        timeStyle: 'short'
    }).format(date);
}

function updateBar() {
    const bar = document.getElementById('updateBar');
    if (!bar) return;
    const lastUpdate = getLatestUpdateTime();
    bar.replaceChildren();
    if (!lastUpdate) return;
    bar.appendChild(document.createTextNode(`${storeNames[lang].update}: ${formatUpdateTime(lastUpdate)} • ${storeNames[lang].nextUpdate}: `));
    bar.appendChild(createElement('span', { text: '--:--:--', attrs: { id: 'nextUpdateCountdown', 'aria-hidden': 'true' } }));
}

function startUpdateCountdown() {
    if (countdownId) window.clearInterval(countdownId);
    const updatedAt = parseDateTime(getLatestUpdateTime(), '+03:00');
    if (!updatedAt) return;
    const tick = () => {
        const element = document.getElementById('nextUpdateCountdown');
        if (!element) return;
        const elapsed = Math.max(0, Date.now() - updatedAt.getTime());
        let remaining = DATA_REFRESH_MS - (elapsed % DATA_REFRESH_MS);
        if (!Number.isFinite(remaining) || remaining <= 0) remaining = DATA_REFRESH_MS;
        const hours = Math.floor(remaining / 3600000);
        const minutes = Math.floor((remaining % 3600000) / 60000);
        const seconds = Math.floor((remaining % 60000) / 1000);
        const pad = value => String(value).padStart(2, '0');
        element.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    };
    tick();
    countdownId = window.setInterval(tick, 1000);
}

function activateTab(nextTab, updateUrl = true) {
    tab = ['all', 'steam', 'epic'].includes(nextTab) ? nextTab : 'all';
    document.querySelectorAll('.tab').forEach(button => {
        const active = button.dataset.tab === tab;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
    });
    if (hasLoadedData) renderGames();
    if (updateUrl) syncUrlState();
}

function initTabs() {
    document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => activateTab(button.dataset.tab)));
    activateTab(tab, false);
}

function updateTabs() {
    document.querySelectorAll('.tab').forEach(button => {
        const store = button.dataset.tab;
        button.replaceChildren();
        if (store === 'steam' || store === 'epic') {
            button.appendChild(createElement('img', {
                className: 'tab-icon',
                attrs: { src: store === 'steam' ? 'icons/steam.svg' : 'icons/Epic.svg', alt: '', 'aria-hidden': 'true' }
            }));
        }
        button.appendChild(document.createTextNode(storeNames[lang][store] || store));
        button.setAttribute('aria-label', storeNames[lang][store] || store);
    });
}

function initLanguageToggle() {
    const button = document.getElementById('langBtn');
    if (!button) return;
    button.addEventListener('click', () => {
        lang = lang === 'ar' ? 'en' : 'ar';
        safeStorageSet('games100_language', lang);
        syncUrlState();
        updateInterface();
    });
}

function updateLanguageState() {
    const button = document.getElementById('langBtn');
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    if (button) {
        button.textContent = lang === 'ar' ? 'EN' : 'AR';
        button.setAttribute('aria-label', storeNames[lang].language);
    }
}

function updateNavigation() {
    const skipLink = document.querySelector('.skip-link');
    const tabs = document.querySelector('.tabs');
    const gamesGrid = document.getElementById('gamesGrid');
    const themeButton = document.getElementById('themeBtn');
    if (skipLink) skipLink.textContent = storeNames[lang].skip;
    if (tabs) tabs.setAttribute('aria-label', storeNames[lang].tabsLabel);
    if (gamesGrid) gamesGrid.setAttribute('aria-label', storeNames[lang].gamesLabel);
    if (themeButton) themeButton.setAttribute('aria-label', storeNames[lang].theme);
    updateHomeCount();
}

function updateHomeCount() {
    const link = document.querySelector('.header-nav .nav-link[href="index.html"]');
    if (!link) return;
    const count = hasLoadedData ? allGames.length : 0;
    link.textContent = `🏠 ${storeNames[lang].home}${count ? ` (${count})` : ''}`;
}

function updateFooterContent() {
    document.querySelectorAll('[data-ar][data-en]').forEach(element => {
        const value = element.getAttribute(`data-${lang}`);
        if (!value) return;
        const images = Array.from(element.querySelectorAll('img'));
        element.replaceChildren(...images, document.createTextNode(images.length ? ` ${value}` : value));
    });
}

function updateInterface() {
    updateLanguageState();
    applyTheme();
    updateTabs();
    updateNavigation();
    updateFooterContent();
    updateCookieBannerText();
    if (hasLoadedData) {
        renderGames();
        updateBar();
        startUpdateCountdown();
    }
}

function loadAnalytics() {
    if (document.querySelector(`script[data-analytics-id="${ANALYTICS_ID}"]`)) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', ANALYTICS_ID, { anonymize_ip: true });
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(ANALYTICS_ID)}`;
    script.dataset.analyticsId = ANALYTICS_ID;
    document.head.appendChild(script);
}

function initCookieConsent() {
    const banner = document.getElementById('cookieConsent');
    const acceptButton = document.getElementById('acceptCookies');
    const rejectButton = document.getElementById('rejectCookies');
    if (!banner || !acceptButton || !rejectButton) return;
    const consent = safeStorageGet('cookieConsent');
    if (consent === 'accepted') {
        banner.hidden = true;
        loadAnalytics();
    } else if (consent === 'rejected') banner.hidden = true;
    else banner.hidden = false;

    acceptButton.addEventListener('click', () => {
        safeStorageSet('cookieConsent', 'accepted');
        banner.hidden = true;
        loadAnalytics();
    });
    rejectButton.addEventListener('click', () => {
        safeStorageSet('cookieConsent', 'rejected');
        banner.hidden = true;
    });
}

function updateCookieBannerText() {
    const text = document.getElementById('cookieConsentText');
    const acceptButton = document.getElementById('acceptCookies');
    const rejectButton = document.getElementById('rejectCookies');
    if (text) text.textContent = storeNames[lang].consentText;
    if (acceptButton) acceptButton.textContent = storeNames[lang].accept;
    if (rejectButton) rejectButton.textContent = storeNames[lang].reject;
}

function applyTheme() {
    if (!themes.includes(theme)) theme = 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    const button = document.getElementById('themeBtn');
    if (button) button.textContent = { dark: '🌙', light: '☀️', ocean: '🌊', violet: '💜' }[theme];
}

function initThemeToggle() {
    const button = document.getElementById('themeBtn');
    if (!button) return;
    button.addEventListener('click', () => {
        theme = themes[(themes.indexOf(theme) + 1) % themes.length];
        safeStorageSet('games100_theme', theme);
        applyTheme();
    });
}

function initApp() {
    loadInitialState();
    initLanguageToggle();
    initThemeToggle();
    initTabs();
    initCookieConsent();
    updateInterface();
    const isHomePage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/';
    if (isHomePage) {
        fetchAllData();
        setupAutoRefresh();
    }
}

document.addEventListener('DOMContentLoaded', initApp);
