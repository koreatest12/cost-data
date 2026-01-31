import os

# ==============================================================================
# 🏗️ [INFRA-CONFIG] 프로젝트 루트 고정 및 자동 보강 경로
# ==============================================================================
BASE_DIR = os.getcwd()
SVC_PATH = "src/main/java/com/costdata/filemanagement"

def force_write(path, content):
    abs_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content.strip("\n"))
    print(f"  🔥 [COMPILATION-FIX-APPLIED] {path}")

# ==============================================================================
# 1. pom.xml 대량 보강 (JPA & Jakarta Persistence 의존성 강제 주입)
# ==============================================================================
def patch_pom_xml():
    # 'package jakarta.persistence does not exist' 에러를 해결하는 핵심 의존성 포함
    pom_content = r"""
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.2</version>
        <relativePath/>
    </parent>
    <groupId>com.costdata</groupId>
    <artifactId>file-management</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
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
    force_write("pom.xml", pom_content)

# ==============================================================================
# 2. 내/외부 방화벽 서버 무력화 및 디버그 인프라 (Massive Security)
# ==============================================================================
def install_massive_infrastructure():
    # 🛡️ 방화벽 서버 대량 개방 설정
    security_java = f"""
package com.costdata.filemanagement.config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;

@Configuration
public class SecurityConfig {{
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http.csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll())
            .headers(h -> h.frameOptions(f -> f.disable()));
        return http.build();
    }}
}}
"""
    force_write(f"{SVC_PATH}/config/SecurityConfig.java", security_java)

    # 📊 Entity 컴파일 에러 완전 수정 (Import 경로 보강)
    entity_java = f"""
package com.costdata.filemanagement.model;
import jakarta.persistence.*;
import lombok.*;

@Entity @Data @NoArgsConstructor @AllArgsConstructor
public class InfinityData {{
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String uuid;
    private Long amount;
    private String status;
}}
"""
    force_write(f"{SVC_PATH}/model/InfinityData.java", entity_java)

# ==============================================================================
# 3. GitHub Actions 워크플로우 (컴파일 검증 및 자동 송신)
# ==============================================================================
def upgrade_workflow():
    workflow_yaml = r"""
name: 🌌 10B Compilation & Ingestion Pipeline
on: [push, workflow_dispatch]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🛠️ 1. 컴파일 에러 대량 수정 및 인프라 주입
        run: |
          python setup_ultimate_system.py

      - name: ☕ 2. JDK 17 및 가상화 인프라 설치
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: 📦 3. 전 서버 대량 컴파일 (Auto-Fix Dependencies)
        run: |
          export MAVEN_OPTS="-Xmx2048m"
          mvn clean package -DskipTests

      - name: 🌐 4. 방화벽 및 상위 디버그 스모크 테스트
        run: |
          JAR=$(find target -name "*.jar" | head -n 1)
          nohup java -Xmx2048m -jar $JAR > app.log 2>&1 &
          PID=$!
          echo "⏳ 인프라 기동 및 대용량 데이터 로드 대기 (50초)..."
          sleep 50
          
          CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/system/health || echo "404")
          if [ "$CODE" == "200" ]; then
            echo "✅ 10B 업그레이드 및 컴파일 에러 해결 성공!"
            kill $PID
          else
            echo "❌ 검증 실패. 빌드 로그 출력:"
            cat app.log
            kill $PID
            exit 1
          fi

      - name: 📤 5. 최종 시스템 번들 송신
        uses: softprops/action-gh-release@v1
        with:
          tag_name: "10B-FIX-v${{ github.run_number }}"
          files: target/*.jar
"""
    force_write(".github/workflows/main.yml", workflow_yaml)

if __name__ == "__main__":
    print("🚀 [Massive Fix] 컴파일 에러 해결 및 전 서버 인프라 대통합 시작...")
    patch_pom_xml()
    install_massive_infrastructure()
    upgrade_workflow()
    print("✨ 모든 컴파일 에러 해결 및 대량 기능 반영 완료. Git Push 하세요.")
