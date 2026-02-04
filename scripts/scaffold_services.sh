#!/bin/bash

echo "🚀 Starting Massive Microservices Scaffolding..."

SERVICES=("omni-security-service" "omni-job-service" "omni-algo-service" "omni-cost-service")
PACKAGES=("security" "job" "algo" "cost")

mkdir -p services

for i in "${!SERVICES[@]}"; do
    SVC_NAME=${SERVICES[$i]}
    PKG_NAME=${PACKAGES[$i]}
    BASE_DIR="services/$SVC_NAME/src/main/java/com/costdata/$PKG_NAME"
    RSRC_DIR="services/$SVC_NAME/src/main/resources"
    
    echo "📦 Generating $SVC_NAME structure..."
    
    # 디렉토리 대량 생성
    mkdir -p $BASE_DIR/controller
    mkdir -p $BASE_DIR/service
    mkdir -p $BASE_DIR/repository
    mkdir -p $BASE_DIR/domain
    mkdir -p $BASE_DIR/dto
    mkdir -p $BASE_DIR/config
    mkdir -p $RSRC_DIR
    
    # 1. Application.java
    cat <<JAVA > $BASE_DIR/ServiceApplication.java
package com.costdata.$PKG_NAME;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class ServiceApplication {
    public static void main(String[] args) { SpringApplication.run(ServiceApplication.class, args); }
}
JAVA
    
    # 2. Controller
    cat <<JAVA > $BASE_DIR/controller/${PKG_NAME^}Controller.java
package com.costdata.$PKG_NAME.controller;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/$PKG_NAME")
public class ${PKG_NAME^}Controller {
    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "UP", "service", "$SVC_NAME"); }
}
JAVA

    # 3. Config (Security)
    cat <<JAVA > $BASE_DIR/config/SecurityConfig.java
package com.costdata.$PKG_NAME.config;
import org.springframework.context.annotation.Configuration;
@Configuration
public class SecurityConfig {
    // TODO: Claude will implement JWT filter here
}
JAVA

    # 4. resources/application.yml
    cat <<YML > $RSRC_DIR/application.yml
server:
  port: 808${i}
spring:
  application:
    name: $SVC_NAME
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
YML

done

echo "✅ Generated 4 Microservices with standard architecture."
