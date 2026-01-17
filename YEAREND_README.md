# 연말정산 시뮬레이션 프로그램
# Year-End Tax Settlement Simulation Program

한국의 연말정산 세금 계산을 시뮬레이션하는 전문 프로그램입니다.

A professional program to simulate year-end tax settlement calculations for Korea.

## 기능 (Features)

- ✅ **근로소득공제 자동 계산** - Automatic earned income deduction calculation
- ✅ **인적공제 계산** - Personal exemption calculation
- ✅ **연금/보험료 공제** - Pension and insurance premium deduction
- ✅ **주택청약 소득공제** - Housing subscription savings deduction
- ✅ **신용카드 등 소득공제** - Credit card usage deduction
- ✅ **의료비 세액공제** - Medical expense tax credit
- ✅ **보장성보험료 세액공제** - Insurance premium tax credit
- ✅ **기부금 세액공제** - Donation tax credit
- ✅ **대화형 모드 지원** - Interactive mode support
- ✅ **JSON 설정 파일 지원** - JSON configuration file support
- ✅ **결과 저장 기능** - Result saving functionality

## 설치 (Installation)

### 필수 요구사항 (Requirements)
- Python 3.6 이상 (Python 3.6 or higher)
- 추가 라이브러리 불필요 (No additional libraries required - uses standard library only)

### 설치 방법 (Installation Steps)

```bash
# 저장소 클론 (Clone the repository)
git clone https://github.com/koreatest12/cost-data.git
cd cost-data

# 실행 권한 부여 (Make scripts executable)
chmod +x yearend_settlement.py run_yearend.sh
```

## 사용법 (Usage)

### 방법 1: 간편 실행 스크립트 사용 (Using Launcher Script)

```bash
./run_yearend.sh
```

메뉴에서 원하는 옵션을 선택하세요:
1. 대화형 모드 - 직접 데이터 입력
2. 설정 파일 사용 - 미리 작성된 JSON 파일 사용
3. 예제 설정 파일 생성
4. 도움말 보기

### 방법 2: 직접 Python 실행 (Direct Python Execution)

#### 대화형 모드 (Interactive Mode)
```bash
python3 yearend_settlement.py
```

#### 설정 파일 사용 (Using Configuration File)
```bash
python3 yearend_settlement.py --config yearend_example.json
```

#### 예제 설정 파일 생성 (Create Example Config)
```bash
python3 yearend_settlement.py --create-example
```

#### 도움말 (Help)
```bash
python3 yearend_settlement.py --help
```

## 설정 파일 형식 (Configuration File Format)

JSON 형식으로 작성합니다:

```json
{
  "name": "홍길동",
  "total_salary": 40000000,
  "deductions": {
    "pension": 1236000,
    "insurance_health": 1378730,
    "housing_saving": 1200000,
    "credit_card": 412670,
    "debit_card": 13086527,
    "cash_receipt": 2502383,
    "medical_expense": 2695380,
    "medical_silson": 1163706,
    "insurance_guarantee": 761880,
    "donation": 120000
  }
}
```

### 항목 설명 (Field Descriptions)

| 항목 | 설명 | 비고 |
|------|------|------|
| name | 납세자 이름 | 필수 |
| total_salary | 총급여액 | 필수, 원 단위 |
| pension | 국민연금 납부액 | 전액 공제 |
| insurance_health | 건강보험+고용보험 | 전액 공제 |
| housing_saving | 주택청약저축 납입액 | 40% 공제 |
| credit_card | 신용카드 사용액 | 조건부 공제 |
| debit_card | 체크카드 사용액 | 조건부 공제 |
| cash_receipt | 현금영수증 | 조건부 공제 |
| medical_expense | 의료비 지출액 | 세액공제 |
| medical_silson | 실손보험 수령액 | 의료비에서 차감 |
| insurance_guarantee | 보장성보험료 | 세액공제 |
| donation | 기부금 | 세액공제 |

## 예제 실행 (Example Execution)

### 예제 1: 기본 예제 파일 사용
```bash
# 예제 파일 생성
python3 yearend_settlement.py --create-example

# 예제 파일로 시뮬레이션 실행
python3 yearend_settlement.py --config yearend_example.json
```

### 예제 2: 김병권님 데이터 사용
```bash
python3 yearend_settlement.py --config yearend_김병권.json
```

### 예제 3: 대화형 모드
```bash
python3 yearend_settlement.py
# 프롬프트에 따라 데이터 입력
```

## 출력 예시 (Output Example)

```
============================================================
   홍길동님의 2025년 귀속 연말정산 시뮬레이션
============================================================
설정된 총급여액: 40,000,000원

[1] 근로소득공제 예상액: 7,500,000원
[2] 본인 기본공제: 1,500,000원
[3] 연금/건강/고용보험 공제: 2,614,730원
[4] 주택청약 소득공제 (40%): 480,000원
[5] 신용카드 등 소득공제 예상액: 1,500,000원
    (총 사용액: 16,001,580원, 최저사용기준: 10,000,000원)
[6] 의료비 세액공제: 79,551원
    (순수 의료비: 1,531,674원, 문턱값: 1,200,000원)
[7] 보장성보험 세액공제: 91,425원
[8] 기부금 세액공제: 18,000원

============================================================
>> 총 예상 소득공제액 합계: 13,594,730원
>> 총 예상 세액공제액 합계: 188,976원
============================================================
```

## 주요 계산 로직 (Calculation Logic)

### 1. 근로소득공제 (Earned Income Deduction)
- 총급여액에 따라 구간별 공제율 적용
- 2024~2025년 귀속 기준

| 총급여액 구간 | 공제율 |
|--------------|--------|
| 500만원 이하 | 70% |
| 500만원 ~ 1,500만원 | 350만원 + 초과액의 40% |
| 1,500만원 ~ 4,500만원 | 750만원 + 초과액의 15% |
| 4,500만원 ~ 1억원 | 1,200만원 + 초과액의 5% |
| 1억원 초과 | 1,475만원 + 초과액의 2% |

### 2. 신용카드 등 소득공제
- 총급여의 25% 초과 사용액에 대해 공제
- 신용카드: 15%, 체크카드/현금: 30% (간소화)
- 한도: 300만원

### 3. 의료비 세액공제
- 총급여의 3% 초과 금액의 15% 세액공제
- 실손보험금 차감 필수
- 한도: 700만원

### 4. 보장성보험료 세액공제
- 납입액의 12% 세액공제
- 한도: 100만원 납입액 기준

### 5. 기부금 세액공제
- 1,000만원 이하: 15%
- 1,000만원 초과: 초과분 30%

## 참고자료 (References)

- 국세청 홈택스: https://www.hometax.go.kr
- 연말정산 간소화서비스
- 2025년 귀속 연말정산 안내

## 주의사항 (Notes)

⚠️ **이 프로그램은 시뮬레이션 목적으로만 사용하세요**
- 실제 연말정산 계산은 더 복잡한 요소들이 있습니다
- 가족 구성원, 부양가족, 특별공제 등은 간소화되었습니다
- 정확한 세액은 국세청 홈택스를 이용하거나 세무사와 상담하세요

⚠️ **This program is for simulation purposes only**
- Actual tax calculations involve more complex factors
- Family members, dependents, and special deductions are simplified
- For accurate calculations, use the National Tax Service Hometax or consult a tax accountant

## 라이선스 (License)

이 프로젝트는 Apache License 2.0을 따릅니다.

## 문의 (Contact)

문제가 있거나 개선 제안이 있으시면 이슈를 등록해주세요.

If you have any issues or suggestions, please open an issue.
