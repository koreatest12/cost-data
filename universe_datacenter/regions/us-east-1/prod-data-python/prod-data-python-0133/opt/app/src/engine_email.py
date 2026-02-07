import os, datetime

def run():
    print("📧 [Engine-Email] Preparing Virtual Email Dispatch...")
    
    sender = "bot@ops.com"
    receiver = "admin@company.com"
    subject = f"💰 [Daily Briefing] Massive Side Hustle Data - {datetime.date.today()}"
    
    # 브리핑 내용 읽기
    body = ""
    report_path = "daily_hustle_briefing.md"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            body = f.read()
    else:
        body = "No briefing report found."

    # 이메일 포맷 생성
    email_content = f"""From: {sender}
To: {receiver}
Subject: {subject}
Date: {datetime.datetime.now()}
Content-Type: text/markdown

{body}
--------------------------------------------------
[System] End of Email
"""

    # 가상 발송 (파일로 저장)
    save_dir = "data/sent_emails"
    os.makedirs(save_dir, exist_ok=True)
    
    filename = f"email_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, "w") as f:
        f.write(email_content)
        
    print(f"✅ Virtual Email 'Sent' to {receiver}")
    print(f"📂 Saved copy at {filepath}")

if __name__ == "__main__": run()
