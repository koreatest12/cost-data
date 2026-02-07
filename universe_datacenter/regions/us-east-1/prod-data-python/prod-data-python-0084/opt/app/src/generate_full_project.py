import os
import sqlite3
import json

# 프로젝트 기본 경로 설정
BASE_DIR = "app_root"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "cost_data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "receipts"), exist_ok=True)

# ----------------------------------------------------------------------
# [1] 소스 코드 정의 (엔터프라이즈급 로직 포함)
# ----------------------------------------------------------------------

# 1. 의존성 정의
REQ_TXT = """
flask
pandas
openpyxl
sqlalchemy
pdfplumber
aiosmtpd
numpy
"""

# 2. 엔진 소스 (지식 베이스 참조 및 대량 연산 엔진)
ENGINE_PY = r'''
import sqlite3
import os
import pandas as pd

DB_NAME = 'tax_master.db'

def run_calculation_engine():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 원천 데이터 가져오기 (DB에 적재된 대량 데이터 스캔)
    cur.execute("SELECT * FROM raw_income_data")
    members = cur.fetchall()

    print(f">>> [연산 시작] 총 {len(members)}명의 세무 분석 진행 중...")

    for member in members:
        # 지식 베이스(세율표)에서 적합한 세율 구간 조회 (지능형 매칭)
        cur.execute("""
            SELECT * FROM tax_knowledge 
            WHERE ? > threshold_min AND ? <= threshold_max
        """, (member['salary'], member['salary']))
        
        rule = cur.fetchone()
        
        if rule:
            # 복합 세액 계산 공식 적용: (급여 * 세율) - 누진공제액
            calc_tax = int(member['salary'] * rule['tax_rate'] - rule['deduction_fixed'])
            rate_display = f"{int(rule['tax_rate'] * 100)}%"
            advice = f"해당 구간({rate_display}) 최적화 절세 전략 적용 가능"
        else:
            calc_tax, rate_display, advice = 0, "0%", "데이터 분석 범위 초과"

        # 최종 분석 결과 테이블에 저장
        cur.execute("""
            INSERT INTO tax_analysis_results (name, salary, final_tax, applied_rate, ai_advice)
            VALUES (?, ?, ?, ?, ?)
        """, (member['name'], member['salary'], calc_tax, rate_display, advice))

    conn.commit()
    conn.close()
    print(">>> [연산 완료] 모든 데이터가 분석 및 업데이트되었습니다.")

if __name__ == "__main__":
    run_calculation_engine()
'''

# 3. 웹 UI 소스 (대시보드 및 리포트)
APP_PY = r'''
from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('tax_master.db')
    conn.row_factory = sqlite3.Row
    results = conn.execute("SELECT * FROM tax_analysis_results").fetchall()
    knowledge = conn.execute("SELECT * FROM tax_knowledge").fetchall()
    conn.close()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>AI 세무 지능형 시스템</title>
    </head>
    <body class="bg-light p-5">
        <div class="container shadow bg-white p-5 rounded">
            <h1 class="mb-4 text-primary">🏢 Intelligent Tax Master Dashboard</h1>
            <hr>
            <h4>📘 시스템 내장 세무 지식 베이스</h4>
            <table class="table table-bordered mb-5">
                <thead class="table-dark"><tr><th>구분</th><th>최소구간</th><th>최대구간</th><th>세율</th><th>누진공제</th></tr></thead>
                <tbody>
                    {% for k in knowledge %}
                    <tr><td>{{k.category}}</td><td>{{k.threshold_min:,}}</td><td>{{k.threshold_max:,}}</td><td>{{k.tax_rate*100}}%</td><td>{{k.deduction_fixed:,}}</td></tr>
                    {% endfor %}
                </tbody>
            </table>
            <h4>📊 지능형 연산 분석 리포트</h4>
            <table class="table table-hover">
                <thead class="table-primary"><tr><th>성명</th><th>연봉</th><th>최종 산출세액</th><th>적용세율</th><th>AI 어드바이스</th></tr></thead>
                <tbody>
                    {% for r in results %}
                    <tr><td>{{r.name}}</td><td>{{r.salary:,}}원</td><td class="fw-bold">{{r.final_tax:,}}원</td><td>{{r.applied_rate}}</td><td>{{r.ai_advice}}</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """, results=results, knowledge=knowledge)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
'''

# ----------------------------------------------------------------------
# [2] 자동화 실행 및 DB 구축 로직 (Self-Executing Logic)
# ----------------------------------------------------------------------

def build_system():
    print("🚀 [System Build] 프로젝트 파일 생성 시작...")
    
    # 파일 쓰기
    with open(os.path.join(BASE_DIR, "requirements.txt"), "w") as f: f.write(REQ_TXT.strip())
    with open(os.path.join(BASE_DIR, "engine.py"), "w", encoding="utf-8") as f: f.write(ENGINE_PY.strip())
    with open(os.path.join(BASE_DIR, "app.py"), "w", encoding="utf-8") as f: f.write(APP_PY.strip())

    # DB 구축 및 지식/데이터 대량 주입
    db_path = os.path.join(BASE_DIR, "tax_master.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 테이블 생성 (지식 베이스, 원천 데이터, 결과 데이터)
    cur.executescript("""
        CREATE TABLE tax_knowledge (
            id INTEGER PRIMARY KEY, category TEXT, threshold_min INTEGER, 
            threshold_max INTEGER, tax_rate REAL, deduction_fixed INTEGER
        );
        CREATE TABLE raw_income_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, salary INTEGER
        );
        CREATE TABLE tax_analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, salary INTEGER,
            final_tax INTEGER, applied_rate TEXT, ai_advice TEXT
        );
    """)

    # 1. 대량 세무 지식 주입 (2026년 세율 가이드)
    knowledge_data = [
        ('INCOME_TAX', 0, 14000000, 0.06, 0),
        ('INCOME_TAX', 14000000, 50000000, 0.15, 1260000),
        ('INCOME_TAX', 50000000, 88000000, 0.24, 5760000),
        ('INCOME_TAX', 88000000, 150000000, 0.35, 15440000),
        ('INCOME_TAX', 150000000, 300000000, 0.38, 19940000)
    ]
    cur.executemany("INSERT INTO tax_knowledge (category, threshold_min, threshold_max, tax_rate, deduction_fixed) VALUES (?,?,?,?,?)", knowledge_data)

    # 2. 분석용 샘플 대량 데이터 주입 (계산 로직 테스트용)
    sample_members = [(f"User_{i}", 30000000 + (i * 5000000)) for i in range(1, 21)]
    cur.executemany("INSERT INTO raw_income_data (name, salary) VALUES (?, ?)", sample_members)

    conn.commit()
    conn.close()
    
    print(f"✅ [Build Complete] DB 구축 및 {len(sample_members)}건의 데이터 주입 완료.")
    print(f"👉 경로: {os.path.abspath(BASE_DIR)}")

if __name__ == "__main__":
    build_system()
