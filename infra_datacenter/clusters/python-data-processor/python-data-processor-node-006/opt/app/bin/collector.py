
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
