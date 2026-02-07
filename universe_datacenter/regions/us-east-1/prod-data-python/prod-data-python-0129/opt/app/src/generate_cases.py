import json, os, random

os.makedirs("data/generated_cases", exist_ok=True)

CRIMES = ["절도", "사기", "횡령", "폭행", "업무상배임"]

for i in range(1, 501):  # ✅ 500건
    case = {
        "case_id": f"CASE-{i:04d}",
        "crime": random.choice(CRIMES),
        "damage_amount": random.randint(100000, 50000000),
        "prior_convictions": random.randint(0, 5),
        "age": random.randint(18, 75)
    }
    with open(f"data/generated_cases/case_{i:04d}.json", "w", encoding="utf-8") as f:
        json.dump(case, f, ensure_ascii=False, indent=2)
