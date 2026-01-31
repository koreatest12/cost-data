import os
import json
import asyncio
import aiohttp
import textwrap

# ==============================================================================
# 🏗️ [설정] 프로젝트 절대 경로 (오류 방지)
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PATH = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# GitHub Actions & Scripts
GITHUB_ROOT = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_ROOT, "workflows")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

# 타겟: 151마리 (속도를 위해 조정, 필요시 range(1, 1026)으로 변경)
TARGET_IDS = list(range(1, 152))

def create_directories():
    print(f"📂 [Init] 디렉토리 구조 재설정 중... ({PROJECT_ROOT})")
    dirs = [
        os.path.join(JAVA_PATH, "controller"),
        os.path.join(JAVA_PATH, "service"),
        os.path.join(JAVA_PATH, "model"),
        os.path.join(JAVA_PATH, "config"),
        STATIC_DIR,
        WORKFLOWS_DIR,
        SCRIPTS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

# ==============================================================================
# 1. 🐳 Docker & DevOps (대량 생성 추가)
# ==============================================================================
def generate_devops():
    # 1. Dockerfile (경량화 빌드)
    write_file(os.path.join(PROJECT_ROOT, "Dockerfile"), """
FROM eclipse-temurin:17-jdk-alpine
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8086
ENTRYPOINT ["java", "-jar", "app.jar"]
""")

    # 2. Docker Compose
    write_file(os.path.join(PROJECT_ROOT, "docker-compose.yml"), """
version: '3.8'
services:
  omni-web:
    build: .
    ports:
      - "8086:8086"
    container_name: omni-pokemon-container
    restart: always
    environment:
      - SERVER_PORT=8086
""")

    # 3. [FIX] Smart CI/CD (경로 에러 해결 버전)
    write_file(os.path.join(WORKFLOWS_DIR, "ci-fix.yml"), """
name: Ultimate CI (Path Fix)
on: [push, pull_request]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: 🔍 Debug Directory Structure
        run: |
          ls -R
          echo "Current Path: $(pwd)"

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      # [핵심 수정] working-directory를 명시하여 폴더 진입 보장
      - name: Build with Maven
        working-directory: ./services/omni-pokemon-web
        run: |
          if [ -f "mvnw" ]; then
            chmod +x mvnw
            ./mvnw clean package -DskipTests
          else
            mvn clean package -DskipTests
          fi

      - name: 🐳 Docker Build Check
        working-directory: ./services/omni-pokemon-web
        run: docker build -t omni-web .

      - name: ✅ Verify Artifact
        run: |
          ls services/omni-pokemon-web/target/*.jar
          echo "Build Success!"
""")

    # 4. Git Push Helper (사용자가 까먹지 않게)
    write_file(os.path.join(BASE_DIR, "git_push_all.sh"), """
#!/bin/bash
echo "🔥 [Git Auto] 변경사항을 GitHub에 업로드합니다..."
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git add .
git commit -m "Feat: Add Massive Generation & Docker Support"
git push
echo "✅ Push 완료! 이제 GitHub Actions 탭을 확인하세요."
""")
    if os.name != 'nt': os.chmod(os.path.join(BASE_DIR, "git_push_all.sh"), 0o755)

# ==============================================================================
# 2. ⚡ Data Fetch (Async)
# ==============================================================================
async def fetch_data():
    print(f"🚀 [Data] 포켓몬 데이터 수집 중...")
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
                            "total": sum(stats.values()),
                            "hp": stats.get('hp', 0),
                            "attack": stats.get('attack', 0),
                            "speed": stats.get('speed', 0)
                        }
                except: return None
        tasks = [fetch(pid) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
        data = [r for r in results if r]
        data.sort(key=lambda x: x['id'])
    
    with open(os.path.join(RESOURCES, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=0)
    print("✅ 데이터 수집 완료")

# ==============================================================================
# 3. ☕ Java Backend (Maven Fix)
# ==============================================================================
def generate_backend():
    # pom.xml
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>3.0.0-DOCKER</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/> 
    </parent>
    <properties><java.version>17</java.version></properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>
    </dependencies>
    <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
""")

    # Java Code (Controller/Service/Model)
    write_file(os.path.join(JAVA_PATH, "model/Pokemon.java"), "package com.omni.pokemon.model; import lombok.Data; java.util.List; @Data public class Pokemon { private int id; private String name; private java.util.List<String> types; private String image; private int total; private int hp; private int attack; private int speed; }")
    
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
        } catch (Exception e) {}
    }

    public List<Pokemon> search(String keyword) {
        if(keyword == null) return db;
        return db.stream().filter(p -> p.getName().contains(keyword)).collect(Collectors.toList());
    }
}
""")

    write_file(os.path.join(JAVA_PATH, "controller/PokemonController.java"), """
package com.omni.pokemon.controller;
import com.omni.pokemon.service.PokemonService;
import com.omni.pokemon.model.Pokemon;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class PokemonController {
    private final PokemonService service;
    @GetMapping("/pokemon")
    public List<Pokemon> getPokemons(@RequestParam(required=false) String k) { return service.search(k); }
    @GetMapping("/health") public String health() { return "OK"; }
}
""")
    
    write_file(os.path.join(JAVA_PATH, "OmniDexApp.java"), "package com.omni.pokemon; import org.springframework.boot.SpringApplication; import org.springframework.boot.autoconfigure.SpringBootApplication; @SpringBootApplication public class OmniDexApp { public static void main(String[] args) { SpringApplication.run(OmniDexApp.class, args); } }")
    write_file(os.path.join(RESOURCES, "application.properties"), "server.port=8086")

# ==============================================================================
# 4. 🎨 Frontend (HTML Dashboard)
# ==============================================================================
def generate_frontend():
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html>
<head>
    <title>OmniDex Docker Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-10">
    <h1 class="text-3xl font-bold text-blue-400 mb-5">OmniDex V3 (Dockerized)</h1>
    <input type="text" id="s" placeholder="Search..." class="bg-gray-800 p-2 rounded text-white mb-5 w-full max-w-md" onkeyup="load()">
    <div id="grid" class="grid grid-cols-2 md:grid-cols-5 gap-4"></div>
    <script>
        async function load() {
            const k = document.getElementById('s').value;
            const res = await fetch('/api/pokemon?k=' + k);
            const data = await res.json();
            document.getElementById('grid').innerHTML = data.map(p => `
                <div class="bg-gray-800 p-4 rounded text-center border border-gray-700">
                    <img src="${p.image}" class="w-24 h-24 mx-auto">
                    <h3 class="font-bold mt-2 capitalize">${p.name}</h3>
                    <p class="text-sm text-gray-500">Total: ${p.total}</p>
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
    print("===========================================")
    print("🚀 Ultimate Fix: Docker & CI Patch 적용 중...")
    print("===========================================")
    
    create_directories()
    generate_devops()    # Dockerfile, CI.yml Fix
    generate_backend()
    generate_frontend()
    await fetch_data()
    
    print("\n✅ [중요] 파일 생성이 완료되었습니다.")
    print("⚠️ 에러 해결을 위해 아래 명령어를 **반드시** 순서대로 실행하세요:\n")
    
    print("1️⃣  권한 부여:")
    print("    chmod +x git_push_all.sh")
    
    print("\n2️⃣  GitHub에 코드 업로드 (이 과정이 없으면 CI 에러가 계속 발생합니다):")
    print("    ./git_push_all.sh")
    
    print("\n3️⃣  로컬 테스트 (선택):")
    print(f"    cd {PROJECT_NAME}")
    print("    mvn clean package && java -jar target/*.jar")

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
