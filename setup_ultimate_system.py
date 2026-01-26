import os
import subprocess
import shutil

# =========================================================
# [1] 시스템 설정 및 서비스 정의
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

# [WEB 1] 메인 대시보드 (index.html)
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
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .main-layout { display: grid; grid-template-columns: 350px 1fr; gap: 25px; }
        @media (max-width: 900px) { .main-layout { grid-template-columns: 1fr; } }
        .card { background: var(--card); padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        .stat-val { font-size: 2.2rem; font-weight: 800; color: var(--primary); }
        .stat-sub { font-size: 0.9rem; color: #666; margin-top: 5px; }
        input { width: 100%; padding: 12px; margin-bottom: 12px; border: 2px solid #edf2f4; border-radius: 10px; box-sizing: border-box; }
        button { width: 100%; padding: 14px; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-analyze { background: var(--primary); color: white; }
        .btn-analyze:hover { background: #3a53d0; }
        .btn-bulk { background: var(--success); color: white; margin-top: 10px; }
        .btn-bulk:hover { background: #25a296; }
        .btn-manual { background: #fff; color: var(--primary); border: 2px solid var(--primary); width: auto; padding: 8px 16px; font-size: 0.9rem; }
        .btn-manual:hover { background: #eef2ff; }
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; }
        th { text-align: left; padding: 15px; background: #f8f9fa; color: #666; border-bottom: 2px solid #eee; position: sticky; top: 0; }
        td { padding: 15px; border-bottom: 1px solid #f1f1f1; }
        .badge { padding: 6px 12px; border-radius: 20px; color: white; font-size: 0.75rem; font-weight: 700; }
        .bg-perfect { background: linear-gradient(135deg, #ff5722, #f50057); }
        .bg-pvp { background: linear-gradient(135deg, #7209b7, #480ca8); }
        .bg-tank { background: linear-gradient(135deg, #2ec4b6, #20a4f3); }
        .bg-raid { background: linear-gradient(135deg, #f72585, #b5179e); }
        .bg-norm { background: #adb5bd; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0;"><i class="fas fa-dragon"></i> Omni Dashboard Pro</h1>
            <div style="color:#666;">Database: <span style="color:var(--success); font-weight:bold;">Gen 1 ~ Gen 8 Loaded</span></div>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            <button class="btn-manual" onclick="window.location.href='manual.html'">
                <i class="fas fa-book-open"></i> 사용법 가이드
            </button>
            <span style="background:#eef2ff; color:var(--primary); padding:8px 16px; border-radius:30px; font-weight:bold;">
                <i class="fas fa-server"></i> Active
            </span>
        </div>
    </div>

    <div class="grid-stats">
        <div class="card"><h3>Total</h3><div class="stat-val" id="totalCount">0</div><div class="stat-sub">Pokémons</div></div>
        <div class="card"><h3>Perfect (4★)</h3><div class="stat-val" id="perfectCount" style="color:#f50057">0</div><div class="stat-sub">IV 100%</div></div>
        <div class="card"><h3>PVP Gems</h3><div class="stat-val" id="pvpCount" style="color:#7209b7">0</div><div class="stat-sub">Battle Ready</div></div>
        <div class="card"><h3>Avg. Potential</h3><div class="stat-val" id="avgIv">0%</div><div class="stat-sub">Quality</div></div>
    </div>

    <div class="main-layout">
        <div class="card">
            <h2 style="margin-top:0;"><i class="fas fa-calculator"></i> Scanner</h2>
            <div style="background:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:20px;">
                <input type="text" id="name" placeholder="Name (e.g. Mewtwo)">
                <div style="display:flex; gap:10px;">
                    <input type="number" id="att" placeholder="ATK (0-15)" max="15">
                    <input type="number" id="def" placeholder="DEF (0-15)" max="15">
                    <input type="number" id="hp" placeholder="HP (0-15)" max="15">
                </div>
                <button class="btn-analyze" onclick="addManual()"><i class="fas fa-search"></i> 분석하기</button>
            </div>
            <div style="border-top:2px dashed #eee; padding-top:20px;">
                <button class="btn-bulk" onclick="bulkGenerate()">
                    <i class="fas fa-layer-group"></i> 대량 생성 (50ea)
                </button>
            </div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;"><i class="fas fa-database"></i> Live Feed</h2>
                <button class="btn-manual" style="border:1px solid #ddd; background:#f8f9fa;" onclick="exportCSV()"><i class="fas fa-file-csv"></i> CSV 저장</button>
            </div>
            <div style="overflow-x:auto; max-height:600px; overflow-y:auto; margin-top:15px;">
                <table id="dataTable">
                    <thead><tr><th>ID</th><th>Name</th><th>Stats</th><th>IV</th><th>Grade</th><th>Analysis</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let list = []; let id = 1;
        // [DATA] Gen 1~8 대량 데이터베이스
        const POKEMON_DB = ["이상해꽃", "리자몽", "거북왕", "피카츄", "망나뇽", "뮤츠", "마기라스", "루기아", "번치코", "대짱이", "가디안", "게을킹", "한카리아스", "루카리오", "토게키스", "샹델라", "삼삼드래", "개굴닌자", "님피아", "따라큐", "드래펄트", "자시안", "무한다이노"];

        function addManual() {
            const n = document.getElementById('name').value || 'Unknown';
            const a = +document.getElementById('att').value;
            const d = +document.getElementById('def').value;
            const h = +document.getElementById('hp').value;
            if(a>15||d>15||h>15) { alert("0~15 사이 숫자를 입력하세요."); return; }
            process(n, a, d, h);
        }

        function bulkGenerate() {
            for(let i=0; i<50; i++) {
                const name = POKEMON_DB[Math.floor(Math.random() * POKEMON_DB.length)];
                process(name, Math.floor(Math.random()*16), Math.floor(Math.random()*16), Math.floor(Math.random()*16));
            }
        }

        function process(n, a, d, h) {
            const per = Math.round(((a+d+h)/45)*100);
            let t={l:"Normal", c:"bg-norm"};
            if(per===100) t={l:"PERFECT", c:"bg-perfect"};
            else if(a<=2 && d>=13 && h>=13) t={l:"PVP GEM", c:"bg-pvp"};
            else if(d===15 && h===15) t={l:"GYM TANK", c:"bg-tank"};
            else if(a===15 && per>=90) t={l:"RAID ATK", c:"bg-raid"};
            
            const grade = per===100?'4★':per>=82?'3★':per>=66?'2★':'1★';
            list.unshift({id:id++, n, a, d, h, per, grade, t});
            render();
        }

        function render() {
            document.querySelector('tbody').innerHTML = list.slice(0, 500).map(p => `
                <tr>
                    <td>#${p.id}</td><td style="font-weight:bold">${p.n}</td>
                    <td><span style="color:#e63946">${p.a}</span>/<span style="color:#2ec4b6">${p.d}</span>/<span style="color:#4361ee">${p.h}</span></td>
                    <td><b>${p.per}%</b></td><td>${p.grade}</td>
                    <td><span class="badge ${p.t.c}">${p.t.l}</span></td>
                </tr>`).join('');
            document.getElementById('totalCount').innerText = list.length;
            document.getElementById('perfectCount').innerText = list.filter(p=>p.per===100).length;
            document.getElementById('pvpCount').innerText = list.filter(p=>p.t.c==='bg-pvp').length;
            document.getElementById('avgIv').innerText = (list.length ? Math.round(list.reduce((a,b)=>a+b.per,0)/list.length) : 0) + "%";
        }

        function exportCSV() {
            let csv = "ID,Name,Att,Def,HP,IV,Grade,Type\\n";
            list.forEach(p=> csv+=`${p.id},${p.n},${p.a},${p.d},${p.h},${p.per},${p.grade},${p.t.l}\\n`);
            const blob = new Blob(["\\uFEFF"+csv],{type:'text/csv;charset=utf-8;'});
            const link=document.createElement("a"); link.href=URL.createObjectURL(blob);
            link.download=`pokemon_data.csv`; link.click();
        }
    </script>
</body>
</html>"""

# [WEB 2] 사용법 매뉴얼 페이지 (manual.html) - 생성 보장
MANUAL_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni Dashboard - 사용자 매뉴얼</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #4361ee; --text: #2b2d42; --bg: #f8f9fa; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        h1 { color: var(--primary); border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { margin-top: 30px; color: #333; display: flex; align-items: center; gap: 10px; }
        .step { background: #f8f9fa; padding: 15px; border-left: 4px solid var(--primary); margin: 10px 0; border-radius: 4px; }
        .badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.8rem; font-weight: bold; }
        .btn-back { display: inline-block; padding: 10px 20px; background: var(--primary); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
        .btn-back:hover { background: #3a53d0; }
        code { background: #eee; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="btn-back"><i class="fas fa-arrow-left"></i> 대시보드로 돌아가기</a>
        
        <h1>📘 Omni Dashboard 사용 설명서</h1>
        <p>포켓몬 개체값(IV)을 분석하고 대량의 데이터를 관리하는 통합 시스템 사용 가이드입니다.</p>

        <h2>1. 개체값(IV) 수동 분석</h2>
        <div class="step">
            <p>게임 내 <strong>[조사]</strong> 화면을 보고 수치를 입력하세요.</p>
            <ul>
                <li><strong>Name:</strong> 포켓몬 이름 (예: 망나뇽)</li>
                <li><strong>ATK / DEF / HP:</strong> 각 능력치를 <code>0</code> ~ <code>15</code> 사이의 숫자로 입력합니다.</li>
                <li><strong>분석하기 버튼:</strong> 클릭 시 하단 목록에 결과가 추가됩니다.</li>
            </ul>
        </div>

        <h2>2. 대량 생성 (Mass Generation)</h2>
        <div class="step">
            <p><strong>[대량 생성 (50ea)]</strong> 버튼을 클릭하면:</p>
            <ul>
                <li>1세대부터 8세대까지의 포켓몬이 무작위로 50마리 생성됩니다.</li>
                <li>각 포켓몬의 능력치도 랜덤으로 배정되어, <strong>전설의 포켓몬</strong>이나 <strong>이로치(가상)</strong> 확률을 시뮬레이션할 수 있습니다.</li>
            </ul>
        </div>

        <h2>3. 분석 등급 및 태그 설명</h2>
        <table style="width:100%; border-collapse: collapse; margin-top:10px;">
            <tr style="background:#eee;"><th style="padding:10px; text-align:left;">태그</th><th style="padding:10px; text-align:left;">설명</th></tr>
            <tr>
                <td style="padding:10px;"><span class="badge" style="background:#f50057">PERFECT</span></td>
                <td style="padding:10px;">모든 능력치가 15인 <strong>100% (4성)</strong> 완벽 개체입니다.</td>
            </tr>
            <tr>
                <td style="padding:10px;"><span class="badge" style="background:#7209b7">PVP GEM</span></td>
                <td style="padding:10px;">공격은 낮고 방어/체력이 높아 <strong>슈퍼/하이퍼리그</strong>에 최적화된 개체입니다.</td>
            </tr>
            <tr>
                <td style="padding:10px;"><span class="badge" style="background:#f72585">RAID ATK</span></td>
                <td style="padding:10px;">공격력이 15(MAX)이며 전체 등급이 높은 <strong>레이드 공격용</strong> 개체입니다.</td>
            </tr>
        </table>

        <h2>4. 데이터 내보내기</h2>
        <div class="step">
            <p>우측 상단의 <strong>[CSV 저장]</strong> 버튼을 누르면 현재 목록에 있는 모든 데이터를 엑셀 호환 파일(<code>.csv</code>)로 다운로드할 수 있습니다.</p>
        </div>
        
        <hr>
        <p style="text-align:center; color:#999;">Omni System v1.0.0 Manual</p>
    </div>
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
    print("🚀 [Ultimate Setup] 시스템 대량 구축 및 매뉴얼 파일 생성 시작...")
    
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
        
        # [핵심 수정] manual.html 명시적 생성
        if name == "omni-pokemon-web":
            print(f"   📘 [Info] '{name}' 서비스에 매뉴얼 파일 주입 중...")
            files[f"{base}/src/main/resources/static/index.html"] = DASHBOARD_SOURCE
            files[f"{base}/src/main/resources/static/manual.html"] = MANUAL_SOURCE

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

    # [검증] 매뉴얼 파일 생성 확인
    manual_path = "./services/omni-pokemon-web/src/main/resources/static/manual.html"
    if os.path.exists(manual_path):
        print("   ✅ [검증] manual.html 파일이 정상적으로 생성되었습니다.")
    else:
        print("   ❌ [오류] manual.html 파일 생성 실패!")

    print("✅ 파일 생성 완료. Maven 빌드 시작...")
    mvn = "mvn.cmd" if os.name == 'nt' else "mvn"
    for svc in SERVICES_CONFIG:
        subprocess.call(f"{mvn} clean package -f ./services/{svc['name']}/pom.xml -DskipTests -fn", shell=True)
    
    print("\n✨ 설치 완료!")
    print("👉 실행: docker-compose up --build")
    print("👉 대시보드: http://localhost:8086/index.html")
    print("👉 매뉴얼: http://localhost:8086/manual.html")

if __name__ == "__main__":
    run_setup()
