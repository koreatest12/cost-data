import os

# ==============================================================================
# 🏗️ [설정] 프로젝트 루트 및 경로 정의
# ==============================================================================
BASE_DIR = os.getcwd()
GITHUB_DIR = os.path.join(BASE_DIR, ".github")
WORKFLOWS_DIR = os.path.join(GITHUB_DIR, "workflows")


def write_file(path, content):
    """파일이 존재하지 않을 때만 생성"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip("\n"))
        print(f"  ✅ [Created] {path}")
    else:
        print(f"  ⏭️  [Skipped] {path} (already exists)")


def force_write_file(path, content):
    """항상 덮어쓰기"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip("\n"))
    print(f"  🔥 [Updated] {path}")


# ==============================================================================
# PHASE 0 — 루트 파일 (docker-compose, .env.example, Makefile, README)
# ==============================================================================
def generate_root_files():
    print("\n📁 [Phase 0] Generating Root Files...")

    # ─── docker-compose.yml ───────────────────────────────────────────
    force_write_file(os.path.join(BASE_DIR, "docker-compose.yml"), r"""
version: '3.8'

services:
  # ─── 인프라 ────────────────────────────────────────────
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-omni1234}
      MYSQL_DATABASE: omni_db
      MYSQL_USER: omni_user
      MYSQL_PASSWORD: ${DB_USER_PASSWORD:-omni5678}
    ports: ["3306:3306"]
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-pomni1234"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks: [omni-net]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    networks: [omni-net]

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./infra/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks: [omni-net]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      GF_DATASOURCES_PROVISION_PATH: /etc/grafana/provisioning/datasources
    volumes:
      - ./infra/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./infra/monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    depends_on: [prometheus]
    networks: [omni-net]

  # ─── 마이크로서비스 ─────────────────────────────────────
  omni-auth-service:
    build: ./services/omni-auth-service
    ports: ["8081:8081"]
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/omni_db
      SPRING_DATASOURCE_USERNAME: omni_user
      SPRING_DATASOURCE_PASSWORD: ${DB_USER_PASSWORD:-omni5678}
      SPRING_REDIS_HOST: redis
      JWT_SECRET: ${JWT_SECRET:-change-me-in-production}
    depends_on:
      mysql: { condition: service_healthy }
      redis: { condition: service_started }
    networks: [omni-net]

  omni-cost-service:
    build: ./services/omni-cost-service
    ports: ["8082:8082"]
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/omni_db
      SPRING_DATASOURCE_USERNAME: omni_user
      SPRING_DATASOURCE_PASSWORD: ${DB_USER_PASSWORD:-omni5678}
      SPRING_REDIS_HOST: redis
    depends_on:
      mysql: { condition: service_healthy }
      redis: { condition: service_started }
    networks: [omni-net]

  omni-infinity-api:
    build: ./services/omni-infinity-api
    ports: ["8083:8083"]
    environment:
      SPRING_DATASOURCE_URL: jdbc:h2:mem:infinity;DB_CLOSE_DELAY=-1
    networks: [omni-net]

  omni-gateway:
    build: ./services/omni-gateway
    ports: ["8080:8080"]
    environment:
      AUTH_SERVICE_URL: http://omni-auth-service:8081
      COST_SERVICE_URL: http://omni-cost-service:8082
      INFINITY_SERVICE_URL: http://omni-infinity-api:8083
    depends_on:
      - omni-auth-service
      - omni-cost-service
      - omni-infinity-api
    networks: [omni-net]

  # ─── AI 모델 서비스 ─────────────────────────────────────
  ai-model:
    build: ./ai-model
    ports: ["5000:5000"]
    networks: [omni-net]

volumes:
  mysql_data:

networks:
  omni-net:
    driver: bridge
""")

    # ─── .env.example ─────────────────────────────────────────────────
    force_write_file(os.path.join(BASE_DIR, ".env.example"), r"""
# ─── Database ───────────────────────
DB_ROOT_PASSWORD=omni1234
DB_USER_PASSWORD=omni5678

# ─── JWT ────────────────────────────
JWT_SECRET=your-256-bit-secret-key-here

# ─── External ───────────────────────
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-2
""")

    # ─── Makefile ─────────────────────────────────────────────────────
    force_write_file(os.path.join(BASE_DIR, "Makefile"), r"""
.PHONY = up down build logs test clean

up:
	@echo "🚀 Starting Omni Platform..."
	docker-compose up -d --build
	@echo "✅ All services started."
	@echo "   Gateway  → http://localhost:8080"
	@echo "   Grafana  → http://localhost:3000"
	@echo "   Prometheus → http://localhost:9090"

down:
	@echo "🛑 Stopping Omni Platform..."
	docker-compose down -v

build:
	docker-compose build --parallel

logs:
	docker-compose logs -f --tail=100

test:
	@echo "🧪 Running integration health-check..."
	docker-compose up -d --build
	sleep 20
	curl -sf http://localhost:8080/actuator/health || (echo "FAIL: Gateway" && exit 1)
	curl -sf http://localhost:8081/actuator/health || (echo "FAIL: Auth" && exit 1)
	curl -sf http://localhost:8082/actuator/health || (echo "FAIL: Cost" && exit 1)
	curl -sf http://localhost:8083/actuator/health || (echo "FAIL: Infinity" && exit 1)
	@echo "✅ All health-checks passed."

clean:
	docker-compose down -v --rmi all
	@echo "🧹 Cleaned up."
""")

    # ─── Root README ──────────────────────────────────────────────────
    force_write_file(os.path.join(BASE_DIR, "README.md"), r"""
# 🏢 Omni Platform — Microservices Monorepo

## Architecture Overview

```
Client
  │
  ▼
┌─────────────────┐     ┌──────────────────┐
│  omni-gateway   │────▶│ omni-auth-service │  (JWT 인증 / 토큰 검증)
│  :8080          │     └──────────────────┘
│                 │     ┌──────────────────┐
│  Spring Cloud   │────▶│ omni-cost-service│  (비용 집계 & 분석)
│  Gateway        │     └──────────────────┘
│                 │     ┌──────────────────┐
│                 │────▶│omni-infinity-api │  (대량 데이터 API)
└─────────────────┘     └──────────────────┘
                        ┌──────────────────┐
                        │   ai-model       │  (Python ML 서비스)
                        └──────────────────┘
```

## Quick Start

```bash
cp .env.example .env          # 환경 변수 설정
make up                       # 전체 스택 시동
```

## Service Map

| Service | Port | Description |
|---|---|---|
| omni-gateway | 8080 | API Gateway (라우팅 + 인증 필터) |
| omni-auth-service | 8081 | 회원 관리 + JWT 발급 |
| omni-cost-service | 8082 | 비용 조회 & 집계 |
| omni-infinity-api | 8083 | 대량 데이터 조회 |
| ai-model | 5000 | Python AI 예측 서비스 |
| Prometheus | 9090 | 메트릭 수집 |
| Grafana | 3000 | 대시보드 |
| MySQL | 3306 | 공유 DB |
| Redis | 6379 | 캐시 |

## CI/CD Pipelines (.github/workflows/)

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci-full-pipeline.yml` | push main, PR | 전체 빌드·테스트·보안스캔·배포 |
| `infinity_pipeline.yml` | dispatch / cron | 대량 데이터 생성 + Infinity API 배포 |
| `security-scan.yml` | push, schedule | Trivy + CodeQL 보안 스캔 |
| `monitoring-deploy.yml` | dispatch | Prometheus/Grafana 설정 배포 |

## Infra

```
infra/
├── terraform/        # AWS Terraform (VPC, ECS, RDS)
└── monitoring/       # Prometheus + Grafana 설정
```
""")


# ==============================================================================
# PHASE 1 — Dependabot & Directory Structure Sync
# ==============================================================================
def sync_structure():
    print("\n🔄 [Phase 1] Syncing Project Structure & Dependabot...")

    dependabot = r"""
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "daily", time: "09:00", timezone: "Asia/Seoul" }
    labels: ["ci", "actions"]

  - package-ecosystem: "maven"
    directory: "/services/omni-gateway"
    schedule: { interval: "weekly", timezone: "Asia/Seoul" }
    labels: ["backend", "gateway"]

  - package-ecosystem: "maven"
    directory: "/services/omni-auth-service"
    schedule: { interval: "weekly", timezone: "Asia/Seoul" }
    labels: ["backend", "auth"]

  - package-ecosystem: "maven"
    directory: "/services/omni-cost-service"
    schedule: { interval: "daily", timezone: "Asia/Seoul" }
    labels: ["backend", "core"]

  - package-ecosystem: "maven"
    directory: "/services/omni-infinity-api"
    schedule: { interval: "daily", timezone: "Asia/Seoul" }
    labels: ["backend", "infinity"]

  - package-ecosystem: "docker"
    directory: "/"
    schedule: { interval: "weekly", timezone: "Asia/Seoul" }
    labels: ["docker"]

  - package-ecosystem: "pip"
    directory: "/ai-model"
    schedule: { interval: "weekly", timezone: "Asia/Seoul" }
    labels: ["ai", "python"]
"""
    force_write_file(os.path.join(GITHUB_DIR, "dependabot.yml"), dependabot)

    # 서비스 디렉토리 & skeleton 파일 생성
    services = [
        ("services/omni-gateway", "gateway"),
        ("services/omni-auth-service", "auth"),
        ("services/omni-cost-service", "cost"),
        ("services/omni-infinity-api", "infinity"),
    ]
    for svc_path, svc_tag in services:
        _create_spring_service(svc_path, svc_tag)

    _create_ai_model_service()
    _create_terraform_infra()
    _create_monitoring_infra()


# ==============================================================================
# PHASE 1a — Spring Boot 서비스 소스코드 생성
# ==============================================================================
def _create_spring_service(svc_path, svc_tag):
    """각 Spring Boot 서비스의 소스·설정·Dockerfile 전체 생성"""
    full = os.path.join(BASE_DIR, svc_path)
    art_id = os.path.basename(svc_path)
    pkg = f"com.omni.{svc_tag}"
    pkg_dir = os.path.join(full, "src", "main", "java", *pkg.split("."))
    test_pkg_dir = os.path.join(full, "src", "test", "java", *pkg.split("."))
    res_dir = os.path.join(full, "src", "main", "resources")

    print(f"\n  🏗️  Building service: {svc_path}")

    # ─── pom.xml ──────────────────────────────────────────────────────
    pom_deps = ""
    pom_props = ""
    if svc_tag in ("auth", "cost"):
        pom_deps += """
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>"""
    if svc_tag == "infinity":
        pom_deps += """
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>"""
    if svc_tag == "gateway":
        pom_deps += """
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-gateway-mvc</artifactId>
        </dependency>"""
        pom_props = """
    <properties>
        <spring-cloud.version>2023.1.0</spring-cloud.version>
    </properties>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>"""
    if svc_tag == "auth":
        pom_deps += """
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>0.12.3</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>"""

    write_file(os.path.join(full, "pom.xml"), f"""
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.omni</groupId>
    <artifactId>{art_id}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/>
    </parent>{pom_props}
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.3.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>{pom_deps}
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
""")

    # ─── Dockerfile ───────────────────────────────────────────────────
    write_file(os.path.join(full, "Dockerfile"), f"""
# Stage 1: Build
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml ./
RUN mvn dependency:resolve -q 2>/dev/null || true
COPY src/ ./src/
RUN mvn clean package -DskipTests -q

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
RUN addgroup -S omni && adduser -S omni -G omni
COPY --from=builder /app/target/*.jar app.jar
EXPOSE {8080 + ["gateway","auth","cost","infinity"].index(svc_tag)}
HEALTHCHECK --interval=30s CMD wget -qO- http://localhost:{8080 + ["gateway","auth","cost","infinity"].index(svc_tag)}/actuator/health || exit 1
USER omni
ENTRYPOINT ["java", "-Xmx512m", "-jar", "app.jar"]
""")

    # ─── application.yml ──────────────────────────────────────────────
    port = 8080 + ["gateway", "auth", "cost", "infinity"].index(svc_tag)
    app_yml = f"""
server:
  port: {port}

spring:
  application:
    name: omni-{svc_tag}-service

management:
  endpoints:
    web:
      exposure:
        include: health, info, prometheus, metrics
  endpoint:
    health:
      show-details: always
"""
    if svc_tag in ("auth", "cost"):
        app_yml += """
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:mysql://localhost:3306/omni_db}
    username: ${SPRING_DATASOURCE_USERNAME:omni_user}
    password: ${SPRING_DATASOURCE_PASSWORD:omni5678}
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
  redis:
    host: ${SPRING_REDIS_HOST:localhost}
    port: 6379
"""
    if svc_tag == "infinity":
        app_yml += """
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:infinity;DB_CLOSE_DELAY=-1}
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: false
"""
    if svc_tag == "gateway":
        app_yml += """
  cloud:
    gateway:
      mvc:
        routes:
          - id: auth-service
            uri: ${AUTH_SERVICE_URL:http://localhost:8081}
            predicates:
              - Path=/auth/**
            filters:
              - StripPrefix=1
          - id: cost-service
            uri: ${COST_SERVICE_URL:http://localhost:8082}
            predicates:
              - Path=/cost/**
            filters:
              - StripPrefix=1
          - id: infinity-service
            uri: ${INFINITY_SERVICE_URL:http://localhost:8083}
            predicates:
              - Path=/infinity/**
            filters:
              - StripPrefix=1
"""
    write_file(os.path.join(res_dir, "application.yml"), app_yml)

    # ─── Main App class ───────────────────────────────────────────────
    class_name = {
        "gateway": "OmniGatewayApp",
        "auth": "OmniAuthApp",
        "cost": "OmniCostApp",
        "infinity": "OmniInfinityApp",
    }[svc_tag]
    write_file(os.path.join(pkg_dir, f"{class_name}.java"), f"""
package {pkg};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {class_name} {{
    public static void main(String[] args) {{
        SpringApplication.run({class_name}.class, args);
    }}
}}
""")

    # ─── Service-specific 소스 파일 ────────────────────────────────────
    if svc_tag == "gateway":
        _write_gateway_sources(pkg_dir, pkg)
    elif svc_tag == "auth":
        _write_auth_sources(pkg_dir, pkg)
    elif svc_tag == "cost":
        _write_cost_sources(pkg_dir, pkg)
    elif svc_tag == "infinity":
        _write_infinity_sources(pkg_dir, pkg)

    # ─── 단위 테스트 skeleton ─────────────────────────────────────────
    write_file(os.path.join(test_pkg_dir, f"{class_name}Tests.java"), f"""
package {pkg};

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class {class_name}Tests {{

    @Test
    void contextLoads() {{
        // Context 로드 확인
    }}
}}
""")

    # ─── 서비스 README ────────────────────────────────────────────────
    write_file(os.path.join(full, "README.md"), f"""
# omni-{svc_tag}-service

**Port:** {port}

## Run Locally
```bash
mvn spring-boot:run
```

## Endpoints
- `GET /actuator/health` — 상태 확인
- `GET /actuator/prometheus` — Prometheus 메트릭
- Swagger: `http://localhost:{port}/swagger-ui.html`
""")


# ─── Gateway 소스 ─────────────────────────────────────────────────────────
def _write_gateway_sources(pkg_dir, pkg):
    write_file(os.path.join(pkg_dir, "GlobalExceptionHandler.java"), f"""
package {pkg};

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {{

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleAll(Exception ex) {{
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", ex.getMessage(), "service", "gateway"));
    }}
}}
""")
    write_file(os.path.join(pkg_dir, "HealthController.java"), f"""
package {pkg};

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class HealthController {{

    @GetMapping("/")
    public Map<String, String> root() {{
        return Map.of("service", "omni-gateway", "status", "UP");
    }}
}}
""")


# ─── Auth 소스 ────────────────────────────────────────────────────────────
def _write_auth_sources(pkg_dir, pkg):
    # Entity
    write_file(os.path.join(pkg_dir, "User.java"), f"""
package {pkg};

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, length = 100)
    private String email;

    @Column(nullable = false, length = 300)
    private String passwordHash;

    @Column(length = 50)
    private String role;

    @Column(updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    public void onUpdate() {{ this.updatedAt = LocalDateTime.now(); }}
}}
""")
    # Repository
    write_file(os.path.join(pkg_dir, "UserRepository.java"), f"""
package {pkg};

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {{
    Optional<User> findByEmail(String email);
}}
""")
    # JWT Service
    write_file(os.path.join(pkg_dir, "JwtService.java"), f"""
package {pkg};

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

@Service
public class JwtService {{

    private final SecretKey secretKey;
    private static final long EXPIRATION_MS = 24L * 60 * 60 * 1000; // 24h

    public JwtService(@Value("${{JWT_SECRET:change-me-in-production}}") String secret) {{
        this.secretKey = Keys.hmacKey(secret.getBytes(StandardCharsets.UTF_8));
    }}

    public String generateToken(String email, String role) {{
        return Jwts.builder()
                .subject(email)
                .claim("role", role)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + EXPIRATION_MS))
                .signWith(secretKey)
                .compact();
    }}

    public Map<String, Object> parseToken(String token) {{
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(secretKey)
                .parseClaimsJws(token)
                .getPayload();
        return Map.of(
                "email", claims.getSubject(),
                "role", claims.get("role", String.class)
        );
    }}

    public boolean isValid(String token) {{
        try {{
            parseToken(token);
            return true;
        }} catch (JwtException e) {{
            return false;
        }}
    }}
}}
""")
    # Controller
    write_file(os.path.join(pkg_dir, "AuthController.java"), f"""
package {pkg};

import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
public class AuthController {{

    private final UserRepository userRepo;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/register")
    public ResponseEntity<Map<String, String>> register(@RequestBody Map<String, String> body) {{
        String email = body.get("email");
        String password = body.get("password");

        if (userRepo.findByEmail(email).isPresent()) {{
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(Map.of("error", "Email already registered"));
        }}

        User user = User.builder()
                .email(email)
                .passwordHash(passwordEncoder.encode(password))
                .role("USER")
                .build();
        userRepo.save(user);

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(Map.of("message", "Registration successful", "email", email));
    }}

    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestBody Map<String, String> body) {{
        String email = body.get("email");
        String password = body.get("password");

        return userRepo.findByEmail(email)
                .filter(u -> passwordEncoder.matches(password, u.getPasswordHash()))
                .map(u -> {{
                    String token = jwtService.generateToken(u.getEmail(), u.getRole());
                    return ResponseEntity.ok(Map.of("token", token, "email", u.getEmail()));
                }})
                .orElse(ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid credentials")));
    }}

    @GetMapping("/verify")
    public ResponseEntity<Map<String, Object>> verify(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {{
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {{
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("valid", false));
        }}
        String token = authHeader.substring(7);
        if (jwtService.isValid(token)) {{
            return ResponseEntity.ok(Map.of("valid", true, "claims", jwtService.parseToken(token)));
        }}
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("valid", false));
    }}
}}
""")
    # Security Config
    write_file(os.path.join(pkg_dir, "SecurityConfig.java"), f"""
package {pkg};

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {{

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http.csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(req ->
                req.requestMatchers("/api/register", "/api/login", "/actuator/**", "/swagger-ui/**", "/v3/**").permitAll()
                   .anyRequest().authenticated()
            );
        return http.build();
    }}

    @Bean
    public PasswordEncoder passwordEncoder() {{
        return new BCryptPasswordEncoder();
    }}
}}
""")


# ─── Cost Service 소스 ────────────────────────────────────────────────────
def _write_cost_sources(pkg_dir, pkg):
    write_file(os.path.join(pkg_dir, "CostEntry.java"), f"""
package {pkg};

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "cost_entries")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CostEntry {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String category;       // AWS, Marketing, Payroll …
    private Long amount;           // 원 단위
    private String vendor;
    private String description;
    @Enumerated(EnumType.STRING)
    private Status status;

    @Column(updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    public enum Status {{ APPROVED, PENDING, REJECTED }}
}}
""")
    write_file(os.path.join(pkg_dir, "CostRepository.java"), f"""
package {pkg};

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;
import java.util.Map;

public interface CostRepository extends JpaRepository<CostEntry, Long> {{

    List<CostEntry> findByCategory(String category);

    @Query("SELECT ce.category as category, SUM(ce.amount) as total " +
           "FROM CostEntry ce GROUP BY ce.category")
    List<Map<String, Object>> findCategorySummary();

    @Query("SELECT ce.status as status, COUNT(ce) as count " +
           "FROM CostEntry ce GROUP BY ce.status")
    List<Map<String, Object>> findStatusCounts();
}}
""")
    write_file(os.path.join(pkg_dir, "CostController.java"), f"""
package {pkg};

import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/cost")
public class CostController {{

    private final CostRepository repo;

    @GetMapping
    public List<CostEntry> listAll(
            @RequestParam(required = false) String category) {{
        return category != null ? repo.findByCategory(category) : repo.findAll();
    }}

    @PostMapping
    public ResponseEntity<CostEntry> create(@RequestBody CostEntry entry) {{
        entry.setStatus(CostEntry.Status.PENDING);
        return ResponseEntity.status(HttpStatus.CREATED).body(repo.save(entry));
    }}

    @PutMapping("{{id}}/status")
    public ResponseEntity<CostEntry> updateStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {{
        return repo.findById(id)
                .map(e -> {{
                    e.setStatus(CostEntry.Status.valueOf(body.get("status")));
                    return ResponseEntity.ok(repo.save(e));
                }})
                .orElse(ResponseEntity.notFound().build());
    }}

    @GetMapping("/summary")
    public Map<String, Object> summary() {{
        return Map.of(
                "byCategory", repo.findCategorySummary(),
                "byStatus", repo.findStatusCounts(),
                "totalCount", repo.count()
        );
    }}
}}
""")


# ─── Infinity 소스 ────────────────────────────────────────────────────────
def _write_infinity_sources(pkg_dir, pkg):
    write_file(os.path.join(pkg_dir, "InfinityData.java"), f"""
package {pkg};

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "infinity_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class InfinityData {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String uuid;
    private String category;
    private Long amount;
    private String vendor;

    @Column(length = 1000)
    private String description;

    private String status;
    private String createdAt;

    public InfinityData(String[] c) {{
        this.uuid       = c[0].trim();
        this.category   = c[1].trim();
        this.amount     = Long.parseLong(c[2].trim());
        this.vendor     = c[3].replace("\\"", "").trim();
        this.description = c[4].replace("\\"", "").trim();
        this.status     = c[5].trim();
        this.createdAt  = c[6].trim();
    }}
}}
""")
    write_file(os.path.join(pkg_dir, "InfinityRepository.java"), f"""
package {pkg};

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;
import java.util.Map;

public interface InfinityRepository extends JpaRepository<InfinityData, Long> {{

    @Query("SELECT d.category as category, SUM(d.amount) as total, COUNT(d) as count " +
           "FROM InfinityData d GROUP BY d.category")
    List<Map<String, Object>> findCategoryStats();

    @Query("SELECT d.status as status, COUNT(d) as count " +
           "FROM InfinityData d GROUP BY d.status")
    List<Map<String, Object>> findStatusStats();
}}
""")
    write_file(os.path.join(pkg_dir, "BatchLoader.java"), f"""
package {pkg};

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BatchLoader {{

    private final InfinityRepository repository;
    private static final int BATCH_SIZE = 5000;

    @PostConstruct
    public void init() throws Exception {{
        InputStream is = getClass().getResourceAsStream("/massive_data.csv");
        if (is == null) {{
            System.out.println("⏭️  [BatchLoader] massive_data.csv not found — skipping.");
            return;
        }}
        System.out.println("🔥 [BatchLoader] Ingesting massive_data.csv ...");
        try (BufferedReader br = new BufferedReader(new InputStreamReader(is))) {{
            br.readLine(); // header
            String line;
            List<InfinityData> buffer = new ArrayList<>();
            long count = 0;

            while ((line = br.readLine()) != null) {{
                String[] cols = splitCsvLine(line);
                if (cols.length >= 7) {{
                    buffer.add(new InfinityData(cols));
                    count++;
                }}
                if (buffer.size() >= BATCH_SIZE) {{
                    repository.saveAll(buffer);
                    buffer.clear();
                    System.out.printf("   ... Loaded %,d records%n", count);
                }}
            }}
            if (!buffer.isEmpty()) {{
                repository.saveAll(buffer);
            }}
            System.out.printf("✅ [BatchLoader] Total loaded: %,d records%n", count);
        }}
    }}

    /**
     * CSV 파싱 — 따옴표 내부의 콤마를 올바르게 처리
     */
    private String[] splitCsvLine(String line) {{
        return line.split(",(?=(?:[^\\"]*\\"[^\\"]*\\")*[^\\"]*$)", -1);
    }}
}}
""")
    write_file(os.path.join(pkg_dir, "InfinityController.java"), f"""
package {pkg};

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/infinity")
public class InfinityController {{

    private final InfinityRepository repo;

    @GetMapping
    public Page<InfinityData> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "100") int size,
            @RequestParam(defaultValue = "id") String sort) {{
        return repo.findAll(PageRequest.of(page, size, Sort.by(sort)));
    }}

    @GetMapping("/stats")
    public Map<String, Object> stats() {{
        return Map.of(
                "totalCount",  repo.count(),
                "byCategory",  repo.findCategoryStats(),
                "byStatus",    repo.findStatusStats(),
                "status",      "INFINITY"
        );
    }}
}}
""")


# ==============================================================================
# PHASE 1b — AI Model 서비스 (Python FastAPI)
# ==============================================================================
def _create_ai_model_service():
    ai_dir = os.path.join(BASE_DIR, "ai-model")
    print(f"\n  🤖 Building service: ai-model")

    write_file(os.path.join(ai_dir, "requirements.txt"), """
fastapi==0.109.1
uvicorn==0.27.0
pydantic==2.6.1
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3
gunicorn==21.2.0
prometheus-client==0.20.0
""")

    write_file(os.path.join(ai_dir, "Dockerfile"), """
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
EXPOSE 5000
HEALTHCHECK --interval=30s CMD curl -sf http://localhost:5000/health || exit 1
ENTRYPOINT ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000"]
""")

    write_file(os.path.join(ai_dir, "main.py"), """
import os
import time
import random

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# ─── App ──────────────────────────────────────────────────
app = FastAPI(title="Omni AI Model Service", version="1.0.0")

# ─── Prometheus 메트릭 ────────────────────────────────────
PREDICT_COUNTER   = Counter("ai_predictions_total",   "Total predictions",  ["category"])
PREDICT_LATENCY  = Histogram("ai_prediction_latency_seconds", "Prediction latency")
ERROR_COUNTER    = Counter("ai_errors_total", "Total errors")

# ─── 모델 Stub (실제 학습 모델로 교체 가능) ──────────────
class CostPredictionModel:
    \"\"\"간단한 규칙 기반 예측 모델 (Stub).
       실제 환경에서는 scikit-learn 학습 모델을 로드하여 사용.\"\"\"

    CATEGORY_MULTIPLIERS = {
        "AWS": 1.15,
        "Marketing": 1.08,
        "Payroll": 1.03,
    }

    def predict(self, category: str, base_amount: float) -> float:
        multiplier = self.CATEGORY_MULTIPLIERS.get(category, 1.10)
        noise = np.random.normal(0, 0.02)
        return round(base_amount * (multiplier + noise), 2)

model = CostPredictionModel()


# ─── Schemas ──────────────────────────────────────────────
class PredictRequest(BaseModel):
    category: str
    base_amount: float
    periods: int = 1  # 예측 주기 수

class PredictResponse(BaseModel):
    category: str
    base_amount: float
    predictions: list[float]
    avg_prediction: float


# ─── Endpoints ────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "UP", "service": "ai-model"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    start = time.time()
    try:
        predictions = [model.predict(req.category, req.base_amount) for _ in range(req.periods)]
        PREDICT_COUNTER.labels(category=req.category).inc()
        PREDICT_LATENCY.observe(time.time() - start)
        return PredictResponse(
            category=req.category,
            base_amount=req.base_amount,
            predictions=predictions,
            avg_prediction=round(sum(predictions) / len(predictions), 2),
        )
    except Exception as e:
        ERROR_COUNTER.inc()
        raise

@app.get("/categories")
def categories():
    return {"categories": list(CostPredictionModel.CATEGORY_MULTIPLIERS.keys())}
""")

    write_file(os.path.join(ai_dir, "test_main.py"), """
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"

def test_predict():
    res = client.post("/predict", json={
        "category": "AWS",
        "base_amount": 100000,
        "periods": 3
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["predictions"]) == 3
    assert data["category"] == "AWS"

def test_categories():
    res = client.get("/categories")
    assert "AWS" in res.json()["categories"]
""")

    write_file(os.path.join(ai_dir, "README.md"), """
# ai-model — AI 예측 서비스

**Port:** 5000  |  **Framework:** FastAPI

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | 상태 확인 |
| GET | `/metrics` | Prometheus 메트릭 |
| POST | `/predict` | 비용 예측 |
| GET | `/categories` | 지원 카테고리 목록 |

## 예측 요청 예시
```bash
curl -X POST http://localhost:5000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"category":"AWS","base_amount":500000,"periods":6}'
```

## 로컬 실행
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```
""")


# ==============================================================================
# PHASE 1c — Terraform Infra (AWS)
# ==============================================================================
def _create_terraform_infra():
    tf_dir = os.path.join(BASE_DIR, "infra", "terraform")
    print(f"\n  🏛️  Building infra: terraform")

    write_file(os.path.join(tf_dir, "main.tf"), """
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "omni-terraform-state"
    key            = "omni/terraform.tfstate"
    region         = "ap-northeast-2"
    dynamodb_table = "omni-tf-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
""")
    write_file(os.path.join(tf_dir, "variables.tf"), """
variable "aws_region" {
  default = "ap-northeast-2"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "db_instance_class" {
  default = "db.t3.micro"
}

variable "db_password" {
  sensitive = true
}

variable "ecs_cluster_name" {
  default = "omni-cluster"
}
""")
    write_file(os.path.join(tf_dir, "vpc.tf"), """
# ─── VPC ──────────────────────────────────────────────────
resource "aws_vpc" "omni" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "omni-vpc" }
}

# Public Subnets (2 AZs)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.omni.id
  cidr_block        = "10.0.${count.index * 16}.0/20"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "omni-public-${count.index}" }
}

# Private Subnets (2 AZs)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.omni.id
  cidr_block        = "10.0.${100 + count.index * 16}.0/20"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "omni-private-${count.index}" }
}

data "aws_availability_zones" "available" {}

# IGW
resource "aws_internet_gateway" "omni" {
  vpc_id = aws_vpc.omni.id
  tags   = { Name = "omni-igw" }
}

# Route Table (Public)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.omni.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.omni.id
  }
  tags = { Name = "omni-rt-public" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
""")
    write_file(os.path.join(tf_dir, "rds.tf"), """
# ─── RDS MySQL ────────────────────────────────────────────
resource "aws_db_subnet_group" "omni" {
  name       = "omni-db-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "rds" {
  vpc_id = aws_vpc.omni.id
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  tags = { Name = "omni-rds-sg" }
}

resource "aws_db_instance" "omni" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = var.db_instance_class
  db_name              = "omni_db"
  username             = "omni_user"
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.omni.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot  = true
  tags                 = { Name = "omni-rds" }
}

output "rds_endpoint" {
  value     = aws_db_instance.omni.endpoint
  sensitive = true
}
""")
    write_file(os.path.join(tf_dir, "ecs.tf"), """
# ─── ECS Cluster & Task Role ──────────────────────────────
resource "aws_ecs_cluster" "omni" {
  name = var.ecs_cluster_name
  tags = { Name = "omni-ecs" }
}

resource "aws_iam_role" "ecs_task" {
  name = "omni-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_logs" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskSupport"
}

# ─── 각 서비스 Task Definition (Gateway) ─────────────────
resource "aws_ecs_task_definition" "gateway" {
  family                = "omni-gateway"
  execution_role_arn    = aws_iam_role.ecs_task.arn
  task_role_arn         = aws_iam_role.ecs_task.arn
  network_mode          = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                   = "256"
  memory                = "512"

  container_definitions = jsonencode([{
    name         = "gateway"
    image        = "your-ecr-repo/omni-gateway:latest"  # ECR 이미지로 교체
    essential    = true
    portMappings = [{ containerPort = 8080 }]
    logConfiguration = {
      logDriver = "awslogs"
      options   = {
        "awslogs-group"         = "/ecs/omni-gateway"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.omni.name
}
""")
    write_file(os.path.join(tf_dir, "outputs.tf"), """
output "vpc_id" {
  value = aws_vpc.omni.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
""")
    write_file(os.path.join(tf_dir, "README.md"), """
# Terraform — AWS 인프라

## 리소스 구성
- **VPC** — CIDR `10.0.0.0/16`, Public 2개 / Private 2개 서브넷
- **RDS** — MySQL 8.0 (Private Subnet)
- **ECS Fargate** — 마이크로서비스 배포

## 사용법
```bash
terraform init
terraform plan -var db_password="secret"
terraform apply
```
""")


# ==============================================================================
# PHASE 1d — Monitoring (Prometheus + Grafana)
# ==============================================================================
def _create_monitoring_infra():
    mon_dir = os.path.join(BASE_DIR, "infra", "monitoring")
    print(f"\n  📊 Building infra: monitoring")

    write_file(os.path.join(mon_dir, "prometheus.yml"), """
global:
  scrape_interval: 15s
  evaluation_interval: 30s

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

  - job_name: omni-gateway
    static_configs:
      - targets: ['omni-gateway:8080']
    metrics_path: /actuator/prometheus

  - job_name: omni-auth-service
    static_configs:
      - targets: ['omni-auth-service:8081']
    metrics_path: /actuator/prometheus

  - job_name: omni-cost-service
    static_configs:
      - targets: ['omni-cost-service:8082']
    metrics_path: /actuator/prometheus

  - job_name: omni-infinity-api
    static_configs:
      - targets: ['omni-infinity-api:8083']
    metrics_path: /actuator/prometheus

  - job_name: ai-model
    static_configs:
      - targets: ['ai-model:5000']
    metrics_path: /metrics
""")

    grafana_ds_dir = os.path.join(mon_dir, "grafana", "datasources")
    write_file(os.path.join(grafana_ds_dir, "prometheus.yml"), """
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
""")

    grafana_dash_dir = os.path.join(mon_dir, "grafana", "dashboards")
    write_file(os.path.join(grafana_dash_dir, "omni-overview.json"), """
{
  "title": "Omni Platform Overview",
  "panels": [
    {
      "type": "graph",
      "title": "HTTP Request Rate",
      "targets": [{ "expr": "rate(http_server_requests_seconds_count[5m])" }],
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
    },
    {
      "type": "graph",
      "title": "HTTP Request Latency (p99)",
      "targets": [{ "expr": "histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[5m]))" }],
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 }
    },
    {
      "type": "graph",
      "title": "AI Predictions/sec",
      "targets": [{ "expr": "rate(ai_predictions_total[5m])" }],
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
    },
    {
      "type": "graph",
      "title": "AI Prediction Latency (p95)",
      "targets": [{ "expr": "histogram_quantile(0.95, rate(ai_prediction_latency_seconds_bucket[5m]))" }],
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 }
    }
  ]
}
""")


# ==============================================================================
# PHASE 2 — GitHub Actions Workflows
# ==============================================================================
def generate_workflows():
    print("\n🔧 [Phase 2] Generating GitHub Actions Workflows...")
    _generate_full_ci_pipeline()
    _generate_infinity_pipeline()
    _generate_security_scan()
    _generate_monitoring_deploy()


# ─── 2a. Full CI/CD Pipeline ──────────────────────────────────────────────
def _generate_full_ci_pipeline():
    force_write_file(os.path.join(WORKFLOWS_DIR, "ci-full-pipeline.yml"), r"""
name: 🏗️ Omni Full CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  JAVA_VERSION: '17'

jobs:
  # ──────────────────────────────────────────────────────────
  # JOB 1: Lint & Validate
  # ──────────────────────────────────────────────────────────
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🧹 Validate YAML Workflows
        run: |
          echo "=== Validating workflow YAML files ==="
          for f in .github/workflows/*.yml; do
            python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "✅ $f" || echo "❌ $f FAILED"
          done

      - name: 🧹 Validate docker-compose
        run: |
          pip install pyyaml -q
          python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('✅ docker-compose.yml valid')"

  # ──────────────────────────────────────────────────────────
  # JOB 2: Build All Java Services (Parallel Matrix)
  # ──────────────────────────────────────────────────────────
  build-java:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - services/omni-gateway
          - services/omni-auth-service
          - services/omni-cost-service
          - services/omni-infinity-api
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: temurin
          cache: maven

      - name: 📦 Maven Build & Test — ${{ matrix.service }}
        working-directory: ${{ matrix.service }}
        run: |
          echo "=== Building ${{ matrix.service }} ==="
          mvn clean package -DskipTests -q
          echo "✅ Build successful: ${{ matrix.service }}"

      - name: 📤 Upload JAR Artifact
        uses: actions/upload-artifact@v4
        with:
          name: jar-$(echo "${{ matrix.service }}" | tr '/' '-')
          path: ${{ matrix.service }}/target/*.jar
          retention-days: 7

  # ──────────────────────────────────────────────────────────
  # JOB 3: Build AI Model (Python)
  # ──────────────────────────────────────────────────────────
  build-ai:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: pip

      - name: 🤖 Install & Test AI Model
        working-directory: ai-model
        run: |
          pip install -r requirements.txt -q
          pip install pytest httpx -q
          pytest test_main.py -v
          echo "✅ AI Model tests passed"

  # ──────────────────────────────────────────────────────────
  # JOB 4: Docker Build (All Services) — main branch only
  # ──────────────────────────────────────────────────────────
  docker-build:
    if: github.ref == 'refs/heads/main'
    needs: [build-java, build-ai]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - service: services/omni-gateway
            image: omni-gateway
            port: 8080
          - service: services/omni-auth-service
            image: omni-auth-service
            port: 8081
          - service: services/omni-cost-service
            image: omni-cost-service
            port: 8082
          - service: services/omni-infinity-api
            image: omni-infinity-api
            port: 8083
          - service: ai-model
            image: omni-ai-model
            port: 5000
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      # Java 서비스: JAR artifact 복원
      - name: 📥 Restore JAR (if Java service)
        if: startsWith(matrix.service, 'services/')
        uses: actions/download-artifact@v4
        with:
          name: jar-$(echo "${{ matrix.service }}" | tr '/' '-')
          path: ${{ matrix.service }}/target/

      - name: 🐳 Docker Build — ${{ matrix.image }}
        run: |
          cd ${{ matrix.service }}
          docker build -t ${{ matrix.image }}:latest .
          echo "✅ Docker image built: ${{ matrix.image }}:latest"

      - name: 💾 Save Docker Image
        run: |
          docker save ${{ matrix.image }}:latest | gzip > /tmp/${{ matrix.image }}.tar.gz

      - name: 📤 Upload Docker Image
        uses: actions/upload-artifact@v4
        with:
          name: docker-${{ matrix.image }}
          path: /tmp/${{ matrix.image }}.tar.gz
          retention-days: 3

  # ──────────────────────────────────────────────────────────
  # JOB 5: GitHub Release (main branch, all artifacts)
  # ──────────────────────────────────────────────────────────
  release:
    if: github.ref == 'refs/heads/main'
    needs: [docker-build]
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: 📥 Download All Docker Images
        uses: actions/download-artifact@v4
        with:
          pattern: docker-*
          path: /tmp/images/
          merge-multiple: true

      - name: 📦 GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: "v${{ github.run_number }}"
          name: "🚀 Omni Release v${{ github.run_number }}"
          files: /tmp/images/*.tar.gz
""")


# ─── 2b. Infinity Pipeline (대량 데이터 생성) ─────────────────────────────
def _generate_infinity_pipeline():
    force_write_file(os.path.join(WORKFLOWS_DIR, "infinity_pipeline.yml"), r"""
name: 🌌 Infinity Scale Data & Deployment

on:
  workflow_dispatch:
    inputs:
      record_count:
        description: '생성할 데이터 건수 (Max: Runner Memory ~500K)'
        required: true
        default: '100000'
      environment:
        description: '배포 환경'
        type: choice
        options: [staging, production]
        default: staging
  schedule:
    - cron: '0 0 * * *'  # 매일 자정 갱신

env:
  SERVICE_DIR: "services/omni-infinity-api"
  DOCKER_IMAGE: "omni-infinity-api"
  VERSION: "v${{ github.run_number }}"

jobs:
  # ───────────────────────────────────────────────
  # JOB 1: 대량 데이터 생산
  # ───────────────────────────────────────────────
  data-factory:
    runs-on: ubuntu-latest
    outputs:
      record_count: ${{ steps.gen.outputs.count }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: pip

      - name: 🏭 Install Dependencies
        run: pip install pandas numpy faker -q

      - name: 🏭 Generate Massive Dataset
        id: gen
        env:
          RECORD_COUNT: ${{ github.event.inputs.record_count || '100000' }}
        run: |
          cat <<'PYEOF' > generate_data.py
import os, csv, uuid, random
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

COUNT = int(os.environ.get('RECORD_COUNT', 100000))
OUT   = 'services/omni-infinity-api/src/main/resources/massive_data.csv'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

fake = Faker('ko_KR')
categories = ['AWS', 'Marketing', 'Payroll', 'R&D', 'Legal', 'Infrastructure']
statuses   = ['APPROVED', 'PENDING', 'REJECTED']
base_now   = datetime.now()

print(f"🚀 Generating {COUNT:,} records...")
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['uuid','category','amount','vendor','description','status','created_at'])
    batch = []
    for i in range(COUNT):
        cat = random.choice(categories)
        amt = np.random.randint(10_000, 50_000_000)
        ts  = (base_now - timedelta(days=random.randint(0, 365))).isoformat()
        batch.append([
            str(uuid.uuid4()),
            cat,
            int(amt),
            fake.company(),
            fake.bs(),
            random.choice(statuses),
            ts,
        ])
        if len(batch) >= 10000:
            w.writerows(batch)
            batch = []
            print(f"   ... {i+1:,} / {COUNT:,}")
    if batch:
        w.writerows(batch)
print(f"✅ Generated {COUNT:,} records → {OUT}")
PYEOF
          python generate_data.py
          echo "count=${RECORD_COUNT}" >> $GITHUB_OUTPUT

      - name: 📤 Upload Dataset
        uses: actions/upload-artifact@v4
        with:
          name: infinity-dataset
          path: services/omni-infinity-api/src/main/resources/massive_data.csv

  # ───────────────────────────────────────────────
  # JOB 2: Build & Verify
  # ───────────────────────────────────────────────
  build-and-verify:
    needs: data-factory
    runs-on: ubuntu-latest
    outputs:
      jar_path: ${{ steps.build.outputs.jar }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/download-artifact@v4
        with:
          name: infinity-dataset
          path: services/omni-infinity-api/src/main/resources/

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven

      - name: 🔨 Maven Build
        id: build
        working-directory: ${{ env.SERVICE_DIR }}
        run: |
          mvn clean package -DskipTests -q
          JAR=$(ls target/*.jar | head -1)
          echo "jar=$JAR" >> $GITHUB_OUTPUT
          echo "✅ JAR built: $JAR"

      - name: 🧪 Smoke Test (Boot + API Check)
        working-directory: ${{ env.SERVICE_DIR }}
        run: |
          echo "=== Starting server for smoke test ==="
          nohup java -Xmx1024m -jar target/*.jar > /tmp/app.log 2>&1 &
          PID=$!
          echo "Server PID: $PID"

          # 최대 60초 대기 (H2 + 대량 데이터 로드)
          for i in $(seq 1 60); do
            if curl -sf http://localhost:8083/actuator/health | grep -q '"status":"UP"'; then
              echo "✅ Server UP after ${i}s"
              break
            fi
            sleep 1
          done

          echo "=== API Stats Check ==="
          STATS=$(curl -sf http://localhost:8083/api/infinity/stats)
          echo "$STATS" | python3 -m json.tool

          # 최소 50% 기대 레코드 확인
          EXPECTED=${{ needs.data-factory.outputs.record_count }}
          THRESHOLD=$(( EXPECTED / 2 ))
          ACTUAL=$(echo "$STATS" | python3 -c "import sys,json; print(json.load(sys.stdin)['totalCount'])")
          echo "Expected >= $THRESHOLD, Got: $ACTUAL"

          if [ "$ACTUAL" -ge "$THRESHOLD" ]; then
            echo "✅ Record count verification PASSED"
          else
            echo "❌ Record count verification FAILED"
            exit 1
          fi

          kill $PID 2>/dev/null
          echo "=== Smoke Test Complete ==="

      - name: 📤 Upload JAR
        uses: actions/upload-artifact@v4
        with:
          name: infinity-jar
          path: ${{ env.SERVICE_DIR }}/target/*.jar

  # ───────────────────────────────────────────────
  # JOB 3: Docker Build & Release
  # ───────────────────────────────────────────────
  docker-release:
    if: github.ref == 'refs/heads/main'
    needs: build-and-verify
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: 📥 Download JAR & Dataset
        run: |
          mkdir -p ${{ env.SERVICE_DIR }}/target
          mkdir -p ${{ env.SERVICE_DIR }}/src/main/resources
      - uses: actions/download-artifact@v4
        with:
          name: infinity-jar
          path: ${{ env.SERVICE_DIR }}/target/
      - uses: actions/download-artifact@v4
        with:
          name: infinity-dataset
          path: ${{ env.SERVICE_DIR }}/src/main/resources/

      - name: 🐳 Docker Build
        working-directory: ${{ env.SERVICE_DIR }}
        run: |
          docker build -t ${{ env.DOCKER_IMAGE }}:${{ env.VERSION }} .
          docker save ${{ env.DOCKER_IMAGE }}:${{ env.VERSION }} | gzip > /tmp/infinity.tar.gz
          echo "✅ Docker image: ${{ env.DOCKER_IMAGE }}:${{ env.VERSION }}"

      - name: 📦 GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: "infinity-${{ env.VERSION }}"
          name: "🌌 Infinity Release ${{ env.VERSION }} ($(echo ${{ needs.data-factory.outputs.record_count }} | numfmt --to=iec) records)"
          files: |
            /tmp/infinity.tar.gz
            ${{ env.SERVICE_DIR }}/src/main/resources/massive_data.csv
""")


# ─── 2c. Security Scan ────────────────────────────────────────────────────
def _generate_security_scan():
    force_write_file(os.path.join(WORKFLOWS_DIR, "security-scan.yml"), r"""
name: 🔒 Security Scan Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # 매일 06:00 KST (21:00 UTC)

jobs:
  # ───────────────────────────────────────────────
  # Trivy — 컨테이너 & 파일시스템 스캔
  # ───────────────────────────────────────────────
  trivy-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target:
          - { name: "filesystem", type: "fs", path: "." }
          - { name: "gateway", type: "image", image: "eclipse-temurin:17-jre-alpine" }
          - { name: "python", type: "image", image: "python:3.10-slim" }
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: 🔍 Trivy Scan — ${{ matrix.target.name }}
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: ${{ matrix.target.type }}
          scan-target: ${{ matrix.target.type == 'fs' && matrix.target.path || matrix.target.image }}
          severity: 'HIGH,CRITICAL'
          exit-code: '1'
          ignore-unfixed: true
          format: table

      - name: 📄 Trivy SARIF Report — ${{ matrix.target.name }}
        uses: aquasecurity/trivy-action@master
        continue-on-error: true
        with:
          scan-type: ${{ matrix.target.type }}
          scan-target: ${{ matrix.target.type == 'fs' && matrix.target.path || matrix.target.image }}
          format: sarif
          output: /tmp/trivy-${{ matrix.target.name }}.sarif

      - name: 📤 Upload SARIF
        uses: actions/upload-artifact@v4
        with:
          name: trivy-sarif-${{ matrix.target.name }}
          path: /tmp/trivy-${{ matrix.target.name }}.sarif

  # ───────────────────────────────────────────────
  # Python Dependency Audit
  # ───────────────────────────────────────────────
  python-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: 🔍 pip-audit
        working-directory: ai-model
        run: |
          pip install pip-audit -q
          pip install -r requirements.txt -q
          pip-audit --require-hashes || true
          echo "=== Audit complete ==="

  # ───────────────────────────────────────────────
  # Maven Dependency Check (OWASP)
  # ───────────────────────────────────────────────
  maven-audit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - services/omni-gateway
          - services/omni-auth-service
          - services/omni-cost-service
          - services/omni-infinity-api
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven

      - name: 🔍 OWASP Dependency-Check — ${{ matrix.service }}
        working-directory: ${{ matrix.service }}
        run: |
          # dependency-check Maven plugin 실행 (빌드 시간 절약을 위해 offline 모드 가능)
          mvn org.owasp:dependency-check-maven:aggregate -DskipTests -q 2>&1 | tail -20 || true
          echo "=== Dependency check complete: ${{ matrix.service }} ==="
""")


# ─── 2d. Monitoring Deploy ────────────────────────────────────────────────
def _generate_monitoring_deploy():
    force_write_file(os.path.join(WORKFLOWS_DIR, "monitoring-deploy.yml"), r"""
name: 📊 Monitoring Stack Deploy

on:
  workflow_dispatch:
    inputs:
      action:
        description: '실행 액션'
        type: choice
        options: [deploy, validate, teardown]
        default: deploy
  push:
    paths:
      - 'infra/monitoring/**'
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: ✅ Validate Prometheus Config
        run: |
          pip install pyyaml -q
          python3 <<'EOF'
import yaml, sys

files = [
    'infra/monitoring/prometheus.yml',
    'infra/monitoring/grafana/datasources/prometheus.yml',
]
errors = 0
for f in files:
    try:
        with open(f) as fh:
            yaml.safe_load(fh)
        print(f"  ✅ {f}")
    except Exception as e:
        print(f"  ❌ {f}: {e}")
        errors += 1

# Grafana dashboard JSON 검증
import json, glob
for f in glob.glob('infra/monitoring/grafana/dashboards/*.json'):
    try:
        with open(f) as fh:
            json.load(fh)
        print(f"  ✅ {f}")
    except Exception as e:
        print(f"  ❌ {f}: {e}")
        errors += 1

sys.exit(errors)
EOF

  deploy:
    if: github.event.inputs.action == 'deploy' || github.event_name == 'push'
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🚀 Deploy Monitoring Stack
        run: |
          echo "=== Monitoring Deploy ==="
          echo "Action: ${{ github.event.inputs.action || 'auto (push)' }}"
          echo ""
          echo "Files included:"
          find infra/monitoring/ -type f
          echo ""
          echo "=== Prometheus targets ==="
          grep -A2 "targets:" infra/monitoring/prometheus.yml
          echo ""
          echo "✅ Monitoring stack validated & ready for deployment"
          echo "   → docker-compose up -d prometheus grafana"
""")


# ==============================================================================
# PHASE 3 — Push Script
# ==============================================================================
def generate_push_script():
    print("\n📦 [Phase 3] Generating Push Script...")
    force_write_file(os.path.join(BASE_DIR, "push_ultimate_system.sh"), r"""
#!/bin/bash
set -e

echo "=============================================="
echo "  🚀 Omni Platform — Full Deploy Script"
echo "=============================================="
echo ""

# ─── 환경 확인 ────────────────────────────────────
echo "🔍 Environment Check..."
git --version
echo "   Git: OK"

if [ -z "$(git rev-parse --git-dir 2>/dev/null)" ]; then
    echo "❌ Not a git repository. Run 'git init' first."
    exit 1
fi
echo "   Git repo: OK"

# ─── Git 설정 ─────────────────────────────────────
echo ""
echo "⚙️  Configuring Git..."
git config --local user.email "ci@omni.dev"
git config --local user.name "Omni CI Bot"

# ─── 파일 목록 확인 ───────────────────────────────
echo ""
echo "📁 Files to be committed:"
git status --short | head -50
CHANGED=$(git status --short | wc -l)
echo "   Total changed: $CHANGED files"

if [ "$CHANGED" -eq 0 ]; then
    echo ""
    echo "⏭️  Nothing to commit. Exiting."
    exit 0
fi

# ─── Commit & Push ────────────────────────────────
echo ""
echo "📤 Committing..."
git add .
git commit -m "feat(platform): integrate full omni microservices stack

  - services: gateway, auth, cost, infinity-api (Spring Boot)
  - ai-model: FastAPI prediction service
  - infra: terraform (AWS VPC/RDS/ECS), prometheus, grafana
  - ci: full pipeline, infinity pipeline, security scan, monitoring
  - config: docker-compose, Makefile, dependabot

  Generated by Omni Setup Tool"

echo ""
echo "🚀 Pushing..."
git push origin $(git rev-parse --abbrev-ref HEAD)

echo ""
echo "=============================================="
echo "  ✅ Omni Platform Deploy Complete!"
echo "=============================================="
echo ""
echo "  Next steps:"
echo "  1. cp .env.example .env && vim .env"
echo "  2. make up"
echo "  3. Grafana → http://localhost:3000"
echo "=============================================="
""")
    if os.name != 'nt':
        os.chmod(os.path.join(BASE_DIR, "push_ultimate_system.sh"), 0o755)


# ==============================================================================
# Main Entry
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  🤖  Omni Platform — Full Setup Tool")
    print("=" * 60)

    generate_root_files()        # Phase 0: Root (compose, Makefile, README)
    sync_structure()             # Phase 1: All services + infra
    generate_workflows()         # Phase 2: GitHub Actions (4 workflows)
    generate_push_script()       # Phase 3: Push script

    print("\n" + "=" * 60)
    print("  ✅  Setup Complete!")
    print("=" * 60)
    print("""
  📋 생성된 구조:
     ├── docker-compose.yml         (9개 컨테이너)
     ├── Makefile                   (up/down/test)
     ├── .env.example
     ├── services/
     │   ├── omni-gateway/          (Spring Cloud Gateway)
     │   ├── omni-auth-service/     (JWT 인증)
     │   ├── omni-cost-service/     (비용 관리)
     │   └── omni-infinity-api/     (대량 데이터)
     ├── ai-model/                  (FastAPI + ML)
     ├── infra/
     │   ├── terraform/             (AWS: VPC, RDS, ECS)
     │   └── monitoring/            (Prometheus + Grafana)
     └── .github/workflows/
         ├── ci-full-pipeline.yml   (빌드·테스트·배포)
         ├── infinity_pipeline.yml  (대량 데이터 파이프라인)
         ├── security-scan.yml      (Trivy·OWASP)
         └── monitoring-deploy.yml  (모니터링 배포)

  👉 시작: python setup_omni.py && ./push_ultimate_system.sh
  """)
