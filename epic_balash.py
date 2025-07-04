#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Epic Games Balash - جلب الألعاب المجانية من Epic Games
Epic Games Balash - Fetch free games from Epic Games Store
"""

import requests
import json
import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_epic_free_games():
    """
    جلب الألعاب المجانية من Epic Games Store
    Fetch free games from Epic Games Store
    """
    print("بدء جلب الألعاب المجانية من Epic Games...")
    
    # Epic Games API endpoint للعروض المجانية
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    
    # Headers مطلوبة للوصول لـ Epic API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Origin': 'https://store.epicgames.com',
        'Referer': 'https://store.epicgames.com/'
    }
    
    try:
        print("جاري الاتصال بـ Epic Games API...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("تم جلب البيانات بنجاح من Epic Games")
        
        free_games = []
        
        # استخراج الألعاب المجانية من البيانات
        if 'data' in data and 'Catalog' in data['data']:
            catalog = data['data']['Catalog']
            
            if 'searchStore' in catalog and 'elements' in catalog['searchStore']:
                games = catalog['searchStore']['elements']
                
                for game in games:
                    # التحقق من أن اللعبة مجانية
                    if 'promotions' in game and game['promotions']:
                        promotions = game['promotions']
                        
                        # البحث عن عروض مجانية
                        is_free = False
                        end_date = None
                        
                        if 'promotionalOffers' in promotions:
                            for offer in promotions['promotionalOffers']:
                                for promo in offer['promotionalOffers']:
                                    if promo.get('discountSetting', {}).get('discountType') == 'PERCENTAGE':
                                        if promo['discountSetting']['discountPercentage'] == 0:
                                            is_free = True
                                            end_date = promo.get('endDate')
                                            break
                        
                        if is_free:
                            game_name = game.get('title', 'Unknown Game')
                            game_url = f"https://store.epicgames.com/en-US/p/{game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug', '')}"
                            
                            # استخراج صورة اللعبة
                            image_url = ""
                            if 'keyImages' in game:
                                for img in game['keyImages']:
                                    if img.get('type') == 'OfferImageWide':
                                        image_url = img.get('url', '')
                                        break
                            
                            # استخراج وصف اللعبة
                            description = game.get('description', '')
                            
                            # تنسيق تاريخ الانتهاء
                            formatted_end_date = None
                            if end_date:
                                try:
                                    # Epic يستخدم تنسيق ISO 8601
                                    end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                    formatted_end_date = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    formatted_end_date = None
                            
                            free_games.append([
                                game_name,
                                game_url,
                                image_url,
                                description,
                                formatted_end_date
                            ])
                            
                            print(f"تم العثور على لعبة مجانية: {game_name}")
        
        print(f"إجمالي الألعاب المجانية من Epic: {len(free_games)}")
        return free_games
        
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الاتصال بـ Epic Games: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"خطأ في تحليل بيانات Epic Games: {e}")
        return []
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")
        return []

def save_epic_games_data(games_list):
    """
    حفظ بيانات الألعاب المجانية من Epic في ملف JSON
    Save Epic free games data to JSON file
    """
    try:
        data = {
            "total_count": len(games_list),
            "free_list": games_list,
            "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
            "source": "Epic Games Store"
        }
        
        with open("epic_goods_detail.json", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ بيانات Epic Games بنجاح في epic_goods_detail.json")
        return True
        
    except Exception as e:
        print(f"خطأ في حفظ بيانات Epic Games: {e}")
        return False

def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("=" * 50)
    print("🎮 Epic Games Balash - جلب الألعاب المجانية")
    print("🎮 Epic Games Balash - Fetch Free Games")
    print("=" * 50)
    
    # جلب الألعاب المجانية من Epic
    epic_games = get_epic_free_games()
    
    if epic_games:
        # حفظ البيانات
        if save_epic_games_data(epic_games):
            print(f"✅ تم تحديث قائمة الألعاب المجانية من Epic بنجاح!")
            print(f"📊 عدد الألعاب: {len(epic_games)}")
            
            # عرض قائمة الألعاب
            print("\n📋 قائمة الألعاب المجانية من Epic:")
            for i, game in enumerate(epic_games, 1):
                print(f"{i}. {game[0]}")
                if game[4]:  # تاريخ الانتهاء
                    print(f"   ينتهي في: {game[4]}")
                print()
        else:
            print("❌ فشل في حفظ البيانات")
    else:
        print("⚠️ لم يتم العثور على ألعاب مجانية من Epic Games حالياً")
        print("قد يكون السبب عدم وجود عروض مجانية أو تغيّر في API")

if __name__ == "__main__":
    main() 