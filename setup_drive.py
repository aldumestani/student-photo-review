#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""إنشاء ملف تطابق صور Google Drive من مجلد عام"""

import os, json, requests

OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'drive_images.json')

def main():
    print("=" * 60)
    print("   رفع الصور على Google Drive")
    print("=" * 60)
    print()
    print("الطريقة: أنشئ مجلد عام في Google Drive وارفع الصور")
    print()
    folder_url = input("1. الصق رابط المجلد العام من Google Drive:\n   ").strip()
    
    # Extract folder ID from URL
    folder_id = None
    if '/folders/' in folder_url:
        folder_id = folder_url.split('/folders/')[1].split('?')[0].split('/')[0]
    elif 'id=' in folder_url:
        folder_id = folder_url.split('id=')[1].split('&')[0]
    
    if not folder_id:
        print("❌ لم أجد folder ID في الرابط")
        return
    
    print(f"   📁 Folder ID: {folder_id}")
    api_key = input("\n2. الصق API Key من Google Cloud Console:\n   (أو اتركه فارغاً للمتابعة بطريقة يدوية)\n   ").strip()
    
    files = {}
    
    if api_key:
        # Use API to list files
        page_token = None
        while True:
            params = {
                'q': f"'{folder_id}' in parents and mimeType='image/jpeg'",
                'key': api_key,
                'fields': 'files(id,name),nextPageToken',
                'pageSize': 100,
            }
            if page_token:
                params['pageToken'] = page_token
            
            r = requests.get('https://www.googleapis.com/drive/v3/files', params=params)
            if r.status_code != 200:
                print(f"❌ خطأ من API: {r.text}")
                return
            
            data = r.json()
            for f in data.get('files', []):
                files[f['name']] = f['id']
            
            page_token = data.get('nextPageToken')
            if not page_token:
                break
        
        if not files:
            print("❌ لم أجد صوراً في المجلد")
            return
        
        print(f"   ✅ وجدت {len(files)} صورة")
    else:
        # Manual mode - user enters file IDs
        print("\n🖼️  طريقة يدوية:")
        print("   لاحظ أن 153 صورة كثير للطريقة اليدوية.")
        print("   الأفضل: استخدم API Key من Google Cloud Console.")
        print()
        choice = input("   هل تريد متابعة يدوية؟ (n للخروج): ").strip().lower()
        if choice != 'y':
            print("   ارجع وشغّل البرنامج مرة ثانية مع API Key")
            return
        
        print("\n   افتح المجلد في Google Drive، ولكل صورة:")
        print("   1. اضغط على الصورة")
        print("   2. انسخ الـ ID من الرابط (بعد /d/ أو ?id=)")
        print("   3. اكتب اسم الملف و ID مفصولين بفاصلة")
        print("   مثال: 1.jpg,1a2b3c4d5e6f7g8h9i0j")
        print("   (اكتب 'تم' للانتهاء)")
        print()
        while True:
            line = input("   > ").strip()
            if line == 'تم':
                break
            parts = line.split(',')
            if len(parts) == 2:
                files[parts[0].strip()] = parts[1].strip()
                print(f"      ✅ {parts[0].strip()}")
    
    # Save mapping
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'folder_id': folder_id, 'files': files}, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 تم حفظ {len(files)} صورة في {OUTPUT_JSON}")
    print("🚀 الآن ادفع الكود لـ GitHub و Render راح يخدم الصور من Drive")

if __name__ == '__main__':
    main()
