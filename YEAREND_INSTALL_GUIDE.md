# 연말정산 시뮬레이션 프로그램 설치 가이드
# Year-End Tax Settlement Simulation Program Installation Guide

## 개요 (Overview)

이 문서는 연말정산 시뮬레이션 프로그램의 설치 및 사용 방법을 상세히 설명합니다.

This document provides detailed installation and usage instructions for the Year-End Tax Settlement Simulation Program.

---

## 시스템 요구사항 (System Requirements)

### 필수 요구사항 (Required)
- **Python**: 3.6 이상 (Python 3.6 or higher)
  - Python 표준 라이브러리만 사용 (No external dependencies)
  
### 권장 환경 (Recommended)
- **운영체제**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **디스크 공간**: 최소 10MB
- **메모리**: 최소 100MB

---

## 설치 방법 (Installation)

### 1. 저장소 클론 (Clone Repository)

```bash
git clone https://github.com/koreatest12/cost-data.git
cd cost-data
```

### 2. Python 설치 확인 (Verify Python Installation)

**Linux/macOS:**
```bash
python3 --version
```

**Windows:**
```cmd
python --version
```

최소 Python 3.6 이상이 필요합니다. 설치되지 않은 경우:
- Windows: https://www.python.org/downloads/
- macOS: `brew install python3`
- Linux: `sudo apt-get install python3`

### 3. 실행 권한 부여 (Set Execute Permissions)

**Linux/macOS:**
```bash
chmod +x yearend_settlement.py run_yearend.sh
```

**Windows:** (권한 설정 불필요)

---

## 사용 방법 (Usage)

### 방법 1: 간편 실행 스크립트 (Launcher Scripts)

#### Linux/macOS:
```bash
./run_yearend.sh
```

#### Windows:
```cmd
run_yearend.bat
```

메뉴에서 원하는 옵션을 선택:
1. **대화형 모드**: 프롬프트에 따라 직접 데이터 입력
2. **설정 파일 사용**: JSON 파일에서 데이터 로드
3. **예제 설정 파일 생성**: 샘플 JSON 파일 생성
4. **도움말**: 사용 방법 안내

### 방법 2: Python 직접 실행 (Direct Python Execution)

#### 대화형 모드 (Interactive Mode)
```bash
# Linux/macOS
python3 yearend_settlement.py

# Windows
python yearend_settlement.py
```

대화형 모드에서는 다음 정보를 입력합니다:
1. 이름
2. 총급여액
3. 각종 공제 항목 (국민연금, 건강보험, 신용카드 사용액 등)

#### 설정 파일 모드 (Configuration File Mode)
```bash
# Linux/macOS
python3 yearend_settlement.py --config yearend_example.json

# Windows
python yearend_settlement.py --config yearend_example.json
```

#### 예제 파일 생성 (Create Example)
```bash
# Linux/macOS
python3 yearend_settlement.py --create-example

# Windows
python yearend_settlement.py --create-example
```

#### 도움말 (Help)
```bash
# Linux/macOS
python3 yearend_settlement.py --help

# Windows
python yearend_settlement.py --help
```

---

## 설정 파일 작성 (Creating Configuration Files)

### 1. 예제 파일 생성

```bash
python3 yearend_settlement.py --create-example
```

이 명령어는 `yearend_example.json` 파일을 생성합니다.

### 2. 설정 파일 편집

생성된 파일을 텍스트 에디터로 열어 본인의 데이터로 수정:

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

### 3. 항목별 설명

| 항목 | 필드명 | 설명 | 단위 |
|------|--------|------|------|
| 이름 | name | 납세자 이름 | 문자열 |
| 총급여액 | total_salary | 연간 총급여 | 원 (숫자) |
| 국민연금 | pension | 국민연금 납부액 | 원 |
| 건강/고용보험 | insurance_health | 건강보험+장기요양+고용보험 합계 | 원 |
| 주택청약 | housing_saving | 주택청약저축 납입액 | 원 |
| 신용카드 | credit_card | 신용카드 사용액 | 원 |
| 체크카드 | debit_card | 체크카드 사용액 | 원 |
| 현금영수증 | cash_receipt | 현금영수증 발급액 | 원 |
| 의료비 | medical_expense | 총 의료비 지출액 | 원 |
| 실손보험 | medical_silson | 실손보험 수령액 | 원 |
| 보장성보험 | insurance_guarantee | 보장성보험료 납입액 | 원 |
| 기부금 | donation | 기부금액 | 원 |

---

## 데이터 준비 (Data Preparation)

### 연말정산 간소화서비스 활용

1. **국세청 홈택스 접속**
   - https://www.hometax.go.kr
   - 로그인

2. **연말정산 간소화서비스 이용**
   - 조회·발급 > 연말정산간소화 > 소득·세액공제 자료 조회

3. **자료 수집**
   - 국민연금: 공제 항목 조회
   - 건강보험: 건강보험료 + 장기요양보험료
   - 고용보험: 고용보험료
   - 신용카드: 신용카드 사용액
   - 체크카드: 직불카드·현금영수증 사용액
   - 의료비: 의료비 지출액 (실손보험금 차감 전)
   - 보험료: 보장성보험료
   - 기부금: 기부금 명세

4. **설정 파일에 입력**
   - 조회한 금액을 JSON 파일의 해당 항목에 입력

---

## 사용 예시 (Usage Examples)

### 예시 1: 신규 사용자

```bash
# 1단계: 예제 파일 생성
python3 yearend_settlement.py --create-example

# 2단계: 파일 편집
nano yearend_example.json  # 또는 다른 텍스트 에디터 사용

# 3단계: 시뮬레이션 실행
python3 yearend_settlement.py --config yearend_example.json
```

### 예시 2: 여러 사람의 데이터 관리

```bash
# 각 사람별 설정 파일 생성
cp yearend_example.json yearend_홍길동.json
cp yearend_example.json yearend_김철수.json

# 파일 편집 후 각각 실행
python3 yearend_settlement.py --config yearend_홍길동.json
python3 yearend_settlement.py --config yearend_김철수.json
```

### 예시 3: 대화형 모드로 빠른 테스트

```bash
# 대화형 모드 실행
python3 yearend_settlement.py

# 프롬프트에 따라 입력
이름을 입력하세요: 테스트
총급여액을 입력하세요 (원): 35000000
...
```

---

## 출력 결과 해석 (Understanding Results)

### 출력 예시

```
============================================================
   홍길동님의 2025년 귀속 연말정산 시뮬레이션
============================================================
설정된 총급여액: 40,000,000원

[1] 근로소득공제 예상액: 11,250,000원
[2] 본인 기본공제: 1,500,000원
[3] 연금/건강/고용보험 공제: 2,614,730원
[4] 주택청약 소득공제 (40%): 480,000원
[5] 신용카드 등 소득공제 예상액: 1,800,474원
    (총 사용액: 16,001,580원, 최저사용기준: 10,000,000원)
[6] 의료비 세액공제: 49,751원
    (순수 의료비: 1,531,674원, 문턱값: 1,200,000원)
[7] 보장성보험 세액공제: 91,425원
[8] 기부금 세액공제: 18,000원

============================================================
>> 총 예상 소득공제액 합계: 17,645,204원
>> 총 예상 세액공제액 합계: 159,176원
============================================================
```

### 항목 설명

1. **근로소득공제**: 총급여액에 따라 자동 계산되는 공제
2. **본인 기본공제**: 본인에 대한 인적공제 (150만원 고정)
3. **연금/보험료 공제**: 국민연금, 건강보험, 고용보험 납부액 전액
4. **주택청약 공제**: 납입액의 40% (한도 있음)
5. **신용카드 공제**: 총급여의 25% 초과 사용액에 대한 공제
6. **의료비 세액공제**: 총급여의 3% 초과분의 15%
7. **보험료 세액공제**: 보장성보험료의 12%
8. **기부금 세액공제**: 기부금의 15%

---

## 문제 해결 (Troubleshooting)

### Q1: "Python을 찾을 수 없습니다" 오류

**문제**: Python이 설치되지 않았거나 PATH에 추가되지 않음

**해결**:
```bash
# Python 설치 확인
python3 --version  # Linux/macOS
python --version   # Windows

# 설치되지 않은 경우 Python 설치
# https://www.python.org/downloads/
```

### Q2: "파일을 찾을 수 없습니다" 오류

**문제**: 설정 파일 경로가 잘못됨

**해결**:
```bash
# 현재 디렉토리 확인
pwd  # Linux/macOS
cd   # Windows

# 파일 목록 확인
ls yearend*.json  # Linux/macOS
dir yearend*.json  # Windows
```

### Q3: JSON 파일 형식 오류

**문제**: JSON 파일이 올바른 형식이 아님

**해결**:
- JSON 문법 확인 (쉼표, 중괄호, 따옴표 등)
- 온라인 JSON 검증 도구 사용: https://jsonlint.com/
- 예제 파일을 다시 생성하여 비교

### Q4: 계산 결과가 이상함

**문제**: 입력 데이터 오류 또는 프로그램 제한사항

**해결**:
- 모든 금액을 원 단위로 입력했는지 확인
- 실손보험 수령액이 의료비보다 크지 않은지 확인
- 프로그램은 시뮬레이션이므로 실제 값과 차이가 있을 수 있음

---

## 제한사항 및 주의사항 (Limitations)

### 프로그램 제한사항

⚠️ **이 프로그램은 시뮬레이션 목적입니다**

다음 사항들이 간소화되어 있습니다:
- 가족 구성원 및 부양가족 공제
- 특별 세액공제의 세부 항목
- 연금저축, 퇴직연금 공제
- 월세 세액공제
- 교육비 공제
- 자녀 공제
- 장애인, 경로우대 추가 공제

### 정확한 계산이 필요한 경우

실제 연말정산을 위해서는:
1. **국세청 홈택스** 사용: https://www.hometax.go.kr
2. **회사 급여 담당자** 문의
3. **세무사** 상담

---

## 추가 리소스 (Additional Resources)

### 공식 사이트
- 국세청 홈택스: https://www.hometax.go.kr
- 연말정산 간소화서비스: 홈택스 내 제공
- 국세청 고객센터: 126

### 관련 문서
- [YEAREND_README.md](YEAREND_README.md) - 프로그램 상세 설명
- [README.md](README.md) - 전체 프로젝트 개요

---

## 라이선스 (License)

Apache License 2.0

---

## 지원 (Support)

문제가 발생하거나 개선 제안이 있으시면:
- GitHub Issues: https://github.com/koreatest12/cost-data/issues
- 이메일: (필요시 추가)

---

**마지막 업데이트**: 2025년 1월
**버전**: 1.0.0
