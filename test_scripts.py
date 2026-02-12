#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للتحقق من عمل السكريبتات
Quick test to verify scripts are working
"""

import sys
import subprocess
import json
import os
from datetime import datetime

def print_header(text):
    """طباعة عنوان مميز"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_steam_script():
    """اختبار سكريبت Steam"""
    print_header("🎮 اختبار سكريبت Steam")
    
    try:
        # تشغيل السكريبت
        result = subprocess.run(
            [sys.executable, "steam.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 دقائق
        )
        
        if result.returncode == 0:
            print("✅ سكريبت Steam يعمل بنجاح")
            
            # التحقق من الملف الناتج
            if os.path.exists("free_goods_detail.json"):
                with open("free_goods_detail.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    free_count = len(data.get("free_games", []))
                    disc_count = len(data.get("discounted_games", []))
                    print(f"📊 الألعاب المجانية: {free_count}")
                    print(f"📊 الألعاب المخصومة: {disc_count}")
                    print(f"⏰ آخر تحديث: {data.get('update_time', 'غير متوفر')}")
            else:
                print("⚠️ لم يتم إنشاء ملف free_goods_detail.json")
                return False
        else:
            print("❌ فشل سكريبت Steam")
            print(f"الخطأ: {result.stderr}")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة تنفيذ سكريبت Steam (أكثر من 5 دقائق)")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار Steam: {e}")
        return False

def test_epic_script():
    """اختبار سكريبت Epic"""
    print_header("🎮 اختبار سكريبت Epic")
    
    try:
        # تشغيل السكريبت
        result = subprocess.run(
            [sys.executable, "epic.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 دقائق
        )
        
        if result.returncode == 0:
            print("✅ سكريبت Epic يعمل بنجاح")
            
            # التحقق من الملف الناتج
            if os.path.exists("epic_goods_detail.json"):
                with open("epic_goods_detail.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    free_count = len(data.get("free_games", []))
                    disc_count = len(data.get("discounted_games", []))
                    print(f"📊 الألعاب المجانية: {free_count}")
                    print(f"📊 الألعاب المخصومة: {disc_count}")
                    print(f"⏰ آخر تحديث: {data.get('update_time', 'غير متوفر')}")
            else:
                print("⚠️ لم يتم إنشاء ملف epic_goods_detail.json")
                return False
        else:
            print("❌ فشل سكريبت Epic")
            print(f"الخطأ: {result.stderr}")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة تنفيذ سكريبت Epic (أكثر من 5 دقائق)")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار Epic: {e}")
        return False

def test_timestamp_script():
    """اختبار سكريبت تحديث الوقت"""
    print_header("⏰ اختبار سكريبت تحديث الوقت")
    
    try:
        # تشغيل السكريبت
        result = subprocess.run(
            [sys.executable, "update_timestamp.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ سكريبت تحديث الوقت يعمل بنجاح")
            
            # التحقق من الملف الناتج
            if os.path.exists("update_timestamp.json"):
                with open("update_timestamp.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"⏰ آخر تحديث: {data.get('last_update', 'غير متوفر')}")
                    print(f"📊 الملفات المحدثة: {data.get('updated_files', 0)}/{data.get('total_files', 0)}")
            else:
                print("⚠️ لم يتم إنشاء ملف update_timestamp.json")
                return False
        else:
            print("❌ فشل سكريبت تحديث الوقت")
            print(f"الخطأ: {result.stderr}")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ انتهت مهلة تنفيذ سكريبت تحديث الوقت")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار تحديث الوقت: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print_header("🧪 بدء اختبار السكريبتات")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "steam": False,
        "epic": False,
        "timestamp": False
    }
    
    # اختبار Steam (اختياري - قد يستغرق وقتاً طويلاً)
    print("\n⚠️ ملاحظة: اختبار Steam قد يستغرق عدة دقائق...")
    user_input = input("هل تريد اختبار Steam؟ (y/n): ").lower()
    if user_input == 'y':
        results["steam"] = test_steam_script()
    else:
        print("⏭️ تم تخطي اختبار Steam")
        results["steam"] = None
    
    # اختبار Epic (اختياري)
    print("\n⚠️ ملاحظة: اختبار Epic قد يستغرق عدة دقائق...")
    user_input = input("هل تريد اختبار Epic؟ (y/n): ").lower()
    if user_input == 'y':
        results["epic"] = test_epic_script()
    else:
        print("⏭️ تم تخطي اختبار Epic")
        results["epic"] = None
    
    # اختبار تحديث الوقت (سريع)
    results["timestamp"] = test_timestamp_script()
    
    # النتيجة النهائية
    print_header("📊 النتائج النهائية")
    
    for test_name, result in results.items():
        if result is None:
            print(f"⏭️ {test_name}: تم التخطي")
        elif result:
            print(f"✅ {test_name}: نجح")
        else:
            print(f"❌ {test_name}: فشل")
    
    # التحقق من نجاح جميع الاختبارات
    tested_results = [r for r in results.values() if r is not None]
    if tested_results and all(tested_results):
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ السكريبتات جاهزة للعمل في GitHub Actions")
        return 0
    elif not tested_results:
        print("\n⚠️ لم يتم تشغيل أي اختبارات")
        return 1
    else:
        print("\n⚠️ بعض الاختبارات فشلت - راجع الأخطاء أعلاه")
        return 1

if __name__ == "__main__":
    sys.exit(main())
