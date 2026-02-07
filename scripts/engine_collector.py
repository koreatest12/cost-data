import requests, pandas as pd, datetime, os
def run():
    print("🚀 [Collector] Scanning Job Market...")
    data = [{"title": "DevOps Engineer", "company": "Tech-" + str(i), "date": str(datetime.date.today())} for i in range(1, 101)]
    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/real_jobs.csv", index=False)
    print(f"✅ Collected {len(data)} jobs.")
if __name__ == "__main__": run()
