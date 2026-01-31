import os

# 🏗️ 경로 정의 (사용자 환경에 맞춰 자동 감지)
BASE_DIR = os.getcwd()
# 서비스 디렉토리가 있을 경우와 없을 경우를 모두 대비
SERVICE_SUB_PATH = "services/omni-pokemon-web"
if os.path.exists(os.path.join(BASE_DIR, SERVICE_SUB_PATH)):
    TARGET_BASE = os.path.join(BASE_DIR, SERVICE_SUB_PATH)
else:
    TARGET_BASE = BASE_DIR

SVC_PATH = os.path.join(TARGET_BASE, "src/main/java/com/costdata/filemanagement")

def force_write(path, content):
    abs_path = os.path.join(TARGET_BASE, path) if not path.startswith("/") else path
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content.strip("\n"))
    print(f"🔥 [Applied] {path}")

def patch_infrastructure():
    # 1. pom.xml 보강 (Validation & Jakarta API 강제 주입)
    pom_content = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
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
</project>
"""
    force_write("pom.xml", pom_content)

    # 2. 컴파일 에러 발생하던 DTO 자동 수정
    dto_content = """
package com.costdata.filemanagement.dto;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DirectoryRequest {
    @NotBlank(message = "Path is mandatory")
    private String path;
}
"""
    force_write("src/main/java/com/costdata/filemanagement/dto/DirectoryRequest.java", dto_content)
    force_write("src/main/java/com/costdata/filemanagement/dto/FileRequest.java", dto_content.replace("DirectoryRequest", "FileRequest"))

if __name__ == "__main__":
    patch_infrastructure()
    print("✨ Infrastructure Patch Completed.")
