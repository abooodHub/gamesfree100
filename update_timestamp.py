#!/usr/bin/env python3
import json
import datetime
import os

def update_timestamps():
    # الحصول على التوقيت الحالي
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # قائمة ملفات JSON
    json_files = [
        'free_goods_detail.json',
        'epic_goods_detail.json',
        'gog_goods_detail.json',
        'ubisoft_goods_detail.json',
        'playstation_goods_detail.json',
        'xbox_goods_detail.json'
    ]
    
    # تحديث كل ملف
    for file_path in json_files:
        try:
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تحديث التوقيت
            data['update_time'] = current_time
            
            # حفظ الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f'Updated timestamp in {file_path}')
        except Exception as e:
            print(f'Error updating {file_path}: {e}')
            # إنشاء ملف جديد إذا لم يكن موجوداً
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'update_time': current_time, 'free_list': [], 'discounted_list': []}, f, ensure_ascii=False, indent=2)
            print(f'Created new {file_path}')

if __name__ == '__main__':
    update_timestamps() 