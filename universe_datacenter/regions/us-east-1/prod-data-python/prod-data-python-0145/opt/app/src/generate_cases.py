import json, os, random
from faker import Faker

fake = Faker('ko_KR')
OUTPUT_DIR = "data/generated_cases"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- [V2.0 업데이트] 고난도/특수 범죄 카테고리 추가 ---
CRIME_SCENARIOS = {
    "자본시장법 위반": {
        "details": ["시세 조종(주가 조작)", "미공개 중요 정보 이용", "허위 공시", "부정 거래 행위"],
        "keywords": ["통정매매", "작전 세력", "유상증자", "콜옵션", "차명 계좌"],
        "base_sentence": "징역 3년 이상",
        "complexity": "최상"
    },
    "청탁금지법 위반": {
        "details": ["금품 등 수수(명품백 등)", "부정 청탁", "직무 관련 향응 제공", "배우자 금품 수수"],
        "keywords": ["직무 관련성", "대가성", "사교적 의례 범위", "반환 여부", "알선수재"],
        "base_sentence": "징역 1년 이하 또는 과태료",
        "complexity": "상"
    },
    "업무방해 및 저작권법": {
        "details": ["논문 위조 및 표절", "연구 데이터 조작", "입시 비리", "허위 경력 기재"],
        "keywords": ["인용 누락", "데이터 가공", "심사 위원 기망", "학위 취소", "연구 윤리"],
        "base_sentence": "징역 2년 이하",
        "complexity": "중"
    },
    "특경제가중처벌법(횡령/배임)": {
        "details": ["법인 자금 횡령", "배임수재", "비자금 조성"],
        "keywords": ["이사회 결의", "경영 판단의 원칙", "비자금", "가족 회사"],
        "base_sentence": "징역 5년 이상",
        "complexity": "상"
    }
}

def generate_case(case_id):
    # 70% 확률로 특수 범죄 생성 (사용자 요청 반영)
    if random.random() < 0.7:
        crime_cat = random.choice(list(CRIME_SCENARIOS.keys()))
    else:
        crime_cat = "일반 형법(절도/폭행 등)" # 기존 범죄

    # 특수 범죄 데이터 생성 로직
    if crime_cat in CRIME_SCENARIOS:
        scenario = CRIME_SCENARIOS[crime_cat]
        detail = random.choice(scenario['details'])
        keyword = random.sample(scenario['keywords'], 2)
        damage = random.randint(10000000, 50000000000) # 1천만 ~ 500억
        desc = f"피고인은 {detail}을(를) 목적으로 {keyword[0]} 및 {keyword[1]} 수법을 동원함."
    else:
        # 일반 범죄 fallback
        detail = "단순 절도/폭행"
        damage = random.randint(100000, 5000000)
        desc = "일반 형사 사건임."

    return {
        "case_id": case_id,
        "case_type": "특수/공안/금융" if crime_cat != "일반 형법(절도/폭행 등)" else "일반 형사",
        "defendant": {
            "name": fake.name(),
            "position": fake.job(),
            "history": f"동종 전과 {random.randint(0,2)}회"
        },
        "charge": {
            "category": crime_cat,
            "specific_charge": detail,
            "facts": desc,
            "damage_amount_krw": damage
        },
        "evidence_list": ["포렌식 분석 결과", "계좌 추적 내역", "통화 녹취록", "내부 고발자 진술"],
        "defense_argument": "직무 관련성이 없었으며, 단순 관행이었다고 주장함."
    }

if __name__ == "__main__":
    print("🚀 [V2.0] 고도화된 사건 데이터(주가조작, 뇌물 등) 생성을 시작합니다...")
    # 대량 생성: 200건
    for i in range(1, 201):
        c_id = f"CASE-HIGH-STAKES-{i:04d}"
        data = generate_case(c_id)
        with open(os.path.join(OUTPUT_DIR, f"{c_id}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 총 {i}건의 고난도 사건 파일 생성 완료.")
