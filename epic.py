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
import time

def get_epic_free_games():
    """
    جلب الألعاب المجانية من Epic Games Store
    Fetch free games from Epic Games Store
    """
    print("بدء جلب الألعاب المجانية من Epic Games...")
    
    free_games = []
    
    # 1. Epic Games API للعروض المجانية الحالية
    url1 = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    
    # 2. Epic Games API للعروض والخصومات
    url2 = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"
    
    # Headers مطلوبة للوصول لـ Epic API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Origin': 'https://store.epicgames.com',
        'Referer': 'https://store.epicgames.com/'
    }
    
    urls_to_try = [url1, url2]
    
    for url in urls_to_try:
        try:
            print(f"جاري الاتصال بـ Epic Games API: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print("تم جلب البيانات بنجاح من Epic Games")
            
            # استخراج الألعاب المجانية من البيانات
            if 'data' in data and 'Catalog' in data['data']:
                catalog = data['data']['Catalog']
                
                if 'searchStore' in catalog and 'elements' in catalog['searchStore']:
                    games = catalog['searchStore']['elements']
                    
                    for game in games:
                        # التحقق من أن اللعبة مجانية أو لديها خصم عالي
                        if 'promotions' in game and game['promotions']:
                            promotions = game['promotions']
                            
                            # البحث عن عروض مجانية أو خصومات عالية
                            is_free = False
                            discount_percentage = 0
                            end_date = None
                            original_price = ""
                            discounted_price = ""
                            
                            # فحص العروض الحالية
                            if 'promotionalOffers' in promotions:
                                for offer in promotions['promotionalOffers']:
                                    for promo in offer['promotionalOffers']:
                                        if promo.get('discountSetting', {}).get('discountType') == 'PERCENTAGE':
                                            discount_percentage = promo['discountSetting']['discountPercentage']
                                            if discount_percentage == 0:  # مجانية 100%
                                                is_free = True
                                                end_date = promo.get('endDate')
                                                break
                            
                            # فحص العروض المستقبلية أيضاً
                            if not is_free and 'upcomingPromotionalOffers' in promotions:
                                for offer in promotions['upcomingPromotionalOffers']:
                                    for promo in offer['promotionalOffers']:
                                        if promo.get('discountSetting', {}).get('discountType') == 'PERCENTAGE':
                                            discount_percentage = promo['discountSetting']['discountPercentage']
                                            if discount_percentage == 0:  # مجانية 100%
                                                is_free = True
                                                end_date = promo.get('endDate')
                                                break
                            
                            # فحص السعر الأساسي للعبة
                            if 'price' in game and game['price']:
                                price_data = game['price']
                                if 'totalPrice' in price_data:
                                    total_price = price_data['totalPrice']
                                    
                                    # إذا كان السعر الحالي 0، فهي مجانية
                                    if total_price.get('discountPrice', 0) == 0:
                                        is_free = True
                                        original_price = f"{total_price.get('originalPrice', 0) / 100:.2f} USD"
                                        discounted_price = "Free"
                                    elif total_price.get('originalPrice', 0) > 0:
                                        original_price = f"{total_price.get('originalPrice', 0) / 100:.2f} USD"
                                        discounted_price = f"{total_price.get('discountPrice', 0) / 100:.2f} USD"
                                        
                                        # حساب نسبة الخصم
                                        if total_price.get('originalPrice', 0) > 0:
                                            calculated_discount = ((total_price.get('originalPrice', 0) - total_price.get('discountPrice', 0)) / total_price.get('originalPrice', 0)) * 100
                                            if calculated_discount >= 90:  # خصم 90% أو أكثر
                                                is_free = True
                                                discount_percentage = calculated_discount
                            
                            if is_free:
                                game_name = game.get('title', 'Unknown Game')
                                
                                # بناء رابط اللعبة
                                game_url = ""
                                if 'catalogNs' in game and 'mappings' in game['catalogNs']:
                                    mappings = game['catalogNs']['mappings']
                                    if mappings and len(mappings) > 0:
                                        page_slug = mappings[0].get('pageSlug', '')
                                        if page_slug:
                                            game_url = f"https://store.epicgames.com/en-US/p/{page_slug}"
                                
                                if not game_url:
                                    # محاولة بديلة للحصول على الرابط
                                    if 'id' in game:
                                        game_url = f"https://store.epicgames.com/en-US/p/{game['id']}"
                                    else:
                                        game_url = "https://store.epicgames.com/"
                                
                                # استخراج صورة اللعبة
                                image_url = ""
                                if 'keyImages' in game:
                                    # البحث عن أفضل صورة متاحة
                                    for img_type in ['OfferImageWide', 'Thumbnail', 'DieselStoreFrontWide', 'DieselStoreFrontTall']:
                                        for img in game['keyImages']:
                                            if img.get('type') == img_type:
                                                image_url = img.get('url', '')
                                                break
                                        if image_url:
                                            break
                                
                                # استخراج وصف اللعبة
                                description = game.get('description', '')
                                if not description:
                                    description = game.get('longDescription', '')
                                
                                # تنسيق تاريخ الانتهاء
                                formatted_end_date = None
                                if end_date:
                                    try:
                                        # Epic يستخدم تنسيق ISO 8601
                                        end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                        formatted_end_date = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
                                    except:
                                        formatted_end_date = None
                                
                                # تحديد نسبة الخصم للعرض
                                discount_text = ""
                                if discount_percentage == 0:
                                    discount_text = "خصم 100% - مجاني"
                                elif discount_percentage > 0:
                                    discount_text = f"خصم {discount_percentage:.0f}%"
                                
                                # التحقق من الألعاب التي تحتوي على "Coming Soon"
                                if 'promotions' in game and game['promotions']:
                                    promotions = game['promotions']
                                    has_coming_soon = False
                                    
                                    # فحص العروض المستقبلية للعثور على "Coming Soon"
                                    if 'upcomingPromotionalOffers' in promotions:
                                        for offer in promotions['upcomingPromotionalOffers']:
                                            for promo in offer['promotionalOffers']:
                                                if promo.get('discountSetting', {}).get('discountType') == 'PERCENTAGE':
                                                    if promo['discountSetting']['discountPercentage'] == 0:
                                                        has_coming_soon = True
                                                        break
                                    
                                    if has_coming_soon:
                                        discount_text = "Coming Soon - مجاني قريباً"
                                
                                # بناء البيانات النهائية
                                game_data = [
                                    game_name,                    # [0] اسم اللعبة
                                    game_url,                     # [1] رابط اللعبة
                                    image_url,                    # [2] صورة اللعبة
                                    description,                  # [3] وصف اللعبة
                                    original_price,               # [4] السعر الأصلي
                                    discounted_price,             # [5] السعر بعد الخصم
                                    discount_text,                # [6] نسبة الخصم
                                    formatted_end_date            # [7] تاريخ انتهاء العرض
                                ]
                                
                                # التحقق من عدم وجود اللعبة مسبقاً
                                game_exists = False
                                for existing_game in free_games:
                                    if existing_game[0] == game_name and existing_game[1] == game_url:
                                        game_exists = True
                                        break
                                
                                if not game_exists:
                                    free_games.append(game_data)
                                    print(f"تم العثور على لعبة مجانية: {game_name}")
                                    if discount_text:
                                        print(f"  الخصم: {discount_text}")
            
            # إضافة تأخير قصير بين الطلبات
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"خطأ في الاتصال بـ Epic Games API ({url}): {e}")
            continue
        except json.JSONDecodeError as e:
            print(f"خطأ في تحليل بيانات Epic Games: {e}")
            continue
        except Exception as e:
            print(f"خطأ غير متوقع: {e}")
            continue
    
    # لا نضيف الألعاب المجانية دائماً - فقط الألعاب التي عليها خصم 100%
    print("تم تجاهل الألعاب المجانية دائماً - نريد فقط الألعاب التي عليها خصم 100%")
    
    print(f"إجمالي الألعاب المجانية من Epic: {len(free_games)}")
    return free_games

def get_epic_additional_games():
    """
    جلب ألعاب مجانية إضافية من Epic Games
    """
    additional_games = []
    
    # قائمة ببعض الألعاب المجانية الثابتة في Epic Games
    permanent_free_games = [
        {
            "name": "Fortnite",
            "url": "https://store.epicgames.com/en-US/p/fortnite",
            "image": "https://cdn2.unrealengine.com/Diesel%2Fproductv2%2Ffortnite%2Fhome%2Ffortnite-br-1200x1600-1200x1600-63bb5bb2f96f.jpg",
            "description": "Fortnite is the completely free multiplayer game where you and your friends collaborate to create your dream world or compete against each other in Battle Royale.",
        },
        {
            "name": "Rocket League",
            "url": "https://store.epicgames.com/en-US/p/rocket-league",
            "image": "https://cdn1.epicgames.com/spt/9408a40499f647de8ecebfe41ae03c55/rocket-league-35bma.jpg",
            "description": "Winner or nominee of more than 150 'Game of the Year' awards, Rocket League is one of the most critically-acclaimed sports games of all time.",
        },
        {
            "name": "Fall Guys",
            "url": "https://store.epicgames.com/en-US/p/fall-guys",
            "image": "https://cdn1.epicgames.com/spt/b7c1c96f72274bbcb5fbbf93dd8b6dc5/fall-guys-offer-6ow21.jpg",
            "description": "Fall Guys is a free, cross-platform massively multiplayer party royale game where up to 60 players compete in rounds of escalating chaos until one victor remains!",
        }
    ]
    
    for game in permanent_free_games:
        game_data = [
            game["name"],                          # [0] اسم اللعبة
            game["url"],                           # [1] رابط اللعبة  
            game["image"],                         # [2] صورة اللعبة
            game["description"],                   # [3] وصف اللعبة
            "Free",                                # [4] السعر الأصلي
            "Free",                                # [5] السعر الحالي
            "مجاني دائماً",                        # [6] نوع العرض
            None                                   # [7] تاريخ الانتهاء
        ]
        additional_games.append(game_data)
    
    return additional_games

def is_game_expired(game):
    """
    التحقق من انتهاء صلاحية اللعبة
    Check if a game's discount period has expired
    """
    try:
        # البحث عن تاريخ الانتهاء في game[7]
        end_date = None
        
        if len(game) > 7 and game[7] and game[7] != 'null' and game[7] != 'None':
            end_date = game[7]
        
        # إذا لم يكن هناك تاريخ انتهاء، اللعبة ليست منتهية (مجانية دائماً)
        if not end_date:
            return False
        
        # التحقق من انتهاء التاريخ
        try:
            end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # منتهية إذا كان التاريخ في الماضي
            is_expired = end_datetime <= now
            
            if is_expired:
                print(f"⏰ اللعبة منتهية: {game[0]} (انتهت في {end_date})")
            
            return is_expired
        except Exception as e:
            print(f"خطأ في تحليل تاريخ الانتهاء: {e}")
            return False
            
    except Exception as e:
        print(f"خطأ في التحقق من انتهاء اللعبة: {e}")
        return False

def clean_expired_games(games_list):
    """
    تنظيف قائمة الألعاب من الألعاب المنتهية
    Clean the games list from expired games
    """
    if not games_list:
        return []
    
    cleaned_games = []
    expired_count = 0
    
    for game in games_list:
        if not is_game_expired(game):
            cleaned_games.append(game)
        else:
            expired_count += 1
    
    if expired_count > 0:
        print(f"🗑️ تم إزالة {expired_count} لعبة منتهية من القائمة")
    
    return cleaned_games

def save_epic_games_data(games_list):
    """
    حفظ بيانات الألعاب المجانية من Epic في ملف JSON
    Save Epic free games data to JSON file
    """
    try:
        # تنظيف الألعاب المنتهية من القائمة الجديدة
        print("\n🔍 فحص الألعاب الجديدة للتأكد من عدم انتهائها...")
        games_list = clean_expired_games(games_list)
        
        # قراءة البيانات الموجودة وتنظيفها من الألعاب المنتهية
        existing_data = {}
        try:
            import os
            if os.path.exists("epic_goods_detail.json"):
                with open("epic_goods_detail.json", "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    
                print("\n🔍 فحص الألعاب الموجودة في الملف...")
                if "free_games" in existing_data:
                    existing_data["free_games"] = clean_expired_games(existing_data["free_games"])
                if "discounted_games" in existing_data:
                    existing_data["discounted_games"] = clean_expired_games(existing_data["discounted_games"])
        except Exception as e:
            print(f"⚠️ لم يتم العثور على ملف سابق أو حدث خطأ: {e}")
        
        # فصل الألعاب المجانية عن الألعاب بخصم
        free_games = []
        discounted_games = []
        
        for game in games_list:
            discount_text = game[6] if len(game) > 6 else ""
            
            # الألعاب التي عليها خصم 100% فقط (بدون Coming Soon) وليس مجاني دائماً
            if discount_text and "100%" in discount_text and "Coming Soon" not in discount_text and "مجاني دائماً" not in discount_text:
                free_games.append(game)
            # إذا كانت لديها خصم عالي (90% أو أكثر)
            elif discount_text and any(x in discount_text for x in ["90%", "95%", "99%"]):
                discounted_games.append(game)
        
        # دمج مع البيانات الموجودة (بعد التنظيف)
        if existing_data:
            existing_free = existing_data.get("free_games", [])
            existing_discounted = existing_data.get("discounted_games", [])
            
            # إضافة الألعاب الجديدة فقط (تجنب التكرار)
            for game in free_games:
                if game not in existing_free:
                    existing_free.append(game)
            
            for game in discounted_games:
                if game not in existing_discounted:
                    existing_discounted.append(game)
            
            free_games = existing_free
            discounted_games = existing_discounted
        
        data = {
            "total_count": len(free_games),
            "free_games": free_games,
            "discounted_games": discounted_games,
            "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
            "source": "Epic Games Store"
        }
        
        with open("epic_goods_detail.json", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ بيانات Epic Games بنجاح في epic_goods_detail.json")
        print(f"📊 الألعاب المجانية: {len(free_games)}, الألعاب بخصم: {len(discounted_games)}")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في حفظ بيانات Epic Games: {e}")
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
                if len(game) > 6 and game[6]:  # نسبة الخصم
                    print(f"   العرض: {game[6]}")
                if len(game) > 7 and game[7]:  # تاريخ الانتهاء
                    print(f"   ينتهي في: {game[7]}")
                print()
        else:
            print("❌ فشل في حفظ البيانات")
    else:
        print("⚠️ لم يتم العثور على ألعاب مجانية من Epic Games حالياً")
        print("قد يكون السبب عدم وجود عروض مجانية أو تغيّر في API")

if __name__ == "__main__":
    main() 