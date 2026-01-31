import os
import shutil

# ==============================================================================
# 🏗️ [설정] 프로젝트 루트 및 경로 정의
# ==============================================================================
BASE_DIR = os.getcwd()
GITHUB_DIR = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_DIR, "workflows")

def force_write_file(path, content):
    """디렉토리를 보장하며 항상 덮어쓰기 (No such file or directory 방지)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip("\n"))
    print(f"  🔥 [Updated/Created] {path}")

# ==============================================================================
# PHASE 1 — 대량 데이터 처리를 위한 Java 인프라 수정 (JPA 에러 해결)
# ==============================================================================
def patch_java_services():
    print("\n🛠️ [Phase 1] Patching Java Services for Massive Data & JPA...")
    
    # 1. 공통 pom.xml 패치 (Jakarta Persistence & Hibernate 의존성 강제 주입)
    infinity_pom = r"""
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>omni-infinity-api</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/>
    </parent>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
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
    force_write_file(os.path.join(BASE_DIR, "services/omni-infinity-api/pom.xml"), infinity_pom)

# ==============================================================================
# PHASE 2 — 대량 데이터 생성 스크립트 (Python 데이터 팩토리)
# ==============================================================================
def generate_data_factory():
    print("\n🏭 [Phase 2] Generating Massive Data Factory Script...")
    
    factory_script = r"""
import csv, uuid, random, os
from datetime import datetime

def generate_massive_csv(file_path, count=100000):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    categories = ['AWS', 'Marketing', 'Payroll', 'R&D', 'Legal']
    statuses = ['APPROVED', 'PENDING', 'REJECTED']
    
    print(f"🚀 Creating {count} records at {file_path}...")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['uuid', 'category', 'amount', 'vendor', 'description', 'status', 'created_at'])
        for _ in range(count):
            writer.writerow([
                str(uuid.uuid4()),
                random.choice(categories),
                random.randint(1000, 1000000),
                f"Vendor-{random.randint(1, 100)}",
                "Massive data dump for performance testing",
                random.choice(statuses),
                datetime.now().isoformat()
            ])
    print("✅ Generation Complete.")

if __name__ == "__main__":
    target = "services/omni-infinity-api/src/main/resources/massive_data.csv"
    generate_massive_csv(target, 100000)
"""
    force_write_file(os.path.join(BASE_DIR, "data_factory.py"), factory_script)

# ==============================================================================
# PHASE 3 — 워크플로우 업그레이드 (디렉토리 생성 자동화 포함)
# ==============================================================================
def upgrade_workflow():
    print("\n🔧 [Phase 3] Upgrading GitHub Actions Workflow...")
    
    workflow_content = r"""
name: 🌌 Ultimate CI/CD (Auto-Repair & Massive Scale)
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:
    inputs:
      data_size:
        description: '생성할 데이터 건수'
        default: '50000'

jobs:
  build-and-dump:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🛠️ 1. 구조 강제 복구 (Auto-Repair)
        run: |
          mkdir -p services/omni-infinity-api/src/main/resources
          mkdir -p services/omni-infinity-api/src/main/java/com/omni/infinity
          ls -R services

      - name: 🐍 2. 데이터 덤프 실행
        run: |
          python data_factory.py
          echo "CSV Size: $(du -sh services/omni-infinity-api/src/main/resources/massive_data.csv)"

      - name: ☕ 3. JDK 설정 및 빌드
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: 📦 4. 대량 데이터 포함 빌드
        run: |
          cd services/omni-infinity-api
          mvn clean package -DskipTests

      - name: 📤 5. 결과물 업로드
        uses: actions/upload-artifact@v4
        with:
          name: massive-infinity-server
          path: services/omni-infinity-api/target/*.jar
"""
    force_write_file(os.path.join(WORKFLOWS_DIR, "ci-full-pipeline.yml"), workflow_content)

# ==============================================================================
# Main Execution
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Omni System Upgrade Starting...")
    
    # 디렉토리 구조 우선 생성 (가장 중요)
    os.makedirs(os.path.join(BASE_DIR, "services/omni-infinity-api/src/main/java/com/omni/infinity"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "services/omni-infinity-api/src/main/resources"), exist_ok=True)
    
    patch_java_services()
    generate_data_factory()
    upgrade_workflow()
    
    print("\n✅ 모든 수정 사항이 반영되었습니다.")
    print("👉 이제 git add/commit/push를 실행하면 워크플로우가 디렉토리를 자동 생성하고 빌드합니다.")
