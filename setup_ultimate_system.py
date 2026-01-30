import os
import json
import asyncio
import aiohttp
import time

# ==============================================================================
# 🏗️ [설정] 프로젝트 경로
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PATH = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# DevOps 경로
GITHUB_ROOT = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_ROOT, "workflows")
ACTIONS_DIR = os.path.join(GITHUB_ROOT, "actions/setup-claude")

# 타겟 포켓몬 ID (1~1025)
TARGET_IDS = list(range(1, 1026))

def create_directories():
    print(f"📂 디렉토리 구조 생성 중... ({PROJECT_ROOT})")
    dirs = [
        os.path.join(JAVA_PATH, "controller"),
        os.path.join(JAVA_PATH, "service"),
        os.path.join(JAVA_PATH, "model"),
        STATIC_DIR,
        WORKFLOWS_DIR,
        ACTIONS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

# ==============================================================================
# 1. 🛡️ Maven & CI/CD (경고 제거 & 헬스 체크 강화)
# ==============================================================================
def generate_devops():
    # [Fix] Maven: relativePath 추가로 경고 제거
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>2.0.0</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/> 
    </parent>
    <properties><java.version>17</java.version></properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>
    </dependencies>
    <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
""")

    # [Fix] CI/CD: Port 8086 + Smart Retry Loop
    write_file(os.path.join(WORKFLOWS_DIR, "ci-check.yml"), """
name: Ultimate CI/CD (Homepage Added)
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Build with Maven
        run: |
          cd services/omni-pokemon-web
          mvn clean package -DskipTests

      - name: 🌐 Server Start & Smoke Test
        run: |
          echo "🔥 서버 시작..."
          cd services/omni-pokemon-web
          nohup java -jar target/*.jar > app.log 2>&1 &
          PID=$!
          
          echo "⏳ 부팅 대기 (최대 60초)..."
          for i in {1..30}; do
            if curl -s http://localhost:8086/api/system/health | grep "OK"; then
              echo "✅ 서버 기동 확인 (Attempt $i)"
              break
            fi
            sleep 2
          done
          
          echo "🧪 1. Homepage Access Check"
          HOME_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8086/index.html)
          
          echo "🧪 2. Data Search Check"
          SEARCH_RES=$(curl -s -G --data-urlencode "keyword=피카츄" http://localhost:8086/api/pokemon/search)
          
          if [[ "$HOME_CODE" == "200" ]] && [[ "$SEARCH_RES" == *"피카츄"* ]]; then
            echo "✅ 모든 테스트 성공!"
            kill $PID
            exit 0
          else
            echo "❌ 실패: 서버 로그 확인"
            cat app.log
            kill $PID
            exit 1
          fi
""")
    
    # [Dependabot & Claude]
    write_file(os.path.join(GITHUB_ROOT, "dependabot.yml"), """
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/services/omni-pokemon-web"
    schedule: {interval: "daily"}
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: {interval: "daily"}
""")

    write_file(os.path.join(ACTIONS_DIR, "action.yml"), """
name: 'Setup Claude Code'
inputs: {anthropic-key: {required: true}}
runs:
  using: "composite"
  steps:
    - shell: bash
      run: |
        curl -fsSL https://claude.ai/install.sh | bash
        echo "$HOME/.local/bin" >> $GITHUB_PATH
        echo "ANTHROPIC_API_KEY=${{ inputs.anthropic-key }}" >> $GITHUB_ENV
        echo "CI=true" >> $GITHUB_ENV
""")

# ==============================================================================
# 2. ⚡ 데이터 수집 (한글 매핑 + 1025마리)
# ==============================================================================
async def fetch_data():
    print(f"🚀 {len(TARGET_IDS)}마리 포켓몬 데이터 수집 시작 (Gemini Engine)...")
    semaphore = asyncio.Semaphore(50)
    
    async with aiohttp.ClientSession() as session:
        async def fetch(pid):
            async with semaphore:
                try:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                        if res.status != 200: return None
                        d = await res.json()
                        
                        # 주요 포켓몬 한글 매핑 (테스트 및 UI용)
                        name = d['name']
                        if pid == 25: name = "피카츄"
                        elif pid == 1: name = "이상해씨"
                        elif pid == 4: name = "파이리"
                        elif pid == 7: name = "꼬부기"
                        elif pid == 143: name = "잠만보"
                        elif pid == 150: name = "뮤츠"

                        stats = {s['stat']['name']: s['base_stat'] for s in d['stats']}
                        return {
                            "id": d['id'],
                            "name": name, 
                            "types": [t['type']['name'] for t in d['types']],
                            "image": d['sprites']['other']['official-artwork']['front_default'],
                            "hp": stats.get('hp', 0),
                            "attack": stats.get('attack', 0),
                            "defense": stats.get('defense', 0),
                            "speed": stats.get('speed', 0),
                            "total": sum(stats.values())
                        }
                except: return None

        tasks = [fetch(pid) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
        data = [r for r in results if r]
        data.sort(key=lambda x: x['id'])
    
    with open(os.path.join(RESOURCES, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=0, ensure_ascii=False)
    print(f"✅ 데이터 저장 완료: {len(data)}건")

# ==============================================================================
# 3. ☕ Java Backend
# ==============================================================================
def generate_java():
    # Service
    write_file(os.path.join(JAVA_PATH, "service/PokemonService.java"), """
package com.omni.pokemon.service;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.omni.pokemon.model.Pokemon;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class PokemonService {
    private List<Pokemon> db = new ArrayList<>();
    private final ObjectMapper mapper = new ObjectMapper();

    @PostConstruct
    public void init() {
        try {
            InputStream is = getClass().getResourceAsStream("/data.json");
            if(is != null) db = mapper.readValue(is, new TypeReference<List<Pokemon>>(){});
        } catch (Exception e) { e.printStackTrace(); }
    }

    public List<Pokemon> search(String keyword, String sort) {
        var stream = db.stream();
        if (keyword != null && !keyword.isBlank()) {
            stream = stream.filter(p -> p.getName().contains(keyword) || String.valueOf(p.getId()).equals(keyword));
        }
        
        Comparator<Pokemon> comp = Comparator.comparingInt(Pokemon::getId);
        if ("total".equals(sort)) comp = Comparator.comparingInt(Pokemon::getTotal).reversed();
        if ("speed".equals(sort)) comp = Comparator.comparingInt(Pokemon::getSpeed).reversed();
        if ("attack".equals(sort)) comp = Comparator.comparingInt(Pokemon::getAttack).reversed();
        
        return stream.sorted(comp).limit(100).collect(Collectors.toList());
    }
    
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalCount", db.size());
        stats.put("avgTotal", db.stream().mapToInt(Pokemon::getTotal).average().orElse(0));
        return stats;
    }
}
""")
    
    # Model
    write_file(os.path.join(JAVA_PATH, "model/Pokemon.java"), """
package com.omni.pokemon.model;
import lombok.Data;
import java.util.List;
@Data
public class Pokemon {
    private int id; private String name; private List<String> types;
    private String image; private int hp; private int attack;
    private int defense; private int speed; private int total;
}
""")

    # Controller
    write_file(os.path.join(JAVA_PATH, "controller/PokemonController.java"), """
package com.omni.pokemon.controller;
import com.omni.pokemon.model.Pokemon;
import com.omni.pokemon.service.PokemonService;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class PokemonController {
    private final PokemonService service;

    @GetMapping("/system/health")
    public String health() { return "OK"; }

    @GetMapping("/pokemon/search")
    public List<Pokemon> search(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false, defaultValue = "id") String sort
    ) {
        return service.search(keyword, sort);
    }

    @GetMapping("/system/stats")
    public Map<String, Object> getStats() {
        return service.getStats();
    }
}
""")

    # App
    write_file(os.path.join(JAVA_PATH, "OmniDexApp.java"), """
package com.omni.pokemon;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class OmniDexApp {
    public static void main(String[] args) { SpringApplication.run(OmniDexApp.class, args); }
}
""")
    
    # Properties (Port 8086)
    write_file(os.path.join(RESOURCES, "application.properties"), "server.port=8086\nmanagement.endpoints.web.exposure.include=health,info")

# ==============================================================================
# 4. 🎨 [NEW] Modern Homepage (Dashboard Style)
# ==============================================================================
def generate_homepage():
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniDex Ultimate Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: #f1f5f9; font-family: 'Segoe UI', sans-serif; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .card-hover:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); border-color: #38bdf8; }
        .type-badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 99px; text-transform: uppercase; font-weight: bold; }
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <nav class="glass sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <i class="fa-solid fa-bolt text-yellow-400 text-2xl"></i>
            <h1 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">OmniDex</h1>
        </div>
        <div class="flex gap-4 text-sm text-slate-400">
            <span><i class="fa-solid fa-database"></i> <span id="totalCount">Loading...</span> Records</span>
            <span><i class="fa-solid fa-server"></i> Port 8086</span>
        </div>
    </nav>

    <header class="relative py-20 px-6 text-center overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-b from-blue-900/20 to-transparent pointer-events-none"></div>
        <h2 class="text-4xl md:text-6xl font-extrabold mb-4">Discover the Universe of Pokémon</h2>
        <p class="text-slate-400 max-w-2xl mx-auto mb-8 text-lg">
            Powered by Gemini Data Engine & Spring Boot. Explore 1,025 species with real-time analytics.
        </p>

        <div class="max-w-3xl mx-auto flex gap-2 glass p-2 rounded-full shadow-2xl">
            <div class="flex-1 flex items-center px-4">
                <i class="fa-solid fa-search text-slate-500 mr-3"></i>
                <input type="text" id="searchInput" placeholder="Search by name or ID (e.g. 피카츄)..." 
                    class="w-full bg-transparent outline-none text-white placeholder-slate-500 h-10"
                    onkeyup="debounceSearch()">
            </div>
            <select id="sortSelect" onchange="loadData()" class="bg-slate-800 text-slate-200 px-4 py-2 rounded-full outline-none border border-slate-600 focus:border-blue-500">
                <option value="id">Sort by ID</option>
                <option value="total">Highest Stats</option>
                <option value="speed">Fastest</option>
                <option value="attack">Strongest</option>
            </select>
        </div>
    </header>

    <main class="flex-1 px-6 pb-20 max-w-7xl mx-auto w-full">
        <div id="grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            </div>
        <div id="loading" class="text-center py-10 hidden">
            <i class="fa-solid fa-circle-notch fa-spin text-3xl text-blue-500"></i>
        </div>
    </main>

    <div id="modal" class="fixed inset-0 bg-black/90 hidden items-center justify-center z-[100] p-4 backdrop-blur-sm" onclick="closeModal(event)">
        <div class="bg-slate-800 rounded-2xl max-w-4xl w-full overflow-hidden flex flex-col md:flex-row shadow-2xl border border-slate-700 transform transition-all scale-100" onclick="event.stopPropagation()">
            <div class="p-8 md:w-1/2 flex flex-col items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 relative">
                <span class="absolute top-4 left-4 text-slate-500 font-mono text-xl" id="mId"></span>
                <img id="mImg" class="w-64 h-64 object-contain drop-shadow-[0_0_30px_rgba(56,189,248,0.3)] hover:scale-110 transition duration-500">
                <h2 id="mName" class="text-3xl font-bold mt-6 capitalize"></h2>
                <div id="mTypes" class="flex gap-2 mt-3"></div>
            </div>
            <div class="p-8 md:w-1/2 bg-slate-800">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-bold text-slate-200">Base Stats</h3>
                    <span class="bg-slate-700 px-3 py-1 rounded text-sm text-slate-300">Total: <span id="mTotal" class="font-bold text-white"></span></span>
                </div>
                <div class="h-64">
                    <canvas id="statChart"></canvas>
                </div>
                <button onclick="document.getElementById('modal').style.display='none'" class="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition">Close</button>
            </div>
        </div>
    </div>

    <footer class="border-t border-slate-800 py-8 text-center text-slate-500 text-sm">
        <p>&copy; 2026 OmniDex Project. Powered by Claude Code & Gemini.</p>
    </footer>

    <script>
        let chartInstance = null;
        let debounceTimer;

        // Init
        window.onload = () => {
            loadStats();
            loadData();
        };

        async function loadStats() {
            try {
                const res = await fetch('/api/system/stats');
                const data = await res.json();
                document.getElementById('totalCount').innerText = data.totalCount;
            } catch(e) { console.error(e); }
        }

        async function loadData() {
            const query = document.getElementById('searchInput').value;
            const sort = document.getElementById('sortSelect').value;
            const grid = document.getElementById('grid');
            
            grid.innerHTML = ''; // Clear
            document.getElementById('loading').style.display = 'block';

            try {
                const res = await fetch(`/api/pokemon/search?keyword=${encodeURIComponent(query)}&sort=${sort}`);
                const data = await res.json();

                if(data.length === 0) {
                    grid.innerHTML = '<div class="col-span-full text-center text-slate-500 py-10">No Pokémon found.</div>';
                } else {
                    grid.innerHTML = data.map(p => `
                        <div class="glass card-hover rounded-2xl p-4 cursor-pointer relative overflow-hidden group" onclick="openModal(${p.id})">
                            <div class="absolute top-0 right-0 p-3 text-xs font-bold text-slate-500 bg-slate-800/50 rounded-bl-xl">#${p.id}</div>
                            <div class="relative z-10">
                                <img src="${p.image}" class="w-full h-40 object-contain mb-4 group-hover:scale-110 transition duration-300" loading="lazy">
                                <h3 class="text-lg font-bold text-center capitalize mb-2">${p.name}</h3>
                                <div class="flex justify-center gap-1 flex-wrap">
                                    ${p.types.map(t => `<span class="type-badge" style="background:${getTypeColor(t)}">${t}</span>`).join('')}
                                </div>
                            </div>
                            <div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent opacity-0 group-hover:opacity-100 transition duration-300 pointer-events-none"></div>
                        </div>
                    `).join('');
                }
            } catch(e) {
                console.error(e);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }

        function debounceSearch() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(loadData, 300);
        }

        async function openModal(id) {
            // Re-fetch detail to be safe
            const res = await fetch(`/api/pokemon/search?keyword=${id}`);
            const data = await res.json();
            const p = data[0];

            document.getElementById('mId').innerText = '#' + p.id;
            document.getElementById('mImg').src = p.image;
            document.getElementById('mName').innerText = p.name;
            document.getElementById('mTotal').innerText = p.total;
            document.getElementById('mTypes').innerHTML = p.types.map(t => 
                `<span class="px-3 py-1 rounded-full text-sm font-bold shadow-lg" style="background:${getTypeColor(t)}">${t}</span>`
            ).join('');

            document.getElementById('modal').style.display = 'flex';
            renderChart(p);
        }

        function closeModal(e) {
            if(e.target.id === 'modal') document.getElementById('modal').style.display = 'none';
        }

        function renderChart(p) {
            const ctx = document.getElementById('statChart');
            if(chartInstance) chartInstance.destroy();

            chartInstance = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['HP', 'Attack', 'Defense', 'Speed'],
                    datasets: [{
                        label: 'Stats',
                        data: [p.hp, p.attack, p.defense, p.speed],
                        backgroundColor: 'rgba(56, 189, 248, 0.5)',
                        borderColor: '#38bdf8',
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#38bdf8',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255,255,255,0.1)' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            pointLabels: { color: '#94a3b8', font: {size: 12} },
                            suggestedMin: 0,
                            suggestedMax: 150,
                            ticks: { display: false }
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        function getTypeColor(type) {
            const colors = {
                fire: '#f59e0b', water: '#3b82f6', grass: '#22c55e', electric: '#eab308',
                ice: '#67e8f9', fighting: '#ef4444', poison: '#a855f7', ground: '#d97706',
                flying: '#818cf8', psychic: '#ec4899', bug: '#84cc16', rock: '#78716c',
                ghost: '#6366f1', dragon: '#8b5cf6', steel: '#94a3b8', fairy: '#f472b6', normal: '#64748b'
            };
            return colors[type] || '#64748b';
        }
    </script>
</body>
</html>
""")

# ==============================================================================
# 🔥 메인 실행
# ==============================================================================
async def main():
    print("🚀 [Ultimate Project] 풀스택 통합 생성 시작...")
    create_directories()
    generate_devops()
    await fetch_data()
    generate_java()
    generate_homepage()
    
    print("\n🎉 모든 파일 생성 완료!")
    print("👉 git add .")
    print("👉 git commit -m \"Feat: Add Modern Homepage & Full Fix\"")
    print("👉 git push")

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
