import os

# ==============================================================================
# 🏗️ [설정] 프로젝트 절대 경로
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)
GITHUB_WORKFLOWS = os.path.join(BASE_DIR, ".github/workflows")
SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_CONTROLLER = os.path.join(SRC_MAIN, "java/com/omni/pokemon/controller")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 수정 완료: {os.path.basename(path)}")

# ==============================================================================
# 1. 🤖 CI/CD 워크플로우 수정 (Exit Code 7 해결)
# ==============================================================================
def fix_github_action():
    # Health Check 로직을 'Wait-for-it' 방식으로 변경
    write_file(os.path.join(GITHUB_WORKFLOWS, "ci-fix-connection.yml"), """
name: Ultimate CI (Connection Fix)
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: 🔨 Build with Maven
        working-directory: ./services/omni-pokemon-web
        run: mvn clean package -DskipTests

      - name: 🌐 Server Start & Smart Health Check
        working-directory: ./services/omni-pokemon-web
        run: |
          echo "🔥 서버 시작 (JVM 메모리 옵션 추가)..."
          # -Xmx512m: 힙 메모리 제한 (GitHub Runner 환경 고려)
          # -Dfile.encoding=UTF-8: 한글 깨짐 방지
          nohup java -Xmx512m -Dfile.encoding=UTF-8 -jar target/*.jar > app.log 2>&1 &
          PID=$!
          echo "PID: $PID"
          
          echo "⏳ 부팅 대기 (최대 120초 polling)..."
          
          # 스마트 재시도 루프 (Connection Refused 방지)
          for i in {1..24}; do
            sleep 5
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8086/api/system/health || echo "000")
            echo "Attempt $i: HTTP $HTTP_CODE"
            
            if [ "$HTTP_CODE" -eq 200 ]; then
              echo "✅ 서버 가동 확인 완료!"
              break
            fi
            
            if [ $i -eq 24 ]; then
              echo "❌ 타임아웃: 서버가 120초 내에 응답하지 않았습니다."
              echo "=== 앱 로그 (app.log) ==="
              cat app.log
              kill $PID
              exit 1
            fi
          done
          
          echo "🧪 데이터 검색 테스트"
          SEARCH_RES=$(curl -s -G --data-urlencode "keyword=피카츄" http://localhost:8086/api/pokemon/search)
          
          if [[ "$SEARCH_RES" == *"피카츄"* ]]; then
             echo "✅ 테스트 성공! (피카츄 발견)"
          else
             echo "❌ 검색 실패 (데이터 로드 문제)"
             echo "응답: $SEARCH_RES"
             cat app.log
             kill $PID
             exit 1
          fi
          
          kill $PID
""")

# ==============================================================================
# 2. 🛡️ Controller 경로 수정 (404 방지)
# ==============================================================================
def fix_controller_path():
    # API 경로가 /api/system/health 인지 /api/health 인지 확실히 매핑
    write_file(os.path.join(JAVA_CONTROLLER, "SystemController.java"), """
package com.omni.pokemon.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/api/system")
public class SystemController {
    
    @GetMapping("/health")
    public String health() {
        return "OK";
    }
    
    @GetMapping("/info")
    public Map<String, String> info() {
        return Map.of("status", "UP", "version", "v3.0-FIX");
    }
}
""")

# ==============================================================================
# 3. 🚀 Git Push Script
# ==============================================================================
def generate_push_script():
    script_path = os.path.join(BASE_DIR, "push_connection_fix.sh")
    write_file(script_path, """
#!/bin/bash
echo "🔧 Applying Connection Fix & Pushing..."

git config --global user.email "bot@omni.com"
git config --global user.name "Omni Bot"

git add .
git commit -m "Fix: Add Smart Health Check (Loop) & JVM Options"
git push

echo "✅ Pushed! Check GitHub Actions now."
""")
    if os.name != 'nt':
        os.chmod(script_path, 0o755)

# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Fixing Connection Refused Error...")
    fix_github_action()
    fix_controller_path()
    generate_push_script()
    print("\n🎉 수정 파일 생성 완료.")
    print("👉 아래 명령어를 실행하여 GitHub에 반영하세요:")
    print("    ./push_connection_fix.sh")
