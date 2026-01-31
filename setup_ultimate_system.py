import os
import json

# ==============================================================================
# 🏗️ [설정] 프로젝트: AI Trends 2026 + PWA + Stable CI
# ==============================================================================
BASE_DIR = os.getcwd()
# Git 호환성을 위해 폴더명은 유지하되, 내부는 AI 프로젝트로 전면 개편
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PKG = os.path.join(SRC_MAIN, "java/com/omni/ai")
RESOURCES = os.path.join(SRC_MAIN, "resources")
STATIC_DIR = os.path.join(RESOURCES, "static")
WORKFLOWS_DIR = os.path.join(BASE_DIR, ".github/workflows")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ [생성] {os.path.basename(path)}")

# ==============================================================================
# 1. 📊 [DATA] 2026 AI Trends Data (Massive Update)
# ==============================================================================
def generate_data():
    data = {
        "meta": {"version": "2026.1.0", "topic": "Generative AI Rankings"},
        "text_rankings": [
            {"rank": 1, "model": "Gemini-3-Pro", "elo": 1492, "corp": "Google", "desc": "압도적인 멀티모달 성능 및 생태계 통합"},
            {"rank": 2, "model": "Grok-4.1-Thinking", "elo": 1482, "corp": "xAI", "desc": "실시간 데이터 분석 및 추론 능력 급상승"},
            {"rank": 3, "model": "Gemini-3-Flash", "elo": 1470, "corp": "Google", "desc": "속도와 성능의 완벽한 밸런스"},
            {"rank": 4, "model": "Claude Opus 4.5", "elo": 1466, "corp": "Anthropic", "desc": "복잡한 추론 및 긴 문맥 처리에 특화"},
            {"rank": 5, "model": "GPT-5.2-high", "elo": 1465, "corp": "OpenAI", "desc": "비즈니스 자동화 및 범용성 우수"}
        ],
        "coding_rankings": [
            {"rank": 1, "model": "Claude Opus 4.5", "elo": 1510, "desc": "SWE-bench 1위, 시스템 아키텍처 설계 강자"},
            {"rank": 2, "model": "Gemini-3-Pro", "elo": 1501, "desc": "구글 클라우드/안드로이드 개발 최적화"},
            {"rank": 3, "model": "Claude Sonnet 4.5", "elo": 1485, "desc": "편집 오류율 0%, 속도 5배, 실무 코딩 표준"}
        ],
        "sonnet_specs": [
            {"title": "SWE-bench Verified", "val": "77.2%", "desc": "업계 최고 점수 달성"},
            {"title": "Zero Edit Error", "val": "0%", "desc": "코드 수정 시 문법 오류 없음"},
            {"title": "Speed Factor", "val": "5x", "desc": "기존 모델 대비 5배 빠른 처리"},
            {"title": "Integration", "val": "VS Code", "desc": "네이티브 확장 지원 (Claude Code 2.0)"}
        ],
        "commands": [
            {"cmd": "claude --dangerously-skip-permissions", "desc": "모든 권한 자동 승인 (주의: Sandbox 권장)"},
            {"cmd": "/checkpoint & /rewind", "desc": "작업 상태 저장 및 되감기 (타임머신 기능)"},
            {"cmd": "claude --allowed-tools 'Edit,Bash'", "desc": "특정 도구만 허용하여 보안 강화"},
            {"cmd": "/model sonnet-4.5", "desc": "모델 즉시 전환 (가성비 및 속도 최적화)"}
        ]
    }
    write_file(os.path.join(RESOURCES, "ai_data.json"), json.dumps(data, indent=2, ensure_ascii=False))

# ==============================================================================
# 2. ☕ Java Backend (Stable & Optimized)
# ==============================================================================
def generate_backend():
    # Model
    write_file(os.path.join(JAVA_PKG, "model/AiData.java"), """
package com.omni.ai.model;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class AiData {
    private Map<String, String> meta;
    private List<Ranking> text_rankings;
    private List<Ranking> coding_rankings;
    private List<Spec> sonnet_specs;
    private List<Cmd> commands;

    @Data public static class Ranking { int rank; String model; int elo; String corp; String desc; }
    @Data public static class Spec { String title; String val; String desc; }
    @Data public static class Cmd { String cmd; String desc; }
}
""")
    
    # Service
    write_file(os.path.join(JAVA_PKG, "service/AiService.java"), """
package com.omni.ai.service;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.omni.ai.model.AiData;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.InputStream;

@Service
public class AiService {
    private AiData data;
    private final ObjectMapper mapper = new ObjectMapper();

    @PostConstruct
    public void init() {
        try {
            InputStream is = getClass().getResourceAsStream("/ai_data.json");
            if(is != null) data = mapper.readValue(is, AiData.class);
        } catch(Exception e) { e.printStackTrace(); }
    }
    public AiData getData() { return data; }
}
""")

    # Controllers
    write_file(os.path.join(JAVA_PKG, "controller/AiController.java"), """
package com.omni.ai.controller;
import com.omni.ai.model.AiData;
import com.omni.ai.service.AiService;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class AiController {
    private final AiService service;
    @GetMapping("/trends") public AiData getTrends() { return service.getData(); }
}
""")
    
    write_file(os.path.join(JAVA_PKG, "controller/SystemController.java"), """
package com.omni.ai.controller;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/system")
public class SystemController {
    @GetMapping("/health") public String health() { return "OK"; }
    @GetMapping("/info") public Map<String, String> info() { return Map.of("app", "AI-Trends", "ver", "2026.V3"); }
}
""")

    # Main App
    write_file(os.path.join(JAVA_PKG, "OmniAiApp.java"), """
package com.omni.ai;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class OmniAiApp {
    public static void main(String[] args) { SpringApplication.run(OmniAiApp.class, args); }
}
""")
    
    # Config
    write_file(os.path.join(RESOURCES, "application.properties"), "server.port=8086\nserver.compression.enabled=true")

# ==============================================================================
# 3. 📱 Frontend (PWA + Dashboard + Install)
# ==============================================================================
def generate_frontend():
    # 1. Manifest
    write_file(os.path.join(STATIC_DIR, "manifest.json"), """
{
  "name": "2026 AI Insight",
  "short_name": "AI 2026",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#3b82f6",
  "icons": [
    {"src": "https://cdn-icons-png.flaticon.com/512/4712/4712109.png", "sizes": "192x192", "type": "image/png"},
    {"src": "https://cdn-icons-png.flaticon.com/512/4712/4712109.png", "sizes": "512x512", "type": "image/png"}
  ]
}
""")
    
    # 2. Service Worker
    write_file(os.path.join(STATIC_DIR, "sw.js"), """
const CACHE_NAME = 'ai-trends-v3';
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(['/', '/index.html', '/manifest.json']))));
self.addEventListener('fetch', e => {
    if(e.request.url.includes('/api/')) e.respondWith(fetch(e.request));
    else e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});
""")

    # 3. HTML (UI)
    write_file(os.path.join(STATIC_DIR, "index.html"), """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2026 AI Trends Master</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0f172a; color: #f1f5f9; font-family: sans-serif; -webkit-tap-highlight-color: transparent; }
        .glass { background: rgba(30,41,59,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
        .grad-text { background: linear-gradient(135deg, #60a5fa, #a855f7); -webkit-background-clip: text; color: transparent; }
    </style>
</head>
<body class="min-h-screen pb-20">
    
    <nav class="sticky top-0 z-50 glass border-b-0 border-slate-800 px-6 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold flex items-center gap-2">
            <i class="fa-solid fa-brain text-purple-500"></i> <span class="grad-text">AI 2026</span>
        </h1>
        <button id="installBtn" class="hidden bg-blue-600 hover:bg-blue-500 px-4 py-1.5 rounded-full text-sm font-bold shadow-lg transition animate-pulse">
            <i class="fa-solid fa-download"></i> 앱 설치
        </button>
    </nav>

    <main class="max-w-6xl mx-auto p-6 space-y-10">
        
        <div class="text-center py-10">
            <h2 class="text-4xl md:text-5xl font-extrabold mb-4">Generative AI Landscape</h2>
            <p class="text-slate-400">Gemini 3 Pro, Grok 4, Claude Sonnet 4.5 완벽 분석</p>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-bold mb-4 text-blue-400"><i class="fa-solid fa-trophy"></i> Chatbot Arena (Text)</h3>
                <div id="textList" class="space-y-3"></div>
            </div>
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-bold mb-4 text-purple-400"><i class="fa-solid fa-code"></i> SWE-bench (Coding)</h3>
                <div id="codeList" class="space-y-3"></div>
            </div>
        </div>

        <div class="glass rounded-2xl p-8 relative overflow-hidden">
            <div class="absolute -right-20 -top-20 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl"></div>
            <h3 class="text-2xl font-bold mb-6">Claude Sonnet 4.5 Highlights</h3>
            <div id="specGrid" class="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10"></div>
        </div>

        <div class="glass rounded-2xl overflow-hidden">
            <div class="bg-slate-800/50 p-4 border-b border-slate-700 font-bold">Claude Code 2.0 CLI Cheat Sheet</div>
            <div id="cmdList" class="divide-y divide-slate-700/50"></div>
        </div>

    </main>

    <script>
        // PWA Install
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault(); deferredPrompt = e;
            document.getElementById('installBtn').classList.remove('hidden');
        });
        document.getElementById('installBtn').addEventListener('click', async () => {
            if(deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                if(outcome === 'accepted') document.getElementById('installBtn').classList.add('hidden');
                deferredPrompt = null;
            }
        });
        if('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');

        // Load Data
        fetch('/api/ai/trends').then(res => res.json()).then(data => {
            // Text Rank
            document.getElementById('textList').innerHTML = data.text_rankings.map(r => `
                <div class="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
                    <div class="flex items-center gap-3">
                        <span class="text-xl font-bold ${r.rank===1?'text-yellow-400':'text-slate-500'}">#${r.rank}</span>
                        <div>
                            <div class="font-bold">${r.model}</div>
                            <div class="text-xs text-slate-400">${r.corp}</div>
                        </div>
                    </div>
                    <div class="font-mono font-bold text-blue-300">${r.elo}</div>
                </div>
            `).join('');

            // Code Rank
            document.getElementById('codeList').innerHTML = data.coding_rankings.map(r => `
                <div class="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
                    <div>
                        <div class="font-bold text-purple-200">${r.model}</div>
                        <div class="text-xs text-slate-500">${r.desc.substring(0,30)}...</div>
                    </div>
                    <div class="font-mono font-bold text-purple-400">${r.elo}</div>
                </div>
            `).join('');

            // Specs
            document.getElementById('specGrid').innerHTML = data.sonnet_specs.map(s => `
                <div class="bg-slate-900/50 p-4 rounded-xl text-center border border-slate-700">
                    <div class="text-2xl font-extrabold text-white mb-1">${s.val}</div>
                    <div class="text-sm font-bold text-purple-400 mb-2">${s.title}</div>
                    <div class="text-xs text-slate-500">${s.desc}</div>
                </div>
            `).join('');

            // Commands
            document.getElementById('cmdList').innerHTML = data.commands.map(c => `
                <div class="p-4 hover:bg-slate-800/30 transition">
                    <code class="block text-green-400 font-mono text-sm mb-1">${c.cmd}</code>
                    <div class="text-slate-400 text-sm">${c.desc}</div>
                </div>
            `).join('');
        });
    </script>
</body>
</html>
""")

# ==============================================================================
# 4. 🛡️ DevOps (The Ultimate Fix)
# ==============================================================================
def generate_devops():
    # 1. POM
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>2026.3.0-FINAL</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
    </parent>
    <properties><java.version>17</java.version></properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>
    </dependencies>
    <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
""")

    # 2. CI/CD (Smart Check + Connection Fix)
    write_file(os.path.join(WORKFLOWS_DIR, "ci-ultimate.yml"), """
name: Ultimate Platform CI
on: [push, pull_request]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: 🔨 Build
        working-directory: ./services/omni-pokemon-web
        run: mvn clean package -DskipTests

      - name: 🚀 Start & Health Check (Smart Polling)
        working-directory: ./services/omni-pokemon-web
        run: |
          echo "🔥 Starting Server (512MB Heap)..."
          nohup java -Xmx512m -Dfile.encoding=UTF-8 -jar target/*.jar > app.log 2>&1 &
          PID=$!
          
          echo "⏳ Waiting for server (up to 120s)..."
          for i in {1..24}; do
            sleep 5
            if curl -s http://localhost:8086/api/system/health | grep "OK"; then
              echo "✅ Server is UP!"
              exit 0
            fi
            echo "Attempt $i: waiting..."
          done
          
          echo "❌ Server failed to respond."
          cat app.log
          kill $PID
          exit 1
""")
    
    # 3. Docker
    write_file(os.path.join(PROJECT_ROOT, "Dockerfile"), "FROM eclipse-temurin:17-jdk-alpine\nCOPY target/*.jar app.jar\nENTRYPOINT [\"java\",\"-Xmx512m\",\"-jar\",\"app.jar\"]")
    
    # 4. Push Script
    script_path = os.path.join(BASE_DIR, "push_ultimate.sh")
    write_file(script_path, """
#!/bin/bash
echo "🚀 Deploying Ultimate V3 (AI + PWA + Stability)..."
git config --global user.email "bot@omni.com"
git config --global user.name "Omni Bot"
git add .
git commit -m "Feat: Complete Overhaul - AI Trends 2026, PWA, Smart CI"
git push
echo "✅ Deployed. Check GitHub Actions."
""")
    if os.name != 'nt': os.chmod(script_path, 0o755)

# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    print("🤖 Building Ultimate AI Platform V3...")
    generate_data()    # 2026 Content
    generate_backend() # Java Logic
    generate_frontend()# PWA + UI
    generate_devops()  # Fixes
    
    print("\n🎉 [최종 완료] 모든 기능이 통합되었습니다.")
    print("1. 2026 AI 데이터 (Gemini 3/Claude 4.5)")
    print("2. PWA 앱 설치 기능 (Manifest/SW)")
    print("3. CI/CD 연결 오류 완전 해결 (Smart Polling)")
    print("\n👉 아래 명령어로 배포하세요:\n    ./push_ultimate.sh")
