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
# [Helper] 서비스 설정 및 리소스 할당 정의
# =========================================================
# 각 서비스별로 포트, 메모리 할당량(Docker Limit), JVM 힙 사이즈, CPU 제한을 정의합니다.
MICROSERVICES_CONFIG = [
    {"name": "omni-gateway",       "port": 8080, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "API Gateway"},
    {"name": "omni-auth-service",  "port": 8081, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "Authentication"},
    {"name": "omni-cost-service",  "port": 8082, "mem_limit": "1024m", "jvm_heap": "800m", "cpu": "1.0", "desc": "Cost Calculation (Core)"},
    {"name": "omni-batch-service", "port": 8083, "mem_limit": "2048m", "jvm_heap": "1600m", "cpu": "1.5", "desc": "High Load Batch"},
    {"name": "omni-log-service",   "port": 8084, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "Log Aggregator"},
    {"name": "omni-payment-service","port": 8085, "mem_limit": "768m", "jvm_heap": "600m", "cpu": "0.8", "desc": "Payment Gateway"}
]

# =========================================================
# [Helper] 서비스 템플릿 생성기 (리소스 & 컴파일 타겟 반영)
# =========================================================
def generate_java_service(config):
    name = config["name"]
    port = config["port"]
    desc = config["desc"]
    jvm_heap = config["jvm_heap"]
    
    base_dir = f"./services/{name}"
    safe_name = name.replace("-", "")
    
    return {
        # 1. POM.XML (컴파일 타겟 및 리소스 설정 완비)
        f"{base_dir}/pom.xml": f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.koreatest12</groupId>
  <artifactId>{name}</artifactId>
  <version>1.0.0</version>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.14</version>
    <relativePath/> 
  </parent>
  
  <properties>
    <java.version>17</java.version>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
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
    <dependency>
      <groupId>org.projectlombok</groupId>
      <artifactId>lombok</artifactId>
      <optional>true</optional>
    </dependency>
  </dependencies>
  
  <build>
    <resources>
      <resource>
        <directory>src/main/resources</directory>
        <filtering>true</filtering>
      </resource>
    </resources>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.10.1</version>
        <configuration>
          <source>17</source>
          <target>17</target>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
</project>""",

        # 2. Dockerfile (JVM 메모리 옵션 주입 - 용량 분할 핵심)
        f"{base_dir}/Dockerfile": f"""FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{name}-1.0.0.jar app.jar
# [Resource Partitioning] JVM Heap Size set to {jvm_heap}
ENTRYPOINT ["java", "-Xms{jvm_heap}", "-Xmx{jvm_heap}", "-jar", "app.jar"]
EXPOSE {port}
""",

        # 3. Application.yml (프로파일 및 로그 설정)
        f"{base_dir}/src/main/resources/application.yml": f"""server:
  port: {port}
spring:
  application:
    name: {name}
  profiles:
    active: dev
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
logging:
  level:
    root: INFO
    com.koreatest12: DEBUG
""",

        # 4. Banner.txt (리소스 파일 예시)
        f"{base_dir}/src/main/resources/banner.txt": f"""
=========================================================
  SERVICE: {name}
  PORT:    {port}
  MEMORY:  Max {jvm_heap}
=========================================================
""",

        # 5. Java Code
        f"{base_dir}/src/main/java/com/koreatest12/{safe_name}/App.java": f"""package com.koreatest12.{safe_name};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.lang.management.ManagementFactory;

@SpringBootApplication
@RestController
public class App {{
    public static void main(String[] args) {{
        SpringApplication.run(App.class, args);
    }}

    @GetMapping("/")
    public String status() {{
        long maxMemory = Runtime.getRuntime().maxMemory() / (1024 * 1024);
        return String.format("[{name}] OK | Port: {port} | Max Heap: %d MB", maxMemory);
    }}
}}""",
        f"{base_dir}/README.md": f"# {name}\n\n{desc}\n\n## Resources\n- Docker Limit: {config['mem_limit']}\n- JVM Heap: {config['jvm_heap']}"
    }

# =========================================================
# 1. 파일 대량 생성 및 업데이트 함수
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    print(f"📝 [파일 관리] 서비스별 용량 분할 및 리소스 파일 생성을 시작합니다...")

    default_files = {
        "./README.md": "# Omni Cost System (MSA Resource Partitioned)\n\n각 서비스별로 메모리와 CPU가 격리된 환경입니다.",
        "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/\n.DS_Store\n.mvn/\n*.iml",
        
        # [Fix] Dependabot
        "./api-server/pom.xml": '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>com.kt</groupId><artifactId>api-server</artifactId><version>1.0.0</version><build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build></project>',
        
        # Python AI Service
        "./ai-model/requirements.txt": "fastapi==0.95.0\nuvicorn==0.21.1\nnumpy==1.24.3\npandas==2.0.3",
        "./ai-model/main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {'msg': 'AI Model', 'resource': 'Shared'}",
        "./ai-model/Dockerfile": "FROM python:3.9-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
    }

    # 1. 서비스별 파일 생성
    docker_services_yml = ""
    
    for config in MICROSERVICES_CONFIG:
        # Java 파일 생성
        files = generate_java_service(config)
        default_files.update(files)
        
        # Docker Compose (Resource Limits 추가)
        docker_services_yml += f"""
  {config['name']}:
    build: ./services/{config['name']}
    ports:
      - "{config['port']}:{config['port']}"
    deploy:
      resources:
        limits:
          cpus: '{config['cpu']}'
          memory: {config['mem_limit']}
    networks:
      - omni-net
    environment:
      - JAVA_OPTS=-Xmx{config['jvm_heap']}
"""

    # Python Service Compose (Add to Docker)
    docker_services_yml += """
  ai-model:
    build: ./ai-model
    ports:
      - "5000:5000"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512m
    networks:
      - omni-net
"""

    default_files["./docker-compose.yml"] = f"""version: '3.8'
services:{docker_services_yml}
networks:
  omni-net:
    driver: bridge
"""

    # 2. JSON 생성 및 쓰기
    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(default_files, f, indent=2, ensure_ascii=False)
            
        # 파일 실제 생성
        with open(manifest_file, 'r', encoding='utf-8') as f:
            files_map = json.load(f)
            
        for file_path, content in files_map.items():
            full_path = os.path.abspath(file_path)
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            with open(full_path, 'w', encoding='utf-8') as dest:
                dest.write(content)
                
        print(f"   ✅ [설정 완료] 서비스 {len(MICROSERVICES_CONFIG)}개 리소스 할당 완료.")
            
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")

# =========================================================
# 2. 모듈 대량 빌드 (컴파일 리소스 포함)
# =========================================================
def install_modules(root_path):
    print(f"🔄 [대량 컴파일] 리소스 및 타겟 빌드 시작...")
    
    for dirpath, _, filenames in os.walk(root_path):
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Build: {pom_path}")
            
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            # clean package: 컴파일 -> 테스트(스킵) -> 리소스 복사 -> JAR 생성
            cmd = f"{mvn_cmd} clean package -f {pom_path} -DskipTests -fn"
            
            try:
                subprocess.call(cmd, shell=True)
            except: pass
            
        if "requirements.txt" in filenames:
            # Python 설치는 생략하거나 필요시 주석 해제
            # cmd = f"{sys.executable} -m pip install -r {os.path.join(dirpath, 'requirements.txt')}"
            # subprocess.call(cmd, shell=True)
            pass

# =========================================================
# 3. 모델 다운로드
# =========================================================
def download_models():
    if not os.path.exists("models.json"):
        with open("models.json", 'w') as f: json.dump({}, f)

# =========================================================
# 메인 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 [시스템 관리자] - Service Resource Partitioning & Bulk Update\n")
    
    manage_files(FILES_MANIFEST)
    download_models()
    install_modules(ROOT_DIR)
    
    print("\n✨ [완료] 각 서비스별 메모리/CPU 할당 및 파일 생성이 완료되었습니다.")
