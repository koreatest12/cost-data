import requests, pandas as pd, datetime, os, random

def run_collector():
    print("🚀 [Engine 1] Starting Job Collector...")
    jobs = []
    targets = ["Java", "Spring", "Security", "DevOps", "Python", "Cloud", "AI"]
    
    # 1. 실제 API 시뮬레이션 (RemoteOK)
    try:
        url = "https://remoteok.com/api"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            for item in r.json()[1:]:
                title = item.get('position', '')
                if any(t.lower() in title.lower() for t in targets):
                    jobs.append({
                        'type': 'Real-API',
                        'title': title,
                        'company': item.get('company', 'Unknown'),
                        'date': item.get('date', datetime.date.today()),
                        'link': item.get('url', '#')
                    })
    except Exception as e: print(f"API Error: {e}")

    # 2. 결과 저장
    df = pd.DataFrame(jobs)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/real_jobs.csv", index=False)
    print(f"✅ [Engine 1] Collected {len(jobs)} real jobs.")

if __name__ == "__main__": run_collector()
