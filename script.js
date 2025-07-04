// --- بيانات المتاجر ---
let gamesData = {
    steam: null, epic: null, gog: null, ubisoft: null, playstation: null, xbox: null
};
let allGames = [];
let lang = 'ar';
let tab = 'all';

const storeNames = {
    ar: {
        steam: 'ستيم', 
        epic: 'إيبك', 
        gog: 'جوج', 
        ubisoft: 'يوبيسوفت', 
        playstation: 'بلايستيشن', 
        xbox: 'إكس بوكس', 
        all: 'كل الألعاب', 
        shop: 'رابط الشراء', 
        old: 'السعر الأصلي', 
        new: 'السعر بعد الخصم', 
        update: 'آخر تحديث', 
        noGames: 'لا توجد ألعاب حالياً', 
        percent: 'خصم'
    },
    en: {
        steam: 'Steam', 
        epic: 'Epic', 
        gog: 'GOG', 
        ubisoft: 'Ubisoft', 
        playstation: 'PlayStation', 
        xbox: 'Xbox', 
        all: 'All Games', 
        shop: 'Shop Link', 
        old: 'Old Price', 
        new: 'New Price', 
        update: 'Last Update', 
        noGames: 'No games found', 
        percent: 'OFF'
    }
};

// --- تحميل البيانات ---
function fetchAllData() {
    const files = [
        ['steam', 'free_goods_detail.json'],
        ['epic', 'epic_goods_detail.json'],
        ['gog', 'gog_goods_detail.json'],
        ['ubisoft', 'ubisoft_goods_detail.json'],
        ['playstation', 'playstation_goods_detail.json'],
        ['xbox', 'xbox_goods_detail.json']
    ];
    
    let loaded = 0;
    const totalFiles = files.length;
    
    // إظهار حالة التحميل
    showLoading();
    
    files.forEach(([key, file]) => {
        fetch(file)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                gamesData[key] = data;
                loaded++;
                if (loaded === totalFiles) {
                    mergeAllGames();
                    renderGames();
                    updateBar();
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
                    hideLoading();
                }
            });
    });
}

function mergeAllGames() {
    allGames = [];
    Object.keys(gamesData).forEach(key => {
        if (gamesData[key] && (gamesData[key].free_list || gamesData[key].discounted_list)) {
            let arr = gamesData[key].free_list || gamesData[key].discounted_list;
            arr.forEach(g => allGames.push({...g, _store: key}));
        }
    });
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
            case 'epic': iconPath = 'icons/epic.svg'; break;
            case 'gog': iconPath = 'icons/gog.svg'; break;
            case 'ubisoft': iconPath = 'icons/ubisoft.svg'; break;
            case 'playstation': iconPath = 'icons/playstation.svg'; break;
            case 'xbox': iconPath = 'icons/xbox.svg'; break;
            default: iconPath = '';
        }
        store = `<div class="store-badge">${iconPath ? `<img src='${iconPath}' class='card-store-icon' alt='${game._store}'>` : ''}${storeNames[lang][game._store] || game._store}</div>`;
    }
    
    let discount = '';
    if (game[4] && (game[4].includes('خصم') || game[4].includes('OFF'))) {
        discount = `<div class="discount-badge">${game[4]}</div>`;
    }
    
    let priceRow = '';
    if (game[5] && game[6]) {
        priceRow = `
            <div class="price-row">
                <span class="old-price">${game[5]}</span>
                <span class="new-price">${game[6]}</span>
            </div>
        `;
    }
    
    let desc = '';
    if (game[3] && typeof game[3] === 'string' && !game[3].startsWith('http')) {
        desc = escapeHtml(game[3]);
    }
    
    return htmlToElement(`
        <div class="game-card">
            ${store}
            ${discount}
            ${img}
            <div class="game-title">${escapeHtml(game[0])}</div>
            <div class="game-desc">${desc}</div>
            ${priceRow}
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
    document.getElementById('updateBar').textContent = `${storeNames[lang].update}: ${last}`;
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
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            tab = this.getAttribute('data-tab');
            renderGames();
        });
    });
}

// --- تبديل اللغة ---
function initLanguageToggle() {
    document.getElementById('langBtn').addEventListener('click', function() {
        lang = (lang === 'ar') ? 'en' : 'ar';
        
        // تغيير اتجاه الصفحة
        document.body.dir = (lang === 'ar') ? 'rtl' : 'ltr';
        
        // تحديث زر اللغة
        this.textContent = (lang === 'ar') ? 'EN' : 'AR';
        
        // تحديث الشعار
        document.querySelector('.logo').innerHTML = (lang === 'ar') 
            ? '🎮 games100'
            : '🎮 games100';
        
        // تحديث التبويبات
        document.querySelectorAll('.tab').forEach(btn => {
            let t = btn.getAttribute('data-tab');
            btn.textContent = storeNames[lang][t] || t;
        });
        
        updateBar();
        renderGames();
    });
}

// --- تهيئة التطبيق ---
function initApp() {
    initTabs();
    initLanguageToggle();
    fetchAllData();
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