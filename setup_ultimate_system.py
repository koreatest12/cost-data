import os
import sys
import json
import asyncio
import aiohttp
import time
import random

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

# --- 대량 데이터 타겟 (1세대 전체 + 최신 전설 포켓몬 등) ---
# API 부하 분산을 위해 주요 포켓몬 위주로 선정 (실제로는 range(1, 1025) 가능)
TARGET_IDS = list(range(1, 152)) + list(range(1000, 1010)) 

def create_structure():
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

def create_pom_xml():
    # Spring Boot 3.1.5 (Java 17 호환)
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

# --- 비동기 데이터 수집 (초고속) ---
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
        
        # 3. 스탯 합계 계산
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        total = sum(stats.values())
        
        # 4. 등급 판정
        grade = "B"
        if total >= 600: grade = "S (전설급)"
        elif total >= 500: grade = "A (엘리트)"
        
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
    print(f"✅ {len(valid_data)}마리 데이터 확보 완료!")
    return valid_data

# --- Java 소스 생성 (에러 수정 포함) ---
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

    # 2. Service (🚨 중요: javax -> jakarta 수정)
    json_data = json.dumps(data, ensure_ascii=False).replace('"', '\\"')
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write(f"""
        package com.omni.pokemon.service;

        import com.fasterxml.jackson.core.type.TypeReference;
        import com.fasterxml.jackson.databind.ObjectMapper;
        import com.omni.pokemon.model.Pokemon;
        import org.springframework.stereotype.Service;
        import jakarta.annotation.PostConstruct; // ✅ FIXED: javax -> jakarta
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

    # 3. Controller
    with open(os.path.join(DIRS["controller"], "PokemonController.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.controller;
        import com.omni.pokemon.model.Pokemon;
        import com.omni.pokemon.service.PokemonService;
        import org.springframework.web.bind.annotation.*;
        import lombok.RequiredArgsConstructor;
        import java.util.List;

        @RestController
        @RequestMapping("/api/pokemon")
        @RequiredArgsConstructor
        public class PokemonController {
            private final PokemonService service;
            
            @GetMapping("/search")
            public List<Pokemon> search(@RequestParam(required = false) String keyword) {
                return service.search(keyword);
            }
        }
        """)

    # 4. App
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

    # 5. Properties
    with open(os.path.join(RESOURCES, "application.properties"), "w") as f:
        f.write("server.port=8086")

# --- 프론트엔드 (UI 개선) ---
def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Omni Pokedex Pro</title>
        <style>
            :root { --bg: #1e272e; --card: #2f3640; --text: #f5f6fa; }
            body { background: var(--bg); color: var(--text); font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
            
            /* 타입별 색상 */
            .type-fire { border-top: 5px solid #e84118; }
            .type-water { border-top: 5px solid #0097e6; }
            .type-grass { border-top: 5px solid #4cd137; }
            .type-electric { border-top: 5px solid #fbc531; }
            .type-psychic { border-top: 5px solid #9c88ff; }
            .type-dragon { border-top: 5px solid #8c7ae6; }
            
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; max-width: 1400px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 15px; padding: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); transition: 0.3s; position: relative; overflow: hidden; }
            .card:hover { transform: translateY(-7px); box-shadow: 0 15px 30px rgba(0,0,0,0.5); }
            
            img { width: 140px; height: 140px; object-fit: contain; filter: drop-shadow(0 5px 5px rgba(0,0,0,0.5)); }
            h3 { margin: 10px 0 5px; font-size: 1.4rem; }
            
            .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: rgba(255,255,255,0.1); }
            .stats-bar { display: flex; justify-content: space-between; font-size: 0.9rem; color: #dcdde1; margin-top: 15px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px; }
            
            input { width: 50%; padding: 15px; border-radius: 30px; border: none; font-size: 1.2rem; background: #dfe4ea; color: #333; outline: none; box-shadow: 0 0 15px rgba(255,255,255,0.1); }
        </style>
    </head>
    <body>
        <h1 style="font-size: 3rem; margin-bottom: 10px;">⚡ Omni Pokédex Pro</h1>
        <p>1세대 전체 ~ 9세대 통합 데이터베이스</p>
        
        <input type="text" id="search" placeholder="🔍 포켓몬 이름 또는 번호 검색..." onkeyup="search()">
        
        <div id="result" class="grid"></div>

        <script>
            let allData = [];
            async function init() {
                const res = await fetch('/api/pokemon/search');
                allData = await res.json();
                render(allData);
            }
            
            function render(list) {
                const html = list.map(p => `
                    <div class="card type-${p.type}">
                        <div style="text-align:left; color:#718093; font-weight:bold;">#${p.id}</div>
                        <img src="${p.imageUrl}" loading="lazy">
                        <h3>${p.name}</h3>
                        <div class="badge">${p.type.toUpperCase()}</div>
                        <div class="stats-bar">
                            <span>❤️ ${p.hp}</span>
                            <span>⚔️ ${p.attack}</span>
                            <span>🛡️ ${p.defense}</span>
                        </div>
                        <div style="margin-top:10px; font-size:0.9rem;">
                            총합: <b>${p.total}</b> <span style="color:${p.grade.startsWith('S') ? '#f1c40f' : '#fff'}">${p.grade}</span>
                        </div>
                    </div>
                `).join('');
                document.getElementById('result').innerHTML = html;
            }

            function search() {
                const query = document.getElementById('search').value.toLowerCase();
                const filtered = allData.filter(p => 
                    p.name.includes(query) || 
                    p.engName.toLowerCase().includes(query) || 
                    String(p.id).includes(query)
                );
                render(filtered);
            }
            init();
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    print("🚀 Ultimate System: Fix Compilation & Mass Data Fetch...")
    create_structure()
    create_pom_xml()
    
    # Run Async Fetch
    data = asyncio.run(fetch_all())
    
    create_java_files(data)
    create_frontend()
    print("✅ System Ready for Maven Build!")

if __name__ == "__main__":
    main()
