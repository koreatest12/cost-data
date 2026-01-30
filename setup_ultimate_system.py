import os
import json
import asyncio
import aiohttp
import time

# ==============================================================================
# 🏗️ [설정] 프로젝트 경로 및 구조 정의
# ==============================================================================
# GitHub Actions 가상 머신 경로 문제 해결을 위해 상대 경로 명확화
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
# 1. 🛡️ CI/CD & DevOps (Exit Code 7 해결 및 기능 통합)
# ==============================================================================
def generate_devops():
    # [Fix] Main Pipeline: 스마트 헬스 체크 & 로그 출력 추가
    write_file(os.path.join(WORKFLOWS_DIR, "ci-cd-pipeline.yml"), f"""
name: 🚀 Build & Deploy (Fixed)
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build-deploy:
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
          cd {PROJECT_NAME}
          mvn clean package -DskipTests

      - name: Start Application (Background)
        run: |
          cd {PROJECT_NAME}
          # nohup으로 백그라운드 실행 및 로그 저장
          nohup java -jar target/*.jar > app.log 2>&1 &
          echo "⏳ Server launching..."
          echo "PID=$!" >> $GITHUB_ENV
          sleep 10 # 초기 구동 대기

      - name: 🧪 Health Check (Smart Retry)
        run: |
          echo "Waiting for Actuator..."
          # 60초 동안 2초 간격으로 반복 확인 (Exit Code 7 방지)
          for i in {{1..30}}; do
            STATUS=$(curl -s -o /dev/null -w "%{{http_code}}" http://localhost:8080/actuator/health)
            if [ "$STATUS" == "200" ]; then
              echo "✅ Server is UP and Healthy!"
              exit 0
            fi
            echo "zzz... ($i/30) [Status: $STATUS]"
            sleep 2
          done
          echo "❌ Server failed to start."
          exit 1

      - name: 🔍 Debug Logs (If Failed)
        if: failure() || cancelled()
        run: |
          echo "=== APP LOGS ==="
          cat {PROJECT_NAME}/app.log
""")

    # [Claude] Feature Builder Workflow
    write_file(os.path.join(WORKFLOWS_DIR, "03-feature-builder.yml"), """
name: 🏗️ Feature Builder (Claude)
on:
  workflow_dispatch:
    inputs:
      requirement: {description: 'Feature Request', required: true}
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Claude
        uses: ./.github/actions/setup-claude
        with: {anthropic-key: '${{ secrets.ANTHROPIC_API_KEY }}'}
      - name: Implement
        run: |
          claude -p "TASK: ${{ inputs.requirement }}"
""")

    # [Dependabot]
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

    # [Setup Claude Action]
    write_file(os.path.join(ACTIONS_DIR, "action.yml"), """
name: 'Setup Claude Code'
inputs: {anthropic-key: {required: true}}
runs:
  using: "composite"
  steps:
    - shell: bash
      run: curl -fsSL https://claude.ai/install.sh | bash
""")

    # [Maven] pom.xml (Actuator 필수)
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

# ==============================================================================
# 2. ⚡ 데이터 수집 (Gemini Engine Mockup - Async)
# ==============================================================================
async def fetch_data():
    print(f"🚀 {len(TARGET_IDS)}마리 포켓몬 데이터 수집 시작...")
    semaphore = asyncio.Semaphore(50)
    
    async with aiohttp.ClientSession() as session:
        async def fetch(pid):
            async with semaphore:
                try:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                        if res.status != 200: return None
                        d = await res.json()
                        stats = {s['stat']['name']: s['base_stat'] for s in d['stats']}
                        return {
                            "id": d['id'],
                            "name": d['name'],
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
        json.dump(data, f, indent=0)
    print(f"✅ 데이터 저장 완료: {len(data)}건")

# ==============================================================================
# 3. ☕ Java Backend (Robust Error Handling)
# ==============================================================================
def generate_java():
    # Service (안전한 리소스 로딩)
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
            // JAR 내부/외부 어디서든 읽을 수 있도록 getResourceAsStream 사용
            InputStream is = getClass().getResourceAsStream("/data.json");
            if (is == null) {
                System.err.println("❌ Critical: data.json not found in resources!");
            } else {
                db = mapper.readValue(is, new TypeReference<List<Pokemon>>(){});
                System.out.println("✅ DB Loaded: " + db.size() + " records");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public List<Pokemon> search(String query) {
        if (query == null || query.isBlank()) return db.stream().limit(100).collect(Collectors.toList());
        return db.stream()
            .filter(p -> p.getName().toLowerCase().contains(query.toLowerCase()))
            .limit(100)
            .collect(Collectors.toList());
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

@RestController
@RequestMapping("/api/pokemons")
@RequiredArgsConstructor
public class PokemonController {
    private final PokemonService service;
    @GetMapping
    public List<Pokemon> get(@RequestParam(required=false) String query) {
        return service.search(query);
    }
}
""")

    # Main App
    write_file(os.path.join(JAVA_PATH, "OmniDexApp.java"), """
package com.omni.pokemon;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class OmniDexApp {
    public static void main(String[] args) { SpringApplication.run(OmniDexApp.class, args); }
}
""")
    
    # Properties (Actuator 오픈)
    write_file(os.path.join(RESOURCES, "application.properties"), "server.port=8080\nmanagement.endpoints.web.exposure.include=health,info")

# ==============================================================================
# 4. 🎨 Frontend (Modern UI)
# ==============================================================================
def generate_html():
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OmniDex</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <body class="bg-slate-900 text-white p-5">
        <h1 class="text-3xl font-bold text-center mb-5 text-blue-400">💎 OmniDex Ultimate</h1>
        <div class="max-w-xl mx-auto mb-5">
            <input type="text" id="q" placeholder="Search Pokemon..." class="w-full p-3 rounded bg-slate-800 border border-slate-600 focus:border-blue-500 outline-none" onkeyup="load(this.value)">
        </div>
        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4"></div>
        <script>
            async function load(q='') {
                const res = await fetch(`/api/pokemons?query=${q}`);
                const data = await res.json();
                document.getElementById('grid').innerHTML = data.map(p => `
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 hover:scale-105 transition duration-200">
                        <div class="text-right text-xs text-slate-500">#${p.id}</div>
                        <img src="${p.image}" class="w-full h-32 object-contain my-2">
                        <h3 class="text-center font-bold capitalize">${p.name}</h3>
                        <div class="flex justify-center gap-1 mt-2">${p.types.map(t=>`<span class="text-xs px-2 py-1 bg-slate-700 rounded-full">${t}</span>`).join('')}</div>
                    </div>
                `).join('');
            }
            load();
        </script>
    </body>
</html>
""")

# ==============================================================================
# 🔥 메인 실행
# ==============================================================================
async def main():
    print("🚀 [Fix & Deploy] 시스템 재구축 시작...")
    create_directories()
    generate_devops()
    await fetch_data()
    generate_java()
    generate_html()
    print("\n✅ 모든 생성 완료!")
    print("👉 1. 'git add .'")
    print("👉 2. 'git commit -m \"Fix: Complete System Restore\"'")
    print("👉 3. 'git push'")

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
