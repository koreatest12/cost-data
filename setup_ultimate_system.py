import os
import sys
import json
import asyncio
import aiohttp
import time

# --- 설정 ---
BASE_DIR = "services/omni-pokemon-web"
SRC_MAIN = os.path.join(BASE_DIR, "src/main")
JAVA_ROOT = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# 패키지별 폴더
DIRS = {
    "controller": os.path.join(JAVA_ROOT, "controller"),
    "service": os.path.join(JAVA_ROOT, "service"),
    "model": os.path.join(JAVA_ROOT, "model"),
}

# 수집 범위 (1세대 ~ 9세대 주요 포켓몬 + 전설 + 환상 등 대량 샘플링)
# 실제 운영 시 range(1, 1010) 으로 설정하면 됨. 여기서는 테스트용으로 100마리+ 선정
TARGET_IDS = list(range(1, 152)) + list(range(249, 252)) + [800, 900, 1000]

def create_structure():
    """디렉토리 구조 생성"""
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    print("📁 디렉토리 구조 생성 완료")

def create_pom_xml():
    """Maven POM 파일 생성 (오류 수정: relativePath 추가)"""
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
            <relativePath/> </parent>
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
    print("📄 pom.xml (Fix Applied) 생성 완료")

# ---------------- 비동기 데이터 수집 (핵심) ----------------

async def fetch_single_pokemon(session, pid):
    """단일 포켓몬 데이터 비동기 요청"""
    try:
        # 1. 기본 정보 (Stats, Types)
        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as resp:
            if resp.status != 200: return None
            data = await resp.json()

        # 2. 종족값 파싱
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        
        # 3. 한국어 이름 (별도 요청)
        ko_name = data['name'] # fallback
        async with session.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}") as resp_spec:
            if resp_spec.status == 200:
                spec_data = await resp_spec.json()
                for n in spec_data['names']:
                    if n['language']['name'] == 'ko':
                        ko_name = n['name']
                        break
        
        # 4. 데이터 조립
        total_stats = sum(stats.values())
        return {
            "id": pid,
            "name": ko_name,
            "type": data['types'][0]['type']['name'],
            "imageUrl": data['sprites']['other']['official-artwork']['front_default'],
            "hp": stats.get('hp', 0),
            "attack": stats.get('attack', 0),
            "defense": stats.get('defense', 0),
            "speed": stats.get('speed', 0),
            "total": total_stats,
            "grade": "S" if total_stats >= 600 else ("A" if total_stats >= 500 else "B")
        }
    except Exception as e:
        # print(f"Error {pid}: {e}")
        return None

async def fetch_all_data():
    """모든 타겟 데이터를 병렬로 수집"""
    print(f"🚀 {len(TARGET_IDS)}개의 포켓몬 데이터 수집 시작 (Async)...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_pokemon(session, pid) for pid in TARGET_IDS]
        results = await asyncio.gather(*tasks)
    
    # None 값 제거 (에러 난 경우)
    valid_results = [r for r in results if r is not None]
    
    end_time = time.time()
    print(f"✨ {len(valid_results)}개 데이터 수집 완료! 소요 시간: {end_time - start_time:.2f}초")
    return valid_results

# ---------------- Java 파일 생성 ----------------

def create_java_files(pokemon_data):
    # 1. Model
    model_code = """
    package com.omni.pokemon.model;
    import lombok.Data;
    import lombok.AllArgsConstructor;
    import lombok.NoArgsConstructor;

    @Data @AllArgsConstructor @NoArgsConstructor
    public class Pokemon {
        private int id;
        private String name;
        private String type;
        private String imageUrl;
        private int hp;
        private int attack;
        private int defense;
        private int speed;
        private int total;
        private String grade;
    }
    """
    with open(os.path.join(DIRS["model"], "Pokemon.java"), "w", encoding="utf-8") as f:
        f.write(model_code)

    # 2. Service (JSON 데이터 임베딩)
    # JSON 문자열 이스케이프 처리
    json_str = json.dumps(pokemon_data, ensure_ascii=False).replace('"', '\\"')
    
    service_code = f"""
    package com.omni.pokemon.service;
    import com.fasterxml.jackson.core.type.TypeReference;
    import com.fasterxml.jackson.databind.ObjectMapper;
    import com.omni.pokemon.model.Pokemon;
    import org.springframework.stereotype.Service;
    import javax.annotation.PostConstruct;
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
                String raw = "{json_str}";
                db = mapper.readValue(raw, new TypeReference<List<Pokemon>>() {{}});
            }} catch (Exception e) {{ e.printStackTrace(); }}
        }}

        public List<Pokemon> search(String keyword) {{
            if (keyword == null || keyword.isEmpty()) return db;
            return db.stream()
                .filter(p -> p.getName().contains(keyword) || String.valueOf(p.getId()).equals(keyword))
                .collect(Collectors.toList());
        }}
        
        public List<Pokemon> getAll() {{ return db; }}
    }}
    """
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write(service_code)

    # 3. Controller
    controller_code = """
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
        
        @GetMapping("/list")
        public List<Pokemon> list() { return service.getAll(); }
    }
    """
    with open(os.path.join(DIRS["controller"], "PokemonController.java"), "w", encoding="utf-8") as f:
        f.write(controller_code)

    # 4. Application
    app_code = """
    package com.omni.pokemon;
    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;
    @SpringBootApplication
    public class PokemonApp {
        public static void main(String[] args) { SpringApplication.run(PokemonApp.class, args); }
    }
    """
    with open(os.path.join(JAVA_ROOT, "PokemonApp.java"), "w", encoding="utf-8") as f:
        f.write(app_code)
        
    # 5. Properties
    with open(os.path.join(RESOURCES, "application.properties"), "w") as f:
        f.write("server.port=8086")

def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Omni Global Pokemon DB</title>
        <style>
            body { font-family: 'Noto Sans KR', sans-serif; background: #2c3e50; color: white; text-align: center; }
            .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; padding: 20px; max-width: 1400px; margin: 0 auto; }
            .card { background: #34495e; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: 0.3s; }
            .card:hover { transform: translateY(-5px); background: #3e5871; }
            img { width: 120px; height: 120px; }
            .stats { font-size: 0.8rem; color: #bdc3c7; margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
            .grade-S { color: #f1c40f; font-weight: bold; }
            input { padding: 15px; width: 60%; font-size: 1.2rem; border-radius: 30px; border: none; margin: 30px 0; text-align: center; }
        </style>
    </head>
    <body>
        <h1>🪐 Omni Global Pokémon Database</h1>
        <input type="text" id="search" placeholder="포켓몬 이름(한국어) 또는 번호 검색..." onkeyup="doSearch()">
        <div id="grid" class="card-grid">Loading...</div>
        <script>
            async function load(keyword='') {
                const res = await fetch(`/api/pokemon/search?keyword=${keyword}`);
                const data = await res.json();
                const html = data.map(p => `
                    <div class="card">
                        <div style="color:#7f8c8d">#${p.id}</div>
                        <h3>${p.name}</h3>
                        <img src="${p.imageUrl}" loading="lazy">
                        <div>타입: ${p.type}</div>
                        <div class="stats">
                            <div>HP: ${p.hp}</div> <div>ATK: ${p.attack}</div>
                            <div>DEF: ${p.defense}</div> <div>SPD: ${p.speed}</div>
                        </div>
                        <div style="margin-top:10px">종족값: ${p.total} <span class="grade-${p.grade}">(${p.grade})</span></div>
                    </div>
                `).join('');
                document.getElementById('grid').innerHTML = html;
            }
            let timeout = null;
            function doSearch() {
                clearTimeout(timeout);
                timeout = setTimeout(() => load(document.getElementById('search').value), 300);
            }
            load();
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    # Windows 환경에서 asyncio 정책 설정 (선택 사항)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    print("🚀 Ultimate System Setup Started...")
    create_structure()
    create_pom_xml()
    
    # 비동기 데이터 수집 실행
    data = asyncio.run(fetch_all_data())
    
    create_java_files(data)
    create_frontend()
    print("✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
