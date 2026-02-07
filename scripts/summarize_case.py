import sys, json
if len(sys.argv) < 2: sys.exit(1)
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"[AI 요약] 피고인 {data['defendant']['name']} ({data['defendant']['job']})")
print(f"혐의: {data['crime_summary']['category']} - {data['crime_summary']['detail']}")
print(f"피해규모: {data['crime_summary']['damage_amount_krw']:,}원")
