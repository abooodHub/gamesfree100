#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث timestamp في ملفات JSON
يقوم بتحديث حقل update_time في جميع ملفات بيانات الألعاب
"""

import json
import os
from datetime import datetime
import pytz

def update_json_timestamp(filepath: str) -> bool:
    """
    تحديث timestamp في ملف JSON
    
    Args:
        filepath: مسار ملف JSON
        
    Returns:
        True إذا تم التحديث بنجاح، False خلاف ذلك
    """
    try:
        # التحقق من وجود الملف
        if not os.path.exists(filepath):
            print(f"⚠️  الملف غير موجود: {filepath}")
            return False
        
        # قراءة الملف
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # إذا كان الملف فارغاً أو ليس dictionary
        if not isinstance(data, dict):
            print(f"⚠️  تنسيق غير صحيح في {filepath}")
            return False
        
        # تحديث الـ timestamp
        current_time = datetime.now(tz=pytz.timezone('Asia/Riyadh')).strftime('%Y-%m-%d %H:%M:%S')
        data['update_time'] = current_time
        
        # حفظ الملف
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم تحديث {os.path.basename(filepath)} - {current_time}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في قراءة JSON من {filepath}: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في تحديث {filepath}: {e}")
        return False

def main():
    """الدالة الرئيسية - تحديث جميع ملفات JSON"""
    print("🔄 بدء تحديث timestamps في ملفات JSON...")
    print("=" * 60)
    
    # قائمة الملفات المطلوب تحديثها
    json_files = [
        'free_goods_detail.json',
        'epic_goods_detail.json',
        'gog_goods_detail.json',
        'update_timestamp.json',
    ]
    
    updated_count = 0
    
    for json_file in json_files:
        if update_json_timestamp(json_file):
            updated_count += 1
    
    print("=" * 60)
    print(f"📊 تم تحديث {updated_count} من {len(json_files)} ملف")
    
    # إنشاء/تحديث ملف update_timestamp.json
    try:
        timestamp_data = {
            'last_update': datetime.now(tz=pytz.timezone('Asia/Riyadh')).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_files': updated_count,
            'total_files': len(json_files)
        }
        
        with open('update_timestamp.json', 'w', encoding='utf-8') as f:
            json.dump(timestamp_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم إنشاء/تحديث update_timestamp.json")
    except Exception as e:
        print(f"⚠️  خطأ في إنشاء update_timestamp.json: {e}")
    
    print("\n🎉 اكتمل تحديث timestamps!")

if __name__ == "__main__":
    main()
