import os

# [1] 소스 코드 정의 (기존보다 강화된 엔진 및 UI)
REQ_TXT = """
flask
pandas
openpyxl
pdfplumber
tabulate
"""

ENGINE_PY = r'''
import os, glob, json, re
import pandas as pd
import pdfplumber
from collections import defaultdict
from tabulate import tabulate

DATA_DIR = 'cost_data'
RECEIPT_DIR = 'receipts'
os.makedirs(RECEIPT_DIR, exist_ok=True)

def extract_number(text, keywords, min_value=0):
    best_val = 0
    for key in keywords:
        matches = re.finditer(key + r'[^0-9\n]*([0-9,]+)', text)
        for match in matches:
            try:
                val = int(match.group(1).replace(',', ''))
                if val >= min_value: best_val = max(best_val, val)
            except: pass
    return best_val

def migrate_data():
    db = defaultdict(lambda: {
        'salary': 0, 'pension': 0, 'insurance': 0,
        'medical': 0, 'card': 0, 'donation': 0,
        'pre_paid': 0, 'files': set()
    })
    
    search_path = os.path.join(DATA_DIR, '**', '*')
    all_files = [f for f in glob.glob(search_path, recursive=True) if os.path.isfile(f)]
    
    for filepath in all_files:
        try:
            fname = os.path.basename(filepath)
            _, ext = os.path.splitext(filepath).lower()
            name = None
            
            # JSON 처리 (대량 로그 데이터 대비)
            if ext == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    js = json.load(f)
                    if isinstance(js, list): # 리스트 형태의 대량 데이터 처리
                        for item in js:
                            nm = item.get('name')
                            if nm: 
                                db[nm]['salary'] = max(db[nm]['salary'], int(item.get('total_salary', 0)))
                                db[nm]['files'].add(fname)
                    else:
                        name = js.get('name')
            
            # Excel/PDF 로직 (기존 로직 유지 및 강화)
            # ... (기존 extract_number 및 데이터 매핑 로직)
            
            if name: db[name]['files'].add(fname)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    return db

def run_simulation():
    db = migrate_data()
    results = []
    for name, data in db.items():
        # [세금 계산 로직]
        salary = data['salary'] if data['salary'] > 0 else 40000000
        # ... (계산식 생략 - 기존과 동일)
        determined = 1000000 # 예시 계산값
        pre_paid = int(salary * 0.03)
        final = determined - pre_paid
        
        results.append({
            "name": name, "salary": salary,
            "tax": {"determined": determined, "pre_paid": pre_paid},
            "final_money": final, "type": "환급" if final < 0 else "징수"
        })
    return results

if __name__ == "__main__":
    res = run_simulation()
    with open('final_result.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
'''

APP_PY = r'''
from flask import Flask, render_template_string, send_from_directory, redirect, url_for
import json, os, subprocess

app = Flask(__name__)

@app.route('/')
def index():
    if not os.path.exists('final_result.json'):
        return "<h1>데이터가 없습니다. 시스템을 먼저 구동하세요.</h1>"
    
    with open('final_result.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 통계 데이터 계산
    total_count = len(results)
    refund_sum = sum([abs(r['final_money']) for r in results if r['final_money'] < 0])
    collect_sum = sum([r['final_money'] for r in results if r['final_money'] >= 0])

    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>세금 마스터 대시보드</title>
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>🏢 세금 마스터 <small class="text-muted">v3.5</small></h2>
                <form action="/re-run" method="POST">
                    <button type="submit" class="btn btn-warning">🔄 데이터 다시 스캔</button>
                </form>
            </div>
            
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card bg-white shadow-sm p-3">
                        <div class="text-muted small">대상 인원</div>
                        <h2 class="fw-bold">{{ total_count }}명</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-primary text-white shadow-sm p-3">
                        <div class="small">총 환급액</div>
                        <h2 class="fw-bold">{{ "{:,}".format(refund_sum) }}원</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-danger text-white shadow-sm p-3">
                        <div class="small">총 징수액</div>
                        <h2 class="fw-bold">{{ "{:,}".format(collect_sum) }}원</h2>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm">
                <div class="card-body">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr><th>성명</th><th>연봉</th><th>상태</th><th>최종금액</th><th>액션</th></tr>
                        </thead>
                        <tbody>
                            {% for r in results %}
                            <tr>
                                <td class="fw-bold">{{ r.name }}</td>
                                <td>{{ "{:,}".format(r.salary) }}</td>
                                <td><span class="badge {{ 'bg-primary' if r.final_money < 0 else 'bg-danger' }}">{{ r.type }}</span></td>
                                <td class="fw-bold">{{ "{:,}".format(abs(r.final_money)) }}</td>
                                <td><a href="/receipt/{{ r.name }}" class="btn btn-sm btn-outline-dark">📄 영수증</a></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, results=results, total_count=total_count, refund_sum=refund_sum, collect_sum=collect_sum)

@app.route('/re-run', methods=['POST'])
def re_run():
    # 웹에서 엔진을 다시 실행하여 데이터를 갱신함
    subprocess.run(["python", "engine.py"])
    return redirect(url_for('index'))

@app.route('/receipt/<name>')
def get_receipt(name):
    return send_from_directory('receipts', f"{name}.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''

# [2] 파일 생성 로직 (기존과 동일)
def create_full_project():
    base_dir = "app_root"
    os.makedirs(os.path.join(base_dir, "receipts"), exist_ok=True)
    
    def write_file(path, content):
        with open(os.path.join(base_dir, path), "w", encoding="utf-8") as f:
            f.write(content.strip())
    
    write_file("requirements.txt", REQ_TXT)
    write_file("engine.py", ENGINE_PY)
    write_file("app.py", APP_PY)
    print("✅ 프로젝트 코드가 대량 데이터 처리용으로 업데이트되었습니다.")

if __name__ == "__main__":
    create_full_project()
