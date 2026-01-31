-- 1. 기존 테이블 데이터 초기화
TRUNCATE TABLE infra_config_management RESTART IDENTITY;

-- 2. 모든 인프라 및 소스코드 데이터 일괄 삽입
INSERT INTO infra_config_management (file_name, target_path, category, content, is_active)
VALUES 
-- [Build 설정] pom.xml
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
</project>', true),

-- [DTO] DirectoryRequest.java
('DirectoryRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'JAVA_DTO', 
'package com.costdata.filemanagement.dto;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DirectoryRequest {
    @NotBlank(message = "Path is mandatory")
    private String path;
}', true),

-- [DTO] FileRequest.java (DirectoryRequest 내용 기반 치환 반영)
('FileRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'JAVA_DTO', 
'package com.costdata.filemanagement.dto;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class FileRequest {
    @NotBlank(message = "Path is mandatory")
    private String path;
}', true);
