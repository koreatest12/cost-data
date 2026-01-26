import os
import subprocess
import json
import sys

# =========================================================
# 설정: 프로젝트 루트 경로 및 파일 정의
# =========================================================
ROOT_DIR = "."
FILES_MANIFEST = "files.json"

# =========================================================
# [Resource] 포켓몬고 IV 매니저 웹 소스 (HTML/CSS/JS)
# f-string 충돌 방지를 위해 일반 문자열 변수로 분리
# =========================================================
POKEMON_WEB_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포켓몬고 IV 매니저 + 디펜더 봇</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #3b4cca; --secondary: #ffcb05; --bg: #f4f6f8; --surface: #ffffff; --danger: #dc3545; --success: #28a745; --bot-color: #6f42c1; }
        body { font-family: 'Noto Sans KR', sans-serif; background-color: var(--bg); margin: 0; padding: 20px; color: #333; display: flex; flex-direction: column; align-items: center; }
        .main-container { display: grid; grid-template-columns: 350px 1fr; gap: 20px; max-width: 1400px; width: 100%; }
        @media (max-width: 900px) { .main-container { grid-template-columns: 1fr; } }
        .card { background: var(--surface); padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h2 { margin-top: 0; color: var(--primary); font-size: 1.2rem; }
        .input-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.9rem; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-add { background-color: var(--primary); color: white; }
        .btn-add:hover { background-color: #2a3699; }
        .btn-reset { background-color: #e2e6ea; color: #333; }
        .btn-download { background-color: var(--success); color: white; width: auto; padding: 10px 20px; }
        .dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; width: 100%; max-width: 1400px; }
        .stat-card { background: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .stat-val { font-size: 1.5rem; font-weight: bold; color: var(--primary); }
        .stat-label { font-size: 0.85rem; color: #666; }
        .bot-area { background-color: #eef0ff; border-left: 5px solid var(--bot-color); padding: 15px; margin-bottom: 15px; border-radius: 4px; font-size: 0.95rem; color: #444; animation: fadeIn 0.5s; }
        .bot-title { font-weight: bold; color: var(--bot-color); margin-bottom: 5px; display: block; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; min-width: 600px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; vertical-align: middle; }
        th { background-color: #f8f9fa; color: #555; font-weight: 600; }
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; color: white; display: inline-block; margin-right: 4px; }
        .bg-4 { background-color: #ff5722; } .bg-3 { background-color: #ff9800; } .bg-2 { background-color: #2196f3; } .bg-1 { background-color: #9e9e9e; }
        .tag-pvp { background-color: #6f42c1; color: white; border: 1px solid #5a32a3; }
        .tag-def { background-color: #28a745; color: white; border: 1px solid #1e7e34; }
        .tag-att { background-color: #dc3545; color: white; border: 1px solid #bd2130; }
        .tag-nor { background-color: #f8f9fa; color: #666; border: 1px solid #ddd; }
        .delete-btn { color: var(--danger); background: none; border: none; cursor: pointer; font-size: 1rem; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="stat-card"><div class="stat-val" id="totalCount">0</div><div class="stat-label">조사한 포켓몬</div></div>
        <div class="stat-card"><div class="stat-val" id="perfectCount" style="color: #ff5722;">0</div><div class="stat-label">4★ (완벽)</div></div>
        <div class="stat-card"><div class="stat-val" id="pvpCount" style="color: #6f42c1;">0</div><div class="stat-label">PVP 유망주</div></div>
        <div class="stat-card"><div class="stat-val" id="avgIv">0%</div><div class="stat-label">평균 IV</div></div>
    </div>
    <div class="main-container">
        <div class="card">
            <h2>📝 개체값 입력</h2>
            <div class="input-group"><label>포켓몬 이름 (선택)</label><input type="text" id="pokeName" placeholder="예: 망나뇽"></div>
            <div class="input-group"><label>공격력 (Attack)</label><input type="number" id="attack" min="0" max="15" placeholder="0 ~ 15"></div>
            <div class="input-group"><label>방어력 (Defense)</label><input type="number" id="defense" min="0" max="15" placeholder="0 ~ 15"></div>
            <div class="input-group"><label>HP (Stamina)</label><input type="number" id="stamina" min="0" max="15" placeholder="0 ~ 15"></div>
            <div class="btn-group"><button class="btn-reset" onclick="clearInputs()">초기화</button><button class="btn-add" onclick="addPokemon()">봇 분석 및 추가</button></div>
        </div>
        <div class="card">
            <div id="botMessage" class="bot-area" style="display:none;"><span class="bot-title"><i class="fas fa-robot"></i> 디펜더 봇 분석 결과:</span><span id="botText">대기 중...</span></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><h2>📊 분석 목록</h2><button class="btn-download" onclick="exportToCSV()"><i class="fas fa-file-csv"></i> 엑셀(CSV) 다운로드</button></div>
            <div class="table-container"><table id="dataTable"><thead><tr><th>No.</th><th>이름</th><th>능력치(공/방/체)</th><th>IV (%)</th><th>등급</th><th>🤖 봇 분석</th><th>삭제</th></tr></thead><tbody></tbody></table></div>
        </div>
    </div>
    <script>
        let pokemonList = []; let idCounter = 1;
        function addPokemon() {
            const name = document.getElementById('pokeName').value || "이름없음";
            const att = parseInt(document.getElementById('attack').value) || 0;
            const def = parseInt(document.getElementById('defense').value) || 0;
            const hp = parseInt(document.getElementById('stamina').value) || 0;
            if ([att, def, hp].some(val => val < 0 || val > 15)) { alert("능력치는 0에서 15 사이여야 합니다."); return; }
            const total = att + def + hp; const percentage = (total / 45) * 100; const rounded = Math.round(percentage);
            let grade = percentage === 100 ? "4★" : percentage >= 82.2 ? "3★" : percentage >= 66.7 ? "2★" : "1★";
            let gradeClass = percentage === 100 ? "bg-4" : percentage >= 82.2 ? "bg-3" : percentage >= 66.7 ? "bg-2" : "bg-1";
            let analysis = analyzeStats(att, def, hp, percentage);
            const pokemon = { id: idCounter++, name, att, def, hp, total, percentage, rounded, grade, gradeClass, analysis, timestamp: new Date().toLocaleString() };
            pokemonList.unshift(pokemon); renderTable(); updateStats(); showBotMessage(pokemon);
            document.getElementById('attack').value = ''; document.getElementById('defense').value = ''; document.getElementById('stamina').value = ''; document.getElementById('attack').focus();
        }
        function analyzeStats(att, def, hp, percentage) {
            if (percentage === 100) return { text: "완벽한 개체 (Perfect)", type: "tag-pvp", code: "perfect" };
            if (att <= 5 && def >= 10 && hp >= 10) return { text: "배틀리그 유망주 (PVP)", type: "tag-pvp", code: "pvp" };
            if (def >= 14 && hp >= 14) return { text: "체육관 방어용 (Tank)", type: "tag-def", code: "tank" };
            if (att === 15 && percentage >= 82.2) return { text: "레이드/공격용", type: "tag-att", code: "raid" };
            if (percentage < 50) return { text: "박사에게 보내기", type: "tag-nor", code: "trash" };
            return { text: "일반 성장형", type: "tag-nor", code: "normal" };
        }
        function showBotMessage(p) {
            const botArea = document.getElementById('botMessage'); const botText = document.getElementById('botText'); botArea.style.display = "block";
            let msg = `[${p.name}] 분석 완료! IV: ${p.rounded}% (${p.grade}). `;
            if (p.analysis.code === 'perfect') msg += "🎉 축하합니다! 100% 완벽한 포켓몬입니다!";
            else if (p.analysis.code === 'pvp') msg += "⚔️ PVP용 숨겨진 보석일 수 있습니다!";
            else if (p.analysis.code === 'tank') msg += "🛡️ 체육관 방어용으로 적합합니다.";
            else if (p.analysis.code === 'raid') msg += "💥 레이드 공격용으로 훌륭합니다.";
            else if (p.analysis.code === 'trash') msg += "🗑️ 사탕으로 교환하는 게 좋겠습니다.";
            else msg += "도감 등록용으로 적합합니다.";
            botText.innerText = msg;
        }
        function renderTable() {
            const tbody = document.querySelector('#dataTable tbody'); tbody.innerHTML = "";
            pokemonList.forEach((p, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${pokemonList.length - index}</td><td><strong>${p.name}</strong></td><td><span style="color:#dc3545">A:${p.att}</span>/<span style="color:#28a745">D:${p.def}</span>/<span style="color:#007bff">H:${p.hp}</span></td><td><strong>${p.rounded}%</strong></td><td><span class="badge ${p.gradeClass}">${p.grade}</span></td><td><span class="badge ${p.analysis.type}">${p.analysis.text}</span></td><td><button class="delete-btn" onclick="deletePokemon(${p.id})"><i class="fas fa-trash"></i></button></td>`;
                tbody.appendChild(tr);
            });
        }
        function deletePokemon(id) { pokemonList = pokemonList.filter(p => p.id !== id); renderTable(); updateStats(); }
        function updateStats() {
            const total = pokemonList.length; const perfect = pokemonList.filter(p => p.analysis.code === 'perfect').length;
            const pvpCount = pokemonList.filter(p => p.analysis.code === 'pvp').length;
            const avg = total === 0 ? 0 : Math.round(pokemonList.reduce((acc, cur) => acc + cur.percentage, 0) / total);
            document.getElementById('totalCount').innerText = total; document.getElementById('perfectCount').innerText = perfect; document.getElementById('pvpCount').innerText = pvpCount; document.getElementById('avgIv').innerText = avg + "%";
        }
        function clearInputs() { document.getElementById('pokeName').value = ''; document.getElementById('attack').value = ''; document.getElementById('defense').value = ''; document.getElementById('stamina').value = ''; document.getElementById('botMessage').style.display = 'none'; }
        function exportToCSV() {
            if (pokemonList.length === 0) { alert("저장할 데이터가 없습니다."); return; }
            let csvContent = "data:text/csv;charset=utf-8,\\uFEFFID,이름,공격,방어,HP,총합,퍼센트,등급,봇분석,시간\\n";
            pokemonList.forEach(p => { csvContent += `${p.id},${p.name},${p.att},${p.def},${p.hp},${p.total},${p.rounded}%,${p.grade},${p.analysis.text},${p.timestamp}\\n`; });
            const encodedUri = encodeURI(csvContent); const link = document.createElement("a"); link.setAttribute("href", encodedUri); link.setAttribute("download", "pokemon_iv_bot.csv"); document.body.appendChild(link); link.click(); document.body.removeChild(link);
        }
    </script>
</body>
</html>"""

# =========================================================
# [Helper] 서비스 설정 및 리소스 할당 정의 (포켓몬 웹 추가)
# =========================================================
MICROSERVICES_CONFIG = [
    {"name": "omni-gateway",        "port": 8080, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "API Gateway"},
    {"name": "omni-auth-service",   "port": 8081, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "Authentication"},
    {"name": "omni-cost-service",   "port": 8082, "mem_limit": "1024m", "jvm_heap": "800m", "cpu": "1.0", "desc": "Cost Calculation (Core)"},
    {"name": "omni-batch-service",  "port": 8083, "mem_limit": "2048m", "jvm_heap": "1600m", "cpu": "1.5", "desc": "High Load Batch"},
    {"name": "omni-log-service",    "port": 8084, "mem_limit": "512m", "jvm_heap": "400m", "cpu": "0.5", "desc": "Log Aggregator"},
    {"name": "omni-payment-service","port": 8085, "mem_limit": "768m", "jvm_heap": "600m", "cpu": "0.8", "desc": "Payment Gateway"},
    # 🌟 포켓몬 웹 서비스 추가 (Web Frontend)
    {"name": "omni-pokemon-web",    "port": 8086, "mem_limit": "300m", "jvm_heap": "200m", "cpu": "0.4", "desc": "Pokemon IV Manager & Defender Bot"}
]

# =========================================================
# [Helper] 서비스 템플릿 생성기
# =========================================================
def generate_java_service(config):
    name = config["name"]
    port = config["port"]
    desc = config["desc"]
    jvm_heap = config["jvm_heap"]
    
    base_dir = f"./services/{name}"
    safe_name = name.replace("-", "")
    
    files = {
        # 1. POM.XML
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
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
</project>""",

        # 2. Dockerfile
        f"{base_dir}/Dockerfile": f"""FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/{name}-1.0.0.jar app.jar
ENTRYPOINT ["java", "-Xms{jvm_heap}", "-Xmx{jvm_heap}", "-jar", "app.jar"]
EXPOSE {port}
""",

        # 3. Application.yml
        f"{base_dir}/src/main/resources/application.yml": f"""server:
  port: {port}
spring:
  application:
    name: {name}
  profiles:
    active: dev
""",
        # 4. Java Code
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
    public String status() {{
        // omni-pokemon-web인 경우 static/index.html로 자동 라우팅되지만, 
        // 헬스 체크용으로 남겨둠
        return "Service {name} is Running!";
    }}
}}""",
        f"{base_dir}/README.md": f"# {name}\n\n{desc}\n\n## Resources\n- Docker Limit: {config['mem_limit']}\n- JVM Heap: {config['jvm_heap']}"
    }

    # 🌟 특수 처리: omni-pokemon-web 서비스인 경우 HTML 파일 주입
    if name == "omni-pokemon-web":
        files[f"{base_dir}/src/main/resources/static/index.html"] = POKEMON_WEB_SOURCE

    return files

# =========================================================
# 1. 파일 관리 및 생성 (메인 로직)
# =========================================================
def manage_files(manifest_file=FILES_MANIFEST):
    print(f"📝 [시스템 구축] 포켓몬 봇 포함 마이크로서비스 파일 생성 중...")

    default_files = {
        "./README.md": "# Omni MSA System with Pokemon IV Manager\n\n- Backend: Spring Boot Microservices\n- AI: Python FastAPI\n- Frontend: Pokemon IV Web (Port 8086)",
        "./.gitignore": "__pycache__/\n*.class\n.idea/\n*.log\ntarget/\nvenv/\n.DS_Store\n.mvn/\n*.iml",
        
        # Python AI Service
        "./ai-model/requirements.txt": "fastapi==0.95.0\nuvicorn==0.21.1\nnumpy==1.24.3\npandas==2.0.3",
        "./ai-model/main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {'msg': 'AI Model', 'resource': 'Shared'}",
        "./ai-model/Dockerfile": "FROM python:3.9-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\"]"
    }

    docker_services_yml = ""
    
    for config in MICROSERVICES_CONFIG:
        files = generate_java_service(config)
        default_files.update(files)
        
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

    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(default_files, f, indent=2, ensure_ascii=False)
            
        with open(manifest_file, 'r', encoding='utf-8') as f:
            files_map = json.load(f)
            
        for file_path, content in files_map.items():
            full_path = os.path.abspath(file_path)
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            with open(full_path, 'w', encoding='utf-8') as dest:
                dest.write(content)
                
        print(f"   ✅ [생성 완료] 총 {len(MICROSERVICES_CONFIG)}개 서비스 생성 (포켓몬 웹 포함).")
            
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")

# =========================================================
# 2. 빌드 실행
# =========================================================
def install_modules(root_path):
    print(f"🔄 [빌드 시작] Maven 빌드 진행 중...")
    
    for dirpath, _, filenames in os.walk(root_path):
        if "pom.xml" in filenames:
            pom_path = os.path.join(dirpath, "pom.xml")
            print(f"   ☕ Java Build: {pom_path}")
            mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
            cmd = f"{mvn_cmd} clean package -f {pom_path} -DskipTests -fn"
            try:
                subprocess.call(cmd, shell=True)
            except: pass

if __name__ == "__main__":
    print("🚀 [System Manager] - Pokemon IV Bot Integration\n")
    manage_files(FILES_MANIFEST)
    install_modules(ROOT_DIR)
    print("\n✨ [완료] 시스템 준비 완료.")
    print("   👉 실행: docker-compose up --build")
    print("   👉 포켓몬 봇 접속: http://localhost:8086/index.html")
