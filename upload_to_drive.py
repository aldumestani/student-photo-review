#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""رفع الصور المصغرة إلى Google Drive وإنشاء ملف التطابق"""

import os, json, pickle, mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
THUMBS_DIR = os.path.join(os.path.dirname(__file__), 'thumbnails')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'drive_images.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'drive_token.json')
CREDS_FILE = os.path.join(os.path.dirname(__file__), 'drive_creds.json')

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print("=" * 60)
                print("   مطلوب ملف credentials من Google Cloud Console")
                print("=" * 60)
                print()
                print("الرجاء اتباع الخطوات:")
                print("1. افتح https://console.cloud.google.com/")
                print("2. أنشئ مشروع جديد (أو استخدم مشروع)")
                print("3. اذهب إلى APIs & Services → Library")
                print("4. فعّل Google Drive API")
                print("5. اذهب إلى Credentials → Create Credentials → OAuth client ID")
                print("6. اختر Desktop app، سمِّه 'Drive Upload'")
                print("7. حمِّل JSON file وسمِّه 'drive_creds.json'")
                print("8. ضع الملف بجانب هذا البرنامج")
                print()
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def main():
    service = get_service()
    if not service:
        return
    
    # Create folder
    folder_meta = {'name': 'student_photo_thumbs', 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=folder_meta, fields='id').execute()
    folder_id = folder['id']
    print(f'📁 أنشئ المجلد: {folder_id}')
    
    # Upload all thumbnails
    mapping = {}
    files = sorted([f for f in os.listdir(THUMBS_DIR) if f.endswith('.jpg')], key=lambda x: int(x.split('.')[0]))
    
    for i, filename in enumerate(files):
        path = os.path.join(THUMBS_DIR, filename)
        mime = 'image/jpeg'
        media = MediaFileUpload(path, mimetype=mime)
        file_meta = {'name': filename, 'parents': [folder_id]}
        file = service.files().create(body=file_meta, media_body=media, fields='id').execute()
        mapping[filename] = file['id']
        
        # Make public
        service.permissions().create(fileId=file['id'], body={'type': 'anyone', 'role': 'reader'}).execute()
        
        if (i + 1) % 20 == 0:
            print(f'  ✅ {i+1}/{len(files)}')
    
    print(f'  ✅ {len(files)}/{len(files)}')
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'folder_id': folder_id, 'files': mapping}, f, ensure_ascii=False, indent=2)
    
    print(f'\n🎉 تم! رُفعت {len(files)} صورة')
    print(f'📄 ملف التطابق: {OUTPUT_JSON}')
    print(f'📁 مجلد Drive: https://drive.google.com/drive/folders/{folder_id}')

if __name__ == '__main__':
    main()
