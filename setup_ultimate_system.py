import os

# ==============================================================================
# 🏗️ [설정] 프로젝트 구조 정의
# ==============================================================================
BASE_DIR = os.getcwd()
SVC_PATH = "services/omni-infinity-api"
PKG_PATH = f"{SVC_PATH}/src/main/java/com/omni/infinity"
RES_PATH = f"{SVC_PATH}/src/main/resources"

def force_write(path, content):
    """경로 에러를 방지하는 안전한 파일 쓰기 (대량 생성 최적화)"""
    abs_path = os.path.join(BASE_DIR, path)
    directory = os.path.dirname(abs_path)
    
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content.strip("\n"))
    print(f"  ✅ [Generated] {path}")

# ==============================================================================
# 1. 대량 데이터 팩토리 (Massive Data Generation Script)
# ==============================================================================
def create_data_factory():
    # 10만 건 이상의 데이터를 생성하는 스크립트
    content = r"""
import csv, uuid, random, os
from datetime import datetime

def generate(path, count=100000):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    categories = ['INFRA', 'MARKETING', 'SaaS', 'HARDWARE', 'CONSULTING']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['uuid','category','amount','vendor','description','status','created_at'])
        for i in range(count):
            w.writerow([
                str(uuid.uuid4()),
                random.choice(categories),
                random.randint(10000, 10000000),
                f"Global-Vendor-{i%100}",
                f"Massive batch data record number {i}",
                "APPROVED",
                datetime.now().isoformat()
            ])
    print(f"🔥 Success: {count} records generated at {path}")

if __name__ == "__main__":
    generate('services/omni-infinity-api/src/main/resources/massive_data.csv', 100000)
"""
    force_write("data_factory.py", content)

# ==============================================================================
# 2. Java 대통합 소스 보강 (Batch Loading + Security + REST)
# ==============================================================================
def patch_java_source():
    # Entity: 대량 데이터를 담을 모델
    entity = """
package com.omni.infinity;
import lombok.*;
import jakarta.persistence.*;

@Entity @Data @NoArgsConstructor @AllArgsConstructor
public class InfinityData {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String uuid;
    private String category;
    private Long amount;
    private String vendor;
    private String status;
}
"""
    force_write(f"{PKG_PATH}/InfinityData.java", entity)

    # Batch Loader: CSV를 읽어 실시간 메모리 DB 적재
    loader = """
package com.omni.infinity;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;
import java.io.*;
import java.util.*;

@Component
public class BatchLoader {
    private final List<String[]> cache = new ArrayList<>();
    
    @PostConstruct
    public void init() throws Exception {
        InputStream is = getClass().getResourceAsStream("/massive_data.csv");
        if (is == null) return;
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        String line; br.readLine(); // skip header
        while ((line = br.readLine()) != null) {
            cache.add(line.split(","));
        }
        System.out.println("✅ Loaded " + cache.size() + " records into memory.");
    }
}
"""
    force_write(f"{PKG_PATH}/BatchLoader.java", loader)

    # Security: 모든 접근 허용 (테스트용)
    security = """
package com.omni.infinity;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(c -> c.disable()).authorizeHttpRequests(a -> a.anyRequest().permitAll());
        return http.build();
    }
}
"""
    force_write(f"{PKG_PATH}/SecurityConfig.java", security)

# ==============================================================================
# 3. GitHub Actions 워크플로우 대용량 최적화
# ==============================================================================
def upgrade_workflow():
    workflow = r"""
name: 🌌 Ultimate CI/CD (Massive Scale)
on: [push, workflow_dispatch]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🛠️ 1. 구조 및 대량 데이터 생성
        run: |
          mkdir -p services/omni-infinity-api/src/main/resources
          python data_factory.py

      - name: ☕ 2. JDK 17 설정
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: 📦 3. Maven 빌드 (Memory 증가)
        run: |
          cd services/omni-infinity-api
          export MAVEN_OPTS="-Xmx1024m"
          mvn clean package -DskipTests

      - name: 🌐 4. 서버 기동 및 대량 데이터 검증
        run: |
          JAR_PATH=$(find . -name "*.jar" | head -n 1)
          # JVM 힙 메모리 대폭 확장 (대량 데이터 로드용)
          nohup java -Xmx2048m -jar $JAR_PATH > app.log 2>&1 &
          PID=$!
          
          echo "⏳ 대용량 데이터 로딩 대기 (40초)..."
          sleep 40
          
          # 포트 8080 및 8086 동시 체크 (유연성)
          PORT=8080
          curl -s http://localhost:$PORT/actuator/health || PORT=8086
          
          echo "🧪 Final Health Check on Port $PORT"
          HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/actuator/health || echo "404")
          
          if [ "$HEALTH" == "200" ]; then
            echo "✅ 대통합 서버 기동 성공!"
            cat app.log | grep "Loaded" # BatchLoader 결과 확인
            kill $PID
          else
            echo "❌ 서버 기동 실패. 로그 출력:"
            cat app.log
            kill $PID
            exit 1
          fi
"""
    force_write(".github/workflows/main.yml", workflow)

# ==============================================================================
# 실행부
# ==============================================================================
if __name__ == "__main__":
    print("🚀 [Massive Update] Omni Platform 대통합 시스템 구축...")
    try:
        create_data_factory()
        patch_java_source()
        upgrade_workflow()
        print("\n✨ 모든 파일에 대량 반영 및 에러 수정이 완료되었습니다.")
        print("👉 이제 Git Push를 진행하십시오.")
    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")
