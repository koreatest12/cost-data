import os
import yaml # pip install pyyaml (없으면 기본 처리)

# ==============================================================================
# 🏗️ [설정] 프로젝트 루트 및 경로 정의
# ==============================================================================
BASE_DIR = os.getcwd()
GITHUB_DIR = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_DIR, "workflows")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ [Created] {path}")

def force_write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"🔥 [Updated] {path}")

# ==============================================================================
# 1. Dependabot & Directory Structure Sync (마이크로서비스 구조화)
# ==============================================================================
DEPENDABOT_CONTENT = """version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: {interval: "daily", time: "09:00", timezone: "Asia/Seoul"}
    labels: ["ci", "actions"]

  - package-ecosystem: "maven"
    directory: "/services/omni-gateway"
    schedule: {interval: "weekly", timezone: "Asia/Seoul"}
    labels: ["backend", "gateway"]
  
  - package-ecosystem: "maven"
    directory: "/services/omni-auth-service"
    schedule: {interval: "weekly", timezone: "Asia/Seoul"}
    labels: ["backend", "auth"]

  - package-ecosystem: "maven"
    directory: "/services/omni-cost-service"
    schedule: {interval: "daily", timezone: "Asia/Seoul"}
    labels: ["backend", "core"]

  - package-ecosystem: "maven"
    directory: "/services/omni-infinity-api" 
    schedule: {interval: "daily", timezone: "Asia/Seoul"}
    labels: ["backend", "infinity"]

  - package-ecosystem: "docker"
    directory: "/"
    schedule: {interval: "weekly", timezone: "Asia/Seoul"}
    labels: ["docker"]
    
  # ... (기타 서비스 포함)
"""

def sync_structure():
    print("\n🔄 [Phase 1] Syncing Project Structure & Dependabot...")
    force_write_file(os.path.join(GITHUB_DIR, "dependabot.yml"), DEPENDABOT_CONTENT)

    # 구조 정의 (경로, 생태계)
    tasks = [
        ("/", "docker"),
        ("/services/omni-gateway", "maven"), ("/services/omni-gateway", "docker"),
        ("/services/omni-auth-service", "maven"), ("/services/omni-auth-service", "docker"),
        ("/services/omni-cost-service", "maven"), ("/services/omni-cost-service", "docker"),
        ("/services/omni-infinity-api", "maven"), ("/services/omni-infinity-api", "docker"), # Infinity API 추가
        ("/ai-model", "pip"), ("/ai-model", "docker"),
        ("/infra/terraform", "terraform")
    ]

    for directory, eco in tasks:
        clean_dir = directory.lstrip("/")
        if clean_dir == "": clean_dir = "."
        full_path = os.path.join(BASE_DIR, clean_dir)
        os.makedirs(full_path, exist_ok=True)

        # Skeleton 파일 생성
        if eco == "maven":
            if not os.path.exists(os.path.join(full_path, "pom.xml")):
                write_file(os.path.join(full_path, "pom.xml"), f"""
<project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>{os.path.basename(clean_dir)}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/>
    </parent>
</project>
""")
        elif eco == "docker":
            if not os.path.exists(os.path.join(full_path, "Dockerfile")):
                write_file(os.path.join(full_path, "Dockerfile"), "FROM eclipse-temurin:17-jdk-alpine\nENTRYPOINT [\"java\", \"-jar\", \"app.jar\"]")
        elif eco == "pip":
            if not os.path.exists(os.path.join(full_path, "requirements.txt")):
                write_file(os.path.join(full_path, "requirements.txt"), "requests==2.31.0")

# ==============================================================================
# 2. Infinity Scale Pipeline (대량 데이터 생성 및 배포 워크플로우)
# ==============================================================================
def generate_infinity_workflow():
    print("\n🌌 [Phase 2] Generating Infinity Scale Workflow...")
    
    workflow_content = """name: 🌌 Infinity Scale Data & Deployment System
on:
  workflow_dispatch:
    inputs:
      record_count:
        description: '생성할 데이터 건수 (Max: Runner Memory)'
        required: true
        default: '100000'
  push:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * *' # 매일 자정 초대량 갱신

env:
  PROJECT_NAME: "services/omni-infinity-api" # 구조에 맞게 경로 수정
  DOCKER_IMAGE: "omni-infinity-server"
  VERSION: "v2026.${{ github.run_number }}.999"

jobs:
  # [Job 1] 초거대 데이터 생산 공장
  data-factory:
    runs-on: ubuntu-latest
    outputs:
      data_path: ${{ steps.gen.outputs.path }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: pip install pandas numpy faker tqdm
      
      - name: 🏭 Infinity Generator 실행
        id: gen
        run: |
          mkdir -p resources_data
          cat <<'EOF' > generator.py
          import os, csv, uuid, random
          from faker import Faker
          from datetime import datetime
          import numpy as np
          
          COUNT = int(os.environ.get('INPUT_COUNT', 100000))
          FILE_PATH = 'resources_data/massive_data.csv'
          fake = Faker('ko_KR')
          
          print(f"🚀 [Generator] Creating {COUNT:,} records...")
          with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
              writer = csv.writer(f)
              writer.writerow(['uuid', 'category', 'amount', 'vendor', 'description', 'status', 'created_at'])
              batch_size = 10000
              for i in range(0, COUNT, batch_size):
                  rows = []
                  curr = min(batch_size, COUNT - i)
                  amounts = np.random.randint(10000, 10000000, size=curr)
                  for j in range(curr):
                      rows.append([
                          str(uuid.uuid4()),
                          random.choice(['AWS', 'Marketing', 'Payroll']),
                          amounts[j],
                          fake.company(),
                          fake.bs(),
                          random.choice(['APPROVED', 'PENDING']),
                          datetime.now().isoformat()
                      ])
                  writer.writerows(rows)
                  print(f"   ... Processed {i + curr:,}")
          EOF
          export INPUT_COUNT=${{ github.event.inputs.record_count || '100000' }}
          python generator.py
          echo "path=resources_data" >> $GITHUB_OUTPUT

      - uses: actions/upload-artifact@v4
        with: { name: raw-massive-data, path: resources_data/ }

  # [Job 2] 백엔드 구축 및 배포
  backend-deploy:
    needs: data-factory
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: raw-massive-data, path: resources_data }
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin', cache: 'maven' }

      - name: 🏗️ 시스템 아키텍처 자동 생성 (Dynamic)
        run: |
          APP_DIR="${{ env.PROJECT_NAME }}"
          PKG_DIR="$APP_DIR/src/main/java/com/omni/infinity"
          RES_DIR="$APP_DIR/src/main/resources"
          mkdir -p $PKG_DIR $RES_DIR
          mv resources_data/massive_data.csv $RES_DIR/
          
          # POM Generation
          cat <<EOF > $APP_DIR/pom.xml
          <project xmlns="http://maven.apache.org/POM/4.0.0" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <modelVersion>4.0.0</modelVersion>
            <groupId>com.omni</groupId>
            <artifactId>infinity-api</artifactId>
            <version>999.0.0</version>
            <parent>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-parent</artifactId>
                <version>3.2.1</version>
                <relativePath/>
            </parent>
            <dependencies>
                <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
                <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
                <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency>
                <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
                <dependency><groupId>org.springdoc</groupId><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId><version>2.3.0</version></dependency>
            </dependencies>
            <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
          </project>
          EOF

          # Java Code (Batch Loader Engine)
          cat <<EOF > $PKG_DIR/BatchLoader.java
          package com.omni.infinity;
          import jakarta.annotation.PostConstruct;
          import lombok.RequiredArgsConstructor;
          import org.springframework.stereotype.Service;
          import java.io.*; import java.util.*;
          @Service @RequiredArgsConstructor
          public class BatchLoader {
              private final CostRepository repository;
              @PostConstruct public void init() throws Exception {
                  System.out.println("🔥 [Engine] Ingesting Data...");
                  try(BufferedReader br = new BufferedReader(new InputStreamReader(getClass().getResourceAsStream("/massive_data.csv")))) {
                      String l; br.readLine();
                      List<CostData> buf = new ArrayList<>();
                      while((l=br.readLine())!=null) {
                          String[] c = l.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
                          if(c.length>=7) buf.add(new CostData(c));
                          if(buf.size()>=5000) { repository.saveAll(buf); repository.flush(); buf.clear(); }
                      }
                      if(!buf.isEmpty()) repository.saveAll(buf);
                      System.out.println("✅ Loaded Complete.");
                  }
              }
          }
          EOF
          
          # Entity, Repository, Controller, App Class 생성 (생략된 부분 자동 포함)
          # ... (Entity Code)
          cat <<EOF > $PKG_DIR/CostData.java
          package com.omni.infinity;
          import jakarta.persistence.*; import lombok.Data; import lombok.NoArgsConstructor;
          @Entity @Data @NoArgsConstructor
          public class CostData {
              @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id;
              String uuid; String category; Long amount; String vendor; @Column(length=1000) String desc; String status; String createdAt;
              public CostData(String[] c) { uuid=c[0]; category=c[1]; amount=Long.parseLong(c[2]); vendor=c[3]; desc=c[4]; status=c[5]; createdAt=c[6]; }
          }
          EOF
          
          # ... (Repository Code)
          cat <<EOF > $PKG_DIR/CostRepository.java
          package com.omni.infinity;
          import org.springframework.data.jpa.repository.JpaRepository;
          public interface CostRepository extends JpaRepository<CostData, Long> {}
          EOF
          
          # ... (App Code)
          cat <<EOF > $PKG_DIR/App.java
          package com.omni.infinity;
          import org.springframework.boot.SpringApplication;
          import org.springframework.boot.autoconfigure.SpringBootApplication;
          @SpringBootApplication public class App { public static void main(String[] a) { SpringApplication.run(App.class, a); } }
          EOF
          
          # ... (Controller Code)
          cat <<EOF > $PKG_DIR/Api.java
          package com.omni.infinity;
          import org.springframework.web.bind.annotation.*; import lombok.RequiredArgsConstructor;
          @RestController @RequiredArgsConstructor @RequestMapping("/api")
          public class Api {
              private final CostRepository repo;
              @GetMapping("/stats") public Object stats() { return Map.of("count", repo.count(), "status", "INFINITY"); }
          }
          EOF

      - name: 🔨 Maven Build
        working-directory: ${{ env.PROJECT_NAME }}
        run: mvn clean package -DskipTests

      - name: 🚀 Verify & Release
        run: |
          # 1. Start Server
          nohup java -Xmx2048m -jar ${{ env.PROJECT_NAME }}/target/*.jar > app.log 2>&1 &
          PID=$!
          sleep 30 # Data Load Wait
          
          # 2. Test API
          curl http://localhost:8080/api/stats
          kill $PID
          
          # 3. Docker Build
          cd ${{ env.PROJECT_NAME }}
          echo 'FROM eclipse-temurin:17-jdk-alpine\nCOPY target/*.jar app.jar\nENTRYPOINT ["java","-jar","app.jar"]' > Dockerfile
          docker build -t ${{ env.DOCKER_IMAGE }}:${{ env.VERSION }} .
          docker save ${{ env.DOCKER_IMAGE }}:${{ env.VERSION }} > ../infinity_image.tar

      - name: 📦 GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ env.VERSION }}
          name: 🚀 Release ${{ env.VERSION }}
          files: |
            ${{ env.PROJECT_NAME }}/target/*.jar
            infinity_image.tar
            resources_data/massive_data.csv
"""
    force_write_file(os.path.join(WORKFLOWS_DIR, "infinity_pipeline.yml"), workflow_content)

# ==============================================================================
# 3. 🚀 Push Script
# ==============================================================================
def generate_push_script():
    script_path = os.path.join(BASE_DIR, "push_ultimate_system.sh")
    force_write_file(script_path, """
#!/bin/bash
echo "🚀 Deploying Ultimate Integrated System..."
git config --global user.email "bot@omni.com"
git config --global user.name "Omni Bot"

git add .
git commit -m "Feat: Integrate Structure Sync & Infinity Scale Pipeline"
git push
echo "✅ Deployment Complete."
""")
    if os.name != 'nt': os.chmod(script_path, 0o755)

# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    print("🤖 Processing Ultimate System Integration...")
    sync_structure()           # 1. Dependabot & 폴더 구조 동기화
    generate_infinity_workflow() # 2. 대량 데이터 파이프라인 생성
    generate_push_script()     # 3. 배포 스크립트
    
    print("\n✅ 통합 시스템 구축 완료.")
    print("👉 './push_ultimate_system.sh' 를 실행하여 GitHub에 반영하세요.")
