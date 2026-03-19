#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت تنظيف الألعاب المنتهية
Cleanup Expired Games Script

هذا السكربت يقوم بتنظيف جميع ملفات JSON من الألعاب التي انتهت فترة خصمها
This script cleans all JSON files from games whose discount period has expired
"""

import json
import datetime
import os

def is_game_expired(game, source="unknown"):
    """
    التحقق من انتهاء صلاحية اللعبة
    Check if a game's discount period has expired
    """
    try:
        end_date = None
        
        # Epic Games: game[7]
        if source == "epic" and len(game) > 7 and game[7] and game[7] != 'null' and game[7] != 'None':
            end_date = game[7]
        # Steam: game[7] للألعاب المخصومة
        elif source == "steam" and len(game) > 7 and game[7] and game[7] != 'null' and game[7] != 'None':
            end_date = game[7]
        # Steam: game[5] للألعاب القديمة
        elif source == "steam" and len(game) > 5 and game[5] and isinstance(game[5], str) and '-' in game[5]:
            end_date = game[5]
        
        # إذا لم يكن هناك تاريخ انتهاء، اللعبة ليست منتهية
        if not end_date:
            return False
        
        # التحقق من انتهاء التاريخ
        try:
            end_datetime = None
            
            # Epic: تنسيق ISO 8601
            if source == "epic":
                try:
                    end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    # تحويل إلى local time للمقارنة
                    end_datetime = end_datetime.replace(tzinfo=None)
                except:
                    pass
            
            # Steam: تنسيق YYYY-MM-DD HH:MM:SS
            if not end_datetime and isinstance(end_date, str):
                try:
                    end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                    except:
                        pass
            
            if not end_datetime:
                return False
            
            now = datetime.datetime.now()
            is_expired = end_datetime <= now
            
            if is_expired:
                print(f"  ⏰ منتهية: {game[0]} (انتهت في {end_date})")
            
            return is_expired
            
        except Exception as e:
            print(f"  ⚠️ خطأ في تحليل تاريخ الانتهاء: {e}")
            return False
            
    except Exception as e:
        print(f"  ⚠️ خطأ في التحقق من انتهاء اللعبة: {e}")
        return False

def clean_json_file(filename, source):
    """
    تنظيف ملف JSON من الألعاب المنتهية
    Clean a JSON file from expired games
    """
    print(f"\n{'='*60}")
    print(f"📁 معالجة ملف: {filename}")
    print(f"{'='*60}")
    
    if not os.path.exists(filename):
        print(f"⚠️ الملف غير موجود: {filename}")
        return
    
    try:
        # قراءة الملف
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # إحصائيات قبل التنظيف
        free_games_before = len(data.get('free_games', []))
        discounted_games_before = len(data.get('discounted_games', []))
        total_before = free_games_before + discounted_games_before
        
        print(f"📊 قبل التنظيف:")
        print(f"  - ألعاب مجانية: {free_games_before}")
        print(f"  - ألعاب مخصومة: {discounted_games_before}")
        print(f"  - الإجمالي: {total_before}")
        
        # تنظيف الألعاب المجانية
        print(f"\n🔍 فحص الألعاب المجانية...")
        cleaned_free_games = []
        expired_free_count = 0
        
        for game in data.get('free_games', []):
            if not is_game_expired(game, source):
                cleaned_free_games.append(game)
            else:
                expired_free_count += 1
        
        # تنظيف الألعاب المخصومة
        print(f"\n🔍 فحص الألعاب المخصومة...")
        cleaned_discounted_games = []
        expired_discounted_count = 0
        
        for game in data.get('discounted_games', []):
            if not is_game_expired(game, source):
                cleaned_discounted_games.append(game)
            else:
                expired_discounted_count += 1
        
        # تحديث البيانات
        data['free_games'] = cleaned_free_games
        data['discounted_games'] = cleaned_discounted_games
        data['total_count'] = len(cleaned_free_games) + len(cleaned_discounted_games)
        
        # إحصائيات بعد التنظيف
        total_after = len(cleaned_free_games) + len(cleaned_discounted_games)
        total_removed = (expired_free_count + expired_discounted_count)
        
        print(f"\n📊 بعد التنظيف:")
        print(f"  - ألعاب مجانية: {len(cleaned_free_games)} (تم حذف {expired_free_count})")
        print(f"  - ألعاب مخصومة: {len(cleaned_discounted_games)} (تم حذف {expired_discounted_count})")
        print(f"  - الإجمالي: {total_after} (تم حذف {total_removed})")
        
        # حفظ الملف المنظف
        if total_removed > 0:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ تم حفظ الملف المنظف بنجاح!")
        else:
            print(f"\n✅ لا توجد ألعاب منتهية للحذف")
        
    except Exception as e:
        print(f"❌ خطأ في معالجة الملف {filename}: {e}")

def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("="*60)
    print("🧹 سكربت تنظيف الألعاب المنتهية")
    print("🧹 Cleanup Expired Games Script")
    print("="*60)
    print(f"⏰ الوقت الحالي: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تنظيف ملف Epic Games
    clean_json_file('epic_goods_detail.json', 'epic')
    
    # تنظيف ملف Steam
    clean_json_file('free_goods_detail.json', 'steam')
    
    print("\n" + "="*60)
    print("✅ تم الانتهاء من تنظيف جميع الملفات!")
    print("="*60)

if __name__ == "__main__":
    main()
