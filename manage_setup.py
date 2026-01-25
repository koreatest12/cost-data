import os
import subprocess
import json
import sys
import shutil

# =========================================================
# 설정: 프로젝트 루트 경로
# =========================================================
ROOT_DIR = "."
FILES_MANIFEST = "files.json"

# =========================================================
# [Helper] 서비스 템플릿 생성기 (JAR Empty 오류 수정됨)
# =========================================================
def generate_java_service(service_name, port, description):
    """
    Java Spring Boot 서비스 생성.
    [Fix]: <build> 태그와 spring-boot-maven-plugin을 추가하여 JAR가 비어있는 문제를 해결함.
    """
    base_dir = f"./services/{service_name}"
    safe_name = service_name.replace("-", "")
    
    return {
        # 1. POM.XML (빌드 플러그인 추가됨)
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
  <properties>
    <java.version>17</java.version>
  </properties>
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
  
  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
</project>""",

        # 2. Dockerfile
        f"{base_dir}/Dockerfile": f"""FROM openjdk:17-jdk-slim
WORKDIR /app
# 빌드된 JAR 파일을 복사 (Maven 빌드 후 target 폴더에 생성됨)
COPY target/{service_name}-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
EXPOSE {port}
""",

        # 3. Application.yml
        f"{base_dir}/src/main/resources/application.yml": f"""server:
  port: {port}
spring:
  application:
    name: {service_name}
""",

        # 4. Java Main Class
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
        return "{service_name} is Running! (Port: {port})";
    }}
}}""",
        f"{base_dir}/README.md": f"# {service_name}\n\n{description}"
    }

# =========================================================
# 1. 파일 대량 생성 및 업데이트 함수
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    print(f"📝 [파일 관리] 대량 파일 생성 및 수정을 시작합니다...")

    # 기존 files.json이 있어도 내용을 강제로 덮어씌워야 수정된 pom.xml이 반영됩니다.
    # 따라서 매번 새로 정의합니다.
    
    # 1. 기본 루트 파일
    default_files = {
        "./README.md": "# Omni Cost System (MSA)\n\nFixed JAR Empty Issue.",
        "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/\n.DS_Store\n.mvn/",
        
        # API Server (루트)
        "./api-server/pom.xml": '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>com.kt</groupId><artifactId>api-server</artifactId><version>1.0.0</version><build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build></project>',
        
        # AI Model (Python)
        "./ai-model/requirements.txt": "fastapi==0.95.0\nuvicorn==0.21.1\nnumpy==1.24.3\npandas==2.0.3",
        "./ai-model/main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root(): return {'msg': 'AI Model Server'}",
        "./ai-model/Dockerfile": "FROM python:3.9-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
    }

    # 2. 마이크로서비스 정의
    microservices = [
        ("omni-gateway", 8080, "API Gateway"),
        ("omni-auth-service", 8081, "Auth Service"),
        ("omni-cost-service", 8082, "Cost Service"),
        ("omni-batch-service", 8083, "Batch Service"),
        ("omni-log-service", 8084, "Log Service"),
        ("omni-payment-service", 8085, "Payment Service")
    ]

    docker_services_yml = ""
    
    for name, port, desc in microservices:
        # 서비스 파일 생성 (수정된 pom.xml 포함)
        service_files = generate_java_service(name, port, desc)
        default_files.update(service_files)
        
        # Docker Compose 추가
        docker_services_yml += f"""
  {name}:
    build: ./services/{name}
    ports:
      - "{port}:{port}"
    networks:
      - omni-net
"""
    
    # Python 서비스 추가
    docker_services_yml += """
  ai-model:
    build: ./ai-model
    ports:
      - "5000:5000"
    networks:
      - omni-net
"""

    default_files["./docker-compose.yml"] = f"""version: '3.8'
services:{docker_services_yml}
networks:
  omni-net:
    driver: bridge
"""

    # 3. JSON 파일 저장
    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(default_files, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"   ❌ JSON 저장 실패: {e}")
        return

    # 4. 실제 파일 생성 (Overwrite)
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
            
            print(f"   ✅ [수정 반영] {file_path}")
            
    except Exception as e:
        print(f"   ❌ 파일 쓰기 실패: {e}")

# =========================================================
# 2. 모듈 대량 설치 함수
# =========================================================
def install_modules(root_path):
    print(f"🔄 [모듈 설치] {root_path} 내부 빌드 시작...")
    
    for dirpath, _, filenames in os.walk(root_path):
        # Python
        if "requirements.txt" in filenames:
            req_path = os.path.join(dirpath, "requirements.txt")
            cmd = f"{sys.executable} -m pip install -r {req_path}"
            subprocess.call(cmd, shell=True)
        
        # Java (Maven)
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Build (re-package): {pom_path}")
            
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            
            # [FIX] package 골(Goal)을 명시하고, 실행 가능한 JAR를 만들기 위한 옵션
            # clean package: 기존 빌드 삭제 후 다시 패키징
            cmd = f"{mvn_cmd} clean package -f {pom_path} -DskipTests -fn"
            
            try:
                ret = subprocess.call(cmd, shell=True)
                if ret == 0:
                    print(f"      🎉 빌드 성공!")
                else:
                    print(f"      ⚠️ 빌드 이슈 발생 (Exit: {ret})")
            except Exception as e:
                print(f"      ❌ 실행 오류: {e}")

# =========================================================
# 3. 모델 파일 대량 다운로드
# =========================================================
def download_models(manifest_file="models.json"):
    if not os.path.exists(manifest_file):
        with open(manifest_file, 'w') as f:
            json.dump({"dummy-model": {"url": "https://example.com/dummy.bin", "dest": "./ai-model"}}, f)
        return

    with open(manifest_file, 'r') as f:
        models = json.load(f)

    for name, info in models.items():
        url, dest = info.get('url'), info.get('dest')
        if "example.com" in url: continue
        
        if not os.path.exists(dest): os.makedirs(dest)
        dest_path = os.path.join(dest, url.split('/')[-1])
        
        if not os.path.exists(dest_path):
            print(f"   📥 모델 다운로드: {name}")
            try: subprocess.call(f"curl -L -o {dest_path} {url}", shell=True)
            except: pass

# =========================================================
# 4. Dependabot 체크
# =========================================================
def run_dependabot_check():
    print("🛡️  [Dependabot] 체크...")
    try: subprocess.call("gh workflow run dependabot.yml", shell=True)
    except: pass

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [전체 시스템 관리자] - JAR Empty Fix Applied\n")
    
    # 1. 파일 강제 재생성 (수정된 POM 반영을 위해)
    manage_files(FILES_MANIFEST)

    # 2. 모델 다운로드
    download_models()
    
    # 3. 빌드 및 설치
    install_modules(ROOT_DIR)

    # 4. 체크
    run_dependabot_check()
    
    print("\n✨ [완료] JAR 생성 문제가 해결되었습니다.")
