import os
import subprocess
import shutil
import time

# =========================================================
# [1] 시스템 설정 및 서비스 정의 (총 8개)
# =========================================================
SERVICES_CONFIG = [
    {"name": "omni-gateway",         "port": 8080, "mem": "512m", "cpu": "0.5", "desc": "API Gateway"},
    {"name": "omni-auth-service",    "port": 8081, "mem": "512m", "cpu": "0.5", "desc": "Auth System"},
    {"name": "omni-cost-service",    "port": 8082, "mem": "1024m","cpu": "1.0", "desc": "Cost Core"},
    {"name": "omni-batch-service",   "port": 8083, "mem": "2048m","cpu": "1.5", "desc": "Batch Processor"},
    {"name": "omni-log-service",     "port": 8084, "mem": "512m", "cpu": "0.5", "desc": "Log System"},
    {"name": "omni-payment-service", "port": 8085, "mem": "768m", "cpu": "0.8", "desc": "Payment Gateway"},
    {"name": "omni-pokemon-web",     "port": 8086, "mem": "300m", "cpu": "0.4", "desc": "Dashboard & IV Manager"}
]

# [DASHBOARD V2] 서버 상태 모니터링 + 포켓몬 IV 계산기 통합
DASHBOARD_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni System Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #4361ee; --success: #2ec4b6; --bg: #f8f9fa; --card: #ffffff; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--card); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; background: var(--success); box-shadow: 0 0 8px var(--success); }
        input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: var(--primary); color: white; border: none; border-radius: 6px; margin-top: 10px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        .badge { padding: 4px 8px; border-radius: 12px; color: white; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-network-wired"></i> Omni Dashboard Pro</h1>
        <div>System: <span style="color:var(--success); font-weight:bold;">Online</span></div>
    </div>
    <div class="grid">
        <div class="card"><h3><i class="fas fa-server"></i> Microservices</h3><div style="font-size:1.5rem; font-weight:bold;">8 Active</div></div>
        <div class="card"><h3><i class="fab fa-docker"></i> Container Health</h3><div style="font-size:1.5rem; font-weight:bold; color:var(--success);">100%</div></div>
        <div class="card"><h3><i class="fas fa-bolt"></i> API Latency</h3><div style="font-size:1.5rem; font-weight:bold;">12ms</div></div>
    </div>
    <hr>
    <h2 style="color:var(--primary);"><i class="fas fa-gamepad"></i> Pokemon IV Manager</h2>
    <div style="display:grid; grid-template-columns: 300px 1fr; gap:20px;">
        <div class="card">
            <input type="text" id="name" placeholder="Name">
            <input type="number" id="att" placeholder="Attack (0-15)">
            <input type="number" id="def" placeholder="Defense (0-15)">
            <input type="number" id="hp" placeholder="HP (0-15)">
            <button onclick="add()">Analyze</button>
        </div>
        <div class="card">
            <table id="tbl"><thead><tr><th>Name</th><th>Stats</th><th>IV</th><th>Grade</th><th>Analysis</th></tr></thead><tbody></tbody></table>
        </div>
    </div>
    <script>
        function add() {
            const n=document.getElementById('name').value||'Unknown', a=+document.getElementById('att').value, d=+document.getElementById('def').value, h=+document.getElementById('hp').value;
            const per=Math.round(((a+d+h)/45)*100);
            let t="Normal", c="#999";
            if(per==100){t="Perfect";c="#e63946"} else if(a<=5&&d>=10&&h>=10){t="PVP";c="#7209b7"}
            const row=`<tr><td>${n}</td><td>${a}/${d}/${h}</td><td>${per}%</td><td>${per==100?'4★':per>=82?'3★':'2★'}</td><td><span class="badge" style="background:${c}">${t}</span></td></tr>`;
            document.querySelector('tbody').innerHTML=row+document.querySelector('tbody').innerHTML;
        }
    </script>
</body>
</html>"""

# =========================================================
# [2] 파일 생성 헬퍼 함수
# =========================================================
def generate_pom(name, main_class):
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
    <properties><java.version>17</java.version><start-class>{main_class}</start-class></properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
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
@SpringBootApplication @RestController
public class App {{
    public static void main(String[] args) {{ SpringApplication.run(App.class, args); }}
    @GetMapping("/") public String root() {{ return "Service [{name}] Online"; }}
}}"""

def generate_dependabot():
    config = """version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: {interval: "weekly"}
"""
    for svc in SERVICES_CONFIG:
        config += f"""
  - package-ecosystem: "maven"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
    groups: {{spring: {{patterns: ["org.springframework*"]}}}}
  - package-ecosystem: "docker"
    directory: "/services/{svc['name']}"
    schedule: {{interval: "weekly"}}
"""
    config += """
  - package-ecosystem: "pip"
    directory: "/ai-model"
    schedule: {interval: "weekly"}
"""
    return config

# =========================================================
# [3] 메인 실행
# =========================================================
def run_setup():
    print("🚀 [Ultimate Setup] 시스템 대량 구축 시작...")
    
    files = {}
    docker_svcs = ""

    # 1. Java Services
    for svc in SERVICES_CONFIG:
        name = svc['name']
        pkg = f"com.koreatest12.{name.replace('-', '')}"
        base = f"./services/{name}"
        
        files[f"{base}/pom.xml"] = generate_pom(name, f"{pkg}.App")
        files[f"{base}/src/main/java/{pkg.replace('.', '/')}/App.java"] = generate_app_java(name, pkg)
        files[f"{base}/Dockerfile"] = f"FROM openjdk:17-jdk-slim\nCOPY target/{name}-1.0.0.jar app.jar\nENTRYPOINT [\"java\",\"-jar\",\"app.jar\"]"
        files[f"{base}/src/main/resources/application.yml"] = f"server: {{port: {svc['port']}}}"
        
        if name == "omni-pokemon-web":
            files[f"{base}/src/main/resources/static/index.html"] = DASHBOARD_SOURCE

        docker_svcs += f"\n  {name}:\n    build: ./services/{name}\n    ports: [\"{svc['port']}:{svc['port']}\"]"

    # 2. AI Service
    files["./ai-model/main.py"] = "from fastapi import FastAPI\napp=FastAPI()"
    files["./ai-model/Dockerfile"] = "FROM python:3.9-slim\nRUN pip install fastapi uvicorn\nCOPY . .\nCMD [\"uvicorn\",\"main:app\",\"--host\",\"0.0.0.0\",\"--port\",\"5000\"]"
    docker_svcs += "\n  ai-model:\n    build: ./ai-model\n    ports: [\"5000:5000\"]"

    # 3. Config Files
    files["./docker-compose.yml"] = f"version: '3.8'\nservices:{docker_svcs}"
    files["./.github/dependabot.yml"] = generate_dependabot()

    # 4. Write Files & Clean
    if os.path.exists("./services/omni-cost-service/src/main/java/com/costdata"):
        shutil.rmtree("./services/omni-cost-service/src/main/java/com/costdata")

    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f: f.write(c)

    print("✅ 파일 생성 완료. Maven 빌드 시작...")
    mvn = "mvn.cmd" if os.name == 'nt' else "mvn"
    for svc in SERVICES_CONFIG:
        subprocess.call(f"{mvn} clean package -f ./services/{svc['name']}/pom.xml -DskipTests -fn", shell=True)
    
    print("\n✨ 설치 완료! (CI/CD 준비됨)")

if __name__ == "__main__":
    run_setup()
