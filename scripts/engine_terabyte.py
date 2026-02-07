import csv, random, uuid, os
def run():
    print("💾 [Engine-TB] Generating Massive Data Index...")
    save_dir = "data/big_data_storage"
    os.makedirs(save_dir, exist_ok=True)
    index_path = os.path.join(save_dir, "terabyte_index.csv")
    
    with open(index_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shard_id", "storage_location", "link_url", "allocated_size"])
        total_size_gb = 0
        for i in range(100000):
            size = random.randint(1, 100)
            total_size_gb += size
            w.writerow([f"SHARD-{uuid.uuid4()}", f"s3://bucket/block_{i}", f"url_{i}", f"{size} GB"])
    
    tb_size = round(total_size_gb / 1024, 2)
    with open(os.path.join(save_dir, "capacity_report.txt"), "w") as f:
        f.write(f"Total Indexed Volume: {tb_size} TB")
    print(f"📊 Total Virtual Capacity: {tb_size} TB")
if __name__ == "__main__": run()
