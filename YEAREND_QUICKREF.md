# 연말정산 시뮬레이션 빠른 참조 가이드
# Year-End Tax Settlement Quick Reference

## 🚀 빠른 시작 (Quick Start)

### 가장 빠른 방법 (Fastest Way)
```bash
# 1. 실행 스크립트 사용
./run_yearend.sh          # Linux/macOS
run_yearend.bat           # Windows

# 2. 메뉴에서 "1" 선택 (대화형 모드)
```

### 설정 파일 사용 (Using Config File)
```bash
# 1. 예제 파일 생성
python3 yearend_settlement.py --create-example

# 2. 파일 편집 (본인 데이터 입력)
nano yearend_example.json

# 3. 실행
python3 yearend_settlement.py --config yearend_example.json
```

---

## 📋 명령어 요약 (Command Summary)

| 명령어 | 설명 |
|--------|------|
| `./run_yearend.sh` | 간편 실행 (Linux/macOS) |
| `run_yearend.bat` | 간편 실행 (Windows) |
| `python3 yearend_settlement.py` | 대화형 모드 |
| `python3 yearend_settlement.py --config FILE` | 설정 파일 사용 |
| `python3 yearend_settlement.py --create-example` | 예제 파일 생성 |
| `python3 yearend_settlement.py --help` | 도움말 |

---

## 💾 설정 파일 템플릿 (Config Template)

```json
{
  "name": "이름",
  "total_salary": 0,
  "deductions": {
    "pension": 0,
    "insurance_health": 0,
    "housing_saving": 0,
    "credit_card": 0,
    "debit_card": 0,
    "cash_receipt": 0,
    "medical_expense": 0,
    "medical_silson": 0,
    "insurance_guarantee": 0,
    "donation": 0
  }
}
```

**주의**: 위 템플릿에서 숫자 값들을 실제 금액으로 교체하세요.

**예시**:
```json
{
  "name": "홍길동",
  "total_salary": 40000000,
  "deductions": {
    "pension": 1236000,
    "insurance_health": 1378730,
    "housing_saving": 1200000,
    ...
  }
}
```

---

## 🔍 데이터 준비 체크리스트 (Data Preparation Checklist)

### 국세청 홈택스에서 조회
- [ ] 국민연금 납부액
- [ ] 건강보험료 + 장기요양보험료
- [ ] 고용보험료
- [ ] 신용카드 사용액
- [ ] 체크카드 사용액
- [ ] 현금영수증 발급액
- [ ] 의료비 지출액
- [ ] 실손보험 수령액
- [ ] 보장성보험료
- [ ] 기부금

### 홈택스 접속 방법
1. https://www.hometax.go.kr 접속
2. 로그인
3. 조회·발급 > 연말정산간소화
4. 소득·세액공제 자료 조회

---

## 📊 계산 항목 (Calculation Items)

### 소득공제 (Income Deductions)
1. **근로소득공제** - 자동 계산
2. **인적공제** - 본인 기본 150만원
3. **연금보험료** - 전액 공제
4. **주택청약** - 40% 공제
5. **신용카드 등** - 조건부 공제

### 세액공제 (Tax Credits)
1. **의료비** - 15% 세액공제
2. **보험료** - 12% 세액공제
3. **기부금** - 15% 세액공제

---

## ⚠️ 주의사항 (Important Notes)

### 이 프로그램은 시뮬레이션입니다
- 실제 연말정산과 차이가 있을 수 있습니다
- 부양가족, 특별공제 등은 포함되지 않았습니다
- 정확한 계산은 홈택스 또는 세무사 상담 필요

### 금액 입력 시
- 모든 금액은 원 단위로 입력
- 쉼표(,) 없이 숫자만 입력: `40000000`
- 실손보험 수령액은 반드시 차감

---

## 🆘 문제 해결 (Quick Troubleshooting)

### Python을 찾을 수 없음
```bash
# Python 설치 확인
python3 --version  # Linux/macOS
python --version   # Windows
```

### 파일을 찾을 수 없음
```bash
# 파일 목록 확인
ls yearend*.json  # Linux/macOS
dir yearend*.json # Windows

# 올바른 경로에서 실행
cd /path/to/cost-data
```

### JSON 형식 오류
- 예제 파일을 다시 생성: `python3 yearend_settlement.py --create-example`
- JSON 검증: https://jsonlint.com/

---

## 📚 상세 문서 (Detailed Documentation)

- **프로그램 설명**: [YEAREND_README.md](YEAREND_README.md)
- **설치 가이드**: [YEAREND_INSTALL_GUIDE.md](YEAREND_INSTALL_GUIDE.md)
- **전체 프로젝트**: [README.md](README.md)

---

## 💡 팁 (Tips)

### 여러 시나리오 비교
```bash
# 여러 설정 파일 만들기
cp yearend_example.json yearend_시나리오1.json
cp yearend_example.json yearend_시나리오2.json

# 각각 다른 금액으로 테스트
python3 yearend_settlement.py --config yearend_시나리오1.json
python3 yearend_settlement.py --config yearend_시나리오2.json
```

### 결과 저장
- 대화형 모드에서 실행 후 "y" 선택하여 결과 저장
- 저장된 파일을 다시 로드하여 재실행 가능

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-01-17
