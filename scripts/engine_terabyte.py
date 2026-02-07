import csv, random, uuid, os

def run():
    print("💾 [Engine-TB] Generating Massive Data Index...")
    
    save_dir = "data/big_data_storage"
    os.makedirs(save_dir, exist_ok=True)
    
    index_path = os.path.join(save_dir, "terabyte_index.csv")
    
    with open(index_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shard_id", "storage_location", "link_url", "allocated_size", "checksum"])
        
        total_size_gb = 0
        rows = 100000  # 10만 줄 생성
        
        for i in range(rows):
            size = random.randint(1, 100)
            total_size_gb += size
            w.writerow([
                f"SHARD-{uuid.uuid4()}",
                f"s3://bucket-hustle-data/block_{i}",
                f"https://data-lake.com/download?id={uuid.uuid4()}",
                f"{size} GB",
                "a1b2c3d4e5"
            ])
            
    tb_size = round(total_size_gb / 1024, 2)
    print(f"✅ Indexed {rows} massive files.")
    print(f"📊 Total Virtual Capacity: {tb_size} TB")
    
    # 메타데이터 생성
    with open(os.path.join(save_dir, "capacity_report.txt"), "w") as f:
        f.write(f"Total Indexed Volume: {tb_size} TB\nStatus: Online")

if __name__ == "__main__": run()
