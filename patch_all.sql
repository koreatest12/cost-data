-- 1. 테이블이 없으면 생성
CREATE TABLE IF NOT EXISTS infra_config_management (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(100) NOT NULL,
    target_path VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 기존 데이터 초기화 (중복 방지)
TRUNCATE TABLE infra_config_management RESTART IDENTITY;

-- 3. 모든 파일 데이터 대량 주입
INSERT INTO infra_config_management (file_name, target_path, category, content)
VALUES 
-- POM 설정
('pom.xml', './', 'MAVEN', 
'<project xmlns="http://maven.apache.org/POM/4.0.0">
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
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
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
</project>'),

-- DTO: DirectoryRequest
('DirectoryRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'JAVA_DTO', 
'package com.costdata.filemanagement.dto;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DirectoryRequest {
    @NotBlank(message = "Path is mandatory")
    private String path;
}'),

-- DTO: FileRequest
('FileRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'JAVA_DTO', 
'package com.costdata.filemanagement.dto;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class FileRequest {
    @NotBlank(message = "Path is mandatory")
    private String path;
}');
