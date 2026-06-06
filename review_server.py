#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
خادم مطابقة الصور - للمعلم لربط أسماء الطلبة بالصور
يدعم التشغيل المحلي وعلى Render.com
"""

import os, sys, json, shutil, threading, socket
from flask import Flask, render_template_string, send_from_directory, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_JSON = os.path.join(BASE_DIR, 'students_data.json')
HQ_TO_STUDENT = os.path.join(BASE_DIR, 'hq_to_student.json')
MATCHES_FILE = os.path.join(BASE_DIR, 'teacher_matches.json')
THUMBS_DIR = os.path.join(BASE_DIR, 'static', 'thumbs')
FINAL_DIR = os.path.join(BASE_DIR, 'النتيجة النهائية')
LOCAL_HQ_DIR = r'C:\Users\Jehad\Downloads\OpenCode Projects\امنيات الطلبة\الصور النهائية للطباعة'

app = Flask(__name__)

# ============ LOAD DATA ============
def load_students():
    with open(STUDENTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_matches():
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_matches(matches):
    with open(MATCHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

students = load_students()
hq_photos = [f'{i}.jpg' for i in range(1, 154)]
all_students = students

# Group by class
from collections import OrderedDict
classes = OrderedDict()
for s in students:
    classes.setdefault(s['class'], []).append(s)

# Load saved matches
matches = load_matches()

# Pre-create initial matches from filename-to-student mapping
if not matches:
    if os.path.exists(HQ_TO_STUDENT):
        with open(HQ_TO_STUDENT, 'r', encoding='utf-8') as f:
            initial = json.load(f)
            matches = {k: v for k, v in initial.items() if v}
    save_matches(matches)

matched_count = sum(1 for hq in hq_photos if matches.get(hq))

# ============ ROUTES ============
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE,
        hq_photos=hq_photos,
        classes={k: [{'arabic_name': s['arabic_name'], 'profession': s['profession']} for s in v] for k, v in classes.items()},
        all_students=[{'arabic_name': s['arabic_name'], 'class': s['class'], 'profession': s['profession']} for s in all_students],
        matches=matches,
        matched_count=matched_count,
        total_hq=len(hq_photos),
    )

@app.route('/thumb/<name>')
def thumb(name):
    return send_from_directory(THUMBS_DIR, name)

@app.route('/full/<name>')
def full(name):
    return send_from_directory(THUMBS_DIR, name)

@app.route('/hq_img/<name>')
def hq_img(name):
    return send_from_directory(THUMBS_DIR, name)

@app.route('/save_matches', methods=['POST'])
def save():
    data = request.get_json()
    global matches, matched_count
    matches = data.get('matches', {})
    save_matches(matches)
    matched_count = sum(1 for hq in hq_photos if matches.get(hq))
    return jsonify({'status': 'ok', 'count': matched_count})

@app.route('/generate', methods=['POST'])
def generate():
    count = 0
    final_dir = FINAL_DIR
    os.makedirs(final_dir, exist_ok=True)
    for hq_name, student_name in matches.items():
        if not student_name:
            continue
        s = next((s for s in all_students if s['arabic_name'] == student_name), None)
        if not s:
            continue
        cls = s['class']
        prof = s['profession']
        cls_dir = os.path.join(final_dir, cls)
        os.makedirs(cls_dir, exist_ok=True)
        safe_name = student_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_prof = prof.replace('/', '_').replace('\\', '_').replace(':', '_')
        new_name = f"{safe_name} - {safe_prof}.jpg"
        dest = os.path.join(cls_dir, new_name)
        c = 1
        while os.path.exists(dest):
            dest = os.path.join(cls_dir, f"{safe_name} ({c}) - {safe_prof}.jpg")
            c += 1
        src = os.path.join(LOCAL_HQ_DIR, hq_name)
        if os.path.exists(src):
            shutil.copy2(src, dest)
            count += 1
    return jsonify({'status': 'ok', 'count': count, 'path': final_dir})

# ============ HTML ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>مطابقة صور الطلبة</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; font-size: 1.6em; }
        .subtitle { text-align: center; color: #7f8c8d; margin-bottom: 20px; font-size: 0.95em; }
        .top-bar { display: flex; gap: 15px; align-items: center; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; }
        .top-bar select, .top-bar input { padding: 10px 15px; border: 2px solid #ddd; border-radius: 8px; font-size: 1em; }
        .top-bar .stats { background: white; padding: 8px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 0.95em; }
        #saveBtn { background: #27ae60; color: white; border: none; padding: 10px 25px; border-radius: 8px; cursor: pointer; font-size: 1em; }
        #saveBtn:hover { background: #219a52; }
        #generateBtn { background: #8e44ad; color: white; border: none; padding: 10px 25px; border-radius: 8px; cursor: pointer; font-size: 1em; }
        #generateBtn:hover { background: #7d3c98; }
        .photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .photo-card { background: white; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); overflow: hidden; transition: 0.2s; }
        .photo-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .photo-card.matched { border-right: 4px solid #27ae60; }
        .photo-card.unmatched { border-right: 4px solid #e74c3c; }
        .photo-card .img-wrap { width: 100%; height: 260px; background: #2c2c2c; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .photo-card .img-wrap img { max-width: 100%; max-height: 100%; object-fit: contain; cursor: pointer; }
        .mobile-review { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 2000; flex-direction: column; }
        .mobile-review.active { display: flex; }
        .mr-img-wrap { flex: 1; display: flex; align-items: center; justify-content: center; background: #000; overflow: hidden; position: relative; }
        .mr-img-wrap img { width: 100%; height: 100%; object-fit: contain; }
        .mr-top-overlay { position: absolute; top: 0; left: 0; right: 0; display: flex; justify-content: space-between; align-items: center; padding: 15px; background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent); z-index: 1; }
        .mr-top-overlay button { background: rgba(255,255,255,0.15); border: none; color: white; font-size: 1.3em; cursor: pointer; padding: 8px 14px; border-radius: 24px; backdrop-filter: blur(4px); }
        .mr-top-overlay .mr-counter { color: white; font-size: 0.85em; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 12px; }
        .mr-bottom { background: rgba(20,20,35,0.95); backdrop-filter: blur(10px); padding: 10px 12px; padding-bottom: max(10px, env(safe-area-inset-bottom)); }
        .mr-bottom .mr-class-row { margin-bottom: 8px; }
        .mr-bottom .mr-class-row select { width: 100%; padding: 12px 12px; border: 2px solid #8e44ad; border-radius: 10px; font-size: 1em; background: #1a1a2e; color: white; -webkit-appearance: none; appearance: none; }
        .mr-bottom .mr-class-row select option { background: #1a1a2e; color: white; }
        .mr-bottom .mr-select-wrap select { width: 100%; padding: 14px 12px; border: 2px solid #0f3460; border-radius: 10px; font-size: 1.05em; background: #1a1a2e; color: white; -webkit-appearance: none; appearance: none; }
        .mr-bottom .mr-select-wrap select option { background: #1a1a2e; color: white; padding: 10px; }
        .mr-bottom .mr-select-wrap select option:disabled { color: #555; }
        .mr-bottom .mr-info { color: #888; text-align: center; font-size: 0.75em; margin-top: 5px; }
        .mr-nav-zones { position: absolute; top: 0; bottom: 0; left: 0; right: 0; display: flex; z-index: 0; }
        .mr-nav-left, .mr-nav-right { flex: 1; cursor: pointer; }
        .mr-nav-left:active, .mr-nav-right:active { background: rgba(255,255,255,0.05); }
        .mr-progress { height: 3px; background: #222; flex-shrink: 0; }
        .mr-progress-bar { height: 100%; background: #27ae60; width: 0%; transition: width 0.3s; }
        .photo-card .card-body { padding: 10px; }
        .photo-card .card-body select { width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 6px; font-size: 0.9em; }
        .photo-card .card-body .filename { color: #999; font-size: 0.75em; margin-top: 4px; text-align: center; }
        .photo-card .card-body .status { font-size: 0.8em; margin-top: 4px; text-align: center; }
        .toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #27ae60; color: white; padding: 12px 25px; border-radius: 8px; display: none; z-index: 999; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 1000; justify-content: center; align-items: center; }
        .lightbox.active { display: flex; }
        .lightbox img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }
        .lightbox .close-lb { position: absolute; top: 15px; left: 25px; color: white; font-size: 2.5em; cursor: pointer; background: none; border: none; }
        .nav-btns { text-align: center; margin: 15px 0; }
        .nav-btns .btn { background: #34495e; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin: 3px; }
        @media (max-width: 768px) {
            body { padding: 10px; background: #1a1a2e; }
            h1 { font-size: 1em; color: #eee; margin-bottom: 10px; }
            .subtitle { display: none; }
            .top-bar { flex-direction: column; align-items: stretch; gap: 8px; margin-bottom: 10px; }
            .top-bar select, .top-bar input { width: 100%; font-size: 0.9em; }
            .top-bar .stats { text-align: center; font-size: 0.85em; background: #2c2c3e; color: #ddd; }
            #saveBtn, #generateBtn { padding: 8px 15px; font-size: 0.85em; }
            .photo-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
            .photo-card .img-wrap { height: 180px; }
            .photo-card .card-body select { display: none; }
            .photo-card .card-body .filename { display: none; }
            .photo-card .card-body .status { font-size: 0.7em; padding: 2px 0; }
            .photo-card { border-radius: 8px; }
            .photo-card.matched { border-right: 3px solid #27ae60; }
            .photo-card.unmatched { border-right: 3px solid #e74c3c; }
            .nav-btns { display: none; }
        }
        @media (max-width: 400px) {
            .photo-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 6px; }
            .photo-card .img-wrap { height: 150px; }
        }
    </style>
</head>
<body>
    <h1>📋 مطابقة أسماء الطلبة بالصور</h1>
    <div class="subtitle">اضغط على الصورة لاختيار الاسم</div>
    
    <div class="top-bar">
        <select id="classFilter" onchange="filterClass()">
            <option value="">📚 جميع الصفوف</option>
            {% for cls in classes.keys()|sort %}
            <option value="{{ cls }}">{{ cls }}</option>
            {% endfor %}
        </select>
        <input type="text" id="searchInput" placeholder="🔍 بحث..." oninput="filterClass()">
        <span class="stats" id="statsDisplay">✅ <span id="matchCount">{{ matched_count }}</span>/{{ total_hq }} مطابقة</span>
        <button id="saveBtn" onclick="saveAll()">💾 حفظ</button>
        <button id="generateBtn" onclick="generateFinal()">🚀 إنشاء النهائي</button>
    </div>
    
    <div id="photoContainer" class="photo-grid"></div>
    
    <div id="toast" class="toast"></div>
    
    <div class="mobile-review" id="mobileReview">
        <div class="mr-img-wrap">
            <div class="mr-top-overlay">
                <button onclick="closeMobileReview()">✕</button>
                <span class="mr-counter" id="mrCounter">1 / 153</span>
                <button id="mrSaveNextBtn" onclick="saveAndNext()">💾 ← حفظ</button>
            </div>
            <div class="mr-nav-zones">
                <div class="mr-nav-left" onclick="navMobile(-1)"></div>
                <div class="mr-nav-right" onclick="navMobile(1)"></div>
            </div>
            <img id="mrImage" src="" ondblclick="toggleMRLightbox()">
        </div>
        <div class="mr-progress"><div class="mr-progress-bar" id="mrProgressBar"></div></div>
        <div class="mr-bottom">
            <div class="mr-class-row">
                <select id="mrClassFilter" onchange="onMRClassChange()">
                    <option value="">📚 اختر الصف</option>
                    {% for cls in classes.keys()|sort %}
                    <option value="{{ cls }}">{{ cls }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mr-select-wrap">
                <select id="mrSelect" onchange="onMRSelect()">
                    <option value="">-- اختر الصف أولاً --</option>
                </select>
            </div>
            <div class="mr-info" id="mrInfo"></div>
        </div>
    </div>
    
    <div class="lightbox" id="lightbox" onclick="if(event.target===this)closeLB()">
        <button class="close-lb" onclick="closeLB()">✕</button>
        <img id="lbImage" src="">
    </div>
    
    <script>
        const hqPhotos = {{ hq_photos|tojson }};
        const classesData = {{ classes|tojson }};
        const allStudents = {{ all_students|tojson }};
        let matches = {{ matches|tojson }};
        
        let isMobile = window.innerWidth < 768 || ('ontouchstart' in window);
        let mobileIndex = 0;
        let mobilePhotos = [];
        
        const allOptionsCache = {};
        function buildOptionsForClass(className, selectedName) {
            const key = className || '__all__';
            if (!allOptionsCache[key]) {
                const items = [];
                if (!className) {
                    for (const [cls, students] of Object.entries(classesData)) {
                        for (const s of students) items.push(s);
                    }
                } else {
                    const students = classesData[className] || [];
                    for (const s of students) items.push(s);
                }
                allOptionsCache[key] = items;
            }
            const items = allOptionsCache[key];
            let opts = '<option value="">-- اختر اسم الطالب --</option>';
            for (const s of items) {
                const sel = s.arabic_name === selectedName ? 'selected' : '';
                opts += '<option value="' + s.arabic_name + '" ' + sel + '>' + s.arabic_name + '</option>';
            }
            return opts;
        }
        
        function render() {
            closeMobileReview();
            const filter = document.getElementById('classFilter').value;
            const search = document.getElementById('searchInput').value.trim();
            const container = document.getElementById('photoContainer');
            
            const studentOptions = [];
            for (const [cls, students] of Object.entries(classesData)) {
                studentOptions.push('<option disabled>--- ' + cls + ' ---</option>');
                for (const s of students) {
                    studentOptions.push('<option value="' + s.arabic_name + '" data-class="' + cls + '">' + s.arabic_name + '</option>');
                }
            }
            const optionsHtml = '<option value="">-- اختر اسم الطالب --</option>' + studentOptions.join('');
            
            let matchedCount = 0;
            let html = '';
            mobilePhotos = [];
            
            for (const hq of hqPhotos) {
                const studentName = matches[hq] || '';
                const isMatched = !!studentName;
                if (isMatched) matchedCount++;
                
                if (filter) {
                    if (studentName) {
                        const s = allStudents.find(x => x.arabic_name === studentName);
                        if (s && s.class !== filter) continue;
                    }
                }
                if (search && studentName && !studentName.includes(search)) continue;
                
                const cardClass = isMatched ? 'matched' : 'unmatched';
                const statusText = isMatched ? '✅ ' + studentName : '⚠️ بدون اسم';
                const photoIdx = mobilePhotos.length;
                mobilePhotos.push(hq);
                
                html += '<div class="photo-card ' + cardClass + '" data-hq="' + hq + '">'
                    + '<div class="img-wrap"><img src="/thumb/' + hq + '" alt="' + hq + '" '
                    + 'onclick="' + (isMobile ? "openMobileReview(" + photoIdx + ")" : "openLB('/full/" + hq + "')") + '"></div>'
                    + '<div class="card-body">'
                    + '<select onchange="assign(\'' + hq + '\', this.value)">'
                    + optionsHtml.replace('value="' + studentName + '"', 'value="' + studentName + '" selected')
                    + '</select>'
                    + '<div class="filename">' + hq + '</div>'
                    + '<div class="status">' + statusText + '</div>'
                    + '</div></div>';
            }
            
            container.innerHTML = html;
            document.getElementById('matchCount').textContent = matchedCount;
        }
        
        function openMobileReview(idx) {
            mobileIndex = idx;
            const mainFilter = document.getElementById('classFilter').value;
            document.getElementById('mrClassFilter').value = mainFilter;
            updateMobileReview();
            document.getElementById('mobileReview').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeMobileReview() {
            document.getElementById('mobileReview').classList.remove('active');
            document.body.style.overflow = '';
        }
        
        function getStudentClass(name) {
            if (!name) return null;
            for (const [cls, students] of Object.entries(classesData)) {
                if (students.some(s => s.arabic_name === name)) return cls;
            }
            return null;
        }
        
        function updateMobileReview() {
            if (mobileIndex < 0) mobileIndex = 0;
            if (mobileIndex >= mobilePhotos.length) mobileIndex = mobilePhotos.length - 1;
            
            const hq = mobilePhotos[mobileIndex];
            const studentName = matches[hq] || '';
            const existingCls = getStudentClass(studentName);
            
            const mrClass = document.getElementById('mrClassFilter');
            const cls = existingCls || mrClass.value || '';
            if (existingCls && mrClass.value !== existingCls) {
                mrClass.value = existingCls;
            }
            
            document.getElementById('mrImage').src = '/full/' + hq;
            document.getElementById('mrCounter').textContent = (mobileIndex + 1) + ' / ' + mobilePhotos.length;
            
            const mrSelect = document.getElementById('mrSelect');
            if (cls) {
                mrSelect.innerHTML = buildOptionsForClass(cls, studentName);
                mrSelect.disabled = false;
            } else {
                mrSelect.innerHTML = '<option value="">-- اختر الصف أولاً --</option>';
                mrSelect.disabled = true;
            }
            document.getElementById('mrInfo').textContent = hq + (studentName ? ' | ✅ ' + studentName : ' | ⚠️ بدون اسم');
            
            const pct = ((mobileIndex + 1) / mobilePhotos.length * 100).toFixed(0);
            document.getElementById('mrProgressBar').style.width = pct + '%';
            
            const btn = document.getElementById('mrSaveNextBtn');
            if (mobileIndex >= mobilePhotos.length - 1) {
                btn.textContent = '✅ تم';
            } else {
                btn.textContent = '💾 ← حفظ';
            }
        }
        
        function navMobile(dir) {
            mobileIndex += dir;
            updateMobileReview();
        }
        
        function onMRClassChange() {
            const cls = document.getElementById('mrClassFilter').value;
            const hq = mobilePhotos[mobileIndex];
            const studentName = matches[hq] || '';
            const mrSelect = document.getElementById('mrSelect');
            if (cls) {
                mrSelect.innerHTML = buildOptionsForClass(cls, studentName);
                mrSelect.disabled = false;
            } else {
                mrSelect.innerHTML = '<option value="">-- اختر الصف أولاً --</option>';
                mrSelect.disabled = true;
            }
        }
        
        function onMRSelect() {
            const hq = mobilePhotos[mobileIndex];
            const val = document.getElementById('mrSelect').value;
            assign(hq, val);
            updateMobileReview();
        }
        
        function saveAndNext() {
            const hq = mobilePhotos[mobileIndex];
            const val = document.getElementById('mrSelect').value;
            if (hq) assign(hq, val);
            saveAll();
            if (mobileIndex < mobilePhotos.length - 1) {
                navMobile(1);
            } else {
                toast('✅ تم الانتهاء من جميع الصور');
                closeMobileReview();
            }
        }
        
        function toggleMRLightbox() {
            const hq = mobilePhotos[mobileIndex];
            if (hq) openLB('/full/' + hq);
        }
        
        document.addEventListener('keydown', function(e) {
            if (document.getElementById('mobileReview').classList.contains('active')) {
                if (e.key === 'Escape') closeMobileReview();
                if (e.key === 'ArrowRight') navMobile(1);
                if (e.key === 'ArrowLeft') navMobile(-1);
            }
            if (e.key === 'Escape') closeLB();
        });
        
        function assign(hq, studentName) {
            if (studentName) {
                matches[hq] = studentName;
            } else {
                delete matches[hq];
            }
            render();
        }
        
        function filterClass() {
            render();
        }
        
        function saveAll() {
            fetch('/save_matches', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({matches: matches})
            }).then(r => r.json()).then(d => {
                toast('💾 تم حفظ ' + d.count + ' مطابقة');
            });
        }
        
        function generateFinal() {
            if (!confirm('هل أنت متأكد؟ سيتم إنشاء المجلد النهائي من المطابقات المحفوظة.')) return;
            const btn = document.getElementById('generateBtn');
            btn.textContent = '⏳ جاري...';
            btn.disabled = true;
            fetch('/generate', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    toast('✅ تم إنشاء ' + d.count + ' صورة في المجلد النهائي');
                    btn.textContent = '✅ تم';
                }).catch(() => {
                    toast('❌ خطأ');
                    btn.textContent = '🚀 إنشاء النهائي';
                    btn.disabled = false;
                });
        }
        
        function openLB(src) {
            document.getElementById('lbImage').src = src;
            document.getElementById('lightbox').classList.add('active');
        }
        
        function closeLB() {
            document.getElementById('lightbox').classList.remove('active');
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeLB();
        });
        
        function toast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 2000);
        }
        
        render();
        if (isMobile && mobilePhotos.length > 0) {
            setTimeout(() => openMobileReview(0), 300);
        }
    </script>
</body>
</html>
'''

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    ip = get_local_ip()
    print("=" * 60)
    print("   🌐 خادم مطابقة صور الطلبة")
    print("=" * 60)
    print(f"   رابط للمعلم: http://{ip}:{port}")
    print(f"   محلياً:       http://localhost:{port}")
    print(f"   من أي مكان:   https://your-app.onrender.com")
    print()
    print("   اضغط Ctrl+C للإيقاف")
    print()
    app.run(host='0.0.0.0', port=port, debug=False)
