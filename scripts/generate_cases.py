import json, os, random
from faker import Faker

fake = Faker('ko_KR')
OUTPUT_DIR = "data/generated_cases"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CRIME_TYPES = {
    "사기": ["보이스피싱", "중고나라 사기", "전세 사기", "투자 사기"],
    "절도": ["빈집털이", "차량 털이", "편의점 절도", "특수 절도"],
    "폭행": ["단순 폭행", "특수 폭행", "상해", "쌍방 폭행"],
    "횡령": ["업무상 횡령", "법인카드 유용", "공금 횡령"],
    "음주운전": ["면허 취소 수준", "사고 후 미조치", "단순 음주 적발"]
}

def generate_case(case_id):
    crime_category = random.choice(list(CRIME_TYPES.keys()))
    crime_detail = random.choice(CRIME_TYPES[crime_category])
    damage_amount = 0
    if crime_category in ["사기", "횡령", "절도"]:
        damage_amount = random.randint(100000, 1000000000)

    return {
        "case_id": case_id,
        "defendant": {
            "name": fake.name(),
            "address": fake.address(),
            "birth_date": fake.date_of_birth(minimum_age=19, maximum_age=80).strftime("%Y-%m-%d"),
            "job": fake.job()
        },
        "crime_summary": {
            "category": crime_category,
            "detail": crime_detail,
            "description": f"피고인은 {fake.date_this_year()} 경, {fake.city()} 일대에서 {crime_detail} 혐의로 기소됨.",
            "damage_amount_krw": damage_amount
        },
        "legal_history": {
            "prior_convictions": random.randint(0, 5),
            "probation_status": random.choice([True, False])
        },
        "submitted_evidence": random.sample(["CCTV 영상", "계좌 이체 내역", "목격자 진술", "피해자 탄원서", "합의서"], k=random.randint(1, 3))
    }

if __name__ == "__main__":
    print("🚀 대량 사건 데이터 생성을 시작합니다...")
    # 50건 생성 (데모용)
    for i in range(1, 51):
        c_id = f"CASE-2026-{i:04d}"
        data = generate_case(c_id)
        file_path = os.path.join(OUTPUT_DIR, f"{c_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 총 {i}건의 사건 파일 생성 완료.")
