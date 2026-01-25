# manage_setup.py
import os
import subprocess
import json
import sys

# =========================================================
# 설정: 프로젝트 루트 경로
# =========================================================
ROOT_DIR = "."

# =========================================================
# 1. 모듈 대량 설치 함수 (Java/Maven & Python/Pip)
# =========================================================
def install_modules(root_path):
    print(f"🔄 [모듈 설치] {root_path} 내부의 의존성을 스캔합니다...")
    
    for dirpath, _, filenames in os.walk(root_path):
        # 1-1. Python (requirements.txt) 발견 시
        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            print(f"   🐍 Python 의존성 설치 중: {req_path}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        
        # 1-2. Java (pom.xml) 발견 시
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Maven 빌드 중: {pom_path}")
            # Windows는 'mvn.cmd', Linux/Mac은 'mvn'
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            subprocess.check_call([mvn_cmd, "clean", "install", "-f", pom_path, "-DskipTests"])

# =========================================================
# 2. 모델 파일 대량 다운로드 함수 (URL 기반)
# =========================================================
def download_models(manifest_file="models.json"):
    """
    models.json 파일에 정의된 모델들을 대량으로 다운로드합니다.
    형식: {"모델명": {"url": "주소", "dest": "저장위치"}}
    """
    if not os.path.exists(manifest_file):
        print(f"ℹ️  [모델 스킵] {manifest_file} 파일이 없습니다.")
        return

    print(f"⬇️  [모델 다운로드] {manifest_file}을 기반으로 모델을 설치합니다...")
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        models = json.load(f)

    for name, info in models.items():
        url = info['url']
        dest_folder = info['dest']
        file_name = url.split('/')[-1]
        dest_path = os.path.join(dest_folder, file_name)

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        
        if os.path.exists(dest_path):
            print(f"   ✅ [이미 있음] {name}: {dest_path}")
            continue

        print(f"   📥 [다운로드 중] {name} -> {dest_path}")
        # curl 사용 (또는 wget, python requests로 대체 가능)
        try:
            subprocess.check_call(["curl", "-L", "-o", dest_path, url])
        except Exception as e:
            print(f"   ❌ [실패] {name} 다운로드 실패: {e}")

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 설정 시작]")
    
    # 1. 모델 정의 파일이 있다면 모델부터 다운로드
    # (프로젝트 루트에 models.json을 만들어두세요)
    download_models("models.json")
    
    # 2. 모든 서브 디렉토리의 라이브러리 설치
    install_modules(ROOT_DIR)
    
    print("\n✨ [완료] 모든 모듈 및 모델 설정이 완료되었습니다.")
