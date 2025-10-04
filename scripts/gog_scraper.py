#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOG Balash - جلب الألعاب المجانية من GOG
GOG Balash - Fetch free games from GOG Store
"""

import requests
import json
import datetime
import pytz
from bs4 import BeautifulSoup
import re

def get_gog_free_games():
    """
    جلب الألعاب المجانية من GOG Store
    Fetch free games from GOG Store
    """
    print("بدء جلب الألعاب المجانية من GOG...")
    
    # GOG صفحة الألعاب المجانية
    url = "https://www.gog.com/games?price=free"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("جاري الاتصال بـ GOG Store...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("تم جلب البيانات بنجاح من GOG")
        
        free_games = []
        
        # البحث عن بطاقات الألعاب
        game_cards = soup.find_all('div', class_='product-tile')
        
        for card in game_cards:
            try:
                # استخراج اسم اللعبة
                title_elem = card.find('span', class_='product-tile__title')
                if not title_elem:
                    continue
                    
                game_name = title_elem.get_text(strip=True)
                
                # استخراج رابط اللعبة
                link_elem = card.find('a', class_='product-tile__link')
                if not link_elem:
                    continue
                    
                game_url = "https://www.gog.com" + link_elem.get('href', '')
                
                # استخراج صورة اللعبة
                img_elem = card.find('img', class_='product-tile__image')
                image_url = ""
                if img_elem:
                    image_url = img_elem.get('src', '')
                    if not image_url.startswith('http'):
                        image_url = "https:" + image_url
                
                # استخراج وصف اللعبة (إذا كان متوفراً)
                desc_elem = card.find('div', class_='product-tile__description')
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # التحقق من أن اللعبة مجانية فعلاً
                price_elem = card.find('span', class_='product-tile__price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True).lower()
                    if 'free' in price_text or '0' in price_text:
                        free_games.append([
                            game_name,
                            game_url,
                            image_url,
                            description,
                            None  # GOG عادة لا يحدد تاريخ انتهاء للعروض المجانية
                        ])
                        print(f"تم العثور على لعبة مجانية: {game_name}")
                
            except Exception as e:
                print(f"خطأ في معالجة لعبة من GOG: {e}")
                continue
        
        print(f"إجمالي الألعاب المجانية من GOG: {len(free_games)}")
        return free_games
        
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الاتصال بـ GOG: {e}")
        return []
    except Exception as e:
        print(f"خطأ غير متوقع في GOG: {e}")
        return []

def save_gog_games_data(games_list):
    """
    حفظ بيانات الألعاب المجانية من GOG في ملف JSON
    Save GOG free games data to JSON file
    """
    try:
        data = {
            "total_count": len(games_list),
            "free_list": games_list,
            "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
            "source": "GOG Store"
        }
        
        with open("../data/gog_goods_detail.json", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ بيانات GOG بنجاح في ../data/gog_goods_detail.json")
        return True
        
    except Exception as e:
        print(f"خطأ في حفظ بيانات GOG: {e}")
        return False

def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("=" * 50)
    print("🎮 GOG Balash - جلب الألعاب المجانية")
    print("🎮 GOG Balash - Fetch Free Games")
    print("=" * 50)
    
    # جلب الألعاب المجانية من GOG
    gog_games = get_gog_free_games()
    
    if gog_games:
        # حفظ البيانات
        if save_gog_games_data(gog_games):
            print(f"✅ تم تحديث قائمة الألعاب المجانية من GOG بنجاح!")
            print(f"📊 عدد الألعاب: {len(gog_games)}")
            
            # عرض قائمة الألعاب
            print("\n📋 قائمة الألعاب المجانية من GOG:")
            for i, game in enumerate(gog_games, 1):
                print(f"{i}. {game[0]}")
                print()
        else:
            print("❌ فشل في حفظ البيانات")
    else:
        print("⚠️ لم يتم العثور على ألعاب مجانية من GOG حالياً")
        print("قد يكون السبب عدم وجود عروض مجانية أو تغيّر في هيكل الموقع")

if __name__ == "__main__":
    main() 