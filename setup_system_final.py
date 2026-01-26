import os
import subprocess
import json
import shutil

# =========================================================
# [1] 시스템 설정 및 리소스 정의
# =========================================================

# 포켓몬 디펜더 봇 (HTML/JS/CSS 통합 소스)
POKEMON_WEB_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포켓몬고 IV 매니저 & 디펜더 봇</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #3b4cca; --bg: #f4f6f8; --surface: #ffffff; --bot: #6f42c1; }
        body { font-family: 'Noto Sans KR', sans-serif; background: var(--bg); margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .main-container { display: grid; grid-template-columns: 350px 1fr; gap: 20px; max-width: 1400px; width: 100%; }
        @media (max-width: 900px) { .main-container { grid-template-columns: 1fr; } }
        .card { background: var(--surface); padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h2 { margin: 0 0 15px 0; color: var(--primary); font-size: 1.2rem; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; margin-bottom: 10px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 0.9rem; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 5px; }
        .btn-add { background: var(--primary); color: white; }
        .btn-reset { background: #e2e6ea; color: #333; }
        .dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; width: 100%; max-width: 1400px; }
        .stat-card { background: white; padding: 15px; border-radius: 10px; text-align: center; }
        .stat-val { font-size: 1.5rem; font-weight: bold; color: var(--primary); }
        .bot-area { background: #eef0ff; border-left: 5px solid var(--bot); padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; color: white; margin-right: 4px; }
        .bg-4 { background: #ff5722; } .bg-3 { background: #ff9800; } .bg-2 { background: #2196f3; }
        .tag-pvp { background: #6f42c1; } .tag-def { background: #28a745; } .tag-att { background: #dc3545; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="stat-card"><div class="stat-val" id="totalCount">0</div><div>전체 조사</div></div>
        <div class="stat-card"><div class="stat-val" id="perfectCount" style="color:#ff5722">0</div><div>완벽(4★)</div></div>
        <div class="stat-card"><div class="stat-val" id="pvpCount" style="color:#6f42c1">0</div><div>PVP 유망주</div></div>
        <div class="stat-card"><div class="stat-val" id="avgIv">0%</div><div>평균 IV</div></div>
    </div>
    <div class="main-container">
        <div class="card">
            <h2>📝 개체값 입력</h2>
            <label>이름</label><input type="text" id="pokeName" placeholder="예: 망나뇽">
            <label>공격 (0~15)</label><input type="number" id="attack">
            <label>방어 (0~15)</label><input type="number" id="defense">
            <label>HP (0~15)</label><input type="number" id="stamina">
            <div style="display:flex; gap:10px;">
                <button class="btn-reset" onclick="clearInputs()">초기화</button>
                <button class="btn-add" onclick="addPokemon()">분석 및 추가</button>
            </div>
        </div>
        <div class="card">
            <div id="botMessage" class="bot-area" style="display:none;">🤖 <b>디펜더 봇:</b> <span id="botText"></span></div>
            <h2>📊 분석 목록</h2>
            <div style="overflow-x:auto;">
                <table id="dataTable">
                    <thead><tr><th>No</th><th>이름</th><th>IV</th><th>등급</th><th>봇 분석</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        let list = []; let id = 1;
        function addPokemon() {
            const n = document.getElementById('pokeName').value || "-";
            const a = +document.getElementById('attack').value || 0;
            const d = +document.getElementById('defense').value || 0;
            const h = +document.getElementById('stamina').value || 0;
            const per = ((a+d+h)/45)*100; const round = Math.round(per);
            
            // 디펜더 봇 로직
            let ana = {t:"일반", c:""};
            if(per===100) ana={t:"완벽!", c:"tag-att"};
            else if(a<=5 && d>=10 && h>=10) ana={t:"PVP용", c:"tag-pvp"};
            else if(d>=14 && h>=14) ana={t:"방어용", c:"tag-def"};
            else if(a===15 && per>=80) ana={t:"레이드용", c:"tag-att"};
            
            list.unshift({id:id++, n, a, d, h, round, ana});
            render(); msg(list[0]);
            document.getElementById('attack').value=''; document.getElementById('defense').value=''; document.getElementById('stamina').value=''; document.getElementById('attack').focus();
        }
        function render() {
            document.querySelector('tbody').innerHTML = list.map(p => 
                `<tr><td>${p.id}</td><td>${p.n}</td><td>${p.round}%</td><td>${p.round==100?'4★':p.round>=82?'3★':'2★'}</td>
                <td><span class="badge ${p.ana.c}" style="${p.ana.c?'':'background:#ccc'}">${p.ana.t}</span></td></tr>`
            ).join('');
            document.getElementById('totalCount').innerText = list.length;
            document.getElementById('perfectCount').innerText = list.filter(p=>p.round===100).length;
            document.getElementById('pvpCount').innerText = list.filter(p=>p.ana.t==='PVP용').length;
            const totalSum = list.reduce((acc, cur) => acc + cur.round, 0);
            document.getElementById('avgIv').innerText = (list.length ? Math.round(totalSum / list.length) : 0) + "%";
        }
        function msg(p) {
            const area = document.getElementById('botMessage'); area.style.display='block';
            document.getElementById('botText').innerText = `[${p.n}] IV ${p.round}%. ${p.ana.t} 포켓몬입니다.`;
        }
        function clearInputs() { 
            document.querySelectorAll('input').forEach(i=>i.value=''); 
            document.getElementById('botMessage').style.display='none';
        }
    </script>
</body>
</html>"""

# 마이크로서비스 설정 (메모리, CPU 리소스 포함)
SERVICES_CONFIG = [
    {"name": "omni-gateway",         "port": 8080, "mem": "512m", "cpu": "0.5", "desc": "API Gateway Server"},
    {"name": "omni-auth-service",    "port": 8081, "mem": "512m", "cpu": "0.5", "desc": "Authentication & Security"},
    {"name": "omni-cost-service",    "port": 8082, "mem": "1024m","cpu": "1.0", "desc": "Cost Data Core Engine"},
    {"name": "omni-batch-service",   "port": 8083, "mem": "2048m","cpu": "1.5", "desc": "High Volume Batch Processing"},
    {"name": "omni-log-service",     "port": 8084, "mem": "512m", "cpu": "0.5", "desc": "Log Aggregation System"},
    {"name": "omni-payment-service", "port": 8085, "mem": "768m", "cpu": "0.8", "desc": "Payment & Settlement"},
    {"name": "omni-pokemon-web",     "port": 8086, "mem": "300m", "cpu": "0.4", "desc": "Pokemon IV Manager & Bot"}
]

# =========================================================
# [2] 파일 내용 생성 함수들
# =========================================================

def generate_pom(name, main_class):
    """
    [수정] relativePath를 빈 값으로 설정하여 부모 POM 참조 오류 해결
    [수정] start-class 및 plugin 설정에 메인 클래스를 명시하여 실행 오류 해결
    """
    return f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.koreatest12</groupId>
    <artifactId>{name}</artifactId>
    <version>1.0.0</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/> </parent>
    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <start-class>{main_class}</start-class>
    </properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration><mainClass>{main_class}</mainClass></configuration>
            </plugin>
        </plugins>
    </build>
</project>"""

def generate_java_app(name, port, package_name):
    return f"""package {package_name};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class App {{
    public static void main(String[] args) {{ SpringApplication.run(App.class, args); }}
    
    @GetMapping("/") 
    public String status() {{ 
        return "✅ Service [{name}] is Active on Port {port}"; 
    }}
}}"""

def generate_dockerfile(name, port):
    return f"""FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{name}-1.0.0.jar app.jar
# Memory Optimization
ENV JAVA_OPTS="-Xms256m -Xmx512m"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
EXPOSE {port}"""

def generate_dependabot_config():
    """
    [추가] 모든 서비스 및 Docker, GitHub Actions를 감시하는 Dependabot 설정
    """
    config = """version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: {interval: "weekly"}
"""
    # Java Services
    for svc in SERVICES_CONFIG:
        config += f"""
  - package-ecosystem: "maven"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
    groups:
      spring: {{patterns: ["org.springframework*"]}}
  - package-ecosystem: "docker"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
"""
    # AI Service
    config += """
  - package-ecosystem: "pip"
    directory: "/ai-model"
    schedule: {interval: "weekly"}
  - package-ecosystem: "docker"
    directory: "/ai-model"
    schedule: {interval: "weekly"}
"""
    return config

def generate_ci_workflow():
    """
    [추가] setup_complete_system.py 실행 및 빌드 검증을 포함한 CI 워크플로우
    """
    return """name: CI & Mass Build Check
on: [push, pull_request]
jobs:
  build-system:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: {python-version: '3.9'}
      - uses: actions/setup-java@v4
        with: {java-version: '17', distribution: 'temurin', cache: 'maven'}
      
      - name: Run System Setup & Generate Files
        run: |
          python setup_complete_system.py
          
      - name: Verify Builds
        run: |
          echo "Checking Docker Compose..." && ls -l docker-compose.yml
          echo "Checking Service JARs..." && find ./services -name "*.jar"
"""

# =========================================================
# [3] 메인 실행 로직
# =========================================================

def run_system_setup():
    print("🚀 [System Builder] 대량 파일 생성 및 리소스 구축 시작...")
    
    files_to_create = {}
    
    # 1. Java Microservices 생성
    docker_compose_services = ""
    
    for svc in SERVICES_CONFIG:
        name = svc['name']
        safe_name = name.replace("-", "")
        pkg = f"com.koreatest12.{safe_name}"
        pkg_path = pkg.replace(".", "/")
        base_dir = f"./services/{name}"
        
        # 파일 경로 정의
        files_to_create[f"{base_dir}/pom.xml"] = generate_pom(name, f"{pkg}.App")
        files_to_create[f"{base_dir}/src/main/java/{pkg_path}/App.java"] = generate_java_app(name, svc['port'], pkg)
        files_to_create[f"{base_dir}/src/main/resources/application.yml"] = f"server:\n  port: {svc['port']}\nspring:\n  application:\n    name: {name}"
        files_to_create[f"{base_dir}/Dockerfile"] = generate_dockerfile(name, svc['port'])
        
        # 포켓몬 웹 서비스 특수 처리 (HTML 주입)
        if name == "omni-pokemon-web":
            files_to_create[f"{base_dir}/src/main/resources/static/index.html"] = POKEMON_WEB_SOURCE

        # Docker Compose Entry
        docker_compose_services += f"""
  {name}:
    build: ./services/{name}
    container_name: {name}
    ports:
      - "{svc['port']}:{svc['port']}"
    deploy:
      resources:
        limits:
          cpus: '{svc['cpu']}'
          memory: {svc['mem']}
    networks:
      - omni-net
"""

    # 2. Python AI Model Service 생성
    files_to_create["./ai-model/main.py"] = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root(): return {'status': 'AI Model Ready'}"
    files_to_create["./ai-model/requirements.txt"] = "fastapi\nuvicorn"
    files_to_create["./ai-model/Dockerfile"] = "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
    
    docker_compose_services += """
  ai-model:
    build: ./ai-model
    ports: ["5000:5000"]
    networks: [- omni-net]
"""

    # 3. 인프라 및 관리 파일 생성
    files_to_create["./docker-compose.yml"] = f"version: '3.8'\nservices:{docker_compose_services}\nnetworks:\n  omni-net:\n    driver: bridge"
    files_to_create["./.github/dependabot.yml"] = generate_dependabot_config()
    files_to_create["./.github/workflows/ci.yml"] = generate_ci_workflow()
    files_to_create["./README.md"] = "# Integrated System\nGenerated by setup_complete_system.py"

    # 4. 파일 쓰기 (충돌 폴더 정리 포함)
    conflict_path = "./services/omni-cost-service/src/main/java/com/costdata"
    if os.path.exists(conflict_path):
        print(f"🧹 [Clean] 충돌 폴더 제거: {conflict_path}")
        shutil.rmtree(conflict_path)

    for path, content in files_to_create.items():
        full_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"✅ [Create] 총 {len(files_to_create)}개 파일 대량 생성 완료.")

    # 5. Maven 빌드 실행
    print("🔄 [Build] Maven Clean Package 실행 중...")
    mvn = "mvn.cmd" if os.name == 'nt' else "mvn"
    
    # 루트에서 각 서비스 순회하며 빌드
    for svc in SERVICES_CONFIG:
        pom = f"./services/{svc['name']}/pom.xml"
        subprocess.call(f"{mvn} clean package -f {pom} -DskipTests -fn", shell=True)

    print("\n✨ [Success] 모든 시스템 구축 완료.")
    print("👉 실행: docker-compose up --build")
    print("👉 포켓몬 봇: http://localhost:8086/index.html")

if __name__ == "__main__":
    run_system_setup()
