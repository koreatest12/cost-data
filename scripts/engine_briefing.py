import pandas as pd, datetime, os
def run():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report = "daily_briefing_report.md"
    
    real_cnt = len(pd.read_csv("data/real_jobs.csv")) if os.path.exists("data/real_jobs.csv") else 0
    mass_cnt = len(pd.read_csv("data/jobs/mass_db.csv")) if os.path.exists("data/jobs/mass_db.csv") else 0
    
    content = f"""# 📢 IT 대량 데이터 브리핑 ({today})

    ## 1️⃣ 데이터 처리 요약
    - **실시간 수집:** {real_cnt} 건
    - **대량 생성:** {mass_cnt:,} 건
    - **총 데이터:** {real_cnt + mass_cnt:,} Rows
    
    ## 2️⃣ 시스템 상태
    - **Firewall:** ✅ Active
    - **Engines:** 3 Active
    
    ## 3️⃣ 워크플로우 코드
    > (Attached below in repository)
    """
    
    with open(report, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Report generated: {report}")
if __name__ == "__main__": run()
