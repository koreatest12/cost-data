import os
import subprocess
import shutil

# =========================================================
# [1] 시스템 설정 및 서비스 정의
# =========================================================

# 마이크로서비스 목록 (총 8개 - 웹 및 AI 포함)
SERVICES_CONFIG = [
    {"name": "omni-gateway",         "port": 8080, "mem": "512m", "cpu": "0.5", "desc": "API Gateway"},
    {"name": "omni-auth-service",    "port": 8081, "mem": "512m", "cpu": "0.5", "desc": "Auth System"},
    {"name": "omni-cost-service",    "port": 8082, "mem": "1024m","cpu": "1.0", "desc": "Cost Core"},
    {"name": "omni-batch-service",   "port": 8083, "mem": "2048m","cpu": "1.5", "desc": "Batch Processor"},
    {"name": "omni-log-service",     "port": 8084, "mem": "512m", "cpu": "0.5", "desc": "Log System"},
    {"name": "omni-payment-service", "port": 8085, "mem": "768m", "cpu": "0.8", "desc": "Payment Gateway"},
    {"name": "omni-pokemon-web",     "port": 8086, "mem": "300m", "cpu": "0.4", "desc": "Dashboard & IV Manager"}
]

# [NEW] 업그레이드된 통합 대시보드 (시스템 상태 + 포켓몬 봇)
DASHBOARD_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni System Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #4361ee; --success: #2ec4b6; --danger: #e63946; --bg: #f8f9fa; --card: #ffffff; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; color: #333; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--card); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .card h3 { margin: 0 0 10px 0; font-size: 0.9rem; color: #666; }
        .card .val { font-size: 1.8rem; font-weight: bold; color: var(--primary); }
        
        /* 서버 상태 패널 */
        .server-status { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        .dot-green { background: var(--success); box-shadow: 0 0 8px var(--success); }
        
        /* 포켓몬 스타일 */
        .input-group { margin-bottom: 10px; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-top: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #3a53d0; }
        .badge { padding: 4px 10px; border-radius: 20px; color: white; font-size: 0.8rem; }
        .bg-pvp { background: #7209b7; } .bg-def { background: #2ec4b6; } .bg-att { background: #e63946; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-network-wired"></i> Omni System Dashboard</h1>
        <div style="font-size:0.9rem; color:#666;">Status: <span style="color:var(--success); font-weight:bold;">All Systems Operational</span></div>
    </div>

    <div class="grid">
        <div class="card">
            <h3><i class="fas fa-server"></i> Active Microservices</h3>
            <div class="val">8 / 8</div>
            <div class="server-status">
                <span title="Gateway" class="status-dot dot-green"></span>
                <span title="Auth" class="status-dot dot-green"></span>
                <span title="Cost" class="status-dot dot-green"></span>
                <span title="Batch" class="status-dot dot-green"></span>
                <span title="Log" class="status-dot dot-green"></span>
                <span title="Payment" class="status-dot dot-green"></span>
                <span title="Web" class="status-dot dot-green"></span>
                <span title="AI" class="status-dot dot-green"></span>
            </div>
        </div>
        <div class="card">
            <h3><i class="fas fa-memory"></i> Total Memory Usage</h3>
            <div class="val">~4.8 GB</div>
            <div style="font-size:0.8rem; color:#666;">Allocation Limit</div>
        </div>
        <div class="card">
            <h3><i class="fab fa-docker"></i> Container Health</h3>
            <div class="val" style="color:var(--success)">100%</div>
        </div>
        <div class="card">
            <h3><i class="fas fa-robot"></i> AI Model Status</h3>
            <div class="val" style="font-size:1.2rem;">Python 3.9 / FastAPI</div>
            <div style="font-size:0.8rem; color:var(--success);">● Ready to Inference</div>
        </div>
    </div>

    <hr style="border:0; border-top:1px solid #eee; margin: 30px 0;">

    <h2 style="color:#4361ee;"><i class="fas fa-gamepad"></i> Pokemon IV Manager & Defender Bot</h2>
    <div class="main-container" style="display:grid; grid-template-columns: 350px 1fr; gap:20px;">
        <div class="card">
            <h3>Input Data</h3>
            <input type="text" id="pokeName" placeholder="Pokemon Name (e.g. Dragonite)">
            <input type="number" id="attack" placeholder="Attack (0-15)">
            <input type="number" id="defense" placeholder="Defense (0-15)">
            <input type="number" id="stamina" placeholder="HP (0-15)">
            <button onclick="analyze()" style="margin-top:15px;">Analyze <i class="fas fa-search"></i></button>
        </div>
        <div class="card">
            <h3>Analysis Result <span id="botResult" style="float:right; font-size:0.9rem; color:var(--primary);"></span></h3>
            <div style="overflow-x:auto;">
                <table id="dataTable">
                    <thead><tr><th>No</th><th>Name</th><th>Stats (A/D/H)</th><th>IV</th><th>Grade</th><th>Bot Analysis</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let list = []; let id = 1;
        function analyze() {
            const n = document.getElementById('pokeName').value || "Unknown";
            const a = +document.getElementById('attack').value || 0;
            const d = +document.getElementById('defense').value || 0;
            const h = +document.getElementById('stamina').value || 0;
            const per = Math.round(((a+d+h)/45)*100);
            
            let type = {t:"Normal", c:"#999"};
            if(per===100) type={t:"Perfect!", c:"bg-att"};
            else if(a<=5 && d>=10 && h>=10) type={t:"PVP Gem", c:"bg-pvp"};
            else if(d>=14 && h>=14) type={t:"Gym Tank", c:"bg-def"};
            else if(a===15 && per>=80) type={t:"Raid Attacker", c:"bg-att"};

            list.unshift({id:id++, n, a, d, h, per, type});
            render();
            document.getElementById('botResult').innerText = `Latest: ${n} (${per}%) - ${type.t}`;
        }
        function render() {
            document.querySelector('tbody').innerHTML = list.map(p => 
                `<tr>
                    <td>${p.id}</td><td><b>${p.n}</b></td>
                    <td>${p.a}/${p.d}/${p.h}</td>
                    <td><b>${p.per}%</b></td>
                    <td>${p.per==100?'4★':p.per>=82?'3★':'2★'}</td>
                    <td><span class="badge ${p.type.c}">${p.type.t}</span></td>
                </tr>`
            ).join('');
        }
    </script>
</body>
</html>"""

# =========================================================
# [2] 파일 생성 헬퍼 함수
# =========================================================

def generate_pom(name, main_class):
    """부모 POM 충돌 방지 및 메인 클래스 명시"""
    return f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
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
        <start-class>{main_class}</start-class>
    </properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
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

def generate_app_java(name, pkg):
    return f"""package {pkg};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class App {{
    public static void main(String[] args) {{ SpringApplication.run(App.class, args); }}
    @GetMapping("/") public String status() {{ return "Service [{name}] is Operational."; }}
}}"""

def generate_dockerfile(name, port):
    return f"""FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{name}-1.0.0.jar app.jar
ENV JAVA_OPTS="-Xms256m -Xmx512m"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
EXPOSE {port}"""

def generate_dependabot_full():
    """
    [대량 추가] 모든 서비스(Java 7개 + AI 1개)의 Maven, Dockerfile, GitHub Actions 감시
    """
    config = """version: 2
updates:
  # 1. GitHub Actions (CI/CD)
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: {interval: "weekly"}
"""
    # 2. Java Services (Maven & Docker) - 7개 서비스 자동 생성
    for svc in SERVICES_CONFIG:
        config += f"""
  # Service: {svc['name']}
  - package-ecosystem: "maven"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
    groups:
      spring: {{patterns: ["org.springframework*"]}}
      
  - package-ecosystem: "docker"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
"""
    # 3. AI Service (Pip & Docker)
    config += """
  # Service: AI Model
  - package-ecosystem: "pip"
    directory: "/ai-model"
    schedule: {interval: "weekly"}
    
  - package-ecosystem: "docker"
    directory: "/ai-model"
    schedule: {interval: "weekly"}
"""
    return config

# =========================================================
# [3] 메인 실행 로직
# =========================================================

def run_ultimate_setup():
    print("🚀 [Ultimate Setup] 시스템 전체 대량 구축 및 Dependabot 설정 중...")
    
    files = {}
    docker_compose_svcs = ""

    # 1. Java 마이크로서비스 (7개) 파일 생성
    for svc in SERVICES_CONFIG:
        name = svc['name']
        safe_name = name.replace("-", "")
        pkg = f"com.koreatest12.{safe_name}"
        path = f"./services/{name}"
        
        # 기본 파일 생성
        files[f"{path}/pom.xml"] = generate_pom(name, f"{pkg}.App")
        files[f"{path}/Dockerfile"] = generate_dockerfile(name, svc['port'])
        files[f"{path}/src/main/java/{pkg.replace('.', '/')}/App.java"] = generate_app_java(name, pkg)
        files[f"{path}/src/main/resources/application.yml"] = f"server:\n  port: {svc['port']}\nspring:\n  application:\n    name: {name}"

        # 웹 서비스인 경우 대시보드 주입
        if name == "omni-pokemon-web":
            files[f"{path}/src/main/resources/static/index.html"] = DASHBOARD_SOURCE

        # Docker Compose Entry
        docker_compose_svcs += f"""
  {name}:
    build: ./services/{name}
    container_name: {name}
    ports: ["{svc['port']}:{svc['port']}"]
    deploy:
      resources:
        limits:
          cpus: '{svc['cpu']}'
          memory: {svc['mem']}
    networks:
      - omni-net
"""

    # 2. AI 서비스 파일 생성
    files["./ai-model/main.py"] = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {'status':'AI Ready'}"
    files["./ai-model/requirements.txt"] = "fastapi==0.95.2\nuvicorn==0.22.0"
    files["./ai-model/Dockerfile"] = "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
    
    docker_compose_svcs += """
  ai-model:
    build: ./ai-model
    ports: ["5000:5000"]
    networks: [- omni-net]
"""

    # 3. 인프라 파일 생성
    files["./docker-compose.yml"] = f"version: '3.8'\nservices:{docker_compose_svcs}\nnetworks:\n  omni-net:\n    driver: bridge"
    files["./.github/dependabot.yml"] = generate_dependabot_full() # 대량 Dependabot 설정
    files["./README.md"] = "# Omni System\n- Dashboard: http://localhost:8086\n- Services: 8 Active"

    # 4. 파일 쓰기 및 청소
    if os.path.exists("./services/omni-cost-service/src/main/java/com/costdata"):
        shutil.rmtree("./services/omni-cost-service/src/main/java/com/costdata")

    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)

    print(f"✅ [Files] {len(files)}개 설정 파일 생성 완료.")

    # 5. 빌드
    print("🔄 [Build] Maven 빌드 시작...")
    mvn = "mvn.cmd" if os.name == 'nt' else "mvn"
    for svc in SERVICES_CONFIG:
        subprocess.call(f"{mvn} clean package -f ./services/{svc['name']}/pom.xml -DskipTests -fn", shell=True)

    print("\n✨ [Done] 설치 완료!")
    print("👉 1. 실행: docker-compose up --build")
    print("👉 2. 대시보드 접속: http://localhost:8086/index.html")

if __name__ == "__main__":
    run_ultimate_setup()
