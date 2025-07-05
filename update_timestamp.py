#!/usr/bin/env python3
import json
import datetime

def update_timestamps():
    # الحصول على التوقيت الحالي
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Updating timestamps to: " + current_time)
    
    # قائمة ملفات JSON
    json_files = [
        'free_goods_detail.json',
        'epic_goods_detail.json',
        'gog_goods_detail.json',
        'ubisoft_goods_detail.json',
        'playstation_goods_detail.json',
        'xbox_goods_detail.json'
    ]
    
    updated_count = 0
    
    # تحديث كل ملف
    for file_path in json_files:
        try:
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تحديث التوقيت
            old_time = data.get('update_time', 'None')
            data['update_time'] = current_time
            
            # حفظ الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("Updated " + file_path + " (was: " + old_time + ")")
            updated_count += 1
            
        except Exception as e:
            print("Error updating " + file_path + ": " + str(e))
            # إنشاء ملف جديد إذا لم يكن موجوداً
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({'update_time': current_time, 'free_list': [], 'discounted_list': []}, f, ensure_ascii=False, indent=2)
                print("Created new " + file_path)
                updated_count += 1
            except Exception as e2:
                print("Failed to create " + file_path + ": " + str(e2))
    
    print("Successfully updated " + str(updated_count) + "/" + str(len(json_files)) + " files")

if __name__ == '__main__':
    update_timestamps() 