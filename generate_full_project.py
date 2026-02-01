import os

# [1] 필요한 패키지 추가 (SQLAlchemy는 가벼운 DB 관리를 위해 추가)
REQ_TXT = """
flask
pandas
openpyxl
pdfplumber
tabulate
sqlalchemy
"""

# [2] 엔진: DB 스캔 및 적재 로직 (engine.py)
ENGINE_PY = r'''
import os, glob, json, sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'tax_master.db'
DATA_DIR = 'cost_data'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 대량 데이터를 담을 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tax_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            salary INTEGER,
            deduction INTEGER,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def migrate_to_db():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    files = glob.glob(os.path.join(DATA_DIR, '**', '*.*'), recursive=True)
    
    for f in files:
        fname = os.path.basename(f)
        ext = os.path.splitext(f)[1].lower()
        try:
            # JSON/Excel 데이터 추출 후 DB Insert (중복 체크 생략/단순화)
            if ext == '.json':
                with open(f, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        conn.execute("INSERT INTO tax_records (name, salary, source_file) VALUES (?, ?, ?)",
                                     (item.get('name'), item.get('total_salary', 0), fname))
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(f)
                for _, row in df.iterrows():
                    conn.execute("INSERT INTO tax_records (name, salary, source_file) VALUES (?, ?, ?)",
                                 (str(row.get('name', '알수없음')), int(row.get('salary', 0)), fname))
        except Exception as e:
            print(f"Error loading {fname}: {e}")
            
    conn.commit()
    conn.close()
    print(f">>> {len(files)}개 파일의 데이터를 DB에 동기화 완료.")

if __name__ == "__main__":
    migrate_to_db()
'''

# [3] 웹 UI: 업로드 및 DB 조회 기능 (app.py)
APP_PY = r'''
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)
UPLOAD_FOLDER = 'cost_data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_data():
    conn = sqlite3.connect('tax_master.db')
    conn.row_factory = sqlite3.Row
    data = conn.execute("SELECT * FROM tax_records ORDER BY id DESC").fetchall()
    conn.close()
    return data

@app.route('/')
def index():
    data = get_db_data()
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>세금 마스터 DB 시스템</title>
    </head>
    <body class="bg-light p-5">
        <div class="container bg-white shadow p-4 rounded">
            <h2 class="mb-4">🏢 데이터베이스 통합 관리 센터</h2>
            
            <div class="card mb-4 border-primary">
                <div class="card-body">
                    <h5 class="card-title">파일 업로드 (Excel, JSON)</h5>
                    <form action="/upload" method="post" enctype="multipart/form-data" class="row g-3">
                        <div class="col-auto"><input type="file" name="file" class="form-control"></div>
                        <div class="col-auto"><button type="submit" class="btn btn-primary">DB 적재</button></div>
                    </form>
                </div>
            </div>

            <table class="table table-striped">
                <thead><tr><th>ID</th><th>성명</th><th>급여</th><th>출처 파일</th><th>등록일</th></tr></thead>
                <tbody>
                    {% for r in data %}
                    <tr>
                        <td>{{ r.id }}</td>
                        <td><strong>{{ r.name }}</strong></td>
                        <td>{{ "{:,}".format(r.salary) }}원</td>
                        <td><small class="text-muted">{{ r.source_file }}</small></td>
                        <td>{{ r.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return redirect('/')
    file = request.files['file']
    if file.filename == '': return redirect('/')
    
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    
    # 업로드 후 엔진을 실행하여 DB에 즉시 반영 (간소화된 방식)
    os.system("python engine.py")
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''

def create_full_system():
    base = "app_root"
    os.makedirs(f"{base}/cost_data", exist_ok=True)
    with open(f"{base}/requirements.txt", "w") as f: f.write(REQ_TXT.strip())
    with open(f"{base}/engine.py", "w", encoding="utf-8") as f: f.write(ENGINE_PY.strip())
    with open(f"{base}/app.py", "w", encoding="utf-8") as f: f.write(APP_PY.strip())
    print("✅ DB 적재 및 업로드 기능이 포함된 프로젝트가 생성되었습니다.")

if __name__ == "__main__":
    create_full_system()
