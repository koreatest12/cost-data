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

# [DASHBOARD V4] Gen 1~8 대량 데이터 탑재 버전
DASHBOARD_SOURCE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni System Dashboard Pro (Gen 1-8)</title>
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
        .stat-val { font-size: 2.2rem; font-weight: 800; color: var(--primary); }
        .stat-sub { font-size: 0.9rem; color: #666; margin-top: 5px; }

        /* Input & Buttons */
        input { width: 100%; padding: 12px; margin-bottom: 12px; border: 2px solid #edf2f4; border-radius: 10px; box-sizing: border-box; }
        button { width: 100%; padding: 14px; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-analyze { background: var(--primary); color: white; }
        .btn-analyze:hover { background: #3a53d0; }
        .btn-bulk { background: var(--success); color: white; margin-top: 10px; }
        .btn-bulk:hover { background: #25a296; }
        .btn-export { background: #2b2d42; color: white; width: auto; padding: 10px 20px; }

        /* Table */
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; }
        th { text-align: left; padding: 15px; background: #f8f9fa; color: #666; border-bottom: 2px solid #eee; position: sticky; top: 0; }
        td { padding: 15px; border-bottom: 1px solid #f1f1f1; }
        
        /* Badges */
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
        <div>
            <span style="background:#eef2ff; color:var(--primary); padding:8px 16px; border-radius:30px; font-weight:bold;">
                <i class="fas fa-server"></i> 8 Services Active
            </span>
        </div>
    </div>

    <div class="grid-stats">
        <div class="card"><h3>Total Analyzed</h3><div class="stat-val" id="totalCount">0</div><div class="stat-sub">Pokémons</div></div>
        <div class="card"><h3>Perfect (4★)</h3><div class="stat-val" id="perfectCount" style="color:#f50057">0</div><div class="stat-sub">IV 100%</div></div>
        <div class="card"><h3>PVP Gems</h3><div class="stat-val" id="pvpCount" style="color:#7209b7">0</div><div class="stat-sub">Battle Ready</div></div>
        <div class="card"><h3>Avg. Potential</h3><div class="stat-val" id="avgIv">0%</div><div class="stat-sub">Overall Quality</div></div>
    </div>

    <div class="main-layout">
        <div class="card">
            <h2 style="margin-top:0;"><i class="fas fa-calculator"></i> Scanner</h2>
            <div style="background:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:20px;">
                <input type="text" id="name" placeholder="Name (e.g. Rayquaza)">
                <div style="display:flex; gap:10px;">
                    <input type="number" id="att" placeholder="ATK (0-15)" max="15">
                    <input type="number" id="def" placeholder="DEF (0-15)" max="15">
                    <input type="number" id="hp" placeholder="HP (0-15)" max="15">
                </div>
                <button class="btn-analyze" onclick="addManual()"><i class="fas fa-search"></i> Analyze</button>
            </div>
            <div style="border-top:2px dashed #eee; padding-top:20px;">
                <button class="btn-bulk" onclick="bulkGenerate()">
                    <i class="fas fa-layer-group"></i> Mass Gen (50ea)
                </button>
                <div style="text-align:center; font-size:0.8rem; color:#999; margin-top:10px;">
                    Supports Gen 1 ~ Gen 8 Data
                </div>
            </div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;"><i class="fas fa-database"></i> Live Feed</h2>
                <button class="btn-export" onclick="exportCSV()"><i class="fas fa-file-csv"></i> Export</button>
            </div>
            <div style="overflow-x:auto; max-height:600px; overflow-y:auto; margin-top:15px;">
                <table id="dataTable">
                    <thead><tr><th>ID</th><th>Name</th><th>Stats</th><th>IV</th><th>Grade</th><th>Bot Analysis</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let list = []; let id = 1;

        // [DATA] Gen 1 ~ Gen 8 Database
        const POKEMON_DB = [
            // Gen 1 (Kanto)
            "이상해꽃", "리자몽", "거북왕", "피카츄", "라이츄", "나인테일", "푸린", "괴력몬", "팬텀", "롱스톤", "나시", "탕구리", "럭키", "캥카", "갸라도스", "라프라스", "메타몽", "이브이", "샤미드", "쥬피썬더", "부스터", "잠만보", "망나뇽", "뮤츠", "뮤",
            // Gen 2 (Johto)
            "메가니움", "블레이범", "장크로다일", "토게틱", "전룡", "마릴리", "왕구리", "해피너스", "헤라크로스", "무장조", "델빌", "킹드라", "해피너스", "마기라스", "루기아", "칠색조", "세레비",
            // Gen 3 (Hoenn)
            "나무킹", "번치코", "대짱이", "가디안", "버섯모", "게을킹", "입치트", "플라이곤", "파비코리", "밀로틱", "보만다", "메타그로스", "레지락", "라티아스", "가이오가", "그란돈", "레쿠쟈", "지라치", "테오키스",
            // Gen 4 (Sinnoh)
            "토대부기", "초염몽", "엠페르트", "렌트라", "로즈레이드", "한카리아스", "루카리오", "자포코일", "토게키스", "리피아", "글레이시아", "맘모꾸리", "엘레이드", "거대코뿌리", "디아루가", "펄기아", "히드런", "기라티나", "크레세리아", "다크라이", "아르세우스",
            // Gen 5 (Unova)
            "샤로다", "염무왕", "대검귀", "몰드류", "엘풍", "불비달마", "조로아크", "샹델라", "액스라이즈", "골루그", "절각참", "워글", "삼삼드래", "불카모스", "코바르온", "테라키온", "볼트로스", "레시라무", "제크로무", "큐레무",
            // Gen 6 (Kalos)
            "브리가론", "마폭시", "개굴닌자", "파이어로", "님피아", "킬가르도", "미끄래곤", "대로트", "제르네아스", "이벨타르", "지가르데", "디안시",
            // Gen 7 (Alola)
            "모크나이퍼", "어흥염", "누리레느", "투구뿌논", "시마사리", "라란티스", "이븐곰", "갑주무사", "미믹큐", "솔가레오", "루나아라", "텅비드", "매시붕", "철화구야", "종이신도", "마샤도", "제라오라", "멜메탈",
            // Gen 8 (Galar)
            "고릴타", "에이스번", "인텔리레온", "아머까오", "이올브", "석탄산", "스트린더", "다태우지네", "오롱털", "가로막구리", "산호르곤", "창파나이트", "빙큐보", "드래펄트", "자시안", "자마젠타", "무한다이노", "우라오스"
        ];

        function addManual() {
            const n = document.getElementById('name').value || 'Unknown';
            const a = +document.getElementById('att').value;
            const d = +document.getElementById('def').value;
            const h = +document.getElementById('hp').value;
            if(a>15||d>15||h>15) { alert("Stats 0-15"); return; }
            process(n, a, d, h);
        }

        function bulkGenerate() {
            // 한번에 50마리 생성
            for(let i=0; i<50; i++) {
                const name = POKEMON_DB[Math.floor(Math.random() * POKEMON_DB.length)];
                const a = Math.floor(Math.random() * 16);
                const d = Math.floor(Math.random() * 16);
                const h = Math.floor(Math.random() * 16);
                process(name, a, d, h);
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
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = list.slice(0, 500).map(p => `
                <tr>
                    <td>#${p.id}</td><td style="font-weight:bold">${p.n}</td>
                    <td><span style="color:#e63946">${p.a}</span>/<span style="color:#2ec4b6">${p.d}</span>/<span style="color:#4361ee">${p.h}</span></td>
                    <td><b>${p.per}%</b></td><td>${p.grade}</td>
                    <td><span class="badge ${p.t.c}">${p.t.l}</span></td>
                </tr>`).join('');
            
            document.getElementById('totalCount').innerText = list.length;
            document.getElementById('perfectCount').innerText = list.filter(p=>p.per===100).length;
            document.getElementById('pvpCount').innerText = list.filter(p=>p.t.c==='bg-pvp').length;
            const avg = list.length ? Math.round(list.reduce((a,b)=>a+b.per,0)/list.length) : 0;
            document.getElementById('avgIv').innerText = avg + "%";
        }

        function exportCSV() {
            let csv = "ID,Name,Att,Def,HP,IV,Grade,Type\\n";
            list.forEach(p=> csv+=`${p.id},${p.n},${p.a},${p.d},${p.h},${p.per},${p.grade},${p.t.l}\\n`);
            const blob = new Blob(["\\uFEFF"+csv],{type:'text/csv;charset=utf-8;'});
            const link=document.createElement("a"); link.href=URL.createObjectURL(blob);
            link.download=`pokemon_gen1-8_${new Date().getTime()}.csv`; link.click();
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
    print("🚀 [Ultimate Setup] 시스템 대량 구축 시작 (Gen 1-8 DB 탑재)...")
    
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
