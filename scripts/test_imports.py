#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Imports - اختبار الاستيراد
Quick test to verify all imports work correctly
"""

import sys
from pathlib import Path

print("=" * 60)
print("🧪 اختبار الاستيراد - Testing Imports")
print("=" * 60)
print()

# Test 1: Check Python version
print("1️⃣ فحص إصدار Python...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 7):
    print("   ❌ يجب استخدام Python 3.7 أو أحدث")
    sys.exit(1)
else:
    print("   ✅ إصدار Python مناسب")
print()

# Test 2: Check required libraries
print("2️⃣ فحص المكتبات المطلوبة...")
required_libs = ['requests', 'bs4', 'pytz', 'pathlib']
missing_libs = []

for lib in required_libs:
    try:
        __import__(lib)
        print(f"   ✅ {lib}")
    except ImportError:
        print(f"   ❌ {lib} - غير مثبتة")
        missing_libs.append(lib)

if missing_libs:
    print()
    print("   ⚠️ بعض المكتبات غير مثبتة!")
    print("   قم بتشغيل: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("   ✅ جميع المكتبات مثبتة")
print()

# Test 3: Check scripts directory structure
print("3️⃣ فحص بنية المجلدات...")
script_dir = Path(__file__).parent
project_root = script_dir.parent
data_dir = project_root / 'data'

print(f"   📁 مجلد المشروع: {project_root}")
print(f"   📁 مجلد السكريبترات: {script_dir}")
print(f"   📁 مجلد البيانات: {data_dir}")

if not data_dir.exists():
    print("   ⚠️ مجلد data غير موجود - سيتم إنشاؤه عند أول تحديث")
    data_dir.mkdir(exist_ok=True)
    print("   ✅ تم إنشاء مجلد data")
else:
    print("   ✅ مجلد data موجود")
print()

# Test 4: Check if scrapers can be imported
print("4️⃣ فحص استيراد السكريبترات...")
scrapers = [
    'epic_scraper',
    'steam_scraper',
    'gog_scraper',
    'playstation_scraper',
    'ubisoft_scraper',
    'xbox_scraper',
    'update_timestamps'
]

failed_imports = []
for scraper in scrapers:
    try:
        __import__(scraper)
        print(f"   ✅ {scraper}.py")
    except Exception as e:
        print(f"   ❌ {scraper}.py - خطأ: {e}")
        failed_imports.append(scraper)

if failed_imports:
    print()
    print("   ⚠️ بعض السكريبترات بها مشاكل!")
    sys.exit(1)
else:
    print("   ✅ جميع السكريبترات جاهزة")
print()

# Test 5: Check pathlib functionality
print("5️⃣ فحص وظائف المسارات...")
try:
    test_file = data_dir / 'test.txt'
    test_file.write_text('test', encoding='utf-8')
    content = test_file.read_text(encoding='utf-8')
    test_file.unlink()
    if content == 'test':
        print("   ✅ القراءة والكتابة تعمل بشكل صحيح")
    else:
        print("   ❌ مشكلة في القراءة/الكتابة")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ خطأ في اختبار المسارات: {e}")
    sys.exit(1)
print()

print("=" * 60)
print("🎉 جميع الاختبارات نجحت! النظام جاهز للعمل")
print("=" * 60)
print()
print("📝 الخطوات التالية:")
print("   1. قم بتشغيل: update_games.bat")
print("   2. أو: python scripts/update_all_games.py")
print()

