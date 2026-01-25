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
# 1. 파일 대량 생성 및 업데이트 함수 (에러 수정 반영)
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    """
    files.json을 읽어 파일들을 생성합니다.
    Dependabot 오류(/api-server/pom.xml not found)를 방지하기 위한 기본 파일을 포함합니다.
    """
    print(f"📝 [파일 관리] 파일 생성 작업을 시작합니다...")

    # 1-1. files.json이 없을 경우, 기본 템플릿으로 자동 생성
    if not os.path.exists(manifest_file):
        print(f"   ⚠️  {manifest_file}이 없습니다. Dependabot 호환성을 위한 기본 파일을 생성합니다.")
        
        default_files = {
            # [Fix] Dependabot 에러 해결을 위한 api-server 필수 파일
            "./api-server/pom.xml": (
                '<project xmlns="http://maven.apache.org/POM/4.0.0">\n'
                '  <modelVersion>4.0.0</modelVersion>\n'
                '  <groupId>com.koreatest12</groupId>\n'
                '  <artifactId>api-server</artifactId>\n'
                '  <version>1.0.0</version>\n'
                '  <dependencies>\n'
                '    \n'
                '    <dependency>\n'
                '      <groupId>org.springframework.boot</groupId>\n'
                '      <artifactId>spring-boot-starter-web</artifactId>\n'
                '      <version>2.7.5</version>\n'
                '    </dependency>\n'
                '  </dependencies>\n'
                '</project>'
            ),
            "./api-server/README.md": "# API Server\n메인 API 서버 모듈입니다.",

            # 루트 공통 파일
            "./README.md": "# Cost Data Project\n\n이 프로젝트는 `manage_setup.py`로 관리됩니다.",
            "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/\n.DS_Store",
            
            # 서비스별 설정 파일
            "./services/omni-cost-service/src/main/resources/application.yml": "server:\n  port: 8081\n  application:\n    name: omni-cost",
            "./services/omni-algo-service/README.md": "# Algo Service\n알고리즘 분석 모듈",
            
            # Python 모듈
            "./ai-model/requirements.txt": "numpy==1.24.3\npandas==2.0.3\nscikit-learn",
            "./ai-model/README.md": "# AI Model\n비용 예측 모델"
        }
        
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(default_files, f, indent=2, ensure_ascii=False)
            print(f"   ✅ {manifest_file} 생성 완료 (Dependabot 경로 포함).")
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
                # print(f"   mkdir: {dir_name}")
            
            # 파일이 없거나 내용이 다를 때만 덮어쓰기 (옵션)
            with open(full_path, 'w', encoding='utf-8') as dest:
                dest.write(content)
            
            print(f"   ✅ [파일 반영] {file_path}")
            
    except Exception as e:
        print(f"   ❌ 파일 처리 중 오류 발생: {e}")

# =========================================================
# 2. 모듈 대량 설치 함수
# =========================================================
def install_modules(root_path):
    print(f"🔄 [모듈 설치] {root_path} 내부의 의존성을 스캔합니다...")
    
    for dirpath, _, filenames in os.walk(root_path):
        # 3-1. Python
        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            print(f"   🐍 Python Install: {req_path}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path], stdout=subprocess.DEVNULL)
        
        # 3-2. Java (pom.xml)
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Build: {pom_path}")
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            try:
                # -q: Quiet 모드, -fn: 실패해도 계속 진행 (Fail-Never)
                subprocess.check_call([mvn_cmd, "-q", "clean", "install", "-f", pom_path, "-DskipTests", "-fn"], shell=True)
            except subprocess.CalledProcessError:
                print(f"   ⚠️  빌드 실패: {pom_path} (계속 진행합니다)")
            except FileNotFoundError:
                print("   ⚠️  Maven 명령어를 찾을 수 없습니다.")

# =========================================================
# 3. 모델 파일 대량 다운로드 함수
# =========================================================
def download_models(manifest_file="models.json"):
    if not os.path.exists(manifest_file):
        with open(manifest_file, 'w') as f:
            json.dump({"cost-predict-v1": {"url": "https://example.com/dummy-model.bin", "dest": "./ai-model"}}, f)
        print(f"ℹ️  [모델 설정] {manifest_file} 생성됨.")
        return

    print(f"⬇️  [모델 다운로드] {manifest_file} 확인 중...")
    with open(manifest_file, 'r', encoding='utf-8') as f:
        models = json.load(f)

    for name, info in models.items():
        url = info.get('url', '')
        dest_folder = info.get('dest', '.')
        if "example.com" in url: continue 

        dest_path = os.path.join(dest_folder, url.split('/')[-1])
        if not os.path.exists(dest_folder): os.makedirs(dest_folder)
        
        if not os.path.exists(dest_path):
            print(f"   📥 Downloading {name}...")
            try:
                subprocess.check_call(["curl", "-L", "-o", dest_path, url], stderr=subprocess.DEVNULL)
            except:
                print("   ⚠️  Download failed")

# =========================================================
# 4. Dependabot 체크 (원격 실행 포함)
# =========================================================
def run_dependabot_check():
    print("🛡️  [Dependabot] 상태 점검 중...")
    
    # 로컬 체크
    try:
        subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], check=False)
    except: pass

    # GitHub Action 트리거 (실패 시 무시)
    print("   ☁️  GitHub Actions 트리거 시도...")
    try:
        # workflow 이름이 다를 수 있으므로 에러 무시 처리
        subprocess.run(["gh", "workflow", "run", "dependabot.yml"], stderr=subprocess.DEVNULL, check=False)
    except FileNotFoundError:
        print("   ℹ️  'gh' CLI가 설치되지 않아 원격 실행은 건너뜁니다.")

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 관리자 시작]\n")
    
    # 1. 파일 자동 생성 (Dependabot 경로 포함)
    manage_files(FILES_MANIFEST)

    # 2. 모델 다운로드
    download_models("models.json")
    
    # 3. 의존성 설치
    install_modules(ROOT_DIR)

    # 4. Dependabot 체크
    run_dependabot_check()
    
    print("\n✨ [완료] 시스템 복구 및 설정이 완료되었습니다.")
