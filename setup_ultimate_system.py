import os
import json
import asyncio
import aiohttp
import time

# ==============================================================================
# 🏗️ [설정] 프로젝트 경로 및 타겟
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web-v2"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PATH = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")

# DevOps & Scripts
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

# 🎯 타겟: 전체 포켓몬 (1 ~ 1025)
TARGET_IDS = list(range(1, 1026))

def create_directories():
    print(f"📂 [Init] 디렉토리 및 패키지 구조 생성... ({PROJECT_ROOT})")
    dirs = [
        os.path.join(JAVA_PATH, "controller"),
        os.path.join(JAVA_PATH, "service"),
        os.path.join(JAVA_PATH, "model"),
        os.path.join(JAVA_PATH, "config"),
        STATIC_DIR,
        os.path.join(STATIC_DIR, "icons"), # PWA 아이콘용
        SCRIPTS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

# ==============================================================================
# 1. 🛡️ Maven & Configuration (PWA & Cache)
# ==============================================================================
def generate_config():
    # pom.xml
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>2.0.0-PWA</version>
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
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin>
        </plugins>
    </build>
</project>
""")

    # application.properties (캐싱 및 압축 활성화)
    write_file(os.path.join(RESOURCES, "application.properties"), """
server.port=8086
server.compression.enabled=true
server.compression.mime-types=text/html,text/xml,text/plain,text/css,text/javascript,application/javascript,application/json
spring.mvc.static-path-pattern=/**
""")

# ==============================================================================
# 2. ⚡ 대량 데이터 수집 (1,025마리)
# ==============================================================================
async def fetch_data():
    print(f"🚀 [Data] 1,025마리 데이터 대량 수집 시작 (Gemini Engine)...")
    print("⏳ 약 30~60초 소요될 수 있습니다. 잠시만 기다려주세요.")
    
    semaphore = asyncio.Semaphore(60) # 동시성 제어
    
    async with aiohttp.ClientSession() as session:
        async def fetch(pid):
            async with semaphore:
                try:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pid}") as res:
                        if res.status != 200: return None
                        d = await res.json()
                        
                        # 주요 포켓몬 한글 매핑 (데이터 양이 많으므로 주요 개체만 예시)
                        name = d['name']
                        if pid == 25: name = "피카츄"
                        elif pid == 1: name = "이상해씨"
                        elif pid == 1000: name = "타부자고"
                        
                        stats = {s['stat']['name']: s['base_stat'] for s in d['stats']}
                        return {
                            "id": d['id'],
                            "name": name,
                            "types": [t['type']['name'] for t in d['types']],
                            "image": d['sprites']['other']['official-artwork']['front_default'] or d['sprites']['front_default'],
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
    print(f"✅ 대량 데이터 저장 완료: {len(data)}건 (resources/data.json)")

# ==============================================================================
# 3. ☕ Java Backend (고성능 검색 및 페이징)
# ==============================================================================
def generate_java():
    # Model
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

    # Service (In-Memory Indexing)
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
            System.out.println("✅ DB Loaded: " + db.size() + " items");
        } catch (Exception e) { e.printStackTrace(); }
    }

    // Paging & Filtering
    public Map<String, Object> search(String keyword, String sort, int page, int size) {
        var stream = db.stream();
        if (keyword != null && !keyword.isBlank()) {
            String k = keyword.toLowerCase();
            stream = stream.filter(p -> p.getName().contains(k) || String.valueOf(p.getId()).equals(k) || p.getTypes().contains(k));
        }
        
        Comparator<Pokemon> comp = Comparator.comparingInt(Pokemon::getId);
        if ("total".equals(sort)) comp = Comparator.comparingInt(Pokemon::getTotal).reversed();
        else if ("speed".equals(sort)) comp = Comparator.comparingInt(Pokemon::getSpeed).reversed();
        
        List<Pokemon> filtered = stream.sorted(comp).collect(Collectors.toList());
        
        int start = Math.min((page - 1) * size, filtered.size());
        int end = Math.min(start + size, filtered.size());
        
        Map<String, Object> response = new HashMap<>();
        response.put("total", filtered.size());
        response.put("data", filtered.subList(start, end));
        response.put("page", page);
        return response;
    }
}
""")

    # Controller
    write_file(os.path.join(JAVA_PATH, "controller/PokemonController.java"), """
package com.omni.pokemon.controller;
import com.omni.pokemon.service.PokemonService;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.Map;

@RestController
@RequestMapping("/api/pokemon")
@RequiredArgsConstructor
public class PokemonController {
    private final PokemonService service;

    @GetMapping("/search")
    public Map<String, Object> search(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false, defaultValue = "id") String sort,
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        return service.search(keyword, sort, page, size);
    }
}
""")

    # App
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
# 4. 📱 PWA & Frontend (설치 기능 구현)
# ==============================================================================
def generate_pwa_frontend():
    # 1. Manifest (앱 설치 정보)
    write_file(os.path.join(STATIC_DIR, "manifest.json"), """
{
  "name": "OmniDex Ultimate",
  "short_name": "OmniDex",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#3b82f6",
  "description": "The Ultimate Pokemon Database",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/master-ball.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/master-ball.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
""")

    # 2. Service Worker (오프라인 지원 & 캐싱)
    write_file(os.path.join(STATIC_DIR, "sw.js"), """
const CACHE_NAME = 'omnidex-v2';
const ASSETS = ['/', '/index.html', '/manifest.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  // API 요청은 네트워크 우선, 나머지는 캐시 우선
  if (e.request.url.includes('/api/')) {
    e.respondWith(fetch(e.request));
  } else {
    e.respondWith(
      caches.match(e.request).then((res) => res || fetch(e.request))
    );
  }
});
""")

    # 3. HTML (PWA Install Button + Infinite Scroll)
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniDex V2</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: white; -webkit-tap-highlight-color: transparent; }
        .card { transition: all 0.2s; background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); }
        .card:active { transform: scale(0.95); }
        /* Install Prompt */
        #installBtn { display: none; }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <nav class="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-700 px-4 py-3 flex justify-between items-center">
        <div class="flex items-center gap-2 font-bold text-xl text-blue-400">
            <i class="fa-solid fa-bolt"></i> OmniDex
        </div>
        <button id="installBtn" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-full text-sm font-bold shadow-lg transition animate-pulse">
            <i class="fa-solid fa-download"></i> Install App
        </button>
    </nav>

    <div class="p-4 sticky top-14 z-40 bg-slate-900/80 backdrop-blur-sm">
        <div class="relative max-w-2xl mx-auto">
            <i class="fa-solid fa-search absolute left-4 top-3.5 text-slate-400"></i>
            <input type="text" id="query" placeholder="Search (1-1025)..." 
                class="w-full bg-slate-800 rounded-full py-3 pl-12 pr-4 outline-none border border-slate-600 focus:border-blue-500 transition shadow-xl"
                oninput="resetAndLoad()">
        </div>
    </div>

    <main class="flex-1 p-4 max-w-7xl mx-auto w-full">
        <div id="grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"></div>
        <div id="loader" class="text-center py-8 hidden"><i class="fa-solid fa-circle-notch fa-spin text-2xl text-blue-500"></i></div>
        <button id="loadMore" onclick="loadNextPage()" class="w-full py-4 mt-4 text-slate-400 font-bold hidden">Load More</button>
    </main>

    <script>
        let page = 1;
        let isLoading = false;
        let deferredPrompt;

        // PWA Install Logic
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            const btn = document.getElementById('installBtn');
            btn.style.display = 'block';
            
            btn.addEventListener('click', () => {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((result) => {
                    if (result.outcome === 'accepted') {
                        console.log('User accepted the install prompt');
                    }
                    deferredPrompt = null;
                    btn.style.display = 'none';
                });
            });
        });

        // Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }

        // Data Logic
        async function loadData(isAppend = false) {
            if (isLoading) return;
            isLoading = true;
            document.getElementById('loader').style.display = 'block';

            const q = document.getElementById('query').value;
            try {
                const res = await fetch(`/api/pokemon/search?keyword=${q}&page=${page}&size=20`);
                const json = await res.json();
                
                const grid = document.getElementById('grid');
                if (!isAppend) grid.innerHTML = '';

                if (json.data.length === 0 && !isAppend) {
                    grid.innerHTML = '<div class="col-span-full text-center py-10 text-slate-500">No Pokemon Found</div>';
                }

                json.data.forEach(p => {
                    const el = document.createElement('div');
                    el.className = 'card rounded-xl p-4 flex flex-col items-center border border-slate-700/50';
                    el.innerHTML = `
                        <div class="w-full flex justify-between text-xs font-mono text-slate-500 mb-2">
                            <span>#${p.id}</span>
                            <span>TOTAL ${p.total}</span>
                        </div>
                        <img src="${p.image}" class="w-32 h-32 object-contain drop-shadow-xl mb-2" loading="lazy">
                        <h3 class="font-bold text-lg capitalize mb-1">${p.name}</h3>
                        <div class="flex gap-1">${p.types.map(t => `<span class="px-2 py-0.5 rounded-md text-[10px] uppercase font-bold bg-slate-700 text-slate-300">${t}</span>`).join('')}</div>
                    `;
                    grid.appendChild(el);
                });

                if (json.data.length < 20) {
                    document.getElementById('loadMore').style.display = 'none';
                } else {
                    document.getElementById('loadMore').style.display = 'block';
                }

            } catch(e) { console.error(e); }
            finally {
                isLoading = false;
                document.getElementById('loader').style.display = 'none';
            }
        }

        function resetAndLoad() {
            page = 1;
            loadData(false);
        }

        function loadNextPage() {
            page++;
            loadData(true);
        }

        // Init
        loadData();
    </script>
</body>
</html>
""")

# ==============================================================================
# 5. 실행 스크립트
# ==============================================================================
def generate_scripts():
    write_file(os.path.join(SCRIPTS_DIR, "run_all.sh"), """
#!/bin/bash
echo "🔥 Building OmniDex V2..."
cd "$(dirname "$0")/../"
mvn clean package -DskipTests
echo "🚀 Starting Server..."
java -jar target/*.jar
""")
    if os.name != 'nt': os.chmod(os.path.join(SCRIPTS_DIR, "run_all.sh"), 0o755)

# ==============================================================================
# 🔥 메인 실행
# ==============================================================================
async def main():
    print("===========================================")
    print("🚀 OmniDex V2: Massive Data & PWA Setup")
    print("===========================================")
    
    create_directories()
    generate_config()
    await fetch_data() # 1025마리 수집
    generate_java()
    generate_pwa_frontend()
    generate_scripts()

    print("\n✅ 설치 완료!")
    print(f"👉 폴더 이동: cd {PROJECT_NAME}")
    print("👉 실행 방법 (Mac/Linux): ./scripts/run_all.sh")
    print("👉 실행 방법 (Windows): mvn clean package && java -jar target/*.jar")
    print("👉 브라우저 접속: http://localhost:8086")
    print("👉 **앱 설치 확인**: 브라우저 주소창 우측 '앱 설치' 아이콘 또는 메뉴 확인")

if __name__ == "__main__":
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
