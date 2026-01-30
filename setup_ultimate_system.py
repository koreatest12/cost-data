import os
import json
import asyncio
import aiohttp
import time

# ==============================================================================
# 🏗️ [설정] 프로젝트 경로 및 구조 정의
# ==============================================================================
PROJECT_ROOT = "services/omni-pokemon-web"
SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PKG = "com.omni.pokemon"
JAVA_PATH = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# GitHub Actions & Claude 설정 경로
GITHUB_ROOT = ".github"
WORKFLOWS_DIR = os.path.join(GITHUB_ROOT, "workflows")
ACTIONS_DIR = os.path.join(GITHUB_ROOT, "actions/setup-claude")

# 타겟 포켓몬 ID (1세대~9세대 전체 + 주요 폼)
# 테스트를 위해 범위를 조절하려면 아래 range를 수정하세요 (예: range(1, 152))
TARGET_IDS = list(range(1, 1026)) 

# ==============================================================================
# 1. 디렉토리 및 유틸리티 함수
# ==============================================================================
def create_directory_structure():
    dirs = [
        os.path.join(JAVA_PATH, "controller"),
        os.path.join(JAVA_PATH, "service"),
        os.path.join(JAVA_PATH, "model"),
        os.path.join(JAVA_PATH, "config"),
        STATIC_DIR,
        WORKFLOWS_DIR,
        ACTIONS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✅ 디렉토리 구조 생성 완료")

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

# ==============================================================================
# 2. DevOps & CI/CD 설정 (Claude, Dependabot, Maven)
# ==============================================================================
def generate_devops_files():
    # [Dependabot] 의존성 자동 업데이트
    write_file(os.path.join(GITHUB_ROOT, "dependabot.yml"), """
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/services/omni-pokemon-web"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "daily"

  - package-ecosystem: "docker"
    directory: "/services/omni-pokemon-web"
    schedule:
      interval: "weekly"
""")

    # [Maven] pom.xml (Swagger, Actuator, Lombok 포함)
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
    </parent>
    <properties>
        <java.version>17</java.version>
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
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.3.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
""")

    # [Docker] Dockerfile
    write_file(os.path.join(PROJECT_ROOT, "Dockerfile"), """
FROM eclipse-temurin:17-jdk-alpine
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
""")

    # [GitHub Action] Main Pipeline (Build + Test + Health Check)
    write_file(os.path.join(WORKFLOWS_DIR, "ci-cd-pipeline.yml"), """
name: 🚀 Build, Test & Deploy
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: maven

    - name: Build with Maven
      run: |
        cd services/omni-pokemon-web
        mvn clean package -DskipTests

    - name: Run Application (Background)
      run: |
        cd services/omni-pokemon-web
        nohup java -jar target/*.jar > app.log 2>&1 &
        echo "⏳ Server is starting..."
        sleep 10

    - name: Health Check (Wait for Actuator)
      run: |
        echo "Waiting for service to be UP..."
        for i in {1..30}; do
          if curl -s http://localhost:8080/actuator/health | grep 'UP'; then
            echo "✅ Service is Healthy!"
            exit 0
          fi
          echo "Retrying... ($i/30)"
          sleep 2
        done
        echo "❌ Service failed to start."
        cat services/omni-pokemon-web/app.log
        exit 1
""")

    # [Claude Action] Setup Script
    write_file(os.path.join(ACTIONS_DIR, "action.yml"), """
name: 'Setup Claude Code'
description: 'Installs Claude CLI'
inputs:
  anthropic-key:
    required: true
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

    print("✅ DevOps 파일 생성 완료")

# ==============================================================================
# 3. 데이터 수집 (Async)
# ==============================================================================
async def fetch_pokemon_data():
    print(f"🚀 {len(TARGET_IDS)}마리 포켓몬 데이터 수집 시작 (Gemini Engine)...")
    
    semaphore = asyncio.Semaphore(50) # 동시 요청 제한
    data_list = []

    async with aiohttp.ClientSession() as session:
        async def fetch(pid):
            async with semaphore:
                try:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                        if res.status != 200: return None
                        d = await res.json()
                    
                    # 간단하게 핵심 데이터만 추출 (속도 최적화)
                    stats = {s['stat']['name']: s['base_stat'] for s in d['stats']}
                    return {
                        "id": d['id'],
                        "name": d['name'], # 영어 이름 (한글 변환은 클라이언트나 별도 API 필요하나 여기선 단순화)
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
        data_list = [r for r in results if r]
        data_list.sort(key=lambda x: x['id'])

    # JSON 저장
    with open(os.path.join(RESOURCES, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=0)
    print(f"✅ {len(data_list)}개 데이터 data.json 저장 완료")

# ==============================================================================
# 4. Java Backend 코드 생성 (Gemini Style Optimization)
# ==============================================================================
def generate_backend_code():
    # Model
    write_file(os.path.join(JAVA_PATH, "model/Pokemon.java"), """
package com.omni.pokemon.model;
import lombok.Data;
import java.util.List;

@Data
public class Pokemon {
    private int id;
    private String name;
    private List<String> types;
    private String image;
    private int hp;
    private int attack;
    private int defense;
    private int speed;
    private int total;
}
""")

    # Service (Resource Loader & Stream Filter)
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
            System.out.println("🔥 DB Loaded: " + db.size());
        } catch (Exception e) { e.printStackTrace(); }
    }

    public List<Pokemon> search(String query, String sort) {
        var stream = db.stream();
        if (query != null && !query.isBlank()) {
            stream = stream.filter(p -> p.getName().toLowerCase().contains(query.toLowerCase()));
        }
        
        Comparator<Pokemon> comp = Comparator.comparingInt(Pokemon::getId);
        if ("total".equals(sort)) comp = Comparator.comparingInt(Pokemon::getTotal).reversed();
        if ("speed".equals(sort)) comp = Comparator.comparingInt(Pokemon::getSpeed).reversed();
        
        return stream.sorted(comp).limit(100).collect(Collectors.toList()); // 성능상 100개 제한
    }
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

@RestController
@RequestMapping("/api/pokemons")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class PokemonController {
    private final PokemonService service;

    @GetMapping
    public List<Pokemon> getPokemons(
        @RequestParam(required = false) String query,
        @RequestParam(required = false, defaultValue = "id") String sort
    ) {
        return service.search(query, sort);
    }
}
""")

    # Application Main
    write_file(os.path.join(JAVA_PATH, "OmniDexApplication.java"), """
package com.omni.pokemon;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OmniDexApplication {
    public static void main(String[] args) {
        SpringApplication.run(OmniDexApplication.class, args);
    }
}
""")
    
    # application.properties
    write_file(os.path.join(RESOURCES, "application.properties"), "server.port=8080")
    print("✅ Java 백엔드 코드 생성 완료")

# ==============================================================================
# 5. Frontend 코드 생성 (Modern UI)
# ==============================================================================
def generate_frontend_code():
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniDex Ultimate</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: sans-serif; }
        .card { background: #1e293b; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); border-color: #38bdf8; }
        .type-badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; }
    </style>
</head>
<body class="p-6">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
            <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">💎 OmniDex</h1>
            <div class="flex gap-4">
                <input type="text" id="search" placeholder="Search..." class="bg-slate-800 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500">
                <select id="sort" class="bg-slate-800 border border-slate-600 rounded px-4 py-2">
                    <option value="id">ID</option>
                    <option value="total">Total Stats</option>
                    <option value="speed">Speed</option>
                </select>
            </div>
        </header>

        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6"></div>
    </div>

    <div id="modal" class="fixed inset-0 bg-black/80 hidden items-center justify-center p-4 z-50" onclick="this.style.display='none'">
        <div class="bg-slate-800 p-6 rounded-2xl max-w-2xl w-full flex gap-8 items-center" onclick="event.stopPropagation()">
            <div class="text-center w-1/3">
                <img id="mImg" class="w-full drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">
                <h2 id="mName" class="text-2xl font-bold mt-4 capitalize"></h2>
            </div>
            <div class="w-2/3 h-64">
                <canvas id="chart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let chartInstance = null;
        async function load(q='', s='id') {
            const res = await fetch(`/api/pokemons?query=${q}&sort=${s}`);
            const data = await res.json();
            const grid = document.getElementById('grid');
            grid.innerHTML = data.map(p => `
                <div class="card border border-slate-700 rounded-xl p-4 cursor-pointer" onclick="openModal(${p.id})">
                    <div class="text-right text-xs text-slate-500">#${p.id}</div>
                    <img src="${p.image}" class="w-full h-32 object-contain mx-auto my-2" loading="lazy">
                    <h3 class="text-lg font-bold capitalize text-center">${p.name}</h3>
                    <div class="flex justify-center gap-2 mt-2">
                        ${p.types.map(t => `<span class="type-badge bg-slate-700 border border-slate-600">${t}</span>`).join('')}
                    </div>
                    <div class="text-center mt-3 text-sm text-slate-400">Total: ${p.total}</div>
                </div>
            `).join('');
        }

        async function openModal(id) {
            // 실제 구현에선 id로 다시 fetch 할 수 있으나 여기선 DOM 활용 예시
            const res = await fetch(`/api/pokemons?query=${id}`); // ID 검색 가정
            const [p] = await res.json(); // 첫번째 결과
            if(!p) return;

            document.getElementById('mImg').src = p.image;
            document.getElementById('mName').innerText = p.name;
            document.getElementById('modal').style.display = 'flex';

            const ctx = document.getElementById('chart');
            if(chartInstance) chartInstance.destroy();
            
            chartInstance = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['HP', 'Atk', 'Def', 'Spd'],
                    datasets: [{
                        label: 'Stats',
                        data: [p.hp, p.attack, p.defense, p.speed],
                        backgroundColor: 'rgba(56, 189, 248, 0.4)',
                        borderColor: '#38bdf8',
                        pointBackgroundColor: '#fff'
                    }]
                },
                options: {
                    scales: { r: { suggestedMin: 0, suggestedMax: 150, grid: { color: 'rgba(255,255,255,0.1)' } } }
                }
            });
        }

        document.getElementById('search').addEventListener('input', (e) => load(e.target.value, document.getElementById('sort').value));
        document.getElementById('sort').addEventListener('change', (e) => load(document.getElementById('search').value, e.target.value));
        load();
    </script>
</body>
</html>
""")
    print("✅ Frontend 코드 생성 완료")

# ==============================================================================
# 🔥 메인 실행
# ==============================================================================
async def main():
    print("🚀 [OmniDex] 프로젝트 대량 생성 시작...")
    
    create_directory_structure()
    generate_devops_files()
    await fetch_pokemon_data()
    generate_backend_code()
    generate_frontend_code()
    
    print("\n🎉 모든 작업이 완료되었습니다!")
    print(f"👉 생성된 위치: {os.path.abspath(PROJECT_ROOT)}")
    print("👉 다음 단계:")
    print("  1. git add .")
    print("  2. git commit -m 'Initial massive generation'")
    print("  3. git push")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
