// بيانات المتاجر والحالة العامة
let allGames = [];
let lang = 'ar';
let tab = 'all';
let theme = safeStorageGet('games100_theme') || 'dark';
let feed = null;
let loadFailed = false;
let loading = false;
let expiryTimer = null;
let lastRenderedSignature = null;

const themes = ['dark', 'light', 'ocean', 'violet'];
const DATA_REFRESH_MS = 15 * 60 * 1000;
const EXPIRY_CHECK_MS = 60 * 1000;

const storeNames = {
    ar: {
        pageTitle: '🎮 Games100 - ألعاب مجانية مؤقتاً بخصم 100% من Steam وEpic',
        steam: 'ستيم', epic: 'إيبك', all: 'الكل',
        shop: 'رابط الحصول على العرض',
        shopFor: (title, store) => `احصل على ${title} من ${store}`,
        update: 'آخر فحص ناجح', free: 'مجاني',
        noGames: 'لا توجد عروض بخصم 100% حالياً', loading: 'جاري تحميل العروض...',
        loadError: 'تعذر تحميل بيانات الألعاب. تحقق من الاتصال ثم حاول مجدداً.',
        partialError: stores => `تعذر التحقق من كل العروض في ${stores}. تُعرض البيانات المتاحة.`,
        refreshError: 'تعذر تحديث البيانات. تُعرض العروض المتاحة من آخر تحميل.',
        retry: 'إعادة المحاولة', endsIn: 'ينتهي خلال', daysLeft: 'يوم', hoursLeft: 'ساعة', minutesLeft: 'دقيقة',
        daysMany: 'أيام', hoursMany: 'ساعات', minutesMany: 'دقائق',
        dayTwo: 'يومان', hourTwo: 'ساعتان', minuteTwo: 'دقيقتان',
        currentPrice: 'السعر الحالي', originalPrice: 'السعر الأصلي', discountedPrice: 'السعر بعد الخصم',
        home: 'الرئيسية', skip: 'تخطي إلى قائمة الألعاب', theme: 'تغيير المظهر',
        language: 'Switch to English', gamesLabel: 'قائمة عروض خصم 100%',
        tabsLabel: 'تصفية حسب متجر الألعاب'
    },
    en: {
        pageTitle: '🎮 Games100 - Temporary 100% Off Games on Steam & Epic',
        steam: 'Steam', epic: 'Epic', all: 'All',
        shop: 'Get this offer',
        shopFor: (title, store) => `Get ${title} from ${store}`,
        update: 'Last successful check', free: 'Free',
        noGames: 'No 100% off deals are available now', loading: 'Loading offers...',
        loadError: 'Could not load game data. Check your connection and try again.',
        partialError: stores => `Some offers from ${stores} could not be verified. Showing available data.`,
        refreshError: 'Could not refresh. Showing available offers from the last load.',
        retry: 'Try again', endsIn: 'Ends in', daysLeft: 'day', hoursLeft: 'hour', minutesLeft: 'minute',
        daysMany: 'days', hoursMany: 'hours', minutesMany: 'minutes',
        currentPrice: 'Current price', originalPrice: 'Original price', discountedPrice: 'Discounted price',
        home: 'Home', skip: 'Skip to the games list', theme: 'Change theme',
        language: 'التبديل إلى العربية', gamesLabel: '100% off deals list',
        tabsLabel: 'Filter by game store'
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
    url.searchParams.set('lang', lang);
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
    const text = value.trim();
    if (!/^https:\/\//i.test(text) || /[\s\\]/.test(text)) return null;
    try {
        const url = new URL(text);
        return url.protocol === 'https:' && !url.username && !url.password && !url.port ? url.href : null;
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

function parseDateTime(value) {
    if (!value || typeof value !== 'string') return null;
    const text = value.trim();
    let normalized = text;
    if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$/.test(text)) normalized = `${text.replace(' ', 'T')}Z`;
    const parsed = new Date(normalized);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function isGameExpired(game) {
    return game.endAt !== null && Date.parse(game.endAt) <= Date.now();
}

function normalizePublicDeal(rawDeal) {
    if (!rawDeal || typeof rawDeal !== 'object') return null;
    if (!['steam', 'epic'].includes(rawDeal.store)) return null;
    if (rawDeal.discount_percent !== 100) return null;
    const title = String(rawDeal.title || '').trim();
    const url = safeStoreUrl(rawDeal.url, rawDeal.store);
    const endAt = parseDateTime(rawDeal.end_at);
    if (!title || !url || (!endAt && (rawDeal.end_at || rawDeal.store === 'epic'))) return null;
    return {
        title,
        url,
        image: String(rawDeal.image || ''),
        capsule: String(rawDeal.fallback_image || ''),
        originalPrice: String(rawDeal.original_price || ''),
        currentPrice: String(rawDeal.current_price || ''),
        endAt: endAt ? endAt.toISOString() : null,
        store: rawDeal.store
    };
}

async function loadPublicFeed() {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
        const response = await fetch('deals.json', { cache: 'no-cache', signal: controller.signal });
        if (!response.ok) throw new Error(`deals.json: HTTP ${response.status}`);
        const data = await response.json();
        if (!data || data.schema_version !== 1 || !Array.isArray(data.deals)
            || data.total_count !== data.deals.length || !data.sources || typeof data.sources !== 'object') {
            throw new Error('deals.json: invalid data schema');
        }
        return data;
    } finally {
        window.clearTimeout(timeout);
    }
}

async function fetchAllData() {
    if (loading) return;
    loading = true;
    loadFailed = false;
    if (!feed) showLoading();

    try {
        feed = await loadPublicFeed();
        allGames = feed.deals
            .map(normalizePublicDeal)
            .filter(Boolean)
            .filter(game => !isGameExpired(game));
    } catch (error) {
        console.error('Failed to load public deals feed:', error);
        loadFailed = true;
    } finally {
        loading = false;
        renderData();
        if (feed) checkExpiredGames();
    }
}

function checkExpiredGames() {
    window.clearTimeout(expiryTimer);
    const previousCount = allGames.length;
    allGames = allGames.filter(game => !isGameExpired(game));
    if (allGames.length !== previousCount) {
        renderGames();
        updateHomeCount();
    } else updateDealCountdowns();

    const now = Date.now();
    const nextCheck = allGames.reduce((delay, game) => game.endAt
        ? Math.min(delay, Math.max(0, Date.parse(game.endAt) - now)) : delay, EXPIRY_CHECK_MS);
    if (allGames.some(game => game.endAt)) expiryTimer = window.setTimeout(checkExpiredGames, nextCheck);
}

function renderData() {
    const strings = storeNames[lang];
    if (!feed) {
        if (loadFailed) renderMessage(strings.loadError, true);
        else if (loading) showLoading();
        return;
    }
    const failedStores = ['steam', 'epic']
        .filter(store => ['partial', 'failed'].includes(feed.sources[store]?.status))
        .map(store => strings[store]);
    const stores = new Intl.ListFormat(lang).format(failedStores);
    const warning = loadFailed ? strings.refreshError : stores ? strings.partialError(stores) : '';
    setDataStatus(warning);
    renderGames();
    updateBar();
    updateHomeCount();
}

function setDataStatus(message) {
    const status = document.getElementById('dataStatus');
    if (!status) return;
    status.textContent = message;
    status.hidden = !message;
}

function renderMessage(message, withRetry = false) {
    lastRenderedSignature = null;
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const wrapper = createElement('div', { className: 'no-games' });
    wrapper.appendChild(createElement('p', { text: message, attrs: { role: 'status' } }));
    if (withRetry) {
        const retryButton = createElement('button', { className: 'retry-btn', text: storeNames[lang].retry, attrs: { type: 'button' } });
        retryButton.addEventListener('click', fetchAllData);
        wrapper.appendChild(retryButton);
    }
    grid.appendChild(wrapper);
}

function showLoading() {
    lastRenderedSignature = null;
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const wrapper = createElement('div', { className: 'no-games' });
    wrapper.appendChild(createElement('div', { className: 'loading', attrs: { 'aria-hidden': 'true' } }));
    wrapper.appendChild(createElement('p', { text: storeNames[lang].loading, attrs: { role: 'status' } }));
    grid.appendChild(wrapper);
}

function renderGames() {
    const visibleGames = tab === 'all' ? allGames : allGames.filter(game => game.store === tab);
    if (!visibleGames.length) {
        renderMessage(storeNames[lang].noGames);
        return;
    }
    const signature = JSON.stringify([lang, tab, visibleGames]);
    if (signature === lastRenderedSignature) {
        updateDealCountdowns();
        return;
    }
    lastRenderedSignature = signature;
    const grid = document.getElementById('gamesGrid');
    grid.replaceChildren();
    const fragment = document.createDocumentFragment();
    visibleGames.forEach((game, index) => fragment.appendChild(gameCard(game, index)));
    grid.appendChild(fragment);
}

function createGameImage(game, isFirstCard) {
    const capsule = safeHttpsUrl(game.capsule);
    const source = safeHttpsUrl(game.image) || capsule;
    if (!source) return createElement('div', { className: 'game-thumb game-thumb-placeholder', attrs: { 'aria-hidden': 'true' } });
    const image = createElement('img', {
        className: 'game-thumb',
        attrs: { src: source, alt: '', loading: isFirstCard ? 'eager' : 'lazy', decoding: 'async' }
    });
    if (isFirstCard) image.setAttribute('fetchpriority', 'high');
    let triedFallback = source === capsule;
    image.addEventListener('error', () => {
        if (capsule && !triedFallback) {
            triedFallback = true;
            image.src = capsule;
            return;
        }
        image.replaceWith(createElement('div', { className: 'game-thumb game-thumb-placeholder', attrs: { 'aria-hidden': 'true' } }));
    });
    return image;
}

function appendPriceInfo(card, game) {
    const original = game.originalPrice.trim();
    const rawCurrent = game.currentPrice.trim();
    const current = /^(?:free|[$€£]?\s*0(?:[.,]00)?)$/i.test(rawCurrent) ? storeNames[lang].free : rawCurrent;
    if (!original && !current) return;
    const priceInfo = createElement('div', { className: 'price-info' });
    const appendPair = (label, value, valueClass) => {
        priceInfo.appendChild(createElement('span', { className: 'price-label', text: label }));
        priceInfo.appendChild(createElement('bdi', { className: `price-value ${valueClass}`, text: value }));
    };
    if (original && current && original !== current) {
        appendPair(storeNames[lang].originalPrice, original, 'old');
        appendPair(storeNames[lang].discountedPrice, current, 'new');
    } else appendPair(storeNames[lang].currentPrice, current || original, 'current');
    card.appendChild(priceInfo);
}

function formatTimeUnit(count, unit) {
    const strings = storeNames[lang];
    if (lang === 'ar') {
        if (count === 1) return `1 ${strings[`${unit}sLeft`]}`;
        if (count === 2) return strings[`${unit}Two`];
        if (count <= 10) return `${count} ${strings[`${unit}sMany`]}`;
        return `${count} ${strings[`${unit}sLeft`]}`;
    }
    return `${count} ${count === 1 ? strings[`${unit}sLeft`] : strings[`${unit}sMany`]}`;
}

function formatTimeLeft(timeLeft) {
    const totalMinutes = Math.max(1, Math.ceil(timeLeft / 60000));
    const days = Math.floor(totalMinutes / 1440);
    const hours = Math.floor((totalMinutes % 1440) / 60);
    const minutes = totalMinutes % 60;
    const parts = [];
    if (days) parts.push(formatTimeUnit(days, 'day'));
    if (hours) parts.push(formatTimeUnit(hours, 'hour'));
    if (minutes || !parts.length) parts.push(formatTimeUnit(minutes, 'minute'));
    return parts.join(lang === 'ar' ? ' و' : ', ');
}

function updateCountdownElement(element) {
    const endDate = parseDateTime(element.getAttribute('datetime'));
    if (!endDate) return;
    const timeLeft = endDate.getTime() - Date.now();
    if (timeLeft > 0) element.textContent = formatTimeLeft(timeLeft);
}

function updateDealCountdowns() {
    document.querySelectorAll('time.end-date-value[datetime]').forEach(updateCountdownElement);
}

function appendEndDate(card, game) {
    const endDate = parseDateTime(game.endAt);
    if (!endDate) return;
    const timeLeft = endDate.getTime() - Date.now();
    if (timeLeft <= 0) return;
    const wrapper = createElement('div', { className: 'end-date-info' });
    wrapper.appendChild(createElement('span', { className: 'end-date-label', text: `${storeNames[lang].endsIn}: ` }));
    wrapper.appendChild(createElement('time', {
        className: 'end-date-value',
        text: formatTimeLeft(timeLeft),
        attrs: {
            datetime: game.endAt,
            title: endDate.toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-US', {
                dateStyle: 'medium', timeStyle: 'short'
            })
        }
    }));
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
    card.appendChild(createElement('div', { className: 'discount-badge', text: '-100%', attrs: { dir: 'ltr' } }));
    card.appendChild(createGameImage(game, index === 0));
    card.appendChild(createElement('h2', { className: 'game-title', text: game.title, attrs: { dir: 'auto' } }));
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

function updateBar() {
    const bar = document.getElementById('updateBar');
    bar.replaceChildren();
    const date = ['steam', 'epic']
        .map(store => parseDateTime(feed.sources[store]?.last_success))
        .filter(Boolean)
        .sort((first, second) => second - first)[0];
    if (!date) return;
    const locale = lang === 'ar' ? 'ar-SA' : 'en-US';
    const formatted = new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(date);
    bar.append(document.createTextNode(`${storeNames[lang].update}: `),
        createElement('time', { text: formatted, attrs: { datetime: date.toISOString() } }));
}

function activateTab(nextTab, updateUrl = true) {
    tab = ['all', 'steam', 'epic'].includes(nextTab) ? nextTab : 'all';
    document.querySelectorAll('.tab').forEach(button => {
        const active = button.dataset.tab === tab;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
    });
    if (feed) renderGames();
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
    document.title = storeNames[lang].pageTitle;
    if (button) {
        button.textContent = lang === 'ar' ? 'EN' : 'AR';
        button.setAttribute('aria-label', storeNames[lang].language);
    }
}

function updateNavigation() {
    const skipLink = document.querySelector('.skip-link');
    const tabs = document.querySelector('.tabs');
    const main = document.getElementById('mainContent');
    const themeButton = document.getElementById('themeBtn');
    if (skipLink) skipLink.textContent = storeNames[lang].skip;
    if (tabs) tabs.setAttribute('aria-label', storeNames[lang].tabsLabel);
    if (main) main.setAttribute('aria-label', storeNames[lang].gamesLabel);
    if (themeButton) themeButton.setAttribute('aria-label', storeNames[lang].theme);
    updateHomeCount();
}

function updateHomeCount() {
    const link = document.querySelector('.header-nav .nav-link[href="index.html"]');
    if (!link) return;
    const count = allGames.length;
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
    renderData();
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
    updateInterface();
    const isHomePage = Boolean(document.getElementById('gamesGrid'));
    if (isHomePage) {
        fetchAllData();
        window.setInterval(fetchAllData, DATA_REFRESH_MS);
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && feed) checkExpiredGames();
        });
    }
}

document.addEventListener('DOMContentLoaded', initApp);
