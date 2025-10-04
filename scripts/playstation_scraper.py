#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlayStation Balash - جلب الألعاب المجانية من PlayStation Store
PlayStation Balash - Fetch free games from PlayStation Store
"""

import requests
import json
import datetime
import pytz
from bs4 import BeautifulSoup

def get_playstation_free_games():
    """
    جلب الألعاب المجانية من PlayStation Store
    Fetch free games from PlayStation Store
    """
    print("بدء جلب الألعاب المجانية من PlayStation Store...")
    
    # محاولة استخدام API أو صفحة مختلفة
    urls = [
        "https://store.playstation.com/en-us/category/44d8bb20-653e-431e-8ad0-c0a365f68d2f",
        "https://store.playstation.com/en-us/grid/STORE-MSF77008-FREEGAMES",
        "https://store.playstation.com/en-us/category/44d8bb20-653e-431e-8ad0-c0a365f68d2f?size=30&start=0"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    free_games = []
    
    for url in urls:
        try:
            print(f"جاري الاتصال بـ PlayStation Store: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print("تم جلب البيانات بنجاح من PlayStation")
            
            # محاولة استخراج الألعاب من HTML
            game_elements = soup.find_all(['div', 'li'])
            game_elements = [elem for elem in game_elements if elem.get('class') and any(keyword in ' '.join(elem.get('class')).lower() for keyword in ['game', 'product', 'tile', 'card'])]
            
            for element in game_elements:
                try:
                    # البحث عن اسم اللعبة
                    title_selectors = ['h3', 'h2', 'span', 'div']
                    game_name = ""
                    
                    for selector in title_selectors:
                        title_elem = element.find(selector)
                        if title_elem and title_elem.get('class'):
                            class_text = ' '.join(title_elem.get('class')).lower()
                            if any(keyword in class_text for keyword in ['title', 'name', 'product']):
                                game_name = title_elem.get_text(strip=True)
                                break
                    
                    if not game_name:
                        continue
                    
                    # البحث عن الرابط
                    link_elem = element.find('a')
                    game_url = ""
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('/'):
                            game_url = "https://store.playstation.com" + href
                        elif href.startswith('http'):
                            game_url = href
                    
                    # البحث عن الصورة
                    img_elem = element.find('img')
                    image_url = ""
                    if img_elem and img_elem.get('src'):
                        image_url = img_elem.get('src')
                        if not image_url.startswith('http'):
                            image_url = "https:" + image_url
                    
                    # البحث عن الوصف
                    desc_elem = element.find(['p', 'span'])
                    description = ""
                    if desc_elem and desc_elem.get('class'):
                        class_text = ' '.join(desc_elem.get('class')).lower()
                        if any(keyword in class_text for keyword in ['desc', 'summary']):
                            description = desc_elem.get_text(strip=True)
                    
                    # البحث عن السعر
                    price_elem = element.find(['span', 'div'])
                    is_free = False
                    if price_elem and price_elem.get('class'):
                        class_text = ' '.join(price_elem.get('class')).lower()
                        if any(keyword in class_text for keyword in ['price', 'cost']):
                            price_text = price_elem.get_text(strip=True).lower()
                            if any(keyword in price_text for keyword in ['free', '0', '$0', 'gratis']):
                                is_free = True
                    else:
                        # إذا لم نجد عنصر السعر، نفترض أنها مجانية (لأننا في صفحة الألعاب المجانية)
                        is_free = True
                    
                    if is_free and game_name and game_url:
                        # تجنب التكرار
                        if not any(game[0] == game_name for game in free_games):
                            free_games.append([
                                game_name,
                                game_url,
                                image_url,
                                description,
                                None
                            ])
                            print(f"تم العثور على لعبة مجانية: {game_name}")
                
                except Exception as e:
                    print(f"خطأ في معالجة لعبة من PlayStation: {e}")
                    continue
            
            if free_games:
                break
                
        except Exception as e:
            print(f"خطأ في الاتصال بـ PlayStation: {e}")
            continue
    
    print(f"إجمالي الألعاب المجانية من PlayStation: {len(free_games)}")
    return free_games

def save_playstation_games_data(games_list):
    """
    حفظ بيانات الألعاب المجانية من PlayStation في ملف JSON
    Save PlayStation free games data to JSON file
    """
    try:
        data = {
            "total_count": len(games_list),
            "free_list": games_list,
            "update_time": datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
            "source": "PlayStation Store"
        }
        
        with open("../data/playstation_goods_detail.json", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ بيانات PlayStation بنجاح في ../data/playstation_goods_detail.json")
        return True
        
    except Exception as e:
        print(f"خطأ في حفظ بيانات PlayStation: {e}")
        return False

def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("=" * 50)
    print("🎮 PlayStation Balash - جلب الألعاب المجانية")
    print("🎮 PlayStation Balash - Fetch Free Games")
    print("=" * 50)
    
    # جلب الألعاب المجانية من PlayStation
    playstation_games = get_playstation_free_games()
    
    if playstation_games:
        # حفظ البيانات
        if save_playstation_games_data(playstation_games):
            print(f"✅ تم تحديث قائمة الألعاب المجانية من PlayStation بنجاح!")
            print(f"📊 عدد الألعاب: {len(playstation_games)}")
            
            # عرض قائمة الألعاب
            print("\n📋 قائمة الألعاب المجانية من PlayStation:")
            for i, game in enumerate(playstation_games, 1):
                print(f"{i}. {game[0]}")
                print()
        else:
            print("❌ فشل في حفظ البيانات")
    else:
        print("⚠️ لم يتم العثور على ألعاب مجانية من PlayStation حالياً")
        print("قد يكون السبب عدم وجود عروض مجانية أو تغيّر في هيكل الموقع")

if __name__ == "__main__":
    main() 