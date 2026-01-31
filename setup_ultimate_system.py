import os
import json
import asyncio
import aiohttp
import time
import textwrap

# ==============================================================================
# 🏗️ [설정] 프로젝트 경로 및 타겟
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PATH = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# DevOps & Scripts
GITHUB_ROOT = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_ROOT, "workflows")
ACTIONS_DIR = os.path.join(GITHUB_ROOT, "actions/setup-claude")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

# 타겟 포켓몬 ID (1~151: 관동 지방 + 주요 전설) - 테스트 속도를 위해 151로 조정, 필요시 1025로 변경
TARGET_IDS = list(range(1, 152)) 

def create_directories():
    print(f"📂 [Init] 디렉토리 구조 생성 중... ({PROJECT_ROOT})")
    dirs = [
        os.path.join(JAVA_PATH, "controller"),
        os.path.join(JAVA_PATH, "service"),
        os.path.join(JAVA_PATH, "model"),
        os.path.join(JAVA_PATH, "config"),     # [NEW] 설정
        os.path.join(JAVA_PATH, "exception"),  # [NEW] 예외처리
        STATIC_DIR,
        WORKFLOWS_DIR,
        ACTIONS_DIR,
        SCRIPTS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

# ==============================================================================
# 1. 🛡️ Maven & MCP Context (AI 친화적 설정)
# ==============================================================================
def generate_config_files():
    # 1. pom.xml: SpringDoc OpenAPI (MCP 연동용 명세) 추가
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>2.0.0-MCP</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/> 
    </parent>
    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>

        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.3.0</version>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin>
        </plugins>
    </build>
</project>
""")

    # 2. application.properties
    write_file(os.path.join(RESOURCES, "application.properties"), """
server.port=8086
spring.application.name=OmniDex-MCP
management.endpoints.web.exposure.include=health,info,metrics
# Swagger / MCP Context
springdoc.api-docs.path=/v3/api-docs
springdoc.swagger-ui.path=/swagger-ui.html
""")

    # 3. [NEW] PROJECT_CONTEXT.md (AI 에이전트용)
    write_file(os.path.join(PROJECT_ROOT, "PROJECT_CONTEXT.md"), """
# OmniDex Project Context (for Claude/MCP)

## Architecture
- **Type**: Spring Boot 3.2 Web Application
- **Frontend**: Plain HTML5 + TailwindCSS + Chart.js (Single Page Dashboard)
- **Data Source**: Embedded JSON (fetched from PokéAPI during build)
- **Port**: 8086

## Key Commands
- Build: `./scripts/compile.sh`
- Run: `./scripts/run.sh`
- API Docs: `http://localhost:8086/v3/api-docs`

## Design Patterns
- Service Layer Pattern
- Global Exception Handling (@ControllerAdvice)
- DTO-less Simple Model (for lightweight performance)
""")

# ==============================================================================
# 2. ⚡ 데이터 수집 (비동기 엔진)
# ==============================================================================
async def fetch_data():
    print(f"🚀 [Data] {len(TARGET_IDS)}마리 포켓몬 데이터 수집 시작 (Async)...")
    semaphore = asyncio.Semaphore(50)
    
    async with aiohttp.ClientSession() as session:
        async def fetch(pid):
            async with semaphore:
                try:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                        if res.status != 200: return None
                        d = await res.json()
                        
                        # 한글 매핑 (샘플)
                        name_map = {1:"이상해씨", 4:"파이리", 7:"꼬부기", 25:"피카츄", 133:"이브이", 143:"잠만보", 150:"뮤츠"}
                        name = name_map.get(pid, d['name'])

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
    print(f"✅ 데이터 저장 완료: {len(data)}건 -> resources/data.json")

# ==============================================================================
# 3. ☕ Java Backend (Massive Generation)
# ==============================================================================
def generate_java():
    # 1. Config (OpenAPI)
    write_file(os.path.join(JAVA_PATH, "config/OpenApiConfig.java"), """
package com.omni.pokemon.config;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI omniDexOpenAPI() {
        return new OpenAPI()
                .info(new Info().title("OmniDex API").description("Pokemon Data Service for MCP & Web").version("v2.0"));
    }
}
""")

    # 2. Exception Handling
    write_file(os.path.join(JAVA_PATH, "exception/GlobalExceptionHandler.java"), """
package com.omni.pokemon.exception;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Object> handleAll(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", ex.getMessage(), "status", 500));
    }
}
""")

    # 3. Model
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

    # 4. Service (Enhanced Searching)
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
        } catch (Exception e) { System.err.println("❌ DB Load Failed: " + e.getMessage()); }
    }

    public List<Pokemon> search(String keyword, String sort, int limit) {
        var stream = db.stream();
        if (keyword != null && !keyword.isBlank()) {
            String k = keyword.toLowerCase();
            stream = stream.filter(p -> p.getName().contains(k) || String.valueOf(p.getId()).equals(k) || p.getTypes().contains(k));
        }
        
        Comparator<Pokemon> comp = Comparator.comparingInt(Pokemon::getId);
        if ("total".equals(sort)) comp = Comparator.comparingInt(Pokemon::getTotal).reversed();
        else if ("speed".equals(sort)) comp = Comparator.comparingInt(Pokemon::getSpeed).reversed();
        else if ("attack".equals(sort)) comp = Comparator.comparingInt(Pokemon::getAttack).reversed();
        else if ("name".equals(sort)) comp = Comparator.comparing(Pokemon::getName);
        
        return stream.sorted(comp).limit(limit).collect(Collectors.toList());
    }
    
    public Map<String, Object> getStats() {
        return Map.of(
            "totalCount", db.size(),
            "avgTotal", db.stream().mapToInt(Pokemon::getTotal).average().orElse(0),
            "topAttacker", db.stream().max(Comparator.comparingInt(Pokemon::getAttack)).map(Pokemon::getName).orElse("None")
        );
    }
}
""")

    # 5. Controller
    write_file(os.path.join(JAVA_PATH, "controller/PokemonController.java"), """
package com.omni.pokemon.controller;
import com.omni.pokemon.model.Pokemon;
import com.omni.pokemon.service.PokemonService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/pokemon")
@Tag(name = "Pokemon API", description = "Operations for Pokemon Data")
@RequiredArgsConstructor
public class PokemonController {
    private final PokemonService service;

    @Operation(summary = "Search Pokemon", description = "Search by keyword (name, type, id) with sorting")
    @GetMapping("/search")
    public List<Pokemon> search(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false, defaultValue = "id") String sort,
        @RequestParam(required = false, defaultValue = "100") int limit
    ) {
        return service.search(keyword, sort, limit);
    }

    @Operation(summary = "Get Statistics", description = "Returns aggregated statistics of the dataset")
    @GetMapping("/stats")
    public Map<String, Object> getStats() {
        return service.getStats();
    }
}
""")
    
    # 6. System Controller
    write_file(os.path.join(JAVA_PATH, "controller/SystemController.java"), """
package com.omni.pokemon.controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SystemController {
    @GetMapping("/api/system/health")
    public String health() { return "OK"; }
}
""")

    # 7. Main App
    write_file(os.path.join(JAVA_PATH, "OmniDexApp.java"), """
package com.omni.pokemon;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class OmniDexApp {
    public static void main(String[] args) { SpringApplication.run(OmniDexApp.class, args); }
}
""")

# ==============================================================================
# 4. 📜 Scripts (운영 및 컴파일 자동화)
# ==============================================================================
def generate_scripts():
    # 1. Compile Script
    write_file(os.path.join(SCRIPTS_DIR, "compile.sh"), """
#!/bin/bash
echo "🔨 Building OmniDex..."
cd "$(dirname "$0")/../"
if [ -f "mvnw" ]; then
    ./mvnw clean package -DskipTests
else
    mvn clean package -DskipTests
fi
echo "✅ Build Complete!"
""")

    # 2. Run Script
    write_file(os.path.join(SCRIPTS_DIR, "run.sh"), """
#!/bin/bash
cd "$(dirname "$0")/../"
JAR_FILE=$(find target -name "*.jar" | head -n 1)
if [ -z "$JAR_FILE" ]; then
    echo "❌ JAR file not found. Run compile.sh first."
    exit 1
fi
echo "🚀 Starting OmniDex on port 8086..."
java -jar "$JAR_FILE"
""")
    
    # 실행 권한 부여 (Linux/Mac)
    if os.name != 'nt':
        os.chmod(os.path.join(SCRIPTS_DIR, "compile.sh"), 0o755)
        os.chmod(os.path.join(SCRIPTS_DIR, "run.sh"), 0o755)

# ==============================================================================
# 5. 🤖 GitHub Actions (Claude MCP 연동 & CI)
# ==============================================================================
def generate_devops():
    # setup-claude Action
    write_file(os.path.join(ACTIONS_DIR, "action.yml"), """
name: 'Setup Claude Code'
description: 'Installs Claude Code CLI for MCP interactions'
inputs:
  anthropic-key:
    description: 'Anthropic API Key'
    required: true
runs:
  using: "composite"
  steps:
    - shell: bash
      run: |
        if ! command -v claude &> /dev/null; then
             echo "⬇️ Installing Claude Code..."
             curl -fsSL https://claude.ai/install.sh | bash
             echo "$HOME/.local/bin" >> $GITHUB_PATH
        fi
        echo "ANTHROPIC_API_KEY=${{ inputs.anthropic-key }}" >> $GITHUB_ENV
""")

    # CI Workflow
    write_file(os.path.join(WORKFLOWS_DIR, "ci-mcp-check.yml"), """
name: Ultimate CI (MCP & Build)
on: [push, pull_request]

jobs:
  build-and-verify:
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

      - name: 🔍 Verify Artifacts
        run: |
          if [ ! -f services/omni-pokemon-web/target/*.jar ]; then
            echo "❌ Build Failed: JAR not found"
            exit 1
          fi
          echo "✅ JAR File created successfully."

      # (Optional) Claude Code Setup Example
      # - name: Setup Claude Code
      #   uses: ./.github/actions/setup-claude
      #   with:
      #     anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
""")

# ==============================================================================
# 6. 🎨 Frontend (HTML) - 간소화
# ==============================================================================
def generate_frontend():
    # 기존 코드와 동일하거나 유사한 형태의 UI 생성 (여기서는 핵심만 포함)
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>OmniDex MCP</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white p-10">
    <h1 class="text-3xl font-bold mb-5">OmniDex Dashboard (MCP Enabled)</h1>
    <p class="mb-5 text-slate-400">Powered by Spring Boot 3 & OpenAPI</p>
    
    <div class="flex gap-2 mb-8">
        <input id="q" type="text" placeholder="Search..." class="p-2 rounded bg-slate-800 border border-slate-600 w-full max-w-md">
        <button onclick="search()" class="bg-blue-600 px-4 py-2 rounded">Search</button>
    </div>
    
    <div id="grid" class="grid grid-cols-2 md:grid-cols-4 gap-4"></div>

    <script>
        async function search() {
            const q = document.getElementById('q').value;
            const res = await fetch(`/api/pokemon/search?keyword=${q}`);
            const data = await res.json();
            const grid = document.getElementById('grid');
            grid.innerHTML = data.map(p => `
                <div class="bg-slate-800 p-4 rounded-lg border border-slate-700">
                    <img src="${p.image}" class="w-24 h-24 mx-auto">
                    <h3 class="text-center font-bold mt-2">${p.name}</h3>
                    <p class="text-center text-xs text-slate-500">ID: ${p.id} | Total: ${p.total}</p>
                </div>
            `).join('');
        }
        search(); // init
    </script>
</body>
</html>
""")

# ==============================================================================
# 🔥 메인 실행
# ==============================================================================
async def main():
    print("🚀 [Ultimate Setup] MCP 기반 대규모 프로젝트 생성 시작...")
    
    create_directories()
    generate_config_files()  # Maven + MCP Docs
    await fetch_data()       # Async Data Fetch
    generate_java()          # Massive Java Code
    generate_scripts()       # Shell Scripts
    generate_devops()        # CI/CD
    generate_frontend()      # HTML

    print("\n" + "="*50)
    print("🎉 생성 완료! 다음 단계를 수행하세요:")
    print("1. cd services/omni-pokemon-web")
    print("2. chmod +x scripts/*.sh (Linux/Mac)")
    print("3. ./scripts/compile.sh")
    print("4. ./scripts/run.sh")
    print(f"5. 접속: http://localhost:8086 (UI) / http://localhost:8086/v3/api-docs (MCP Context)")
    print("="*50)

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
