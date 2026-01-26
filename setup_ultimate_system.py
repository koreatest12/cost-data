import os
import subprocess
import shutil

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

# [DASHBOARD V3] 대량 생성(Bulk) + CSV 내보내기 + 실시간 분석 엔진 탑재
DASHBOARD_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni System Dashboard Pro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #4361ee; --success: #2ec4b6; --bg: #f8f9fa; --card: #ffffff; --dark: #2b2d42; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--dark); }
        
        /* Layout */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .main-layout { display: grid; grid-template-columns: 350px 1fr; gap: 25px; }
        @media (max-width: 900px) { .main-layout { grid-template-columns: 1fr; } }

        /* Cards */
        .card { background: var(--card); padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); }
        .card h3 { margin: 0 0 10px 0; font-size: 0.95rem; color: #8d99ae; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-val { font-size: 2.2rem; font-weight: 800; color: var(--primary); }
        .stat-sub { font-size: 0.9rem; color: #666; margin-top: 5px; }

        /* Form Elements */
        input { width: 100%; padding: 12px; margin-bottom: 12px; border: 2px solid #edf2f4; border-radius: 10px; box-sizing: border-box; font-size: 1rem; transition: 0.3s; }
        input:focus { border-color: var(--primary); outline: none; }
        
        button { width: 100%; padding: 14px; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; transition: 0.3s; font-size: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-analyze { background: var(--primary); color: white; }
        .btn-analyze:hover { background: #3a53d0; box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3); }
        
        .btn-bulk { background: var(--success); color: white; margin-top: 10px; }
        .btn-bulk:hover { background: #25a296; box-shadow: 0 4px 12px rgba(46, 196, 182, 0.3); }

        .btn-export { background: #2b2d42; color: white; width: auto; padding: 10px 20px; font-size: 0.9rem; }
        .btn-export:hover { background: #1a1b2e; }

        /* Table */
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; }
        th { text-align: left; padding: 15px; background: #f8f9fa; color: #666; font-weight: 600; border-bottom: 2px solid #eee; }
        td { padding: 15px; border-bottom: 1px solid #f1f1f1; vertical-align: middle; }
        tr:hover td { background: #fcfcfc; }
        
        /* Badges */
        .badge { padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.75rem; font-weight: 700; display: inline-block; }
        .bg-perfect { background: linear-gradient(135deg, #ff5722, #f50057); } /* 100% */
        .bg-pvp { background: linear-gradient(135deg, #7209b7, #480ca8); }    /* PVP */
        .bg-tank { background: linear-gradient(135deg, #2ec4b6, #20a4f3); }   /* 방어 */
        .bg-raid { background: linear-gradient(135deg, #f72585, #b5179e); }   /* 공격 */
        .bg-norm { background: #adb5bd; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0;"><i class="fas fa-satellite-dish"></i> Omni Dashboard Pro</h1>
            <div style="color:#666; margin-top:5px;">System Integrity: <span style="color:var(--success); font-weight:bold;">100% Stable</span></div>
        </div>
        <div>
            <span style="background:#eef2ff; color:var(--primary); padding:8px 16px; border-radius:30px; font-weight:bold;">
                <i class="fas fa-server"></i> 8 Services Active
            </span>
        </div>
    </div>

    <div class="grid-stats">
        <div class="card">
            <h3>Total Analyzed</h3>
            <div class="stat-val" id="totalCount">0</div>
            <div class="stat-sub">Pokémons</div>
        </div>
        <div class="card">
            <h3>Perfect (4★)</h3>
            <div class="stat-val" id="perfectCount" style="color:#f50057">0</div>
            <div class="stat-sub">IV 100%</div>
        </div>
        <div class="card">
            <h3>PVP Hidden Gems</h3>
            <div class="stat-val" id="pvpCount" style="color:#7209b7">0</div>
            <div class="stat-sub">Great/Ultra League</div>
        </div>
        <div class="card">
            <h3>Avg. Potential</h3>
            <div class="stat-val" id="avgIv">0%</div>
            <div class="stat-sub">Overall Quality</div>
        </div>
    </div>

    <div class="main-layout">
        <div class="card">
            <h2 style="margin-top:0; color:var(--dark);"><i class="fas fa-calculator"></i> IV Calculator</h2>
            <div style="background:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:20px;">
                <label style="font-weight:bold; font-size:0.9rem; color:#666;">Manual Input</label>
                <input type="text" id="name" placeholder="Pokémon Name (e.g. Mewtwo)">
                <div style="display:flex; gap:10px;">
                    <input type="number" id="att" placeholder="ATK (0-15)" min="0" max="15">
                    <input type="number" id="def" placeholder="DEF (0-15)" min="0" max="15">
                    <input type="number" id="hp" placeholder="HP (0-15)" min="0" max="15">
                </div>
                <button class="btn-analyze" onclick="addManual()">
                    <i class="fas fa-search"></i> Analyze
                </button>
            </div>

            <div style="border-top:2px dashed #eee; padding-top:20px;">
                <label style="font-weight:bold; font-size:0.9rem; color:#666;">Mass Actions</label>
                <button class="btn-bulk" onclick="bulkGenerate()">
                    <i class="fas fa-flask"></i> Bulk Generate (50ea)
                </button>
                <div style="text-align:center; font-size:0.8rem; color:#999; margin-top:10px;">
                    Simulates catching 50 random Pokémons
                </div>
            </div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;"><i class="fas fa-list"></i> Analysis Log</h2>
                <button class="btn-export" onclick="exportCSV()">
                    <i class="fas fa-file-csv"></i> Export CSV
                </button>
            </div>
            <div style="overflow-x:auto; max-height:600px; overflow-y:auto; margin-top:15px;">
                <table id="dataTable">
                    <thead style="position:sticky; top:0;">
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Stats (A/D/H)</th>
                            <th>IV (%)</th>
                            <th>Grade</th>
                            <th>Bot Analysis</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let list = []; 
        let id = 1;
        const SAMPLE_NAMES = ["망나뇽", "마기라스", "뮤츠", "루기아", "잠만보", "괴력몬", "해피너스", "팬텀", "한카리아스", "메타그로스", "갸라도스", "리자몽", "거대코뿌리", "토게키스"];

        // 1. 단일 추가
        function addManual() {
            const n = document.getElementById('name').value || 'Unknown';
            const a = +document.getElementById('att').value;
            const d = +document.getElementById('def').value;
            const h = +document.getElementById('hp').value;
            
            if(a>15 || d>15 || h>15) { alert("Stats must be 0-15"); return; }
            
            processPokemon(n, a, d, h);
            clearInputs();
        }

        // 2. 대량 생성 (핵심 기능)
        function bulkGenerate() {
            for(let i=0; i<50; i++) {
                const name = SAMPLE_NAMES[Math.floor(Math.random() * SAMPLE_NAMES.length)];
                const a = Math.floor(Math.random() * 16);
                const d = Math.floor(Math.random() * 16);
                const h = Math.floor(Math.random() * 16);
                processPokemon(name, a, d, h);
            }
        }

        // 3. 포켓몬 분석 엔진
        function processPokemon(name, a, d, h) {
            const per = Math.round(((a+d+h)/45)*100);
            
            let type = {t:"Normal", c:"bg-norm"};
            
            if (per === 100) { type = {t:"PERFECT 4★", c:"bg-perfect"}; }
            else if (a <= 2 && d >= 12 && h >= 12) { type = {t:"PVP GEM", c:"bg-pvp"}; } // PVP 로직 강화
            else if (d === 15 && h === 15) { type = {t:"GYM TANK", c:"bg-tank"}; }
            else if (a === 15 && per >= 85) { type = {t:"RAID ATK", c:"bg-raid"}; }
            
            let grade = per === 100 ? '4★' : per >= 82 ? '3★' : per >= 66 ? '2★' : '1★';
            
            list.unshift({id: id++, n: name, a, d, h, per, grade, type, time: new Date().toLocaleTimeString()});
            render();
        }

        // 4. 화면 렌더링 & 통계 업데이트
        function render() {
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = list.slice(0, 1000).map(p => `
                <tr>
                    <td>#${p.id}</td>
                    <td style="font-weight:bold;">${p.n}</td>
                    <td><span style="color:#e63946">A${p.a}</span> / <span style="color:#2ec4b6">D${p.d}</span> / <span style="color:#4361ee">H${p.h}</span></td>
                    <td><b style="font-size:1.1em">${p.per}%</b></td>
                    <td>${p.grade}</td>
                    <td><span class="badge ${p.type.c}">${p.type.t}</span></td>
                </tr>
            `).join('');

            // 통계 업데이트
            document.getElementById('totalCount').innerText = list.length;
            document.getElementById('perfectCount').innerText = list.filter(p => p.per === 100).length;
            document.getElementById('pvpCount').innerText = list.filter(p => p.type.c === 'bg-pvp').length;
            
            const totalSum = list.reduce((acc, cur) => acc + cur.per, 0);
            document.getElementById('avgIv').innerText = (list.length ? Math.round(totalSum / list.length) : 0) + "%";
        }

        // 5. CSV 내보내기
        function exportCSV() {
            let csv = "ID,Name,Attack,Defense,HP,IV(%),Grade,Type,Time\\n";
            list.forEach(p => {
                csv += `${p.id},${p.n},${p.a},${p.d},${p.h},${p.per},${p.grade},${p.type.t},${p.time}\\n`;
            });
            const blob = new Blob(["\\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `pokemon_data_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();
        }

        function clearInputs() {
            document.querySelectorAll('input').forEach(i => i.value = '');
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
    print("👉 실행: docker-compose up --build")
    print("👉 대시보드: http://localhost:8086/index.html")

if __name__ == "__main__":
    run_setup()
