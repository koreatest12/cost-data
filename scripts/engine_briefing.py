import pandas as pd, os, datetime
def run():
    report = "daily_hustle_briefing.md"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    hustle_cnt = 0
    if os.path.exists("data/side_hustle/hustle_listings.csv"):
        hustle_cnt = len(pd.read_csv("data/side_hustle/hustle_listings.csv"))
    
    tb_status = "Unknown"
    if os.path.exists("data/big_data_storage/capacity_report.txt"):
        with open("data/big_data_storage/capacity_report.txt", "r") as f:
            tb_status = f.read().strip()

    content = f"""# 💰 대량 부업 및 빅데이터 브리핑 ({today})
    ## 1️⃣ 부업 정보
    - **수집 공고:** {hustle_cnt:,} 건
    ## 2️⃣ 데이터 스케일
    - **용량:** {tb_status}
    ## 3️⃣ 시스템 상태
    - **Email Service:** Active (Virtual)
    """
    with open(report, "w", encoding="utf-8") as f: f.write(content)
    print(f"✅ Briefing Ready: {report}")
if __name__ == "__main__": run()
