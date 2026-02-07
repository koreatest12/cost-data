import os, csv, random, datetime, uuid
def run():
    print("🏭 [Factory] Generating Massive Data...")
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    
    # CSV 생성
    with open("data/jobs/mass_db.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "role", "salary", "status"])
        for i in range(10000):
            w.writerow([str(uuid.uuid4())[:8], "Security Expert", f"${random.randint(80,150)}k", "Open"])
    
    # 로그 파일 생성
    for i in range(50):
        with open(f"data/logs/server_{i}.log", "w") as f:
            f.write(f"Server {i} Status: OK\nTraffic: {random.randint(100,9999)}MB")
    print("✅ Generated 10,000 jobs & 50 logs.")
if __name__ == "__main__": run()
