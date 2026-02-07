import os, csv, random, datetime, uuid

def run_factory():
    print("🏭 [Engine 2] Starting Mass Data Factory...")
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)

    # 1. 가상 채용 공고 10,000건 생성
    print("   -> Generating 10,000 Mock Job Data...")
    with open("data/jobs/mass_db_v2.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "title", "company", "salary_range", "status", "created_at"])
        roles = ["Backend Dev", "Frontend Dev", "DevOps", "Security Analyst", "Data Engineer"]
        comps = ["TechCorp", "FinBank", "StartupX", "CloudSys", "SecureNet"]
        for i in range(10000):
            w.writerow([
                str(uuid.uuid4())[:8],
                random.choice(roles),
                f"{random.choice(comps)}-{random.randint(1,100)}",
                f"${random.randint(50,150)}k",
                "Hiring",
                datetime.date.today()
            ])

    # 2. 서버 로그 100개 파일 생성
    print("   -> Generating 100 Server Log Files...")
    for i in range(100):
        with open(f"data/logs/server_node_{i:03d}.log", "w") as f:
            f.write(f"Server-ID: NODE-{i}\nStatus: Active\nUptime: {random.randint(100,99999)}s\n")
            f.write("Log Trace:\n" + "INFO: Service Started\nWARN: High Latency\n"*10)

    print("✅ [Engine 2] Massive Data Generation Complete.")

if __name__ == "__main__": run_factory()
