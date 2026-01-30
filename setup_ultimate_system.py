import os
import sys
import json
import asyncio
import aiohttp
import time
import textwrap

# --- 📁 기본 경로 설정 ---
BASE_DIR = "services/omni-pokemon-web"
SRC_MAIN = os.path.join(BASE_DIR, "src/main")
JAVA_ROOT = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# DevOps 경로
GITHUB_DIR = os.path.join(BASE_DIR, ".github")
WORKFLOW_DIR = os.path.join(GITHUB_DIR, "workflows")
ACTION_DIR = os.path.join(GITHUB_DIR, "actions/setup-claude")

DIRS = {
    "controller": os.path.join(JAVA_ROOT, "controller"),
    "service": os.path.join(JAVA_ROOT, "service"),
    "model": os.path.join(JAVA_ROOT, "model"),
    "workflows": WORKFLOW_DIR,
    "actions": ACTION_DIR
}

# --- 🔥 데이터 타겟 (1~1025) ---
TARGET_IDS = list(range(1, 1026))

def create_structure():
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    print("📁 프로젝트 및 DevOps 디렉토리 구조 생성 완료")

# --- ⚙️ Maven 설정 (POM.xml) ---
def create_pom_xml():
    pom = """
    <project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <modelVersion>4.0.0</modelVersion>
        <groupId>com.omni</groupId>
        <artifactId>omni-pokemon-web</artifactId>
        <version>2.1.0</version>
        <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>3.2.0</version>
            <relativePath/>
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
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
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
    """
    with open(os.path.join(BASE_DIR, "pom.xml"), "w", encoding="utf-8") as f:
        f.write(pom)

# --- 🐳 Docker 설정 ---
def create_dockerfile():
    dockerfile = """
    FROM eclipse-temurin:17-jdk-alpine
    VOLUME /tmp
    ARG JAR_FILE=target/*.jar
    COPY ${JAR_FILE} app.jar
    ENTRYPOINT ["java","-jar","/app.jar"]
    """
    with open(os.path.join(BASE_DIR, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile)

# --- 🤖 Claude Code & Dependabot 설정 (핵심 추가) ---
def create_devops_config():
    # 1. Dependabot (의존성 관리)
    dependabot = """
    version: 2
    updates:
      # [GitHub Actions] CI/CD 및 Claude Code 워크플로우 최신화
      - package-ecosystem: "github-actions"
        directory: "/"
        schedule:
          interval: "daily"
          time: "09:00"
          timezone: "Asia/Seoul"
        labels: ["ci", "actions", "claude-automation"]
        commit-message:
          prefix: "ci(actions)"

      # [Maven] Spring Boot 의존성 관리
      - package-ecosystem: "maven"
        directory: "/"
        schedule:
          interval: "weekly"
          timezone: "Asia/Seoul"
        open-pull-requests-limit: 10
        groups:
          spring-boot:
            patterns: ["org.springframework.boot*", "org.springframework*"]
        labels: ["backend", "java"]
        commit-message:
          prefix: "build(deps)"

      # [Docker] Base Image 업데이트
      - package-ecosystem: "docker"
        directory: "/"
        schedule:
          interval: "weekly"
        labels: ["docker"]
    """
    with open(os.path.join(GITHUB_DIR, "dependabot.yml"), "w", encoding="utf-8") as f:
        f.write(dependabot)

    # 2. Setup Claude Action (커스텀 액션)
    setup_action = """
    name: 'Setup Claude Code'
    description: 'Installs Claude Code CLI and persists authentication'
    inputs:
      anthropic-key:
        description: 'API Key'
        required: true
    runs:
      using: "composite"
      steps:
        - name: Install Claude Code
          shell: bash
          run: |
            curl -fsSL https://claude.ai/install.sh | bash
            echo "$HOME/.local/bin" >> $GITHUB_PATH
        - name: Configure Auth
          shell: bash
          run: |
            echo "ANTHROPIC_API_KEY=${{ inputs.anthropic-key }}" >> $GITHUB_ENV
            echo "CI=true" >> $GITHUB_ENV
            echo "CLAUDE_HEADLESS=true" >> $GITHUB_ENV
            git config --global user.name "Claude Bot"
            git config --global user.email "bot@claude.ai"
    """
    with open(os.path.join(ACTION_DIR, "action.yml"), "w", encoding="utf-8") as f:
        f.write(setup_action)

    # 3. Workflow: Feature Builder (기능 구현)
    feature_wf = """
    name: 🏗️ Feature Builder (Dispatch)
    on:
      workflow_dispatch:
        inputs:
          requirement:
            description: '구현할 기능 설명'
            required: true
          branch_name:
            description: '브랜치 이름 (옵션)'
            required: false
    jobs:
      build-feature:
        runs-on: ubuntu-latest
        permissions:
          contents: write
          pull-requests: write
        steps:
          - uses: actions/checkout@v3
          - uses: ./.github/actions/setup-claude
            with:
              anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
          - name: Implement Feature
            id: coding
            env:
              BRANCH_NAME: ${{ inputs.branch_name || format('feature/claude-{0}', github.run_id) }}
            run: |
              git checkout -b $BRANCH_NAME
              claude -p "TASK: ${{ inputs.requirement }} \n CONTEXT: Spring Boot Java Project. \n ACTION: Implement feature."
              if [[ -n $(git status --porcelain) ]]; then
                git add .
                COMMIT=$(git diff --staged | claude -p "Commit msg for this diff")
                git commit -m "$COMMIT"
                git push origin $BRANCH_NAME
                echo "pushed=true" >> $GITHUB_OUTPUT
                echo "branch=$BRANCH_NAME" >> $GITHUB_OUTPUT
              fi
          - name: Create PR
            if: steps.coding.outputs.pushed == 'true'
            env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
            run: gh pr create --title "✨ Feature: ${{ inputs.requirement }}" --body "Implemented by Claude" --head ${{ steps.coding.outputs.branch }} --base main
    """
    with open(os.path.join(WORKFLOW_DIR, "03-feature-builder.yml"), "w", encoding="utf-8") as f:
        f.write(feature_wf)

    # 4. Workflow: Auto Review (코드 리뷰)
    review_wf = """
    name: 🤖 Claude Code Reviewer
    on:
      pull_request:
        types: [opened, synchronize]
    jobs:
      review:
        runs-on: ubuntu-latest
        permissions:
          contents: read
          pull-requests: write
        steps:
          - uses: actions/checkout@v3
            with: { fetch-depth: 0 }
          - uses: ./.github/actions/setup-claude
            with:
              anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
          - name: Analyze Diff
            env:
              PR_NUMBER: ${{ github.event.pull_request.number }}
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
            run: |
              git diff origin/${{ github.base_ref }} > diff.txt
              if [ ! -s diff.txt ]; then exit 0; fi
              cat diff.txt | claude -p "Review Java code for bugs/security. Output Markdown. If good, say 'LGTM'." > review.md
              if ! grep -q "LGTM" review.md; then gh pr comment $PR_NUMBER --body-file review.md; fi
    """
    with open(os.path.join(WORKFLOW_DIR, "01-pr-auto-review.yml"), "w", encoding="utf-8") as f:
        f.write(review_wf)

    # 5. Workflow: Nightly Refactor (리팩토링)
    refactor_wf = """
    name: 🧹 Nightly Refactor
    on:
      schedule:
        - cron: '0 18 * * *' # KST 03:00 AM
    jobs:
      refactor:
        runs-on: ubuntu-latest
        permissions:
          contents: write
          pull-requests: write
        steps:
          - uses: actions/checkout@v3
          - uses: ./.github/actions/setup-claude
            with:
              anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
          - name: Cleanup Code
            run: |
              BRANCH="refactor/nightly-$(date +%Y%m%d)"
              git checkout -b $BRANCH
              claude -p "Scan Java codebase for unused imports, formatting issues, and potential NPEs. Fix them."
              if [[ -n $(git status --porcelain) ]]; then
                git add .
                git commit -m "🧹 Nightly cleanup"
                git push origin $BRANCH
                gh pr create --title "🧹 Nightly Refactor" --body "Automated cleanup" --base main
              fi
            env:
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    """
    with open(os.path.join(WORKFLOW_DIR, "99-nightly-refactor.yml"), "w", encoding="utf-8") as f:
        f.write(refactor_wf)


# --- 🌐 데이터 수집 (Async) ---
async def fetch_pokemon(session, pid, semaphore):
    async with semaphore:
        try:
            async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                if res.status != 200: return None
                data = await res.json()

            ko_name = data['name']
            description = "데이터 없음"
            genus = "분류 없음"

            async with session.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}") as res_spec:
                if res_spec.status == 200:
                    spec = await res_spec.json()
                    for n in spec['names']:
                        if n['language']['name'] == 'ko':
                            ko_name = n['name']; break
                    for entry in spec['flavor_text_entries']:
                        if entry['language']['name'] == 'ko':
                            description = entry['flavor_text'].replace("\n", " "); break
                    for g in spec['genera']:
                        if g['language']['name'] == 'ko':
                            genus = g['genus']; break

            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            total = sum(stats.values())
            types = [t['type']['name'] for t in data['types']]
            abilities = [a['ability']['name'] for a in data['abilities'] if not a['is_hidden']]
            
            grade = "C"
            if total >= 670: grade = "SSS (초전설)"
            elif total >= 600: grade = "S (전설/600족)"
            elif total >= 540: grade = "A+ (엘리트)"
            elif total >= 500: grade = "A (우수)"
            elif total >= 450: grade = "B+ (준수)"
            elif total >= 400: grade = "B (보통)"

            return {
                "id": pid, "name": ko_name, "engName": data['name'].capitalize(),
                "genus": genus, "types": types,
                "imageUrl": data['sprites']['other']['official-artwork']['front_default'] or data['sprites']['front_default'],
                "description": description, "height": data['height'] / 10.0, "weight": data['weight'] / 10.0,
                "abilities": abilities, "hp": stats.get('hp', 0), "attack": stats.get('attack', 0),
                "defense": stats.get('defense', 0), "spAttack": stats.get('special-attack', 0),
                "spDefense": stats.get('special-defense', 0), "speed": stats.get('speed', 0),
                "total": total, "grade": grade
            }
        except Exception: return None

async def fetch_all_and_save():
    print(f"🚀 {len(TARGET_IDS)}마리 포켓몬 데이터 수집 중 (Claude Engine Powered)...")
    semaphore = asyncio.Semaphore(50)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_pokemon(session, pid, semaphore) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
    
    valid_data = [r for r in results if r is not None]
    valid_data.sort(key=lambda x: x['id'])

    with open(os.path.join(RESOURCES, "data.json"), "w", encoding="utf-8") as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=0)
    print(f"✅ 데이터베이스 구축 완료: {len(valid_data)} 개체")

# --- ☕ Java 소스 생성 ---
def create_java_files():
    # Model
    with open(os.path.join(DIRS["model"], "Pokemon.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.model;
        import lombok.Data;
        import lombok.AllArgsConstructor;
        import lombok.NoArgsConstructor;
        import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
        import java.util.List;

        @Data @AllArgsConstructor @NoArgsConstructor
        @JsonIgnoreProperties(ignoreUnknown = true)
        public class Pokemon {
            private int id; private String name; private String engName; private String genus;
            private List<String> types; private String imageUrl; private String description;
            private double height; private double weight; private List<String> abilities;
            private int hp; private int attack; private int defense;
            private int spAttack; private int spDefense; private int speed;
            private int total; private String grade;
        }
        """)

    # Service
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write("""
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
                    if (is != null) db = mapper.readValue(is, new TypeReference<List<Pokemon>>() {});
                } catch (Exception e) { e.printStackTrace(); }
            }

            public List<Pokemon> search(String keyword, String type, String sort, int limit) {
                var stream = db.stream();
                if (keyword != null && !keyword.isEmpty()) {
                    String k = keyword.toLowerCase();
                    stream = stream.filter(p -> p.getName().contains(keyword) || 
                        (p.getEngName() != null && p.getEngName().toLowerCase().contains(k)) ||
                        String.valueOf(p.getId()).equals(k));
                }
                if (type != null && !type.equals("all")) stream = stream.filter(p -> p.getTypes().contains(type));
                
                Comparator<Pokemon> comparator = Comparator.comparingInt(Pokemon::getId);
                if ("total_desc".equals(sort)) comparator = Comparator.comparingInt(Pokemon::getTotal).reversed();
                else if ("atk_desc".equals(sort)) comparator = Comparator.comparingInt(Pokemon::getAttack).reversed();
                else if ("spd_desc".equals(sort)) comparator = Comparator.comparingInt(Pokemon::getSpeed).reversed();

                return stream.sorted(comparator).limit(limit).collect(Collectors.toList());
            }

            public Pokemon getById(int id) {
                return db.stream().filter(p -> p.getId() == id).findFirst().orElse(null);
            }
        }
        """)

    # Controller
    with open(os.path.join(DIRS["controller"], "PokemonController.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.controller;
        import com.omni.pokemon.model.Pokemon;
        import com.omni.pokemon.service.PokemonService;
        import org.springframework.web.bind.annotation.*;
        import lombok.RequiredArgsConstructor;
        import java.util.List;

        @RestController
        @RequestMapping("/api")
        @RequiredArgsConstructor
        public class PokemonController {
            private final PokemonService service;
            
            @GetMapping("/pokemon/list")
            public List<Pokemon> getList(
                @RequestParam(required = false) String keyword,
                @RequestParam(required = false, defaultValue = "all") String type,
                @RequestParam(required = false, defaultValue = "id_asc") String sort,
                @RequestParam(required = false, defaultValue = "50") int limit
            ) {
                return service.search(keyword, type, sort, limit);
            }
            
            @GetMapping("/pokemon/{id}")
            public Pokemon getDetail(@PathVariable int id) { return service.getById(id); }
        }
        """)

    # App
    with open(os.path.join(JAVA_ROOT, "PokemonApp.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon;
        import org.springframework.boot.SpringApplication;
        import org.springframework.boot.autoconfigure.SpringBootApplication;
        @SpringBootApplication
        public class PokemonApp {
            public static void main(String[] args) { SpringApplication.run(PokemonApp.class, args); }
        }
        """)
    with open(os.path.join(RESOURCES, "application.properties"), "w") as f:
        f.write("server.port=8080")

# --- 🎨 프론트엔드 ---
def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OmniDex - AI Powered</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root { --bg:#1e272e; --card:#2d3436; --text:#dfe6e9; --accent:#74b9ff; }
            body { background:var(--bg); color:var(--text); font-family:'Segoe UI', sans-serif; margin:0; }
            .header { position:sticky; top:0; background:rgba(30,39,46,0.95); padding:15px; z-index:100; display:flex; gap:10px; justify-content:center; border-bottom:1px solid #636e72; }
            .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(160px, 1fr)); gap:15px; padding:20px; max-width:1400px; margin:0 auto; }
            .card { background:var(--card); border-radius:12px; padding:10px; cursor:pointer; border-top:4px solid #aaa; transition:0.2s; position:relative; }
            .card:hover { transform:translateY(-5px); }
            .card img { width:100%; height:120px; object-fit:contain; }
            .type-badge { font-size:0.7rem; padding:2px 6px; border-radius:4px; background:rgba(255,255,255,0.1); margin-right:2px; }
            /* Modal Styles */
            .modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); display:none; justify-content:center; align-items:center; z-index:1000; }
            .modal { background:#2d3436; width:90%; max-width:800px; border-radius:15px; padding:20px; display:flex; gap:20px; position:relative; }
            .close { position:absolute; top:10px; right:15px; font-size:1.5rem; cursor:pointer; }
            .chart-box { height:250px; width:100%; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0; color:var(--accent);">💎 OmniDex</h2>
            <input type="text" id="search" placeholder="검색..." onkeyup="debounceLoad()" style="padding:8px; border-radius:5px; border:none;">
            <select id="typeFilter" onchange="loadData()" style="padding:8px; border-radius:5px;"><option value="all">All Types</option><option value="fire">Fire</option><option value="water">Water</option><option value="grass">Grass</option></select>
            <select id="sortFilter" onchange="loadData()" style="padding:8px; border-radius:5px;"><option value="id_asc">ID</option><option value="total_desc">Total Stat</option></select>
        </div>
        <div id="grid" class="grid"></div>
        <div style="text-align:center; padding:20px;"><button onclick="more()" style="padding:10px 30px; border-radius:20px; border:none; background:var(--accent); font-weight:bold; cursor:pointer;">Load More</button></div>

        <div id="modal" class="modal-overlay" onclick="closeModal(event)"><div class="modal" onclick="event.stopPropagation()">
            <span class="close" onclick="document.getElementById('modal').style.display='none'">&times;</span>
            <div style="flex:1; text-align:center;">
                <img id="mImg" src="" style="width:200px;">
                <h2 id="mName"></h2><p id="mDesc" style="background:rgba(0,0,0,0.3); padding:10px; border-radius:8px;"></p>
            </div>
            <div style="flex:1.5;">
                <canvas id="chart"></canvas>
            </div>
        </div></div>

        <script>
            let limit=50, chart=null;
            async function loadData() {
                const k=document.getElementById('search').value, t=document.getElementById('typeFilter').value, s=document.getElementById('sortFilter').value;
                const res = await fetch(`/api/pokemon/list?keyword=${k}&type=${t}&sort=${s}&limit=${limit}`);
                const list = await res.json();
                document.getElementById('grid').innerHTML = list.map(p => `
                    <div class="card" style="border-color:${getColor(p.types[0])}" onclick="openModal(${p.id})">
                        <div style="position:absolute; right:10px; opacity:0.5;">#${p.id}</div>
                        <img src="${p.imageUrl}" loading="lazy">
                        <div style="font-weight:bold;">${p.name}</div>
                        <div>${p.types.map(ty=>`<span class="type-badge" style="background:${getColor(ty)}">${ty}</span>`).join('')}</div>
                        <div style="font-size:0.8rem; color:#aaa;">Total: ${p.total}</div>
                    </div>`).join('');
            }
            let timer; function debounceLoad(){ clearTimeout(timer); timer=setTimeout(()=>{limit=50; loadData()}, 300); }
            function more(){ limit+=50; loadData(); }
            
            async function openModal(id){
                const res = await fetch(`/api/pokemon/${id}`); const p = await res.json();
                document.getElementById('mImg').src=p.imageUrl; document.getElementById('mName').innerText=p.name;
                document.getElementById('mDesc').innerText=p.description;
                document.getElementById('modal').style.display='flex';
                
                if(chart) chart.destroy();
                chart = new Chart(document.getElementById('chart'), {
                    type:'radar', data:{
                        labels:['HP','Atk','Def','SpA','SpD','Spd'],
                        datasets:[{label:'Stats', data:[p.hp,p.attack,p.defense,p.spAttack,p.spDefense,p.speed], backgroundColor:'rgba(116,185,255,0.5)', borderColor:'#74b9ff'}]
                    }, options:{scales:{r:{suggestedMin:0, suggestedMax:150, ticks:{display:false}, grid:{color:'rgba(255,255,255,0.1)'}}}} 
                });
            }
            function closeModal(e){ if(e.target.id==='modal') document.getElementById('modal').style.display='none'; }
            function getColor(t){ const c={fire:'#e17055', water:'#0984e3', grass:'#00b894', electric:'#fdcb6e', normal:'#636e72'}; return c[t]||'#a4b0be'; }
            loadData();
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("🚀 OmniDex + Claude Code + Dependabot 통합 빌드 시작...")
    
    create_structure()
    create_pom_xml()
    create_dockerfile()         # [NEW]
    create_devops_config()      # [NEW] Claude Code & Dependabot
    
    asyncio.run(fetch_all_and_save())
    create_java_files()
    create_frontend()
    
    print("✅ 빌드 완료!")
    print(f"👉 프로젝트 경로: {BASE_DIR}")
    print("👉 실행 방법: mvn spring-boot:run")
    print("👉 DevOps: .github 폴더 내 Workflows 및 Dependabot 설정 확인 가능")

if __name__ == "__main__":
    main()
