import pandas as pd, datetime, random, uuid, os
def run():
    print("🚀 [Engine-Hustle] Starting Side Hustle Crawling...")
    platforms = ["Upwork", "Kmong", "Wishket", "Fiverr", "Toptal"]
    skills = ["Python Scripting", "Excel Macro", "Translation", "Video Editing", "Logo Design"]
    
    hustles = []
    for i in range(10000):
        plat = random.choice(platforms)
        skill = random.choice(skills)
        uid = str(uuid.uuid4())[:8]
        hustles.append({
            "id": uid,
            "platform": plat,
            "title": f"Need expert for {skill} - Urgent",
            "budget": f"${random.randint(50, 5000)}",
            "link": f"https://www.{plat.lower()}.com/jobs/{uid}",
            "data_size": f"{random.randint(1, 100)}MB"
        })
    
    df = pd.DataFrame(hustles)
    save_dir = "data/side_hustle"
    os.makedirs(save_dir, exist_ok=True)
    
    path = os.path.join(save_dir, "hustle_listings.csv")
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} side hustle links.")
if __name__ == "__main__": run()
