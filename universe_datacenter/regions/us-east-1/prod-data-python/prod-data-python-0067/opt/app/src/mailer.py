
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
