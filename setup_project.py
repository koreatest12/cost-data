import os

# ==============================================================================
# [설정] 프로젝트 이름 및 파일 내용 정의
# ==============================================================================
PROJECT_DIR = "algorithm_project"  # 생성될 최상위 폴더 이름

# 1. 알고리즘 코드 (navigation.py)
CODE_NAVIGATION = """
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
    distances = {city: float('inf') for city in city_map.graph}
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
    if distances[end] == float('inf'): return None, None

    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    return distances[end], path

if __name__ == "__main__":
    print("--- [알고리즘 자동 실행 시작] ---")
    korea_map = CityMap()
    korea_map.add_road("서울", "대전", 2)
    korea_map.add_road("서울", "강릉", 3)
    korea_map.add_road("대전", "대구", 2)
    korea_map.add_road("대전", "광주", 3)
    korea_map.add_road("강릉", "대구", 4)
    korea_map.add_road("대구", "부산", 1)
    korea_map.add_road("광주", "부산", 2)

    start, end = "서울", "부산"
    print(f"📡 탐색 경로: {start} -> {end}")
    min_time, path = calculate_shortest_path(korea_map, start, end)

    if path:
        print(f"✅ 결과: 최소 시간 {min_time}시간")
        print(f"📍 경로: {' -> '.join(path)}")
    else:
        print("❌ 경로 없음")
    print("--- [종료] ---")
"""

# 2. GitHub Actions 워크플로우 (run_algorithm.yml)
# 핵심 수정: working-directory를 설정하거나 경로를 명시하여 'File not found' 에러 방지
CODE_WORKFLOW = """name: Algorithm Auto-Run

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  run-algorithm:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.9"

    - name: Run Algorithm Script
      # [수정됨] 파일이 src 폴더 안에 있든 루트에 있든 정확한 경로로 실행
      run: |
        echo "현재 디렉토리 파일 목록 확인:"
        ls -R
        echo "--------------------------------"
        python src/navigation.py
"""

# 3. 로컬 실행용 쉘 스크립트 (run_local.sh)
CODE_SHELL = """#!/bin/bash
echo "로컬에서 알고리즘을 테스트합니다..."
python3 src/navigation.py
"""

# 4. 로컬 실행용 배치 파일 (run_local.bat)
CODE_BATCH = """@echo off
chcp 65001 > nul
echo 로컬에서 알고리즘을 테스트합니다...
python src/navigation.py
pause
"""

# ==============================================================================
# [실행] 파일 및 디렉토리 대량 생성 로직
# ==============================================================================
def create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 생성 완료: {path}")

def main():
    print(f"🚀 프로젝트 자동 생성 중... 대상 폴더: ./{PROJECT_DIR}")

    # 1. 디렉토리 구조 생성
    dirs = [
        f"{PROJECT_DIR}/src",                 # 소스코드 폴더
        f"{PROJECT_DIR}/.github/workflows"    # 깃허브 액션 폴더
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"📁 폴더 생성: {d}")

    # 2. 파일 생성
    # 소스코드 (src 폴더 안에 넣음으로써 구조화)
    create_file(f"{PROJECT_DIR}/src/navigation.py", CODE_NAVIGATION)
    
    # 워크플로우 (YAML)
    create_file(f"{PROJECT_DIR}/.github/workflows/run_algorithm.yml", CODE_WORKFLOW)
    
    # 실행 스크립트
    create_file(f"{PROJECT_DIR}/run_local.sh", CODE_SHELL)
    create_file(f"{PROJECT_DIR}/run_local.bat", CODE_BATCH)
    
    # README
    create_file(f"{PROJECT_DIR}/README.md", "# Algorithm Project\n자동 생성된 알고리즘 프로젝트입니다.")

    print("\n✨ 모든 작업이 완료되었습니다!")
    print(f"👉 1. 'cd {PROJECT_DIR}' 명령어로 폴더에 들어가세요.")
    print("👉 2. 'git init' -> 'git add .' -> 'git commit' -> 'git push'를 진행하세요.")
    print("👉 3. 이제 GitHub Actions에서 에러 없이 실행될 것입니다.")

if __name__ == "__main__":
    main()
