import os
from PIL import Image

SRC_DIR = r'C:\Users\Jehad\Downloads\OpenCode Projects\امنيات الطلبة\الصور النهائية للطباعة'
DST_DIR = r'C:\Users\Jehad\Downloads\OpenCode Projects\امنيات الطلبة\thumbnails'
MAX_LONG = 800
QUALITY = 75

os.makedirs(DST_DIR, exist_ok=True)

count = 0
errors = 0
for i in range(1, 154):
    src = os.path.join(SRC_DIR, f'{i}.jpg')
    dst = os.path.join(DST_DIR, f'{i}.jpg')
    if not os.path.exists(src):
        print(f'  SKIP {i}.jpg - not found')
        continue
    try:
        img = Image.open(src)
        w, h = img.size
        if w >= h:
            new_w = MAX_LONG
            new_h = int(h * MAX_LONG / w)
        else:
            new_h = MAX_LONG
            new_w = int(w * MAX_LONG / h)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img.save(dst, 'JPEG', quality=QUALITY, optimize=True)
        count += 1
        print(f'  OK {i}.jpg ({w}x{h} -> {new_w}x{new_h})')
    except Exception as e:
        print(f'  ERR {i}.jpg: {e}')
        errors += 1

print(f'\nDone: {count} thumbnails created, {errors} errors')
