// ========================================
// Games100 - Modern Gaming Website JS
// سكريبت موقع الألعاب المجانية الحديث
// ========================================

// Global Variables - المتغيرات العامة
let gamesData = {
    steam: null,
    epic: null,
    gog: null,
    ubisoft: null,
    playstation: null,
    xbox: null
};

let allGames = [];
let currentLanguage = 'ar';
let currentStore = 'all';
let isLoading = false;

// Language Support - دعم اللغة
const translations = {
    ar: {
        // Store Filters - مرشحات المتاجر
        lastUpdate: 'آخر تحديث:',
        loading: 'جاري التحميل...',
        all: 'الكل', 
        
        // Game Cards - بطاقات الألعاب
        shopLink: 'رابط الشراء',
        originalPrice: 'السعر الأصلي',
        discountedPrice: 'السعر المخصوم',
        discount: 'خصم',
        free: 'مجاني',
        new: 'جديد',
        endsIn: 'ينتهي في',
        daysLeft: 'يوم متبقي',
        hoursLeft: 'ساعة متبقية',
        endingSoon: 'ينتهي قريباً',
        
        // No Games - لا توجد ألعاب
        noGamesTitle: 'لا توجد ألعاب متاحة',
        noGamesDescription: 'جاري تحديث البيانات، يرجى المحاولة لاحقاً',
        
        // Footer - التذييل
        stores: 'المتاجر',
        footerDescription: 'موقع متخصص في عرض الألعاب المجانية من جميع المتاجر العالمية'
    },
    en: {
        // Store Filters - Store Filters
        lastUpdate: 'Last update:',
        loading: 'Loading...',
        all: 'All', 
        
        // Game Cards - Game Cards
        shopLink: 'Shop Link',
        originalPrice: 'Original Price',
        discountedPrice: 'Discounted Price',
        discount: 'OFF',
        free: 'FREE',
        new: 'NEW',
        endsIn: 'Ends in',
        daysLeft: 'days left',
        hoursLeft: 'hours left',
        endingSoon: 'Ending soon',
        
        // No Games - No Games
        noGamesTitle: 'No games available',
        noGamesDescription: 'Data is being updated, please try again later',
        
        // Footer - Footer
        stores: 'Stores',
        allRightsReserved: 'All rights reserved © 2024 Games100',
        footerDescription: 'Specialized website for displaying free games from all major gaming stores'
    }
};

// Store Names - أسماء المتاجر
const storeNames = {
    ar: {
        steam: 'Steam',
        epic: 'Epic Games',
        gog: 'GOG',
        ubisoft: 'Ubisoft',
        playstation: 'PlayStation',
        xbox: 'Xbox',
        all: 'الكل'
    },
    en: {
        steam: 'Steam',
        epic: 'Epic Games',
        gog: 'GOG',
        ubisoft: 'Ubisoft',
        playstation: 'PlayStation',
        xbox: 'Xbox',
        all: 'All'
    }
};

// Utility Functions - الدوال المساعدة
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

function createElement(tag, className = '', content = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (content) element.innerHTML = content;
    return element;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Loading Screen - شاشة التحميل
function showLoadingScreen() {
    const loadingScreen = $('#loadingScreen');
    if (loadingScreen) {
        loadingScreen.classList.remove('hidden');
    }
}

function hideLoadingScreen() {
    const loadingScreen = $('#loadingScreen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
        }, 1000);
    }
}

// Language Management - إدارة اللغة
function initLanguageToggle() {
    const langToggle = $('#langToggle');
    if (!langToggle) return;

    // Load saved language
    const savedLang = localStorage.getItem('games100_language');
    if (savedLang && translations[savedLang]) {
        currentLanguage = savedLang;
    }

    updateLanguageUI();
    
    langToggle.addEventListener('click', () => {
        currentLanguage = currentLanguage === 'ar' ? 'en' : 'ar';
        localStorage.setItem('games100_language', currentLanguage);
        updateLanguageUI();
        updateInterfaceLanguage();
    });
}

function updateLanguageUI() {
    const langToggle = $('#langToggle');
    if (!langToggle) return;

    const langText = langToggle.querySelector('.lang-text');
    if (langText) {
        langText.textContent = currentLanguage === 'ar' ? 'EN' : 'AR';
    }

    // Update document direction
    document.documentElement.lang = currentLanguage;
    document.body.dir = currentLanguage === 'ar' ? 'rtl' : 'ltr';
}

function updateInterfaceLanguage() {
    // Update all elements with data attributes
    $$('[data-ar][data-en]').forEach(element => {
        const text = currentLanguage === 'ar' ? 
            element.getAttribute('data-ar') : 
            element.getAttribute('data-en');
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = text;
        } else {
            element.textContent = text;
        }
    });

    // Update store filter tabs
    $$('.store-filter-tab').forEach(tab => {
        const store = tab.getAttribute('data-store');
        if (store && storeNames[currentLanguage][store]) {
            const tabText = tab.querySelector('.tab-text');
            if (tabText) {
                tabText.textContent = storeNames[currentLanguage][store];
            }
        }
    });

    // تحديث نص آخر تحديث عند تغيير اللغة
    updateLastUpdateTime();

    // Re-render games to update language
    renderGames();
}

// Store Filter Tabs - تبويبات تصفية المتاجر
function initStoreFilterTabs() {
    $$('.store-filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            $$('.store-filter-tab').forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Update current store
            currentStore = tab.getAttribute('data-store');
            
            // Re-render games
            renderGames();
            
            // Scroll to games section
            const gamesSection = $('.games-section');
            if (gamesSection) {
                gamesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Data Loading - تحميل البيانات
async function loadGamesData() {
    if (isLoading) return;
    isLoading = true;

    const files = [
        ['steam', 'data/free_goods_detail.json'],
        ['epic', 'data/epic_goods_detail.json'],
        ['gog', 'data/gog_goods_detail.json'],
        ['ubisoft', 'data/ubisoft_goods_detail.json'],
        ['playstation', 'data/playstation_goods_detail.json'],
        ['xbox', 'data/xbox_goods_detail.json']
    ];
    
    let loadedCount = 0;
    const totalFiles = files.length;
    
    // Show loading state
    updateLoadingState(true);

    try {
        const promises = files.map(async ([store, filename]) => {
            try {
                const response = await fetch(filename);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = await response.json();
                gamesData[store] = data;
                loadedCount++;
                console.log(`✅ Loaded ${store}: ${filename}`);
                return { store, success: true };
            } catch (error) {
                console.error(`❌ Failed to load ${store}:`, error);
                loadedCount++;
                return { store, success: false, error };
            }
        });

        await Promise.all(promises);
        
        // Process loaded data
        processGamesData();
        
        // Update UI
        updateLoadingState(false);
        updateLastUpdateTime();
        renderGames();
        
    } catch (error) {
        console.error('Error loading games data:', error);
        updateLoadingState(false);
        showError('Failed to load games data');
    } finally {
        isLoading = false;
    }
}

function processGamesData() {
    allGames = [];
    
    Object.keys(gamesData).forEach(store => {
        const data = gamesData[store];
        if (!data) return;

        // Process different data structures
        const gameLists = [
            data.free_list || [],
            data.free_games || [],
            data.discounted_games || [],
            data.discounted_list || []
        ];

        gameLists.forEach(gameList => {
            if (Array.isArray(gameList)) {
                gameList.forEach(game => {
                    if (Array.isArray(game) && game.length >= 2) {
                        // Only include games with 100% discount or free
                        const discountInfo = game[6] || game[4] || '';
                        if (discountInfo.includes('100%') || discountInfo.includes('مجاني') || discountInfo.includes('FREE')) {
                            allGames.push({
                                ...game,
                                _store: store
                            });
                        }
                    }
                });
            }
        });
    });

    console.log(`📊 Processed ${allGames.length} games`);
}

function updateLoadingState(loading) {
    const updateInfo = $('.update-info .update-text');
    if (updateInfo) {
        if (loading) {
            // عرض حالة التحميل
            if (currentLanguage === 'ar') {
                updateInfo.textContent = 'جاري التحميل...';
            } else {
                updateInfo.textContent = 'Loading...';
            }
        } else {
            // عرض آخر تحديث
            updateLastUpdateTime();
        }
    }
}

function updateLastUpdateTime() {
    const updateInfo = $('.update-info .update-text');
    if (!updateInfo) return;

    const times = Object.values(gamesData)
        .map(data => data?.update_time)
        .filter(Boolean);

    if (times.length > 0) {
        const lastUpdate = times.sort().reverse()[0];
        // تحديث النص مع الحفاظ على دعم اللغة
        if (currentLanguage === 'ar') {
            updateInfo.textContent = `آخر تحديث: ${lastUpdate}`;
        } else {
            updateInfo.textContent = `Last update: ${lastUpdate}`;
        }
    }
}

// Game Rendering - عرض الألعاب
function renderGames() {
    const gamesGrid = $('#gamesGrid');
    const noGames = $('#noGames');
    
    if (!gamesGrid) return;

    // Filter games by current store
    let filteredGames = allGames;
    if (currentStore !== 'all') {
        filteredGames = allGames.filter(game => game._store === currentStore);
    }

    // Clear grid
    gamesGrid.innerHTML = '';

    if (filteredGames.length === 0) {
        // Show no games message
        if (noGames) {
            noGames.style.display = 'block';
        }
        return;
    }
    
    // Hide no games message
    if (noGames) {
        noGames.style.display = 'none';
    }

    // Render game cards
    filteredGames.forEach((game, index) => {
        const gameCard = createGameCard(game, index);
        gamesGrid.appendChild(gameCard);
    });

    // Add animation delay to cards
    $$('.game-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-in');
    });
}

function createGameCard(game, index) {
    const card = createElement('div', 'game-card');
    
    // Game image
    const imageUrl = getGameImage(game);
    const image = createElement('img', 'game-image');
    image.src = imageUrl;
    image.alt = game[0] || 'Game';
    image.loading = 'lazy';
    
    // Enhanced error handling for images
    image.onerror = () => {
        console.log(`Failed to load image for ${game[0]}: ${imageUrl}`);
        
        // Try fallback images
        if (game._store === 'epic') {
            // Epic Games fallback
            if (imageUrl.includes('capsule') && game[2] && game[2].startsWith('http')) {
                image.src = game[2]; // Try header image
                return;
            } else if (imageUrl.includes('header') && game[4] && game[4].startsWith('http')) {
                image.src = game[4]; // Try key art
                return;
            }
        } else if (game._store === 'steam') {
            // Steam fallback
            if (game[3] && game[3].startsWith('http')) {
                image.src = game[3]; // Try capsule image
                return;
            }
        }
        
        // Final fallback
        const storeName = game._store ? game._store.charAt(0).toUpperCase() + game._store.slice(1) : 'Game';
        image.src = `https://via.placeholder.com/300x200/1e293b/64748b?text=${storeName}`;
        image.onerror = null; // Prevent infinite loop
    };
    
    // Game content
    const content = createElement('div', 'game-content');
    
    // Game header
    const header = createElement('div', 'game-header');
    const title = createElement('h3', 'game-title', escapeHtml(game[0] || 'Unknown Game'));
    const store = createElement('div', 'game-store');
    
    const storeIcon = createElement('img', 'store-icon');
    storeIcon.src = `assets/icons/${game._store}.svg`;
    storeIcon.alt = game._store;
    storeIcon.onerror = () => {
        console.log(`Failed to load store icon for ${game._store}`);
        storeIcon.style.display = 'none';
    };
    
    const storeName = createElement('span', '', storeNames[currentLanguage][game._store] || game._store);
    store.appendChild(storeIcon);
    store.appendChild(storeName);
    
    header.appendChild(title);
    header.appendChild(store);
    
    // Game badges
    const badges = createElement('div', 'game-badges');
    const discountInfo = game[6] || game[4] || '';
    
    if (discountInfo.includes('100%')) {
        const freeBadge = createElement('span', 'game-badge badge-free', translations[currentLanguage].free);
        badges.appendChild(freeBadge);
    } else if (discountInfo.includes('%')) {
        const discountBadge = createElement('span', 'game-badge badge-discount', discountInfo);
        badges.appendChild(discountBadge);
    }
    
    // Game price
    const price = createElement('div', 'game-price');
    const currentPrice = game[5] || game[4] || '';
    const originalPrice = game[4] || game[5] || '';
    
    if (currentPrice && currentPrice !== originalPrice) {
        const currentPriceEl = createElement('span', 'price-current', currentPrice);
        const originalPriceEl = createElement('span', 'price-original', originalPrice);
        price.appendChild(currentPriceEl);
        price.appendChild(originalPriceEl);
    } else if (currentPrice) {
        const priceEl = createElement('span', 'price-current', currentPrice);
        price.appendChild(priceEl);
    }
    
    // Game actions
    const actions = createElement('div', 'game-actions');
    const shopLink = createElement('a', 'btn-primary', translations[currentLanguage].shopLink);
    shopLink.href = game[1] || '#';
    shopLink.target = '_blank';
    shopLink.rel = 'noopener noreferrer';
    
    actions.appendChild(shopLink);
    
    // Assemble card
    content.appendChild(header);
    content.appendChild(badges);
    content.appendChild(price);
    content.appendChild(actions);
    
    card.appendChild(image);
    card.appendChild(content);
    
    return card;
}

function isValidImageUrl(url) {
    if (!url || typeof url !== 'string') return false;
    
    // Check if it's a valid HTTP/HTTPS URL
    if (!url.startsWith('http://') && !url.startsWith('https://')) return false;
    
    // Check if it's not a placeholder or broken link
    if (url.includes('placeholder') || url.includes('broken') || url.includes('error')) return false;
    
    // Check if it's not empty or just whitespace
    if (url.trim().length === 0) return false;
    
    return true;
}

function getGameImage(game) {
    // Try different image sources based on store
    if (game._store === 'steam') {
        // Steam: prefer header image, then capsule
        if (isValidImageUrl(game[2])) {
            return game[2]; // Steam header image
        } else if (isValidImageUrl(game[3])) {
            return game[3]; // Steam capsule image
        }
    } else if (game._store === 'epic') {
        // Epic Games: try multiple image sources
        if (isValidImageUrl(game[3])) {
            return game[3]; // Epic capsule image
        } else if (isValidImageUrl(game[2])) {
            return game[2]; // Epic header image
        } else if (isValidImageUrl(game[4])) {
            return game[4]; // Epic key art
        } else if (isValidImageUrl(game[5])) {
            return game[5]; // Epic additional image
        }
    } else if (game._store === 'gog') {
        // GOG: try different positions
        if (isValidImageUrl(game[2])) {
            return game[2];
        } else if (isValidImageUrl(game[3])) {
            return game[3];
        } else if (isValidImageUrl(game[4])) {
            return game[4];
        }
    } else if (game._store === 'ubisoft') {
        // Ubisoft: try different positions
        if (isValidImageUrl(game[2])) {
            return game[2];
        } else if (isValidImageUrl(game[3])) {
            return game[3];
        } else if (isValidImageUrl(game[4])) {
            return game[4];
        }
    } else if (game._store === 'playstation') {
        // PlayStation: try different positions
        if (isValidImageUrl(game[2])) {
            return game[2];
        } else if (isValidImageUrl(game[3])) {
            return game[3];
        } else if (isValidImageUrl(game[4])) {
            return game[4];
        }
    } else if (game._store === 'xbox') {
        // Xbox: try different positions
        if (isValidImageUrl(game[2])) {
            return game[2];
        } else if (isValidImageUrl(game[3])) {
            return game[3];
        } else if (isValidImageUrl(game[4])) {
            return game[4];
        }
    } else {
        // Generic fallback for unknown stores
        for (let i = 2; i <= 6; i++) {
            if (isValidImageUrl(game[i])) {
                return game[i];
            }
        }
    }
    
    // Default placeholder with store-specific text
    const storeName = game._store ? game._store.charAt(0).toUpperCase() + game._store.slice(1) : 'Game';
    return `https://via.placeholder.com/300x200/1e293b/64748b?text=${storeName}`;
}

// Error Handling - معالجة الأخطاء
function showError(message) {
    console.error('Error:', message);
    
    const gamesGrid = $('#gamesGrid');
    if (gamesGrid) {
        gamesGrid.innerHTML = `
            <div class="no-games">
                <div class="no-games-icon">⚠️</div>
                <h3 class="no-games-title">خطأ في التحميل</h3>
                <p class="no-games-description">${message}</p>
            </div>
        `;
    }
}

// Notification System - نظام الإشعارات
function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    $$('.notification').forEach(notification => notification.remove());
    
    const notification = createElement('div', `notification notification-${type}`);
    notification.textContent = message;
    
    // Styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'error' ? 'var(--danger)' : 'var(--success)',
        color: 'var(--text-primary)',
        padding: 'var(--space-md) var(--space-lg)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-lg)',
        zIndex: 'var(--z-tooltip)',
        transform: 'translateX(100%)',
        transition: 'transform var(--transition-normal)',
        maxWidth: '300px'
    });
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after duration
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

// Performance Monitoring - مراقبة الأداء
function measurePerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('📊 Performance Metrics:', {
                    loadTime: Math.round(perfData.loadEventEnd - perfData.loadEventStart),
                    domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart)
                });
            }, 1000);
        });
    }
}

// Service Worker - خدمة العمل
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('✅ Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('❌ Service Worker registration failed:', error);
                });
        });
    }
}

// Keyboard Navigation - التنقل بلوحة المفاتيح
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Tab navigation for store filter tabs
        if (e.key === 'Tab' && e.target.classList.contains('store-filter-tab')) {
            const tabs = $$('.store-filter-tab');
            const currentIndex = Array.from(tabs).indexOf(e.target);
            
            if (e.shiftKey && currentIndex > 0) {
                e.preventDefault();
                tabs[currentIndex - 1].focus();
            } else if (!e.shiftKey && currentIndex < tabs.length - 1) {
                e.preventDefault();
                tabs[currentIndex + 1].focus();
            }
        }
        
        // Enter/Space to activate tabs
        if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('store-filter-tab')) {
            e.preventDefault();
            e.target.click();
        }
    });
}

// Intersection Observer - مراقب التقاطع
function initIntersectionObserver() {
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Observe game cards
        $$('.game-card').forEach(card => {
            observer.observe(card);
        });
    }
}

// App Initialization - تهيئة التطبيق
function initApp() {
    console.log('🚀 Initializing Games100 App...');
    
    // Initialize components
    initLanguageToggle();
    initStoreFilterTabs();
    initKeyboardNavigation();
    measurePerformance();
    registerServiceWorker();
    
    // Hide loading screen
    hideLoadingScreen();
    
    // Load games data
    loadGamesData();
    
    // Initialize intersection observer after games are loaded
    setTimeout(initIntersectionObserver, 1000);
    
    console.log('✅ Games100 App initialized successfully!');
}

// Event Listeners - مستمعي الأحداث
document.addEventListener('DOMContentLoaded', initApp);

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && allGames.length === 0) {
        // Reload data if page becomes visible and no games loaded
        loadGamesData();
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    showNotification('Connection restored', 'success');
    if (allGames.length === 0) {
        loadGamesData();
    }
});

window.addEventListener('offline', () => {
    showNotification('Connection lost', 'error');
});
