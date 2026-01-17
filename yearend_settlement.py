#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
연말정산 시뮬레이션 프로그램
Year-End Tax Settlement Simulation Program

이 프로그램은 한국의 연말정산 세금 계산을 시뮬레이션합니다.
This program simulates year-end tax settlement calculations for Korea.
"""

import json
import sys
from typing import Dict, Optional


class YearEndSettlement:
    """연말정산 시뮬레이션 클래스"""
    
    def __init__(self, name: str, total_salary: int):
        """
        초기화
        
        Args:
            name: 납세자 이름
            total_salary: 총급여액
        """
        self.name = name
        self.total_salary = total_salary  # 총급여액
        self.data = {
            "pension": 0,          # 국민연금
            "insurance_health": 0, # 건강/고용보험
            "housing_saving": 0,   # 주택청약
            "credit_card": 0,      # 신용카드 등
            "debit_card": 0,       # 체크카드 등
            "cash_receipt": 0,     # 현금영수증
            "medical_expense": 0,  # 의료비 지출액
            "medical_silson": 0,   # 실손보험 수령액
            "insurance_guarantee": 0, # 보장성 보험
            "donation": 0          # 기부금
        }

    def set_data(self, **kwargs):
        """
        공제 데이터 입력
        
        Args:
            **kwargs: 공제 항목별 데이터
        """
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key] = value

    def load_from_file(self, filename: str) -> bool:
        """
        JSON 파일에서 데이터 로드
        
        Args:
            filename: JSON 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.name = config.get('name', self.name)
                self.total_salary = config.get('total_salary', self.total_salary)
                self.set_data(**config.get('deductions', {}))
            return True
        except Exception as e:
            print(f"파일 로드 오류: {e}")
            return False

    def save_to_file(self, filename: str) -> bool:
        """
        현재 데이터를 JSON 파일로 저장
        
        Args:
            filename: 저장할 JSON 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            config = {
                'name': self.name,
                'total_salary': self.total_salary,
                'deductions': self.data
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"파일 저장 오류: {e}")
            return False

    def calculate(self) -> Dict[str, int]:
        """
        연말정산 계산 수행
        
        Returns:
            계산 결과 딕셔너리
        """
        print(f"\n{'='*60}")
        print(f"   {self.name}님의 2025년 귀속 연말정산 시뮬레이션")
        print(f"{'='*60}")
        print(f"설정된 총급여액: {self.total_salary:,}원\n")

        results = {}

        # 1. 근로소득공제 (간이 계산)
        income_deduction = self._calc_income_deduction()
        results['income_deduction'] = int(income_deduction)
        print(f"[1] 근로소득공제 예상액: {results['income_deduction']:,}원")

        # 2. 인적공제 (본인 1인 가정)
        basic_deduction = 1_500_000
        results['basic_deduction'] = basic_deduction
        print(f"[2] 본인 기본공제: {results['basic_deduction']:,}원")

        # 3. 연금/보험료 공제 (전액 공제)
        pension_deduction = self.data["pension"]
        insurance_deduction = self.data["insurance_health"]
        results['pension_insurance_deduction'] = pension_deduction + insurance_deduction
        print(f"[3] 연금/건강/고용보험 공제: {results['pension_insurance_deduction']:,}원")

        # 4. 주택마련저축 공제 (납입액의 40%, 한도 적용 필요)
        # 총급여 7천만원 이하 가정
        housing_deduction = min(self.data["housing_saving"] * 0.4, 2_400_000)
        results['housing_deduction'] = int(housing_deduction)
        print(f"[4] 주택청약 소득공제 (40%): {results['housing_deduction']:,}원")

        # 5. 신용카드 등 소득공제
        min_usage = self.total_salary * 0.25
        total_usage = self.data["credit_card"] + self.data["debit_card"] + self.data["cash_receipt"]
        
        card_deduction = 0
        if total_usage > min_usage:
            deductible_usage = total_usage - min_usage
            card_deduction = deductible_usage * 0.30  # 대략적 계산
            card_deduction = min(card_deduction, 3_000_000)  # 공제 한도
        
        results['card_deduction'] = int(card_deduction)
        print(f"[5] 신용카드 등 소득공제 예상액: {results['card_deduction']:,}원")
        print(f"    (총 사용액: {total_usage:,}원, 최저사용기준: {int(min_usage):,}원)")

        # 6. 의료비 세액공제
        net_medical = self.data["medical_expense"] - self.data["medical_silson"]
        medical_threshold = self.total_salary * 0.03
        medical_credit = 0
        
        if net_medical > medical_threshold:
            eligible_amount = min(net_medical - medical_threshold, 7_000_000)
            medical_credit = eligible_amount * 0.15
        
        results['medical_credit'] = int(medical_credit)
        print(f"[6] 의료비 세액공제: {results['medical_credit']:,}원")
        print(f"    (순수 의료비: {net_medical:,}원, 문턱값: {int(medical_threshold):,}원)")

        # 7. 보장성보험료 세액공제
        insurance_credit = min(self.data["insurance_guarantee"], 1_000_000) * 0.12
        results['insurance_credit'] = int(insurance_credit)
        print(f"[7] 보장성보험 세액공제: {results['insurance_credit']:,}원")

        # 8. 기부금 세액공제
        donation_credit = self.data["donation"] * 0.15
        results['donation_credit'] = int(donation_credit)
        print(f"[8] 기부금 세액공제: {results['donation_credit']:,}원")
        
        # 총 세액공제액 합계
        total_tax_credit = medical_credit + insurance_credit + donation_credit
        results['total_tax_credit'] = int(total_tax_credit)
        
        # 총 소득공제액 합계
        total_income_deduction = (income_deduction + basic_deduction + 
                                  results['pension_insurance_deduction'] + 
                                  results['housing_deduction'] + 
                                  results['card_deduction'])
        results['total_income_deduction'] = int(total_income_deduction)
        
        print(f"\n{'='*60}")
        print(f">> 총 예상 소득공제액 합계: {results['total_income_deduction']:,}원")
        print(f">> 총 예상 세액공제액 합계: {results['total_tax_credit']:,}원")
        print(f"{'='*60}\n")
        
        return results

    def _calc_income_deduction(self) -> float:
        """
        근로소득공제 계산 (2024~2025년 귀속)
        
        Returns:
            근로소득공제액
        """
        s = self.total_salary
        if s <= 5_000_000:
            return s * 0.7
        elif s <= 15_000_000:
            return 3_500_000 + (s - 5_000_000) * 0.4
        elif s <= 45_000_000:
            return 7_500_000 + (s - 15_000_000) * 0.15
        elif s <= 100_000_000:
            return 12_000_000 + (s - 45_000_000) * 0.05
        else:
            return 14_750_000 + (s - 100_000_000) * 0.02


def print_help():
    """도움말 출력"""
    help_text = """
연말정산 시뮬레이션 프로그램 사용법
=====================================

1. 기본 사용법 (대화형 모드):
   python yearend_settlement.py

2. 설정 파일 사용:
   python yearend_settlement.py --config <설정파일.json>

3. 예제 설정 파일 생성:
   python yearend_settlement.py --create-example

4. 도움말:
   python yearend_settlement.py --help

설정 파일 형식 (JSON):
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
"""
    print(help_text)


def create_example_config(filename: str = "yearend_example.json"):
    """예제 설정 파일 생성"""
    example = {
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
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(example, f, ensure_ascii=False, indent=2)
        print(f"예제 설정 파일이 생성되었습니다: {filename}")
        return True
    except Exception as e:
        print(f"예제 파일 생성 오류: {e}")
        return False


def interactive_mode():
    """대화형 모드로 실행"""
    print("\n연말정산 시뮬레이션 프로그램")
    print("="*40)
    
    try:
        name = input("이름을 입력하세요: ").strip()
        total_salary = int(input("총급여액을 입력하세요 (원): ").strip())
        
        settlement = YearEndSettlement(name, total_salary)
        
        print("\n공제 항목을 입력하세요 (없으면 0 입력):")
        
        deductions = {}
        deductions['pension'] = int(input("국민연금: ").strip() or "0")
        deductions['insurance_health'] = int(input("건강/고용보험: ").strip() or "0")
        deductions['housing_saving'] = int(input("주택청약: ").strip() or "0")
        deductions['credit_card'] = int(input("신용카드 사용액: ").strip() or "0")
        deductions['debit_card'] = int(input("체크카드 사용액: ").strip() or "0")
        deductions['cash_receipt'] = int(input("현금영수증: ").strip() or "0")
        deductions['medical_expense'] = int(input("의료비 지출액: ").strip() or "0")
        deductions['medical_silson'] = int(input("실손보험 수령액: ").strip() or "0")
        deductions['insurance_guarantee'] = int(input("보장성 보험료: ").strip() or "0")
        deductions['donation'] = int(input("기부금: ").strip() or "0")
        
        settlement.set_data(**deductions)
        settlement.calculate()
        
        # 결과 저장 여부 확인
        save = input("\n결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("파일명을 입력하세요 (기본: yearend_result.json): ").strip()
            if not filename:
                filename = "yearend_result.json"
            if settlement.save_to_file(filename):
                print(f"결과가 {filename}에 저장되었습니다.")
        
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except ValueError:
        print("잘못된 입력입니다. 숫자를 입력해주세요.")
    except Exception as e:
        print(f"오류 발생: {e}")


def main():
    """메인 함수"""
    if len(sys.argv) == 1:
        # 인자 없이 실행 시 대화형 모드
        interactive_mode()
    elif '--help' in sys.argv or '-h' in sys.argv:
        print_help()
    elif '--create-example' in sys.argv:
        create_example_config()
    elif '--config' in sys.argv:
        try:
            idx = sys.argv.index('--config')
            if idx + 1 < len(sys.argv):
                config_file = sys.argv[idx + 1]
                settlement = YearEndSettlement("", 0)
                if settlement.load_from_file(config_file):
                    settlement.calculate()
                else:
                    print("설정 파일을 로드할 수 없습니다.")
            else:
                print("설정 파일 경로를 지정해주세요.")
                print_help()
        except Exception as e:
            print(f"오류: {e}")
            print_help()
    else:
        print("잘못된 인자입니다.")
        print_help()


if __name__ == "__main__":
    main()
