#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ubisoft Balash - جلب الألعاب المجانية من Ubisoft Connect
Ubisoft Balash - Fetch free games from Ubisoft Connect
"""

import requests
import json
import datetime
import pytz
import os
from pathlib import Path

def get_ubisoft_free_games():
    """
    جلب الألعاب المجانية من Ubisoft Connect
    Fetch free games from Ubisoft Connect
    """
    print("بدء جلب الألعاب المجانية من Ubisoft Connect...")
    
    # Ubisoft Connect API للعروض المجانية
    url = "https://store.ubisoft.com/uk/api/free-games"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Origin': 'https://store.ubisoft.com',
        'Referer': 'https://store.ubisoft.com/uk/free-games',
        'Cache-Control': 'no-cache'
    }
    
    try:
        print("جاري الاتصال بـ Ubisoft Connect...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("تم جلب البيانات بنجاح من Ubisoft")
        
        free_games = []
        
        # استخراج الألعاب المجانية من البيانات
        if 'games' in data:
            games = data['games']
            
            for game in games:
                try:
                    # التحقق من أن اللعبة مجانية
                    if game.get('price', {}).get('final') == 0:
                        game_name = game.get('name', 'Unknown Game')
                        game_url = f"https://store.ubisoft.com/uk/game/{game.get('slug', '')}"
                        
                        # استخراج صورة اللعبة
                        image_url = ""
                        if 'images' in game and game['images']:
                            for img in game['images']:
                                if img.get('type') == 'MASTER':
                                    image_url = img.get('url', '')
                                    break
                        
                        # استخراج وصف اللعبة
                        description = game.get('description', '')
                        
                        # تاريخ انتهاء العرض (إذا كان متوفراً)
                        end_date = None
                        if 'promotion' in game and game['promotion']:
                            end_date = game['promotion'].get('endDate')
                        
                        free_games.append([
                            game_name,
                            game_url,
                            image_url,
                            description,
                            end_date
                        ])
                        
                        print(f"تم العثور على لعبة مجانية: {game_name}")
                        
                except Exception as e:
                    print(f"خطأ في معالجة لعبة من Ubisoft: {e}")
                    continue
        
        print(f"إجمالي الألعاب المجانية من Ubisoft: {len(free_games)}")
        return free_games
        
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الاتصال بـ Ubisoft: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"خطأ في تحليل بيانات Ubisoft: {e}")
        return []
    except Exception as e:
        print(f"خطأ غير متوقع في Ubisoft: {e}")
        return []

def save_ubisoft_games_data(games_list):
    """
    حفظ بيانات الألعاب المجانية من Ubisoft في ملف JSON
    Save Ubisoft free games data to JSON file
    """
    try:
        # الحصول على المسار الصحيح لمجلد data
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent / 'data'
        data_dir.mkdir(exist_ok=True)
        output_file = data_dir / 'ubisoft_goods_detail.json'
        
        data = {
            "total_count": len(games_list),
            "free_list": games_list,
            "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
            "source": "Ubisoft Connect"
        }
        
        with open(output_file, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ بيانات Ubisoft بنجاح في {output_file}")
        return True
        
    except Exception as e:
        print(f"خطأ في حفظ بيانات Ubisoft: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("=" * 50)
    print("🎮 Ubisoft Balash - جلب الألعاب المجانية")
    print("🎮 Ubisoft Balash - Fetch Free Games")
    print("=" * 50)
    
    # جلب الألعاب المجانية من Ubisoft
    ubisoft_games = get_ubisoft_free_games()
    
    if ubisoft_games:
        # حفظ البيانات
        if save_ubisoft_games_data(ubisoft_games):
            print(f"✅ تم تحديث قائمة الألعاب المجانية من Ubisoft بنجاح!")
            print(f"📊 عدد الألعاب: {len(ubisoft_games)}")
            
            # عرض قائمة الألعاب
            print("\n📋 قائمة الألعاب المجانية من Ubisoft:")
            for i, game in enumerate(ubisoft_games, 1):
                print(f"{i}. {game[0]}")
                if game[4]:  # تاريخ الانتهاء
                    print(f"   ينتهي في: {game[4]}")
                print()
        else:
            print("❌ فشل في حفظ البيانات")
    else:
        print("⚠️ لم يتم العثور على ألعاب مجانية من Ubisoft حالياً")
        print("قد يكون السبب عدم وجود عروض مجانية أو تغيّر في API")

if __name__ == "__main__":
    main() 