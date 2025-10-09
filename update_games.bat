@echo off
chcp 65001 >nul
echo ================================================================================
echo 🎮 تحديث جميع الألعاب المجانية - Update All Free Games
echo ================================================================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت على النظام
    echo    Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python مثبت
echo.

REM التحقق من المكتبات المطلوبة
echo 📦 التحقق من المكتبات المطلوبة...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo ⚠️  المكتبات غير مثبتة. جاري التثبيت...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ فشل في تثبيت المكتبات
        pause
        exit /b 1
    )
)

echo ✅ جميع المكتبات مثبتة
echo.

REM تحديث جميع الألعاب
echo ================================================================================
echo 🚀 بدء تحديث الألعاب...
echo ================================================================================
echo.

REM تشغيل السكريبت الرئيسي
python scripts/update_all_games.py
if errorlevel 1 (
    echo.
    echo ❌ حدث خطأ أثناء تحديث بعض المنصات
) else (
    echo.
    echo ✅ تم التحديث بنجاح
)

echo.
echo ================================================================================
echo 🎮 تحديث Steam (اختياري - يستغرق وقتاً أطول)
echo ================================================================================
echo.
set /p update_steam="هل تريد تحديث Steam الآن؟ (y/n): "
if /i "%update_steam%"=="y" (
    echo جاري تحديث Steam...
    python scripts/steam_scraper.py
)

echo.
echo ================================================================================
echo 🎉 تم الانتهاء من جميع التحديثات
echo ================================================================================
echo.

REM تحديث الطوابع الزمنية
if exist scripts\update_timestamps.py (
    echo 🕒 تحديث الطوابع الزمنية...
    python scripts/update_timestamps.py
)

echo.
pause

