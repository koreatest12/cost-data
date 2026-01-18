import os
import sys

# ==============================================================================
# [설정] 프로젝트 정의
# ==============================================================================
ROOT_DIR = "algorithm_pro_project"

# ------------------------------------------------------------------------------
# 1. 소스 코드 (src/navigation.py)
# ------------------------------------------------------------------------------
CODE_SRC = """
import heapq
import sys

class CityMap:
    def __init__(self):
        self.graph = {}

    def add_road(self, start_city, end_city, travel_time):
        if start_city not in self.graph: self.graph[start_city] = {}
        if end_city not in self.graph: self.graph[end_city] = {}
        
        self.graph[start_city][end_city] = travel_time
        self.graph[end_city][start_city] = travel_time

def calculate_shortest_path(city_map, start, end):
    # 초기화
    distances = {city: float('inf') for city in city_map.graph}
    if start not in distances: return None, None # 시작점이 지도에 없는 경우
    
    distances[start] = 0
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))
    previous_nodes = {city: None for city in city_map.graph}

    while priority_queue:
        current_time, current_city = heapq.heappop(priority_queue)

        if current_time > distances[current_city]: continue

        for neighbor, weight in city_map.graph[current_city].items():
            distance = current_time + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_city
                heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    current = end
    
    if end not in distances or distances[end] == float('inf'):
        return None, None

    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    
    path.reverse()
    return distances[end], path

if __name__ == "__main__":
    # 직접 실행 시 작동하는 코드
    print("--- [Main Execution] ---")
    m = CityMap()
    m.add_road("A", "B", 1)
    m.add_road("B", "C", 2)
    dist, path = calculate_shortest_path(m, "A", "C")
    print(f"Result: {dist}, Path: {path}")
"""

# ------------------------------------------------------------------------------
# 2. 유닛 테스트 코드 (tests/test_navigation.py)
# GitHub Actions가 이 코드를 실행해서 정답인지 채점합니다.
# ------------------------------------------------------------------------------
CODE_TEST = """
import pytest
import sys
import os

# src 폴더를 import 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from navigation import CityMap, calculate_shortest_path

def test_simple_path():
    m = CityMap()
    m.add_road("Seoul", "Daejeon", 2)
    m.add_road("Daejeon", "Busan", 3)
    
    cost, path = calculate_shortest_path(m, "Seoul", "Busan")
    
    assert cost == 5
    assert path == ["Seoul", "Daejeon", "Busan"]

def test_no_path():
    m = CityMap()
    m.add_road("A", "B", 1)
    m.add_road("C", "D", 1)
    # A와 C는 연결되지 않음
    cost, path = calculate_shortest_path(m, "A", "C")
    assert cost is None

def test_better_path():
    m = CityMap()
    m.add_road("Start", "End", 10)       # 느린 길
    m.add_road("Start", "Middle", 2)     # 빠른 길 1
    m.add_road("Middle", "End", 2)       # 빠른 길 2 (총 4)
    
    cost, path = calculate_shortest_path(m, "Start", "End")
    assert cost == 4
    assert path == ["Start", "Middle", "End"]
"""

# ------------------------------------------------------------------------------
# 3. 종합 GitHub Actions 워크플로우 (.github/workflows/ci_pipeline.yml)
# 테스트, 린트, 실행, 디버깅을 모두 포함합니다.
# ------------------------------------------------------------------------------
CODE_WORKFLOW = """name: Professional CI Pipeline

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  build-and-test:
    name: Build & Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10"] # 여러 버전에서 동시에 테스트

    steps:
    # 1. 코드 체크아웃
    - name: Checkout Code
      uses: actions/checkout@v4

    # 2. 파이썬 설정
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    # 3. 파일 구조 디버깅 (에러 발생 시 확인용)
    - name: 🔍 Debug Directory Structure
      run: |
        echo "Root directory contents:"
        ls -R

    # 4. 의존성 설치
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    # 5. 코드 스타일 검사 (선택 사항이지만 추천)
    - name: Lint with flake8
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings.
        flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    # 6. 유닛 테스트 실행 (가장 중요)
    - name: 🧪 Run Unit Tests (pytest)
      run: |
        # src 폴더를 PYTHONPATH에 추가하여 테스트 실행
        export PYTHONPATH=$PYTHONPATH:$(pwd)/src
        pytest tests/

    # 7. 실제 스크립트 실행 (단독 실행 테스트)
    - name: 🚀 Run Main Script
      run: |
        python src/navigation.py
"""

# ------------------------------------------------------------------------------
# 4. 기타 설정 파일들 (requirements.txt, .gitignore)
# ------------------------------------------------------------------------------
CODE_REQ = """
pytest
flake8
"""

CODE_GITIGNORE = """
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
"""

# ==============================================================================
# [로직] 파일 생성기 실행
# ==============================================================================
def write_file(path, content):
    # 상위 디렉토리 생성
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 생성됨: {path}")

def main():
    print(f"🏗️  [종합] 전문가급 프로젝트 생성 시작... ({ROOT_DIR})")
    
    # 기본 파일들 생성
    write_file(f"{ROOT_DIR}/src/navigation.py", CODE_SRC)
    write_file(f"{ROOT_DIR}/tests/test_navigation.py", CODE_TEST)
    write_file(f"{ROOT_DIR}/.github/workflows/ci_pipeline.yml", CODE_WORKFLOW)
    write_file(f"{ROOT_DIR}/requirements.txt", CODE_REQ)
    write_file(f"{ROOT_DIR}/.gitignore", CODE_GITIGNORE)
    write_file(f"{ROOT_DIR}/README.md", "# Algorithm Project\nCI/CD 파이프라인이 적용된 프로젝트입니다.")

    print("\n✨ 모든 파일이 준비되었습니다!")
    print("👇 아래 명령어를 순서대로 실행하여 GitHub에 올리세요:")
    print("-" * 50)
    print(f"cd {ROOT_DIR}")
    print("git init")
    print("git add .")
    print('git commit -m "Initialize professional project structure"')
    print("git remote add origin https://github.com/사용자ID/저장소이름.git")
    print("git branch -M main")
    print("git push -u origin main --force")
    print("-" * 50)

if __name__ == "__main__":
    main()
