import os
import sys
import requests
import json
import random
import time

# --- 설정 ---
BASE_DIR = "services/omni-pokemon-web"
RESOURCES_DIR = os.path.join(BASE_DIR, "src/main/resources/static")
JAVA_PKG_DIR = os.path.join(BASE_DIR, "src/main/java/com/omni/pokemon")
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon-species/"

# CI 속도를 위해 샘플링 (실제 운영 시에는 전체 루프 가능)
# 1세대(1~151), 2세대(152~251)... 9세대(906~)
# 여기서는 데모를 위해 각 세대별 대표 포켓몬들을 포함하도록 설정
TARGET_IDS = list(range(1, 26)) + list(range(150, 152)) + [258, 384, 483, 484, 722, 906, 909, 1000] 

def create_directory_structure():
    """Spring Boot 프로젝트 폴더 구조 생성"""
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    os.makedirs(JAVA_PKG_DIR, exist_ok=True)
    print(f"📁 디렉토리 생성 완료: {BASE_DIR}")

def create_pom_xml():
    """Maven 빌드 파일 생성 (Spring Boot Web)"""
    pom_content = """
    <project xmlns="http://maven.apache.org/POM/4.0.0" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
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
        </dependencies>
        <properties>
            <java.version>17</java.version>
        </properties>
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
        f.write(pom_content)
    print("📄 pom.xml 생성 완료")

def create_java_application():
    """간단한 Spring Boot Application Java 파일 생성"""
    app_code = """
    package com.omni.pokemon;

    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;
    import org.springframework.stereotype.Controller;
    import org.springframework.web.bind.annotation.GetMapping;

    @SpringBootApplication
    public class PokemonApplication {
        public static void main(String[] args) {
            SpringApplication.run(PokemonApplication.class, args);
        }
    }

    @Controller
    class WebController {
        @GetMapping("/")
        public String index() {
            return "index.html"; 
        }
    }
    """
    with open(os.path.join(JAVA_PKG_DIR, "PokemonApplication.java"), "w", encoding="utf-8") as f:
        f.write(app_code)
    
    # application.properties (포트 설정)
    with open(os.path.join(BASE_DIR, "src/main/resources/application.properties"), "w", encoding="utf-8") as f:
        f.write("server.port=8086")
    
    print("☕ Java 소스 코드 생성 완료")

def fetch_pokemon_data_ko():
    """PokéAPI에서 데이터를 가져와 한국어 이름 매핑"""
    print("🌐 포켓몬 데이터 수집 중 (한국어 이름 포함)...")
    pokemon_list = []
    
    # 세션 사용으로 연결 재사용
    session = requests.Session()

    for pid in TARGET_IDS:
        try:
            # 1. Species 정보 (한국어 이름)
            res = session.get(f"{POKEAPI_URL}{pid}")
            if res.status_code != 200: continue
            data = res.json()
            
            # 한국어 이름 추출
            ko_name = next((n['name'] for n in data['names'] if n['language']['name'] == 'ko'), f"Pokemon {pid}")
            
            # 2. 이미지 URL (공식 아트워크)
            img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"
            
            # 세대 정보 추정 (API 데이터 기반 혹은 ID 기반)
            generation = "Unknown"
            if pid <= 151: generation = "1세대 (관동)"
            elif pid <= 251: generation = "2세대 (성도)"
            elif pid <= 386: generation = "3세대 (호연)"
            elif pid <= 493: generation = "4세대 (신오)"
            elif pid <= 649: generation = "5세대 (하나)"
            elif pid <= 721: generation = "6세대 (칼로스)"
            elif pid <= 809: generation = "7세대 (알로라)"
            elif pid <= 905: generation = "8세대 (가라르)"
            else: generation = "9세대 (팔데아)"

            pokemon_list.append({
                "id": pid,
                "name": ko_name,
                "img": img_url,
                "gen": generation
            })
            sys.stdout.write(f"\r✅ {ko_name} ({pid}) 수집 완료")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"❌ Error fetching {pid}: {e}")

    print("\n✨ 데이터 수집 완료!")
    return pokemon_list

def generate_html_dashboard(data):
    """HTML 대시보드 생성"""
    cards_html = ""
    for p in data:
        cards_html += f"""
        <div class="card">
            <span class="gen-badge">{p['gen']}</span>
            <img src="{p['img']}" alt="{p['name']}" loading="lazy">
            <div class="info">
                <h3>No.{p['id']} {p['name']}</h3>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Omni Pokemon Dashboard</title>
        <style>
            :root {{ --primary: #ffcb05; --secondary: #3b4cca; --bg: #f4f4f4; }}
            body {{ font-family: 'Noto Sans KR', sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            header {{ text-align: center; margin-bottom: 40px; }}
            h1 {{ color: var(--secondary); font-size: 2.5rem; margin-bottom: 10px; }}
            p {{ color: #666; }}
            .container {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); 
                gap: 20px; 
                max-width: 1200px; 
                margin: 0 auto; 
            }}
            .card {{ 
                background: white; 
                border-radius: 15px; 
                padding: 20px; 
                text-align: center; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                transition: transform 0.2s;
                position: relative;
            }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 15px rgba(0,0,0,0.2); }}
            .card img {{ width: 120px; height: 120px; object-fit: contain; }}
            .info h3 {{ margin: 10px 0 0; color: #333; font-size: 1.1rem; }}
            .gen-badge {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: #eee;
                color: #555;
                font-size: 0.7rem;
                padding: 4px 8px;
                border-radius: 10px;
            }}
            .stats {{ margin-top: 30px; text-align: center; font-weight: bold; color: #555; }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <header>
            <h1>Pokémon Live Dashboard</h1>
            <p>1세대(관동) ~ 9세대(팔데아) 실시간 통합 데이터</p>
        </header>
        
        <div class="container">
            {cards_html}
        </div>

        <div class="stats">
            총 {len(data)}마리 포켓몬 데이터 로드 완료 | Generated by GitHub Actions
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(RESOURCES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🖼️ index.html 대시보드 생성 완료")

def main():
    print("🚀 Ultimate Setup System 시작...")
    create_directory_structure()
    create_pom_xml()
    create_java_application()
    
    # 포켓몬 데이터 수집 및 HTML 생성
    pokemon_data = fetch_pokemon_data_ko()
    generate_html_dashboard(pokemon_data)
    
    print("✅ 모든 설정 및 파일 생성 완료.")

if __name__ == "__main__":
    main()
