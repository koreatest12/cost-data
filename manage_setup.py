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
# [Helper] 서비스 템플릿 생성기 (Java/Spring Boot)
# =========================================================
def generate_java_service(service_name, port, description):
    """
    Java Spring Boot 서비스의 기본 파일 세트(pom.xml, Dockerfile, Java Code, YML)를 생성하여 반환합니다.
    """
    base_dir = f"./services/{service_name}"
    # 특수문자 제거 후 패키지명 생성
    safe_name = service_name.replace("-", "")
    
    return {
        f"{base_dir}/pom.xml": f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.koreatest12</groupId>
  <artifactId>{service_name}</artifactId>
  <version>1.0.0</version>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.14</version>
    <relativePath/> 
  </parent>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
  </dependencies>
</project>""",

        f"{base_dir}/Dockerfile": f"""# Java Service Dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{service_name}-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
EXPOSE {port}
""",

        f"{base_dir}/src/main/resources/application.yml": f"""server:
  port: {port}
spring:
  application:
    name: {service_name}
""",
        f"{base_dir}/src/main/java/com/koreatest12/{safe_name}/App.java": f"""package com.koreatest12.{safe_name};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class App {{
    public static void main(String[] args) {{
        SpringApplication.run(App.class, args);
    }}

    @GetMapping("/")
    public String home() {{
        return "{service_name} is running on port {port}";
    }}
}}""",
        f"{base_dir}/README.md": f"# {service_name}\n\n{description}\n- Port: {port}"
    }

# =========================================================
# 1. 파일 대량 생성 및 업데이트 함수 (Docker & Bulk API 반영)
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    print(f"📝 [파일 관리] 대량 파일 생성 작업을 시작합니다...")

    # 1-1. files.json이 없을 경우, 대량의 기본 파일 생성
    if not os.path.exists(manifest_file):
        print(f"   ⚠️  {manifest_file} 없음. Docker 및 MSA 환경 파일을 자동 생성합니다.")
        
        # 1. 기본 루트 파일 정의
        default_files = {
            "./README.md": "# Omni Cost System (MSA)\n\n이 프로젝트는 `manage_setup.py`로 자동 생성된 MSA 환경입니다.",
            "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/\n.DS_Store\n.mvn/",
            
            # [Fix] Dependabot 에러 방지용 (루트 레벨 api-server)
            "./api-server/pom.xml": '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>com.kt</groupId><artifactId>api-server</artifactId><version>1.0.0</version></project>',
            "./api-server/Dockerfile": "FROM openjdk:17-slim\nCOPY . /app\nWORKDIR /app",
            
            # Python AI 서비스
            "./ai-model/requirements.txt": "fastapi==0.95.0\nuvicorn==0.21.1\nnumpy==1.24.3\npandas==2.0.3",
            "./ai-model/main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root(): return {'msg': 'AI Model Server'}",
            "./ai-model/Dockerfile": "FROM python:3.9-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
        }

        # 2. 대량의 마이크로서비스 정의 (이름, 포트, 설명)
        microservices = [
            ("omni-gateway", 8080, "API Gateway 서버"),
            ("omni-auth-service", 8081, "인증 및 인가 서비스"),
            ("omni-cost-service", 8082, "비용 계산 핵심 서비스"),
            ("omni-batch-service", 8083, "대용량 배치 처리 서비스"),
            ("omni-log-service", 8084, "통합 로그 수집 서비스"),
            ("omni-payment-service", 8085, "결제 연동 서비스")
        ]

        # 3. 서비스 파일 자동 생성 및 Docker Compose 구성
        docker_compose_services = ""
        
        for name, port, desc in microservices:
            # 서비스 파일 생성
            service_files = generate_java_service(name, port, desc)
            default_files.update(service_files)
            
            # Docker Compose 내용 추가
            docker_compose_services += f"""
  {name}:
    build: ./services/{name}
    ports:
      - "{port}:{port}"
    networks:
      - omni-net
"""
        # Python 서비스 Docker Compose 추가
        docker_compose_services += """
  ai-model:
    build: ./ai-model
    ports:
      - "5000:5000"
    networks:
      - omni-net
"""

        # 4. docker-compose.yml 최종 완성
        default_files["./docker-compose.yml"] = f"""version: '3.8'
services:{docker_compose_services}
networks:
  omni-net:
    driver: bridge
"""

        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(default_files, f, indent=2, ensure_ascii=False)
            print(f"   ✅ {manifest_file} 생성 완료 (Docker, MSA 포함).")
        except Exception as e:
            print(f"   ❌ {manifest_file} 생성 실패: {e}")
            return

    # 1-2. 파일 생성 실행 (Create or Update)
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            files_map = json.load(f)

        for file_path, content in files_map.items():
            full_path = os.path.abspath(file_path)
            dir_name = os.path.dirname(full_path)
            
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
            
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
# 4. Dependabot 체크
# =========================================================
def run_dependabot_check():
    print("🛡️  [Dependabot] 상태 점검 중...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], check=False)
    except: pass
    print("   ☁️  GitHub Actions 트리거 시도...")
    try:
        subprocess.run(["gh", "workflow", "run", "dependabot.yml"], stderr=subprocess.DEVNULL, check=False)
    except FileNotFoundError:
        print("   ℹ️  'gh' CLI 미설치로 건너뜀.")

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 관리자 시작] - Docker & MSA Edition\n")
    
    # 1. 파일 자동 생성 (Docker, MSA 서비스 포함)
    manage_files(FILES_MANIFEST)

    # 2. 모델 다운로드
    download_models("models.json")
    
    # 3. 의존성 설치
    install_modules(ROOT_DIR)

    # 4. Dependabot 체크
    run_dependabot_check()
    
    print("\n✨ [완료] 시스템 복구 및 설정이 완료되었습니다.")
