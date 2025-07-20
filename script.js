// --- بيانات المتاجر ---
let gamesData = {
    steam: null, epic: null, gog: null, ubisoft: null, playstation: null, xbox: null
};
let allGames = [];
let lang = 'ar';
let tab = 'all';

// --- نظام التنبيهات ---
let notificationSettings = {
    enabled: true,
    lastCheck: null,
    seenGames: new Set(),
    newGamesCount: 0
};

const storeNames = {
    ar: {
        steam: 'ستيم', 
        epic: 'إيبك', 
        gog: 'جوج', 
        ubisoft: 'يوبيسوفت', 
        playstation: 'بلايستيشن', 
        xbox: 'إكس بوكس', 
        all: 'الألعاب المجانية والمخصومة', 
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
        notifications: 'التنبيهات'
    },
    en: {
        steam: 'Steam', 
        epic: 'Epic', 
        gog: 'GOG', 
        ubisoft: 'Ubisoft', 
        playstation: 'PlayStation', 
        xbox: 'Xbox', 
        all: 'Free & Discounted Games', 
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
        notifications: 'Notifications'
    }
};

// --- إعداد نظام التنبيهات ---
function initNotificationSystem() {
    // تحميل الإعدادات المحفوظة
    loadNotificationSettings();
    
    // إضافة أزرار التحكم في التنبيهات
    addNotificationControls();
    
    // حماية الأيقونات
    setTimeout(preserveNotificationIcons, 500);
    
    // التحقق من الألعاب الجديدة عند التحميل
    setTimeout(checkForNewGames, 2000);
    
    // فحص دوري كل 5 دقائق
    setInterval(checkForNewGames, 5 * 60 * 1000);
    
    // فحص دوري للأيقونات (كل دقيقة)
    setInterval(preserveNotificationIcons, 60 * 1000);
}

function loadNotificationSettings() {
    const saved = localStorage.getItem('games100_notifications');
    if (saved) {
        const data = JSON.parse(saved);
        notificationSettings.enabled = data.enabled !== false;
        notificationSettings.lastCheck = data.lastCheck;
        notificationSettings.seenGames = new Set(data.seenGames || []);
    }
}

function saveNotificationSettings() {
    localStorage.setItem('games100_notifications', JSON.stringify({
        enabled: notificationSettings.enabled,
        lastCheck: notificationSettings.lastCheck,
        seenGames: Array.from(notificationSettings.seenGames)
    }));
}

function addNotificationControls() {
    const header = document.querySelector('.header .header-nav');
    if (header) {
        // زر التنبيهات
        const notificationBtn = document.createElement('button');
        notificationBtn.className = 'notification-btn';
        notificationBtn.setAttribute('data-notification-control', 'true'); // منع التحديث التلقائي
        notificationBtn.innerHTML = `
            <span class="notification-icon">🔔</span>
            <span class="notification-badge" id="notificationBadge" style="display: none;">0</span>
        `;
        notificationBtn.style.cssText = `
            position: relative;
            background: rgba(126, 214, 223, 0.2);
            border: 1px solid rgba(126, 214, 223, 0.4);
            border-radius: 12px;
            padding: 8px 12px;
            margin: 0 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text);
        `;
        
        // زر إعدادات التنبيهات
        const settingsBtn = document.createElement('button');
        settingsBtn.className = 'notification-settings-btn';
        settingsBtn.setAttribute('data-notification-control', 'true'); // منع التحديث التلقائي
        settingsBtn.innerHTML = '⚙️'; // تغيير إلى innerHTML
        settingsBtn.style.cssText = `
            background: transparent;
            border: none;
            font-size: 16px;
            cursor: pointer;
            margin: 0 5px;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        `;
        
        // إضافة الأزرار
        header.insertBefore(notificationBtn, header.firstChild);
        header.insertBefore(settingsBtn, header.firstChild);
        
        // إضافة الأحداث
        notificationBtn.addEventListener('click', showNotificationPanel);
        settingsBtn.addEventListener('click', toggleNotifications);
        
        // تحديث حالة التنبيهات
        updateNotificationButton();
    }
}

function toggleNotifications() {
    notificationSettings.enabled = !notificationSettings.enabled;
    saveNotificationSettings();
    updateNotificationButton();
    
    showGameNotification(
        notificationSettings.enabled 
            ? storeNames[lang].notificationsEnabled 
            : storeNames[lang].notificationsDisabled,
        notificationSettings.enabled ? 'success' : 'info'
    );
}

function updateNotificationButton() {
    const btn = document.querySelector('.notification-btn');
    const badge = document.getElementById('notificationBadge');
    const settingsBtn = document.querySelector('.notification-settings-btn');
    
    if (btn) {
        // التأكد من أن الأيقونة موجودة
        const notificationIcon = btn.querySelector('.notification-icon');
        if (notificationIcon && !notificationIcon.textContent.includes('🔔')) {
            notificationIcon.textContent = '🔔';
        }
        
        btn.style.opacity = notificationSettings.enabled ? '1' : '0.5';
        
        if (badge && notificationSettings.newGamesCount > 0) {
            badge.textContent = notificationSettings.newGamesCount;
            badge.style.display = 'block';
            badge.style.cssText += `
                position: absolute;
                top: -5px;
                right: -5px;
                background: var(--danger);
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                animation: pulse 2s infinite;
            `;
        } else if (badge) {
            badge.style.display = 'none';
        }
    }
    
    if (settingsBtn) {
        // التأكد من أن أيقونة الإعدادات موجودة
        if (!settingsBtn.innerHTML.includes('⚙️')) {
            settingsBtn.innerHTML = '⚙️';
        }
        settingsBtn.style.opacity = notificationSettings.enabled ? '1' : '0.5';
    }
}

function checkForNewGames() {
    if (!notificationSettings.enabled || !allGames.length) return;
    
    const currentGames = allGames.map(game => `${game._store}-${game[0]}-${game[1]}`);
    const newGames = currentGames.filter(gameId => !notificationSettings.seenGames.has(gameId));
    
    if (newGames.length > 0 && notificationSettings.lastCheck) {
        notificationSettings.newGamesCount = newGames.length;
        updateNotificationButton();
        
        // إظهار إشعار للألعاب الجديدة
        showGameNotification(
            `${storeNames[lang].newGamesFound} (${newGames.length})`,
            'success',
            5000
        );
        
        // طلب إذن الإشعارات من المتصفح
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Games100', {
                body: `${newGames.length} ${storeNames[lang].newGamesFound}`,
                icon: 'icons/steam.svg'
            });
        }
    }
    
    // تحديث وقت آخر فحص
    notificationSettings.lastCheck = Date.now();
    saveNotificationSettings();
}

function showNotificationPanel() {
    // إزالة اللوحة السابقة إن وجدت
    const existingPanel = document.querySelector('.notification-panel');
    if (existingPanel) {
        existingPanel.remove();
        return;
    }
    
    const panel = document.createElement('div');
    panel.className = 'notification-panel';
    panel.style.cssText = `
        position: fixed;
        top: 70px;
        ${lang === 'ar' ? 'right' : 'left'}: 20px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        min-width: 300px;
        max-width: 400px;
        z-index: 1000;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease;
    `;
    
    const newGames = getNewGames();
    
    panel.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: var(--accent2);">${storeNames[lang].notifications}</h3>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text2);">✕</button>
        </div>
        
        ${newGames.length > 0 ? `
            <div style="margin-bottom: 15px;">
                <p style="margin: 0 0 10px 0; color: var(--text2); font-size: 14px;">
                    ${newGames.length} ${storeNames[lang].newGamesFound}
                </p>
                <div style="max-height: 200px; overflow-y: auto;">
                    ${newGames.slice(0, 5).map(game => `
                        <div style="display: flex; align-items: center; padding: 8px; background: rgba(126, 214, 223, 0.1); border-radius: 8px; margin-bottom: 8px;">
                            <img src="icons/${game._store}.svg" style="width: 20px; height: 20px; margin-${lang === 'ar' ? 'left' : 'right'}: 10px;" alt="${game._store}">
                            <div>
                                <div style="font-weight: bold; font-size: 14px;">${escapeHtml(game[0])}</div>
                                <div style="font-size: 12px; color: var(--text2);">${storeNames[lang][game._store]}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button onclick="markAllAsSeen()" style="flex: 1; background: var(--accent2); color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 12px;">
                    ${storeNames[lang].markAllSeen}
                </button>
                <button onclick="showNewGamesOnly()" style="flex: 1; background: var(--accent); color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 12px;">
                    ${storeNames[lang].viewNewGames}
                </button>
            </div>
        ` : `
            <p style="text-align: center; color: var(--text2); margin: 20px 0;">
                ${lang === 'ar' ? 'لا توجد ألعاب جديدة حالياً' : 'No new games currently'}
            </p>
        `}
    `;
    
    document.body.appendChild(panel);
}

function getNewGames() {
    if (!allGames.length) return [];
    
    return allGames.filter(game => {
        const gameId = `${game._store}-${game[0]}-${game[1]}`;
        return !notificationSettings.seenGames.has(gameId);
    });
}

function markAllAsSeen() {
    allGames.forEach(game => {
        const gameId = `${game._store}-${game[0]}-${game[1]}`;
        notificationSettings.seenGames.add(gameId);
    });
    
    notificationSettings.newGamesCount = 0;
    saveNotificationSettings();
    updateNotificationButton();
    
    // إغلاق اللوحة
    const panel = document.querySelector('.notification-panel');
    if (panel) panel.remove();
    
    showGameNotification('تم وضع علامة على جميع الألعاب كمشاهدة', 'success');
}

function showNewGamesOnly() {
    // تغيير التبويب لعرض جميع الألعاب
    tab = 'all';
    document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-tab="all"]').classList.add('active');
    
    // إغلاق اللوحة
    const panel = document.querySelector('.notification-panel');
    if (panel) panel.remove();
    
    // عرض الألعاب الجديدة فقط
    renderNewGamesOnly();
}

function renderNewGamesOnly() {
    let grid = document.getElementById('gamesGrid');
    grid.innerHTML = '';
    
    const newGames = getNewGames();
    
    if (!newGames.length) {
        grid.innerHTML = `<div class="no-games">لا توجد ألعاب جديدة</div>`;
        return;
    }
    
    newGames.forEach(game => {
        const card = gameCard(game, true); // true لإظهار بادج "جديد"
        grid.appendChild(card);
    });
}

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
                console.log(`تم تحميل ${key}: ${file}`);
                if (loaded === totalFiles) {
                    mergeAllGames();
                    renderGames();
                    updateBar();
                    hideLoading();
                    
                    // فحص الألعاب الجديدة بعد التحميل
                    setTimeout(checkForNewGames, 1000);
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
        if (gamesData[key]) {
            // عرض الألعاب بخصم 100% فقط من Steam
            if (gamesData[key].discounted_games) {
                gamesData[key].discounted_games.forEach(g => {
                    // إضافة فقط إذا كان الخصم 100%
                    if (g[6] && g[6].includes('100%')) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
            // للتعامل مع البنية القديمة (discounted_list فقط)
            if (gamesData[key].discounted_list) {
                gamesData[key].discounted_list.forEach(g => {
                    // إضافة فقط إذا كان الخصم 100%
                    if (g[6] && g[6].includes('100%')) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
            // إضافة الألعاب بخصم 100% فقط من Epic وباقي المتاجر
            if (gamesData[key].free_list && key !== 'steam') {
                gamesData[key].free_list.forEach(g => {
                    // إضافة فقط إذا كان الخصم 100% وليس مجاني دائماً
                    if (g[6] && g[6].includes('100%') && !g[6].includes('مجاني دائماً')) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
            // إضافة الألعاب من free_games فقط إذا لم تكن موجودة في free_list
            if (gamesData[key].free_games && key !== 'steam') {
                const existingGames = new Set();
                if (gamesData[key].free_list) {
                    gamesData[key].free_list.forEach(g => {
                        existingGames.add(`${g[0]}-${g[1]}`); // اسم اللعبة + الرابط
                    });
                }
                gamesData[key].free_games.forEach(g => {
                    const gameKey = `${g[0]}-${g[1]}`;
                    // إضافة فقط إذا كان الخصم 100% وليس مجاني دائماً ولم تكن موجودة مسبقاً
                    if (g[6] && g[6].includes('100%') && !g[6].includes('مجاني دائماً') && !existingGames.has(gameKey)) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
            // لـ Steam: إضافة فقط الألعاب التي تحتوي على خصم 100%
            if (gamesData[key].free_list && key === 'steam') {
                gamesData[key].free_list.forEach(g => {
                    // إضافة فقط إذا كان الخصم 100%
                    if (g[6] && g[6].includes('100%')) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
            // إضافة الألعاب من free_games فقط إذا لم تكن موجودة في free_list
            if (gamesData[key].free_games && key === 'steam') {
                const existingGames = new Set();
                if (gamesData[key].free_list) {
                    gamesData[key].free_list.forEach(g => {
                        existingGames.add(`${g[0]}-${g[1]}`); // اسم اللعبة + الرابط
                    });
                }
                gamesData[key].free_games.forEach(g => {
                    const gameKey = `${g[0]}-${g[1]}`;
                    // إضافة فقط إذا كان الخصم 100% ولم تكن موجودة مسبقاً
                    if (g[6] && g[6].includes('100%') && !existingGames.has(gameKey)) {
                        allGames.push({...g, _store: key});
                    }
                });
            }
        }
    });
    
    console.log(`تم دمج ${allGames.length} لعبة (خصم 100% من جميع المتاجر فقط)`);
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

function gameCard(game, isNew = false) {
    // التحقق إذا كانت اللعبة جديدة
    const gameId = `${game._store}-${game[0]}-${game[1]}`;
    const isGameNew = isNew || !notificationSettings.seenGames.has(gameId);
    
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
            case 'ubisoft': iconPath = 'icons/ubisoft.svg'; break;
            case 'playstation': iconPath = 'icons/playstation.svg'; break;
            case 'xbox': iconPath = 'icons/xbox.svg'; break;
            default: iconPath = '';
        }
        store = `<div class="store-badge" style="display: flex; align-items: center; gap: 6px;">
            ${iconPath ? `<img src='${iconPath}' class='card-store-icon' alt='${game._store}'>` : ''}
            <span>${storeNames[lang][game._store] || game._store}</span>
            ${isGameNew ? `<span class="new-badge" data-ar="جديد" data-en="New">${storeNames[lang].newGame}</span>` : ''}
        </div>`;
    }
    
    let discount = '';
    // التحقق من الخصم في البنية الجديدة (game[6] للخصم)
    if (game[6] && (game[6].includes('خصم') || game[6].includes('OFF') || game[6].includes('%'))) {
        discount = `<div class="discount-badge">${game[6]}</div>`;
    } else if (game[4] && (game[4].includes('خصم') || game[4].includes('OFF'))) {
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
    
    return htmlToElement(`
        <div class="game-card" style="position: relative;" onclick="markGameAsSeen('${gameId}')">
            ${store}
            ${discount}
            ${img}
            <div class="game-title">${escapeHtml(game[0])}</div>
            ${priceInfo}
            ${priceRow}
            <a href="${game[1]}" class="btn-shop" target="_blank" rel="noopener noreferrer">
                ${storeNames[lang].shop}
            </a>
        </div>
    `);
}

function markGameAsSeen(gameId) {
    notificationSettings.seenGames.add(gameId);
    saveNotificationSettings();
    
    // تحديث العداد
    notificationSettings.newGamesCount = Math.max(0, notificationSettings.newGamesCount - 1);
    updateNotificationButton();
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

// --- إشعارات الألعاب ---
function showGameNotification(message, type = 'info', duration = 3000) {
    // إزالة الإشعارات السابقة
    const existingNotification = document.querySelector('.game-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // إنشاء الإشعار الجديد
    const notification = document.createElement('div');
    notification.className = 'game-notification';
    notification.textContent = message;
    
    // أنماط الإشعار
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        ${lang === 'ar' ? 'right' : 'left'}: 20px;
        background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : 'var(--accent2)'};
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transform: translateY(100px);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // تأثير الظهور
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
    }, 100);
    
    // إزالة الإشعار
    setTimeout(() => {
        notification.style.transform = 'translateY(100px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
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

// --- تحديث التبويبات مع الأيقونات ---
function updateTabs() {
    document.querySelectorAll('.tab').forEach(btn => {
        const t = btn.getAttribute('data-tab');
        let iconPath = '';
        switch (t) {
            case 'steam': iconPath = 'icons/steam.svg'; break;
            case 'epic': iconPath = 'icons/Epic.svg'; break;
            case 'gog': iconPath = 'icons/gog.svg'; break;
            case 'ubisoft': iconPath = 'icons/ubisoft.svg'; break;
            case 'playstation': iconPath = 'icons/playstation.svg'; break;
            case 'xbox': iconPath = 'icons/xbox.svg'; break;
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
    
    langBtn.addEventListener('click', function() {
        // تغيير اللغة
        lang = (lang === 'ar') ? 'en' : 'ar';
        
        // تحديث localStorage
        localStorage.setItem('games100_language', lang);
        
        // تحديث الواجهة
        updateInterface();
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
}

// تحديث واجهة الموقع بالكامل
function updateInterface() {
    // تحديث حالة زر اللغة
    updateLanguageButtonState();
    
    // تحديث الشعار
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.innerHTML = '🎮 Games100';
        logo.style.direction = 'ltr'; // دائماً من اليسار لليمين
    }
    
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
    
    // تحديث الألعاب والبادجات
    const updateGamesAndBadges = () => {
        renderGames();
        preserveNotificationIcons();
        updateNotificationButton();
        updateNewBadges();
    };

    // تأخير قصير لضمان اكتمال التحديثات
    setTimeout(updateGamesAndBadges, 50);
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
    
    // تحديث بادجات "جديد"
    updateNewBadges();
}

// --- تحديث بادجات "جديد" ---
function updateNewBadges() {
    document.querySelectorAll('.new-badge[data-ar][data-en]').forEach(badge => {
        const newText = lang === 'ar' ? badge.getAttribute('data-ar') : badge.getAttribute('data-en');
        badge.textContent = newText;
        
        // تحديث موضع البادج حسب الاتجاه
        if (lang === 'ar') {
            badge.style.left = '10px';
            badge.style.right = 'auto';
        } else {
            badge.style.right = '10px';
            badge.style.left = 'auto';
        }
    });
}

// --- طلب إذن الإشعارات ---
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showGameNotification('تم تفعيل إشعارات المتصفح!', 'success');
            }
        });
    }
}

// --- حماية أيقونات التنبيهات ---
function preserveNotificationIcons() {
    // التأكد من وجود أيقونة التنبيهات
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        const icon = notificationBtn.querySelector('.notification-icon');
        if (icon && !icon.textContent.includes('🔔')) {
            icon.textContent = '🔔';
        }
    }
    
    // التأكد من وجود أيقونة الإعدادات
    const settingsBtn = document.querySelector('.notification-settings-btn');
    if (settingsBtn && !settingsBtn.innerHTML.includes('⚙️')) {
        settingsBtn.innerHTML = '⚙️';
    }
}

// --- إضافة أنماط CSS للرسوم المتحركة ---
function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .notification-btn:hover {
            background: rgba(126, 214, 223, 0.3) !important;
            transform: translateY(-2px);
        }
        
        .new-badge {
            animation: pulse 2s infinite;
        }
        
        .game-card:hover .new-badge {
            animation: none;
            transform: scale(1.1);
        }
    `;
    document.head.appendChild(style);
}

// --- تهيئة التطبيق ---
function initApp() {
    // إضافة الأنماط أولاً
    addNotificationStyles();
    
    // تهيئة نظام اللغة
    initLanguageToggle();
    
    // تهيئة باقي المكونات
    initTabs();
    initNotificationSystem();
    requestNotificationPermission();
    
    // تحديث الواجهة بالكامل
    updateInterface();
    
    // تحميل البيانات
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