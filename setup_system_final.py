import os
import subprocess
import json
import shutil

# =========================================================
# 설정: 프로젝트 루트
# =========================================================
ROOT_DIR = "."
FILES_MANIFEST = "files.json"

# =========================================================
# [Web Source] 포켓몬 IV 매니저 + 디펜더 봇 (HTML/JS)
# =========================================================
POKEMON_WEB_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포켓몬고 IV 매니저 Pro</title>
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
            <h2>📝 입력</h2>
            <label>이름</label><input type="text" id="pokeName" placeholder="예: 망나뇽">
            <label>공격</label><input type="number" id="attack" placeholder="0~15">
            <label>방어</label><input type="number" id="defense" placeholder="0~15">
            <label>HP</label><input type="number" id="stamina" placeholder="0~15">
            <div style="display:flex; gap:10px;">
                <button class="btn-reset" onclick="clearInputs()">초기화</button>
                <button class="btn-add" onclick="addPokemon()">추가</button>
            </div>
        </div>
        <div class="card">
            <div id="botMessage" class="bot-area" style="display:none;">🤖 <span id="botText"></span></div>
            <h2>📊 목록</h2>
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
            let ana = {t:"성장형", c:""};
            if(per===100) ana={t:"완벽!", c:"tag-att"};
            else if(a<=5 && d>=10 && h>=10) ana={t:"PVP용", c:"tag-pvp"};
            else if(d>=14 && h>=14) ana={t:"방어용", c:"tag-def"};
            
            list.unshift({id:id++, n, a, d, h, round, ana});
            render(); msg(list[0]);
            document.getElementById('attack').value=''; document.getElementById('attack').focus();
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

# =========================================================
# [Service Config] 서비스 목록 및 리소스 할당
# =========================================================
SERVICES = [
    {"name": "omni-gateway",         "port": 8080, "mem": "512m", "cpu": "0.5", "desc": "API Gateway"},
    {"name": "omni-auth-service",    "port": 8081, "mem": "512m", "cpu": "0.5", "desc": "Auth System"},
    {"name": "omni-cost-service",    "port": 8082, "mem": "1024m","cpu": "1.0", "desc": "Cost Core"},
    {"name": "omni-batch-service",   "port": 8083, "mem": "2048m","cpu": "1.5", "desc": "Batch Job"},
    {"name": "omni-log-service",     "port": 8084, "mem": "512m", "cpu": "0.5", "desc": "Log System"},
    {"name": "omni-payment-service", "port": 8085, "mem": "768m", "cpu": "0.8", "desc": "Payment"},
    {"name": "omni-pokemon-web",     "port": 8086, "mem": "300m", "cpu": "0.4", "desc": "Pokemon Web"}
]

# =========================================================
# 1. 파일 생성 함수 (Maven 경로 경고 수정)
# =========================================================
def create_service_files(config):
    name = config["name"]
    port = config["port"]
    safe_name = name.replace("-", "")
    base_dir = f"./services/{name}"
    
    # [핵심 수정] 메인 클래스 명시
    main_class_path = f"com.koreatest12.{safe_name}.App"

    files = {
        # 1. POM.XML (relativePath 추가하여 상위 폴더 참조 방지)
        f"{base_dir}/pom.xml": f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
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
        <start-class>{main_class_path}</start-class>
    </properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration><mainClass>{main_class_path}</mainClass></configuration>
            </plugin>
        </plugins>
    </build>
</project>""",

        # 2. Java Application Class
        f"{base_dir}/src/main/java/com/koreatest12/{safe_name}/App.java": f"""package com.koreatest12.{safe_name};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class App {{
    public static void main(String[] args) {{ SpringApplication.run(App.class, args); }}
    @GetMapping("/") public String home() {{ return "Service [{name}] Running on Port {port}"; }}
}}""",

        # 3. Dockerfile
        f"{base_dir}/Dockerfile": f"""FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{name}-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
EXPOSE {port}""",

        # 4. Application.yml
        f"{base_dir}/src/main/resources/application.yml": f"server:\n  port: {port}\nspring:\n  application:\n    name: {name}"
    }

    # [Web 설치] 포켓몬 웹 서비스인 경우 HTML 파일 주입
    if name == "omni-pokemon-web":
        files[f"{base_dir}/src/main/resources/static/index.html"] = POKEMON_WEB_SOURCE

    return files

# =========================================================
# 2. 실행 로직 (청소 -> 생성 -> 빌드)
# =========================================================
def run():
    print("🚀 [배포 시작] Maven 설정 수정 및 서비스 대량 빌드...")
    
    file_map = {}
    docker_services = ""

    # 1. 서비스별 설정 생성
    for svc in SERVICES:
        # 파일 내용 생성
        file_map.update(create_service_files(svc))
        
        # Docker Compose 내용 생성
        docker_services += f"""
  {svc['name']}:
    build: ./services/{svc['name']}
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

    # 2. Docker Compose 파일 완성
    file_map["./docker-compose.yml"] = f"""version: '3.8'
services:{docker_services}
networks:
  omni-net:
    driver: bridge
"""

    # 3. 기존 충돌 폴더 청소 (매우 중요)
    conflict_dir = "./services/omni-cost-service/src/main/java/com/costdata"
    if os.path.exists(conflict_dir):
        print(f"🧹 [청소] 충돌 유발 폴더 삭제: {conflict_dir}")
        shutil.rmtree(conflict_dir)

    # 4. 파일 쓰기
    for path, content in file_map.items():
        full_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"✅ [설치 완료] {len(SERVICES)}개 서비스 pom.xml 수정 완료.")

    # 5. 빌드 실행
    print("🔄 [빌드 시작] Maven Clean Package...")
    mvn = "mvn.cmd" if os.name == 'nt' else "mvn"
    
    # 루트에서 모든 하위 pom.xml 빌드
    for svc in SERVICES:
        pom_path = f"./services/{svc['name']}/pom.xml"
        subprocess.call(f"{mvn} clean package -f {pom_path} -DskipTests -fn", shell=True)

if __name__ == "__main__":
    run()
    print("\n✨ 빌드 및 설정 완료!")
    print("👉 실행: docker-compose up --build")
    print("👉 홈페이지 접속: http://localhost:8086/index.html")
