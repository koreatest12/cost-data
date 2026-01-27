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

# --- 🔥 대량 데이터 타겟 (1~3세대 전체 + 최신) ---
# 파일로 저장하므로 이제 수천 마리도 문제 없습니다.
# 1세대(151) + 2세대(100) + 3세대(135) + 9세대 일부
TARGET_IDS = list(range(1, 387)) + [1000, 1001, 1007, 1008]

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

        # 2. 한국어 이름 (이름이 없으면 영어 이름 사용)
        ko_name = data['name']
        async with session.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}") as res_spec:
            if res_spec.status == 200:
                spec = await res_spec.json()
                for n in spec['names']:
                    if n['language']['name'] == 'ko':
                        ko_name = n['name']
                        break
        
        # 3. 스탯 계산
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        total = sum(stats.values())
        
        grade = "B"
        if total >= 600: grade = "S (전설급)"
        elif total >= 500: grade = "A (엘리트)"
        elif total >= 450: grade = "A- (우수)"
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

async def fetch_all_and_save():
    print(f"🚀 {len(TARGET_IDS)}마리 데이터 수집 중 (Async)...")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_pokemon(session, pid) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
    
    valid_data = [r for r in results if r is not None]
    
    # 🚨 중요: Java 코드 내부가 아닌, JSON 파일로 리소스 폴더에 저장
    json_path = os.path.join(RESOURCES, "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(valid_data, f, ensure_ascii=False)
        
    print(f"✅ {len(valid_data)}마리 데이터 -> {json_path} 저장 완료!")
    return valid_data

# --- Java 소스 생성 (Resource 로드 방식 적용) ---
def create_java_files():
    # 1. Model
    with open(os.path.join(DIRS["model"], "Pokemon.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.model;
        import lombok.Data;
        import lombok.AllArgsConstructor;
        import lombok.NoArgsConstructor;
        import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

        @Data @AllArgsConstructor @NoArgsConstructor
        @JsonIgnoreProperties(ignoreUnknown = true)
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

    # 2. Service (🚨 핵심 수정: 파일 읽기 방식)
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write("""
        package com.omni.pokemon.service;
        import com.fasterxml.jackson.core.type.TypeReference;
        import com.fasterxml.jackson.databind.ObjectMapper;
        import com.omni.pokemon.model.Pokemon;
        import org.springframework.stereotype.Service;
        import jakarta.annotation.PostConstruct;
        import java.io.InputStream;
        import java.util.ArrayList;
        import java.util.List;
        import java.util.stream.Collectors;

        @Service
        public class PokemonService {
            private List<Pokemon> db = new ArrayList<>();
            private final ObjectMapper mapper = new ObjectMapper();

            @PostConstruct
            public void init() {
                try {
                    // 🚨 Resource 폴더의 data.json 파일을 스트림으로 읽음 (용량 제한 없음)
                    InputStream is = getClass().getResourceAsStream("/data.json");
                    if (is == null) {
                        System.err.println("❌ data.json not found!");
                        return;
                    }
                    db = mapper.readValue(is, new TypeReference<List<Pokemon>>() {});
                    System.out.println("✅ DB Loaded: " + db.size() + " items.");
                } catch (Exception e) { e.printStackTrace(); }
            }

            public List<Pokemon> search(String keyword) {
                if (keyword == null || keyword.isEmpty()) return db;
                return db.stream()
                    .filter(p -> p.getName().contains(keyword) || 
                                 (p.getEngName() != null && p.getEngName().toLowerCase().contains(keyword.toLowerCase())) || 
                                 String.valueOf(p.getId()).equals(keyword))
                    .collect(Collectors.toList());
            }
        }
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
        @RequestMapping("/api")
        @RequiredArgsConstructor
        public class PokemonController {
            private final PokemonService service;
            
            @GetMapping("/pokemon/search")
            public List<Pokemon> search(@RequestParam(required = false) String keyword) {
                return service.search(keyword);
            }
            
            @GetMapping("/system/health")
            public String health() { return "OK"; }
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

# --- 프론트엔드 (UI) ---
def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Omni Massive DB</title>
        <style>
            :root { --bg: #2d3436; --card: #353b48; --text: #dfe6e9; --accent: #0984e3; }
            body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
            .search-container { position: sticky; top: 0; background: var(--bg); padding: 20px; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
            input { width: 60%; padding: 15px; border-radius: 25px; border: 2px solid #636e72; background: var(--card); color: white; font-size: 1.1rem; outline: none; }
            input:focus { border-color: var(--accent); }
            
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; max-width: 1500px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 12px; padding: 15px; transition: 0.2s; position: relative; border-top: 4px solid #7f8c8d; }
            .card:hover { transform: translateY(-5px); background: #3d4452; }
            
            .type-fire { border-color: #e17055; } .type-water { border-color: #74b9ff; } 
            .type-grass { border-color: #55efc4; } .type-electric { border-color: #ffeaa7; }
            
            img { width: 110px; height: 110px; object-fit: contain; }
            .info { margin-top: 10px; font-size: 0.9rem; }
            .total-badge { background: #2d3436; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="search-container">
            <h1>💎 Omni Global DB (1~3세대 + 전설)</h1>
            <input type="text" id="search" placeholder="검색 (이름, 번호)..." onkeyup="search()">
            <div id="stats" style="margin-top:10px; color:#b2bec3;">Loading...</div>
        </div>
        
        <div id="result" class="grid"></div>

        <script>
            let db = [];
            async function init() {
                const res = await fetch('/api/pokemon/search');
                db = await res.json();
                document.getElementById('stats').innerText = `Data Loaded: ${db.length} Species`;
                render(db);
            }
            
            function render(list) {
                // 성능을 위해 최대 100개까지만 렌더링 (검색 시 전체 필터링)
                const view = list.slice(0, 100); 
                
                document.getElementById('result').innerHTML = view.map(p => `
                    <div class="card type-${p.type}">
                        <div style="text-align:left; font-size:0.8rem; opacity:0.6;">#${p.id}</div>
                        <img src="${p.imageUrl}" loading="lazy">
                        <h3 style="margin:5px 0">${p.name}</h3>
                        <div style="font-size:0.8rem; color:#b2bec3;">${p.engName}</div>
                        <div class="info">
                            <div>Type: ${p.type}</div>
                            <div style="margin-top:5px;">
                                Total: <span class="total-badge">${p.total}</span> 
                                <span style="color:${p.grade.includes('S')?'#fdcb6e':'inherit'}">${p.grade}</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
            
            function search() {
                const q = document.getElementById('search').value.toLowerCase();
                const filtered = db.filter(p => p.name.includes(q) || String(p.id).includes(q) || (p.engName && p.engName.toLowerCase().includes(q)));
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
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("🚀 Ultimate Setup: Saving Data to File & Generating Source...")
    
    create_structure()
    create_pom_xml()
    
    # 1. 데이터 수집 및 파일 저장
    asyncio.run(fetch_all_and_save())
    
    # 2. 자바 소스 생성 (파일 로드 로직 포함)
    create_java_files()
    
    # 3. 프론트엔드 생성
    create_frontend()
    
    print("✅ Setup Completed Successfully!")

if __name__ == "__main__":
    main()
