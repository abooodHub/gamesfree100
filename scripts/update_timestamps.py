#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Timestamps - تحديث الطوابع الزمنية
Update the timestamp in all JSON data files
"""

import json
import datetime
import pytz
from pathlib import Path

def update_timestamps():
    # الحصول على التوقيت الحالي بتوقيت آسيا/شنغهاي
    current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S')
    print("🕒 تحديث الطوابع الزمنية إلى: " + current_time)
    print("🕒 Updating timestamps to: " + current_time)
    print()
    
    # الحصول على المسار الصحيح لمجلد data
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    # قائمة ملفات JSON
    json_files = [
        data_dir / 'free_goods_detail.json',
        data_dir / 'epic_goods_detail.json',
        data_dir / 'gog_goods_detail.json',
        data_dir / 'ubisoft_goods_detail.json',
        data_dir / 'playstation_goods_detail.json',
        data_dir / 'xbox_goods_detail.json'
    ]
    
    updated_count = 0
    failed_count = 0
    
    # تحديث كل ملف
    for file_path in json_files:
        file_name = file_path.name
        try:
            # التحقق من وجود الملف
            if not file_path.exists():
                print(f"⚠️  الملف غير موجود: {file_name}")
                # إنشاء ملف جديد
                data_dir.mkdir(exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'update_time': current_time, 
                        'total_count': 0,
                        'free_list': [], 
                        'free_games': [],
                        'discounted_games': []
                    }, f, ensure_ascii=False, indent=2)
                print(f"✅ تم إنشاء ملف جديد: {file_name}")
                updated_count += 1
                continue
            
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تحديث التوقيت
            old_time = data.get('update_time', 'غير محدد')
            data['update_time'] = current_time
            
            # حفظ الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ تم تحديث {file_name}")
            print(f"   الوقت السابق: {old_time}")
            print(f"   الوقت الجديد: {current_time}")
            updated_count += 1
            
        except json.JSONDecodeError as e:
            print(f"❌ خطأ في تحليل JSON لملف {file_name}: {e}")
            failed_count += 1
        except Exception as e:
            print(f"❌ خطأ في تحديث {file_name}: {e}")
            failed_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ تم تحديث {updated_count} ملف بنجاح")
    if failed_count > 0:
        print(f"❌ فشل تحديث {failed_count} ملف")
    print(f"📊 الإجمالي: {updated_count}/{len(json_files)}")
    print("=" * 60)

if __name__ == '__main__':
    update_timestamps() 