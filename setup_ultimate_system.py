import os
import json
import asyncio
import aiohttp
import time

# --- 📁 프로젝트 설정 ---
BASE_DIR = "."  # 현재 디렉토리에 생성
SRC_MAIN = os.path.join(BASE_DIR, "src/main")
JAVA_ROOT = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")
GITHUB_DIR = os.path.join(BASE_DIR, ".github")
WORKFLOW_DIR = os.path.join(GITHUB_DIR, "workflows")

DIRS = {
    "controller": os.path.join(JAVA_ROOT, "controller"),
    "service": os.path.join(JAVA_ROOT, "service"),
    "model": os.path.join(JAVA_ROOT, "model"),
    "workflows": WORKFLOW_DIR
}

# --- 🚀 타겟 데이터 (1~151마리 + 전설) ---
TARGET_IDS = list(range(1, 152)) + [1007, 1008]

def create_dirs():
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    print("📁 디렉토리 구조 생성 완료")

# --- ⚙️ 1. Maven (pom.xml) - 컴파일 및 빌드 설정 ---
def create_pom():
    pom = """
    <project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <modelVersion>4.0.0</modelVersion>
        <groupId>com.omni</groupId>
        <artifactId>omni-pokemon-web</artifactId>
        <version>1.0.0</version>
        <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>3.2.0</version>
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
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <optional>true</optional>
            </dependency>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-actuator</artifactId>
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
    """
    with open("pom.xml", "w", encoding="utf-8") as f: f.write(pom)

# --- 🛡️ 2. Dependabot & Claude Workflow 생성 ---
def create_workflows():
    # Dependabot
    dependabot = """
    version: 2
    updates:
      - package-ecosystem: "maven"
        directory: "/"
        schedule: {interval: "daily"}
      - package-ecosystem: "github-actions"
        directory: "/"
        schedule: {interval: "daily"}
    """
    with open(os.path.join(GITHUB_DIR, "dependabot.yml"), "w") as f: f.write(dependabot)

    # Main CI Pipeline (빌드 및 배포 테스트)
    ci_workflow = """
    name: 🚀 Main Build & Health Check
    on: [push, workflow_dispatch]
    
    jobs:
      build-and-test:
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
            run: mvn clean package -DskipTests
            
          - name: Start Server (Background)
            run: |
              nohup java -jar target/*.jar > app.log 2>&1 &
              echo "PID=$!" >> $GITHUB_ENV
              
          - name: ⏳ Wait for Server (Health Check)
            run: |
              echo "Waiting for server to start..."
              # 30초 동안 5초 간격으로 Health Check 시도 (Exit Code 7 방지)
              for i in {1..10}; do
                if curl -s http://localhost:8080/actuator/health | grep 'UP'; then
                  echo "✅ Server is UP!"
                  exit 0
                fi
                echo "zzz... ($i/10)"
                sleep 5
              done
              echo "❌ Server failed to start."
              cat app.log
              exit 1
    """
    with open(os.path.join(WORKFLOW_DIR, "ci-pipeline.yml"), "w") as f: f.write(ci_workflow)

# --- 🐍 3. 데이터 수집 (Async) ---
async def fetch_data():
    print("🚀 포켓몬 데이터 수집 중...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for pid in TARGET_IDS:
            tasks.append(session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}"))
        responses = await asyncio.gather(*tasks)
        
        data_list = []
        for res in responses:
            if res.status == 200:
                d = await res.json()
                stats = {s['stat']['name']: s['base_stat'] for s in d['stats']}
                data_list.append({
                    "id": d['id'],
                    "name": d['name'].capitalize(),
                    "types": [t['type']['name'] for t in d['types']],
                    "image": d['sprites']['other']['official-artwork']['front_default'],
                    "total": sum(stats.values()),
                    "stats": stats
                })
    
    with open(os.path.join(RESOURCES, "data.json"), "w") as f:
        json.dump(data_list, f)
    print(f"✅ {len(data_list)}마리 데이터 저장 완료")

# --- ☕ 4. Java 소스 코드 ---
def create_java():
    # Model
    with open(os.path.join(DIRS['model'], "Pokemon.java"), "w") as f:
        f.write("""
        package com.omni.pokemon.model;
        import lombok.Data;
        import java.util.List;
        import java.util.Map;
        @Data
        public class Pokemon {
            private int id; private String name; private List<String> types;
            private String image; private int total; private Map<String, Integer> stats;
        }
        """)

    # Service
    with open(os.path.join(DIRS['service'], "PokemonService.java"), "w") as f:
        f.write("""
        package com.omni.pokemon.service;
        import com.fasterxml.jackson.databind.ObjectMapper;
        import com.fasterxml.jackson.core.type.TypeReference;
        import com.omni.pokemon.model.Pokemon;
        import org.springframework.stereotype.Service;
        import jakarta.annotation.PostConstruct;
        import java.io.InputStream;
        import java.util.List;
        import java.util.ArrayList;

        @Service
        public class PokemonService {
            private List<Pokemon> db = new ArrayList<>();
            
            @PostConstruct
            public void init() {
                try {
                    InputStream is = getClass().getResourceAsStream("/data.json");
                    if(is != null) db = new ObjectMapper().readValue(is, new TypeReference<List<Pokemon>>(){});
                } catch(Exception e) { e.printStackTrace(); }
            }
            public List<Pokemon> getAll() { return db; }
        }
        """)

    # Controller
    with open(os.path.join(DIRS['controller'], "PokemonController.java"), "w") as f:
        f.write("""
        package com.omni.pokemon.controller;
        import com.omni.pokemon.model.Pokemon;
        import com.omni.pokemon.service.PokemonService;
        import org.springframework.web.bind.annotation.GetMapping;
        import org.springframework.web.bind.annotation.RestController;
        import lombok.RequiredArgsConstructor;
        import java.util.List;

        @RestController
        @RequiredArgsConstructor
        public class PokemonController {
            private final PokemonService service;
            @GetMapping("/api/pokemons")
            public List<Pokemon> list() { return service.getAll(); }
        }
        """)

    # Main App
    with open(os.path.join(JAVA_ROOT, "App.java"), "w") as f:
        f.write("""
        package com.omni.pokemon;
        import org.springframework.boot.SpringApplication;
        import org.springframework.boot.autoconfigure.SpringBootApplication;
        @SpringBootApplication
        public class App {
            public static void main(String[] args) { SpringApplication.run(App.class, args); }
        }
        """)
    
    # Application Properties (Actuator용)
    with open(os.path.join(RESOURCES, "application.properties"), "w") as f:
        f.write("server.port=8080\nmanagement.endpoints.web.exposure.include=health,info")

# --- 🖥️ 5. Frontend (HTML) ---
def create_html():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Gemini OmniDex</title>
    <style>
        body { background:#2d3436; color:white; font-family:sans-serif; text-align:center; }
        .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:10px; padding:20px; }
        .card { background:#353b48; padding:10px; border-radius:10px; }
        img { width:100px; }
    </style>
    </head>
    <body>
        <h1>🔥 Gemini OmniDex</h1>
        <div id="grid" class="grid"></div>
        <script>
            fetch('/api/pokemons').then(r=>r.json()).then(data=>{
                document.getElementById('grid').innerHTML = data.map(p=>`
                    <div class="card">
                        <img src="${p.image}">
                        <h3>${p.name}</h3>
                        <p>Total: ${p.total}</p>
                    </div>
                `).join('');
            });
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(html)

async def main():
    create_dirs()
    create_pom()
    create_workflows()
    await fetch_data()
    create_java()
    create_html()
    print("✅ 모든 파일 생성 완료!")

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
