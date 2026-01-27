import os
import sys
import requests
import json
import random

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

# 데이터 수집 범위 (샘플링: 1~9세대 주요 포켓몬 + 전설)
TARGET_IDS = list(range(1, 10)) + [25, 133, 143, 149, 150, 151] + \
             [249, 250, 384, 448, 483, 484, 493, 635, 700, 722, 800, 906, 909, 1000]

def create_structure():
    """MVC 디렉토리 구조 대량 생성"""
    for path in DIRS.values():
        os.makedirs(path, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    print("📁 MVC 디렉토리 구조 생성 완료")

def create_pom_xml():
    """Lombok 및 Web 의존성이 추가된 Maven 빌드 파일"""
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

# ---------------- Java 파일 생성 (MVC 패턴) ----------------

def create_model_class():
    """DTO/Model 클래스 생성 (개체값 필드 포함)"""
    code = """
    package com.omni.pokemon.model;

    import lombok.AllArgsConstructor;
    import lombok.Data;
    import lombok.NoArgsConstructor;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public class Pokemon {
        private int id;
        private String name;     // 한국어 이름
        private String type;
        private String imageUrl;
        private String generation;
        
        // 개체값 (IV) 및 종족값 분석
        private int hp;
        private int attack;
        private int defense;
        private String potentialGrade; // S, A, B 등급
    }
    """
    with open(os.path.join(DIRS["model"], "Pokemon.java"), "w", encoding="utf-8") as f:
        f.write(code)

def create_service_class(pokemon_data_json):
    """비즈니스 로직 및 검색 기능 구현"""
    # JSON 데이터를 Java 코드 내에 하드코딩하여 DB 없이도 동작하게 함 (배포 용이성)
    json_str = json.dumps(pokemon_data_json, ensure_ascii=False).replace('"', '\\"')
    
    code = f"""
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
        private List<Pokemon> pokemonList = new ArrayList<>();
        private final ObjectMapper mapper = new ObjectMapper();

        @PostConstruct
        public void init() {{
            try {{
                String rawData = "{json_str}";
                pokemonList = mapper.readValue(rawData, new TypeReference<List<Pokemon>>() {{}});
                System.out.println("✅ 포켓몬 데이터 로드 완료: " + pokemonList.size() + " 마리");
            }} catch (Exception e) {{
                e.printStackTrace();
            }}
        }}

        public List<Pokemon> getAllPokemon() {{
            return pokemonList;
        }}

        // 한국어 검색 로직
        public List<Pokemon> searchPokemon(String keyword) {{
            if (keyword == null || keyword.isEmpty()) {{
                return pokemonList;
            }}
            return pokemonList.stream()
                    .filter(p -> p.getName().contains(keyword) || String.valueOf(p.getId()).equals(keyword))
                    .collect(Collectors.toList());
        }}
    }}
    """
    with open(os.path.join(DIRS["service"], "PokemonService.java"), "w", encoding="utf-8") as f:
        f.write(code)

def create_controller_class():
    """REST API 컨트롤러 생성"""
    code = """
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

        @GetMapping("/list")
        public List<Pokemon> getAll() {
            return service.getAllPokemon();
        }

        @GetMapping("/search")
        public List<Pokemon> search(@RequestParam String keyword) {
            return service.searchPokemon(keyword);
        }
    }
    """
    with open(os.path.join(DIRS["controller"], "PokemonController.java"), "w", encoding="utf-8") as f:
        f.write(code)

def create_main_app():
    """메인 실행 파일"""
    code = """
    package com.omni.pokemon;

    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;

    @SpringBootApplication
    public class PokemonApplication {
        public static void main(String[] args) {
            SpringApplication.run(PokemonApplication.class, args);
        }
    }
    """
    with open(os.path.join(JAVA_ROOT, "PokemonApplication.java"), "w", encoding="utf-8") as f:
        f.write(code)
    
    # application.properties
    with open(os.path.join(RESOURCES, "application.properties"), "w", encoding="utf-8") as f:
        f.write("server.port=8086")

# ---------------- 데이터 수집 로직 ----------------

def fetch_data():
    print("🌐 포켓몬 데이터 및 개체값(IV) 수집 중...")
    results = []
    session = requests.Session()
    
    for pid in TARGET_IDS:
        try:
            # 기본 정보
            res = session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}").json()
            # 종족값 (Base Stats)
            stats = {s['stat']['name']: s['base_stat'] for s in res['stats']}
            
            # 한국어 이름
            res_spec = session.get(f"https://pokeapi.co/api/v2/pokemon-species/{pid}").json()
            ko_name = next((n['name'] for n in res_spec['names'] if n['language']['name'] == 'ko'), res['name'])
            
            # 개체값(IV) 시뮬레이션 및 등급 판정
            total_stats = stats.get('hp', 0) + stats.get('attack', 0) + stats.get('defense', 0)
            grade = "C"
            if total_stats > 300: grade = "S (전설급)"
            elif total_stats > 250: grade = "A (우수)"
            elif total_stats > 200: grade = "B (보통)"

            results.append({
                "id": pid,
                "name": ko_name,
                "type": res['types'][0]['type']['name'],
                "imageUrl": res['sprites']['other']['official-artwork']['front_default'],
                "generation": "Unknown", # 간소화를 위해 생략
                "hp": stats.get('hp', 0),
                "attack": stats.get('attack', 0),
                "defense": stats.get('defense', 0),
                "potentialGrade": grade
            })
            sys.stdout.write(f"\r✅ {ko_name} 데이터 생성 완료")
            sys.stdout.flush()
        except Exception:
            continue
    print("\n✨ 데이터 수집 완료")
    return results

# ---------------- 프론트엔드 (AJAX 검색 기능 포함) ----------------

def create_frontend():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Omni IV Checker & Pokedex</title>
        <style>
            body { font-family: 'Noto Sans KR', sans-serif; background: #f0f2f5; text-align: center; padding: 20px; }
            .search-box { margin: 20px 0; }
            input { padding: 15px; width: 300px; border-radius: 25px; border: 1px solid #ddd; font-size: 16px; }
            .container { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .card img { width: 120px; height: 120px; }
            .stat-box { background: #eee; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 0.9em; }
            .grade-S { color: #e11d48; font-weight: bold; }
            .grade-A { color: #2563eb; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🔍 포켓몬 개체값 & 도감 검색</h1>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="한국어 이름 또는 번호 검색..." onkeyup="search()">
        </div>
        <div id="results" class="container"></div>

        <script>
            let allPokemon = [];

            // 1. 초기 데이터 로드 (API 호출)
            fetch('/api/pokemon/list')
                .then(res => res.json())
                .then(data => {
                    allPokemon = data;
                    render(data);
                });

            // 2. 검색 기능 (API 호출 or 클라이언트 필터링)
            function search() {
                const query = document.getElementById('searchInput').value;
                fetch('/api/pokemon/search?keyword=' + query)
                    .then(res => res.json())
                    .then(data => render(data));
            }

            function render(list) {
                const container = document.getElementById('results');
                container.innerHTML = list.map(p => `
                    <div class="card">
                        <span style="color:#888;">No.${p.id}</span>
                        <h3>${p.name}</h3>
                        <img src="${p.imageUrl}" loading="lazy">
                        <div class="stat-box">
                            <div>체력: ${p.hp} | 공격: ${p.attack}</div>
                            <div>방어: ${p.defense}</div>
                            <div style="margin-top:5px;">등급: <span class="grade-${p.potentialGrade.charAt(0)}">${p.potentialGrade}</span></div>
                        </div>
                    </div>
                `).join('');
            }
        </script>
    </body>
    </html>
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    print("🚀 Ultimate System Builder 시작...")
    create_structure()
    create_pom_xml()
    
    # 데이터 확보
    data = fetch_data()
    
    # Java 소스 대량 생성
    create_model_class()
    create_service_class(data) # 데이터 주입
    create_controller_class()
    create_main_app()
    
    # 프론트엔드 생성
    create_frontend()
    
    print("✅ 모든 API 서버 및 파일 생성 완료!")

if __name__ == "__main__":
    main()
