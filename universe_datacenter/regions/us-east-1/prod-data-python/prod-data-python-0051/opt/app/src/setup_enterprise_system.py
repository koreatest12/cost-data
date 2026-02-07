import os, sqlite3, random, time, json, uuid
from datetime import datetime

# --- 설정 ---
BASE_DIR = "app_root"
NODES = ["server_node_alpha", "server_node_beta", "server_node_gamma"]

# 디렉토리 초기화
os.makedirs(BASE_DIR, exist_ok=True)
for node in NODES:
    os.makedirs(os.path.join(BASE_DIR, "storage", node), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

# --- [모듈 1] 수집기 (Collector) ---
COLLECTOR_CODE = r'''
import sqlite3, os, json, random, uuid
from datetime import datetime

DB_PATH = os.path.join("app_root", "tax_master.db")
NODES = ["server_node_alpha", "server_node_beta", "server_node_gamma"]
PLATFORMS = ["Upwork", "Kmong", "Wishket", "Wanted", "RemoteOK"]
TITLES = ["Python Auto Script", "Excel Macro Expert", "Data Entry", "Translation KR-EN", "Video Editor"]

def run():
    print("🚀 [Collector] Starting Bulk Collection...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 대량 데이터 생성 (100~200건)
    jobs = []
    for _ in range(random.randint(100, 200)):
        job = {
            "id": str(uuid.uuid4()),
            "platform": random.choice(PLATFORMS),
            "title": random.choice(TITLES) + " - Urgent",
            "pay": random.randint(100, 5000) * 1000,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        jobs.append(job)
        
        # DB 적재
        cur.execute("INSERT INTO side_hustle_jobs (job_id, platform, title, pay, collected_at) VALUES (?,?,?,?,?)",
                    (job['id'], job['platform'], job['title'], job['pay'], job['date']))
    
    conn.commit()
    conn.close()
    
    # 2. 분산 서버(JSON 파일) 적재
    for job in jobs:
        node = random.choice(NODES)
        path = os.path.join("app_root", "storage", node, f"{job['id']}.json")
        with open(path, "w") as f: json.dump(job, f, indent=2)
    
    print(f"✅ [Collector] Processed {len(jobs)} jobs across {len(NODES)} nodes.")
if __name__ == "__main__": run()
'''

# --- [모듈 2] 메일러 (Mailer) ---
MAILER_CODE = r'''
import sqlite3, os, random
from datetime import datetime

DB_PATH = os.path.join("app_root", "tax_master.db")

def run():
    print("📧 [Mailer] Starting Mass Email Dispatch...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 대상자 조회
    cur.execute("SELECT name, final_tax FROM tax_analysis_results")
    users = cur.fetchall()
    
    sent = 0
    for user in users:
        status = "SENT" if random.random() > 0.05 else "BOUNCED"
        subj = f"💰 {user[0]}님, 절세 및 부업 추천 알림"
        body = f"예상세액 {user[1]}원을 아끼세요."
        
        cur.execute("INSERT INTO email_logs (recipient, subject, body, status, sent_at) VALUES (?,?,?,?,?)",
                    (user[0], subj, body, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sent += 1
    
    conn.commit()
    conn.close()
    print(f"✅ [Mailer] Sent {sent} emails (Logged in DB).")
if __name__ == "__main__": run()
'''

# --- [시스템 빌더] 실행 로직 ---
def build():
    print("🏗️ Building Enterprise System...")
    
    # 1. 파일 생성
    with open(os.path.join(BASE_DIR, "collector.py"), "w") as f: f.write(COLLECTOR_CODE)
    with open(os.path.join(BASE_DIR, "mailer.py"), "w") as f: f.write(MAILER_CODE)
    
    # 2. DB 초기화
    conn = sqlite3.connect(os.path.join(BASE_DIR, "tax_master.db"))
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS tax_analysis_results (name TEXT, salary INTEGER, final_tax INTEGER, applied_rate TEXT, ai_advice TEXT);
        CREATE TABLE IF NOT EXISTS side_hustle_jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT, platform TEXT, title TEXT, pay INTEGER, collected_at TEXT);
        CREATE TABLE IF NOT EXISTS email_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient TEXT, subject TEXT, body TEXT, status TEXT, sent_at TEXT);
    """)
    
    # 3. 샘플 유저 데이터 주입 (메일 발송 대상)
    cur.execute("SELECT COUNT(*) FROM tax_analysis_results")
    if cur.fetchone()[0] == 0:
        users = [(f"User_{i:03d}", 50000000, 1200000, "15%", "절세필요") for i in range(100)] # 100명 생성
        cur.executemany("INSERT INTO tax_analysis_results VALUES (?,?,?,?,?)", users)
    
    conn.commit()
    conn.close()
    print("✅ System Build Complete.")

if __name__ == "__main__": build()
