#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update All Games - تحديث جميع الألعاب من جميع المنصات
Update All Games - Fetch free games from all platforms
"""

import sys
import os
from pathlib import Path
import datetime
import pytz

# إضافة مجلد scripts إلى المسار
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# استيراد جميع السكريبترات
try:
    from epic_scraper import get_epic_free_games, save_epic_games_data
    from steam_scraper import *
    from gog_scraper import get_gog_free_games, save_gog_games_data
    from playstation_scraper import get_playstation_free_games, save_playstation_games_data
    from ubisoft_scraper import get_ubisoft_free_games, save_ubisoft_games_data
    from xbox_scraper import get_xbox_free_games, save_xbox_games_data
except ImportError as e:
    print(f"❌ خطأ في استيراد المكتبات: {e}")
    print("تأكد من تثبيت جميع المكتبات المطلوبة:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def print_header():
    """طباعة رأس البرنامج"""
    print("=" * 80)
    print("🎮 تحديث جميع الألعاب المجانية من جميع المنصات")
    print("🎮 Update All Free Games from All Platforms")
    print("=" * 80)
    print(f"⏰ وقت البدء: {datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

def update_epic_games():
    """تحديث ألعاب Epic Games"""
    print("\n" + "=" * 80)
    print("🎮 Epic Games Store")
    print("=" * 80)
    try:
        games = get_epic_free_games()
        if games:
            save_epic_games_data(games)
            print(f"✅ تم تحديث Epic Games - عدد الألعاب: {len(games)}")
            return True
        else:
            print("⚠️ لم يتم العثور على ألعاب من Epic Games")
            # حفظ قائمة فارغة لتحديث الوقت
            save_epic_games_data([])
            return False
    except Exception as e:
        print(f"❌ خطأ في تحديث Epic Games: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_steam_games():
    """تحديث ألعاب Steam - يتم تشغيله من الملف الأصلي"""
    print("\n" + "=" * 80)
    print("🎮 Steam Store")
    print("=" * 80)
    print("⚠️ Steam scraper يعمل بشكل مستقل - الرجاء تشغيل steam_scraper.py مباشرة")
    print("السبب: steam_scraper.py يستخدم multi-threading معقد")
    return True

def update_gog_games():
    """تحديث ألعاب GOG"""
    print("\n" + "=" * 80)
    print("🎮 GOG Store")
    print("=" * 80)
    try:
        games = get_gog_free_games()
        if games:
            save_gog_games_data(games)
            print(f"✅ تم تحديث GOG - عدد الألعاب: {len(games)}")
            return True
        else:
            print("⚠️ لم يتم العثور على ألعاب من GOG")
            # حفظ قائمة فارغة لتحديث الوقت
            save_gog_games_data([])
            return False
    except Exception as e:
        print(f"❌ خطأ في تحديث GOG: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_playstation_games():
    """تحديث ألعاب PlayStation"""
    print("\n" + "=" * 80)
    print("🎮 PlayStation Store")
    print("=" * 80)
    try:
        games = get_playstation_free_games()
        if games:
            save_playstation_games_data(games)
            print(f"✅ تم تحديث PlayStation - عدد الألعاب: {len(games)}")
            return True
        else:
            print("⚠️ لم يتم العثور على ألعاب من PlayStation")
            # حفظ قائمة فارغة لتحديث الوقت
            save_playstation_games_data([])
            return False
    except Exception as e:
        print(f"❌ خطأ في تحديث PlayStation: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_ubisoft_games():
    """تحديث ألعاب Ubisoft"""
    print("\n" + "=" * 80)
    print("🎮 Ubisoft Connect")
    print("=" * 80)
    try:
        games = get_ubisoft_free_games()
        if games:
            save_ubisoft_games_data(games)
            print(f"✅ تم تحديث Ubisoft - عدد الألعاب: {len(games)}")
            return True
        else:
            print("⚠️ لم يتم العثور على ألعاب من Ubisoft")
            # حفظ قائمة فارغة لتحديث الوقت
            save_ubisoft_games_data([])
            return False
    except Exception as e:
        print(f"❌ خطأ في تحديث Ubisoft: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_xbox_games():
    """تحديث ألعاب Xbox"""
    print("\n" + "=" * 80)
    print("🎮 Xbox Store")
    print("=" * 80)
    try:
        games = get_xbox_free_games()
        if games:
            save_xbox_games_data(games)
            print(f"✅ تم تحديث Xbox - عدد الألعاب: {len(games)}")
            return True
        else:
            print("⚠️ لم يتم العثور على ألعاب من Xbox")
            # حفظ قائمة فارغة لتحديث الوقت
            save_xbox_games_data([])
            return False
    except Exception as e:
        print(f"❌ خطأ في تحديث Xbox: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # إحصائيات
    total_platforms = 6
    successful_updates = 0
    failed_updates = 0
    
    # تحديث كل منصة
    platforms = [
        ("Epic Games", update_epic_games),
        ("Steam", update_steam_games),
        ("GOG", update_gog_games),
        ("PlayStation", update_playstation_games),
        ("Ubisoft", update_ubisoft_games),
        ("Xbox", update_xbox_games)
    ]
    
    for platform_name, update_func in platforms:
        try:
            if update_func():
                successful_updates += 1
            else:
                failed_updates += 1
        except Exception as e:
            print(f"❌ خطأ في تحديث {platform_name}: {e}")
            failed_updates += 1
    
    # طباعة الملخص
    print("\n" + "=" * 80)
    print("📊 ملخص التحديث - Update Summary")
    print("=" * 80)
    print(f"✅ منصات ناجحة: {successful_updates}/{total_platforms}")
    print(f"❌ منصات فاشلة: {failed_updates}/{total_platforms}")
    print(f"⏰ وقت الانتهاء: {datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # ملاحظة مهمة
    print("\n⚠️ ملاحظة: لتحديث Steam بشكل كامل، قم بتشغيل:")
    print("   python scripts/steam_scraper.py")
    print()
    
    if successful_updates == total_platforms:
        print("🎉 تم تحديث جميع المنصات بنجاح!")
        return 0
    elif successful_updates > 0:
        print("⚠️ تم تحديث بعض المنصات فقط")
        return 1
    else:
        print("❌ فشل في تحديث جميع المنصات")
        return 2

if __name__ == "__main__":
    exit(main())

