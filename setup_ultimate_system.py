import os
import sys
import json
import asyncio
import aiohttp
import time

# --- 경로 설정 ---
BASE_DIR = "services/omni-pokemon-web"
SRC_MAIN = os.path.join(BASE_DIR, "src/main")
JAVA_ROOT = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

DIRS = {
    "controller": os.path.join(JAVA_ROOT, "controller"),
    "service": os.path.join(JAVA_ROOT, "service"),
    "model": os.path.join(JAVA_ROOT, "model"),
}

# --- 🔥 대량 데이터 타겟 (1~251번 + 최신 전설) ---
TARGET_IDS = list(range(1, 252)) + [257, 384, 483, 484, 493, 1000, 1007, 1008]

def create_structure():
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    print("📁 디렉토리 구조 생성 완료")

def create_pom_xml():
    pom = """
    <project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <modelVersion>4.0.0</modelVersion>
        <groupId>com.omni</groupId>
        <artifactId>omni-pokemon-web</artifactId>
        <version>1.0.0</version>
        <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>3.1.5</version>
            <relativePath/>
        </parent>
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

# --- 비동기 데이터 수집 ---
async def fetch_pokemon(session, pid):
    try:
        # 1. 기본 정보
        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
            if res.status != 200: return None
            data = await res.json()

        # 2. 한국어 이름
        ko_name = data['name']
        async with session.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}") as res_spec:
            if res_spec.status == 200:
                spec = await res_spec.json()
                for n in spec['names']:
                    if n['language']['name'] == 'ko':
                        ko_name = n['name']
                        break
        
        # 3. 데이터 가공
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        total = sum(stats.values())
        
        grade = "B"
        if total >= 600: grade = "S (전설급)"
        elif total >= 500: grade = "A (우수)"
        elif total >= 400: grade = "B+ (준수)"
        
        return {
            "id": pid,
            "name": ko_name,
            "engName": data['name'],
            "type": data['types'][0]['type']['name'],
            "imageUrl": data['sprites']['other']['official-artwork']['front_default'],
            "hp": stats.get('hp', 0),
            "attack": stats.get('attack', 0),
            "defense": stats.get('defense', 0),
            "total": total,
            "grade": grade
        }
    except Exception:
        return None

async def fetch_all():
    print(f"🚀 {len(TARGET_IDS)}마리 포켓몬 데이터 수집 시작 (Async)...")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_pokemon(session, pid) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
    
    valid_data = [r for r in results if r is not None]
    print(f"✅ 총 {len(valid_data)}마리 데이터 수집 완료!")
    return valid_data

# --- Java 소스 생성 ---
def create_java_files(data):
    # 1. Model
    with open(os.path.join(DIRS["model"], "Pokemon.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.model;
        import lombok.Data;
        import lombok.AllArgsConstructor;
        import lombok.NoArgsConstructor;

        @Data @AllArgsConstructor @NoArgsConstructor
        public class Pokemon {
            private int id;
            private String name;
            private String engName;
            private String type;
            private String imageUrl;
            private int hp;
            private int attack;
            private int defense;
            private int total;
            private String grade;
        }
        """)

    # 2. Service
    json_data = json.dumps(data, ensure_ascii=False).replace('"', '\\"')
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write(f"""
        package com.omni.pokemon.service;
        import com.fasterxml.jackson.core.type.TypeReference;
        import com.fasterxml.jackson.databind.ObjectMapper;
        import com.omni.pokemon.model.Pokemon;
        import org.springframework.stereotype.Service;
        import jakarta.annotation.PostConstruct;
        import java.util.ArrayList;
        import java.util.List;
        import java.util.stream.Collectors;

        @Service
        public class PokemonService {{
            private List<Pokemon> db = new ArrayList<>();
            private final ObjectMapper mapper = new ObjectMapper();

            @PostConstruct
            public void init() {{
                try {{
                    String raw = "{json_data}";
                    db = mapper.readValue(raw, new TypeReference<List<Pokemon>>() {{}});
                    System.out.println("✅ DB Init: " + db.size() + " items loaded.");
                }} catch (Exception e) {{ e.printStackTrace(); }}
            }}

            public List<Pokemon> search(String keyword) {{
                if (keyword == null || keyword.isEmpty()) return db;
                return db.stream()
                    .filter(p -> p.getName().contains(keyword) || p.getEngName().contains(keyword) || String.valueOf(p.getId()).equals(keyword))
                    .collect(Collectors.toList());
            }}
        }}
        """)

    # 3. Controller (Health Check 추가)
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
            
            @GetMapping("/pokemon/search")
            public List<Pokemon> search(@RequestParam(required = false) String keyword) {
                return service.search(keyword);
            }
            
            @GetMapping("/system/health")
            public String health() {
                return "OK";
            }
        }
        """)

    # 4. App & Properties
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
        f.write("server.port=8086")

# --- 프론트엔드 ---
def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Omni Massive DB</title>
        <style>
            :root { --bg: #1e272e; --card: #2f3640; --text: #d2dae2; }
            body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; max-width: 1400px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 12px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: 0.2s; border-bottom: 3px solid transparent; }
            .card:hover { transform: translateY(-5px); border-bottom-color: #ffd32a; }
            img { width: 100px; height: 100px; }
            .type-badge { font-size: 0.8rem; padding: 3px 8px; background: rgba(255,255,255,0.1); border-radius: 10px; display: inline-block; margin: 5px 0; }
            input { width: 60%; padding: 15px; font-size: 1.1rem; border-radius: 30px; border: none; background: #485460; color: white; outline: none; }
        </style>
    </head>
    <body>
        <h1>🔥 Omni Massive Database</h1>
        <input type="text" id="search" placeholder="🔍 포켓몬 검색..." onkeyup="search()">
        <div id="count" style="margin: 10px; color: #808e9b;"></div>
        <div id="result" class="grid"></div>
        <script>
            let db = [];
            async function init() {
                const res = await fetch('/api/pokemon/search');
                db = await res.json();
                document.getElementById('count').innerText = `Total: ${db.length} loaded`;
                render(db);
            }
            function render(list) {
                document.getElementById('result').innerHTML = list.map(p => `
                    <div class="card">
                        <div style="font-size:0.8rem; opacity:0.7">#${p.id}</div>
                        <img src="${p.imageUrl}" loading="lazy">
                        <div style="font-weight:bold; font-size:1.1rem; margin:5px 0;">${p.name}</div>
                        <div class="type-badge">${p.type}</div>
                        <div style="font-size:0.9rem;">
                             종족값: ${p.total} <br>
                             <span style="color:${p.grade.includes('S')?'#ffdd59':'#d2dae2'}">${p.grade}</span>
                        </div>
                    </div>
                `).join('');
            }
            function search() {
                const q = document.getElementById('search').value.toLowerCase();
                render(db.filter(p => p.name.includes(q) || String(p.id).includes(q) || p.engName.toLowerCase().includes(q)));
            }
            init();
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("🚀 Omni System: Starting Massive Setup...")
    create_structure()
    create_pom_xml()
    data = asyncio.run(fetch_all())
    create_java_files(data)
    create_frontend()
    print("✅ Setup Complete.")

if __name__ == "__main__":
    main()
