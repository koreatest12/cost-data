import os
import subprocess
import json
import sys

# =========================================================
# 설정: 프로젝트 루트 경로
# =========================================================
ROOT_DIR = "."

# =========================================================
# 1. 파일 대량 생성 및 업데이트 함수
# =========================================================
def manage_files(manifest_file="files.json"):
    """
    files.json에 정의된 내용을 바탕으로 파일을 생성하거나 업데이트합니다.
    형식: {"파일경로": "파일내용"}
    """
    if not os.path.exists(manifest_file):
        print(f"ℹ️  [파일 관리 스킵] {manifest_file} 파일이 없습니다.")
        return

    print(f"📝 [파일 관리] {manifest_file} 내용을 반영합니다...")
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        files_map = json.load(f)

    for file_path, content in files_map.items():
        # 디렉토리가 없으면 생성
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # 파일 쓰기 (덮어쓰기)
        with open(file_path, 'w', encoding='utf-8') as dest:
            dest.write(content)
        
        print(f"   ✅ [파일 반영] {file_path}")

# =========================================================
# 2. 신규 API 모듈 자동 생성 (스캐폴딩)
# =========================================================
def create_api_module(module_name, lang="python"):
    """
    새로운 API 모듈 디렉토리와 기본 파일들을 생성합니다.
    """
    base_path = os.path.join(ROOT_DIR, module_name)
    if os.path.exists(base_path):
        print(f"ℹ️  [API 생성 스킵] {module_name} 폴더가 이미 존재합니다.")
        return

    print(f"🏗️  [API 모듈 생성] {module_name} ({lang}) 생성 중...")
    os.makedirs(base_path)

    if lang == "python":
        # requirements.txt 생성
        with open(os.path.join(base_path, "requirements.txt"), "w") as f:
            f.write("fastapi\nuvicorn\n")
        # main.py 생성
        with open(os.path.join(base_path, "main.py"), "w") as f:
            code = "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}"
            f.write(code)
            
    elif lang == "java":
        # pom.xml 생성 (간소화된 예시)
        os.makedirs(os.path.join(base_path, "src", "main", "java"), exist_ok=True)
        with open(os.path.join(base_path, "pom.xml"), "w") as f:
            f.write('<project><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>'+module_name+'</artifactId><version>1.0.0</version></project>')
    
    print(f"   ✅ [생성 완료] {base_path} 생성됨. 설치 단계에서 의존성이 설치됩니다.")

# =========================================================
# 3. 모듈 대량 설치 함수 (Java/Maven & Python/Pip)
# =========================================================
def install_modules(root_path):
    print(f"🔄 [모듈 설치] {root_path} 내부의 의존성을 스캔합니다...")
    
    for dirpath, _, filenames in os.walk(root_path):
        # 3-1. Python (requirements.txt)
        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            print(f"   🐍 Python 의존성 설치 중: {req_path}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        
        # 3-2. Java (pom.xml)
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Maven 빌드 중: {pom_path}")
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            try:
                subprocess.check_call([mvn_cmd, "clean", "install", "-f", pom_path, "-DskipTests"])
            except FileNotFoundError:
                print("   ⚠️  Maven이 설치되어 있지 않아 건너뜁니다.")

# =========================================================
# 4. 모델 파일 대량 다운로드 함수
# =========================================================
def download_models(manifest_file="models.json"):
    if not os.path.exists(manifest_file):
        print(f"ℹ️  [모델 스킵] {manifest_file} 파일이 없습니다.")
        return

    print(f"⬇️  [모델 다운로드] {manifest_file} 기반 다운로드 시작...")
    
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
            print(f"   ✅ [이미 있음] {name}")
            continue

        print(f"   📥 [다운로드] {name} -> {dest_path}")
        try:
            # curl이 없으면 에러가 날 수 있으므로 예외처리
            subprocess.check_call(["curl", "-L", "-o", dest_path, url])
        except Exception:
            print("   ⚠️  curl 명령 실패. wget이나 python requests로 대체 필요.")

# =========================================================
# 5. Dependabot 실행 (로컬 시뮬레이션 및 원격 트리거)
# =========================================================
def run_dependabot_check():
    print("🛡️  [Dependabot 체크] 의존성 보안 및 업데이트 확인 중...")

    # 5-1. 로컬 시뮬레이션 (Outdated 패키지 확인)
    print("   🔍 [Local Check] 로컬에서 업데이트 필요한 패키지 검색...")
    try:
        # Python
        subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], check=False)
        # Java (Maven이 있는 경우)
        if os.name == 'nt':
            subprocess.run(["mvn.cmd", "versions:display-dependency-updates"], shell=True, check=False)
        else:
            subprocess.run(["mvn", "versions:display-dependency-updates"], check=False)
    except Exception as e:
        print(f"   ⚠️  로컬 검사 중 오류 발생 (무시함): {e}")

    # 5-2. GitHub Actions 원격 트리거 (GitHub CLI 필요)
    print("   ☁️  [Remote Trigger] GitHub Actions 워크플로우 실행 시도...")
    try:
        # 'gh' 명령어가 설치되어 있고 로그인이 되어 있어야 함
        # workflow 이름이 'ci-check.yml' 또는 'dependabot.yml'이라고 가정
        subprocess.run(["gh", "workflow", "run", "ci-check.yml"], check=True)
        print("   ✅ GitHub Actions(Dependabot Check)가 성공적으로 트리거되었습니다.")
    except FileNotFoundError:
        print("   ℹ️  GitHub CLI('gh')가 설치되지 않아 원격 실행은 건너뜁니다.")
    except subprocess.CalledProcessError:
        print("   ℹ️  워크플로우 실행 실패 (파일명이 다르거나 권한이 없을 수 있습니다).")

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 관리자 시작]\n")
    
    # 0. 파일 생성/업데이트 (설정 파일 등 배포)
    # files.json 파일이 있으면 실행됨
    manage_files("files.json")

    # 1. 신규 API 모듈 필요 시 생성 (예시: new-api-service라는 이름으로 Python 모듈 생성)
    # 필요 없다면 주석 처리
    # create_api_module("new-api-service", lang="python")

    # 2. 모델 다운로드
    download_models("models.json")
    
    # 3. 전체 모듈 설치 (새로 생성된 API 포함)
    install_modules(ROOT_DIR)

    # 4. Dependabot 체크 실행
    run_dependabot_check()
    
    print("\n✨ [완료] 모든 작업이 종료되었습니다.")
