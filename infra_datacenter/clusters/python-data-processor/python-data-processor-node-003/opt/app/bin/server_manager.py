import os
import subprocess
import json
import sys

# =========================================================
# 설정: 프로젝트 루트 경로
# =========================================================
ROOT_DIR = "."
FILES_MANIFEST = "files.json"

# =========================================================
# 1. 파일 대량 생성 및 업데이트 함수 (자동 생성 기능 추가)
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    """
    files.json을 읽어 파일들을 생성합니다.
    만약 files.json이 없다면, '기본 파일 목록'을 담은 파일을 자동으로 생성하고 실행합니다.
    """
    print(f"📝 [파일 관리] 파일 생성 작업을 시작합니다...")

    # 1-1. files.json이 없을 경우, 기본 템플릿으로 자동 생성
    if not os.path.exists(manifest_file):
        print(f"   ⚠️  {manifest_file}이 없습니다. 기본 설정으로 자동 생성합니다.")
        
        # [여기에 생성할 파일 목록을 정의하세요]
        default_files = {
            # 루트 공통 파일
            "./README.md": "# Omni System Project\n\n이 프로젝트는 `manage_setup.py`로 관리됩니다.",
            "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/",
            
            # 공통 설정 파일
            "./config/application-global.yml": "server:\n  port: 8080\n  env: dev",
            
            # 각 서비스별 기본 README 및 설정 (로그 기반 반영)
            "./services/omni-security-service/README.md": "# Security Service\n보안 관련 인증/인가 처리를 담당합니다.",
            "./services/omni-security-service/src/main/resources/application.yml": "spring:\n  application:\n    name: omni-security",

            "./services/omni-algo-service/README.md": "# Algo Service\n알고리즘 분석 및 처리를 담당합니다.",
            "./services/omni-cost-service/README.md": "# Cost Service\n비용 산정 및 결제 로직을 담당합니다.",
            "./services/omni-job-service/README.md": "# Job Service\n배치 작업 및 스케줄링을 담당합니다.",
            
            # Python 서비스용
            "./ai-model/requirements.txt": "numpy\npandas\nscikit-learn",
            "./ai-model/README.md": "# AI Model Server\nPython 기반 AI 모델 서빙"
        }
        
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(default_files, f, indent=2, ensure_ascii=False)
            print(f"   ✅ {manifest_file} 생성 완료.")
        except Exception as e:
            print(f"   ❌ {manifest_file} 생성 실패: {e}")
            return

    # 1-2. 파일 생성 실행 (Create or Update)
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            files_map = json.load(f)

        for file_path, content in files_map.items():
            # 절대 경로 변환 및 디렉토리 생성
            full_path = os.path.abspath(file_path)
            dir_name = os.path.dirname(full_path)
            
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"   mkdir: {dir_name}")
            
            # 파일 쓰기
            with open(full_path, 'w', encoding='utf-8') as dest:
                dest.write(content)
            
            print(f"   ✅ [파일 반영] {file_path}")
            
    except Exception as e:
        print(f"   ❌ 파일 처리 중 오류 발생: {e}")

# =========================================================
# 2. 신규 API 모듈 자동 생성 (스캐폴딩)
# =========================================================
def create_api_module(module_name, lang="python"):
    base_path = os.path.join(ROOT_DIR, "services", module_name)
    if os.path.exists(base_path):
        return # 이미 있으면 조용히 스킵

    print(f"🏗️  [API 모듈 생성] {module_name} ({lang}) 생성 중...")
    os.makedirs(base_path, exist_ok=True)

    if lang == "python":
        with open(os.path.join(base_path, "requirements.txt"), "w") as f:
            f.write("fastapi\nuvicorn\n")
        with open(os.path.join(base_path, "main.py"), "w") as f:
            f.write("from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {'msg': 'ok'}")
            
    elif lang == "java":
        src_path = os.path.join(base_path, "src", "main", "java", "com", "omni", module_name.replace("-", ""))
        os.makedirs(src_path, exist_ok=True)
        with open(os.path.join(base_path, "pom.xml"), "w") as f:
            f.write(f'<project><groupId>com.omni</groupId><artifactId>{module_name}</artifactId><version>1.0.0</version></project>')
    
    print(f"   ✅ [모듈 생성] {base_path}")

# =========================================================
# 3. 모듈 대량 설치 함수 (Java/Maven & Python/Pip)
# =========================================================
def install_modules(root_path):
    print(f"🔄 [모듈 설치] {root_path} 내부의 의존성을 스캔합니다...")
    
    for dirpath, _, filenames in os.walk(root_path):
        # 3-1. Python
        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            print(f"   🐍 Python Install: {req_path}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path], stdout=subprocess.DEVNULL)
        
        # 3-2. Java
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Build: {pom_path}")
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            try:
                # -q 옵션으로 로그 줄임
                subprocess.check_call([mvn_cmd, "-q", "clean", "install", "-f", pom_path, "-DskipTests"], shell=True)
            except subprocess.CalledProcessError:
                print(f"   ⚠️  빌드 실패: {pom_path} (패스함)")
            except FileNotFoundError:
                print("   ⚠️  Maven이 설치되어 있지 않습니다.")

# =========================================================
# 4. 모델 파일 대량 다운로드 함수
# =========================================================
def download_models(manifest_file="models.json"):
    if not os.path.exists(manifest_file):
        # 모델 정의 파일이 없으면 더미 생성
        with open(manifest_file, 'w') as f:
            json.dump({"default-model": {"url": "https://example.com/dummy.bin", "dest": "./ai-model"}}, f)
        print(f"ℹ️  [모델 설정] {manifest_file} 생성됨 (URL 수정 필요).")
        return

    print(f"⬇️  [모델 다운로드] {manifest_file} 확인 중...")
    with open(manifest_file, 'r', encoding='utf-8') as f:
        models = json.load(f)

    for name, info in models.items():
        url = info.get('url', '')
        dest_folder = info.get('dest', '.')
        if "example.com" in url: continue # 더미 URL 스킵

        dest_path = os.path.join(dest_folder, url.split('/')[-1])
        if not os.path.exists(dest_folder): os.makedirs(dest_folder)
        
        if not os.path.exists(dest_path):
            print(f"   📥 Downloading {name}...")
            try:
                subprocess.check_call(["curl", "-L", "-o", dest_path, url], stderr=subprocess.DEVNULL)
            except:
                print("   ⚠️  Download failed (Check curl or URL)")

# =========================================================
# 5. Dependabot 체크
# =========================================================
def run_dependabot_check():
    print("🛡️  [Dependabot] 의존성 체크 중...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], check=False)
        # GitHub Action 트리거 (실패해도 진행)
        subprocess.run(["gh", "workflow", "run", "ci-check.yml"], stderr=subprocess.DEVNULL, check=False)
    except:
        pass

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 관리자 시작]\n")
    
    # 1. 파일 대량 생성 (없으면 자동 생성 후 반영)
    manage_files(FILES_MANIFEST)

    # 2. 신규 모듈 스캐폴딩 (필요 시 주석 해제하여 사용)
    # create_api_module("omni-new-service", lang="java")

    # 3. 모델 다운로드
    download_models("models.json")
    
    # 4. 의존성 설치
    install_modules(ROOT_DIR)

    # 5. 보안 점검
    run_dependabot_check()
    
    print("\n✨ [완료] 모든 시스템 설정이 최신화되었습니다.")
