import os

# ==============================================================================
# 🏗️ [설정] 프로젝트 절대 경로
# ==============================================================================
BASE_DIR = os.getcwd()
PROJECT_NAME = "services/omni-pokemon-web"
PROJECT_ROOT = os.path.join(BASE_DIR, PROJECT_NAME)

SRC_MAIN = os.path.join(PROJECT_ROOT, "src/main")
JAVA_PKG = os.path.join(SRC_MAIN, "java/com/omni/pokemon")
JAVA_MODEL = os.path.join(JAVA_PKG, "model")
JAVA_SERVICE = os.path.join(JAVA_PKG, "service")
JAVA_CONTROLLER = os.path.join(JAVA_PKG, "controller")
RESOURCES = os.path.join(SRC_MAIN, "resources")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 수정 완료: {os.path.basename(path)}")

# ==============================================================================
# 1. 🚨 [FIX] Java Model (컴파일 에러 원인 해결)
# ==============================================================================
def fix_java_model():
    # 문법 오류가 있던 코드를 정석적인 포맷으로 변경
    write_file(os.path.join(JAVA_MODEL, "Pokemon.java"), """
package com.omni.pokemon.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Pokemon {
    private int id;
    private String name;
    private List<String> types;
    private String image;
    private int total;
    private int hp;
    private int attack;
    private int speed;
}
""")

# ==============================================================================
# 2. 🛡️ [FIX] Service & Controller (안정성 강화)
# ==============================================================================
def fix_java_service():
    write_file(os.path.join(JAVA_SERVICE, "PokemonService.java"), """
package com.omni.pokemon.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.omni.pokemon.model.Pokemon;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class PokemonService {
    private List<Pokemon> db = new ArrayList<>();
    private final ObjectMapper mapper = new ObjectMapper();

    @PostConstruct
    public void init() {
        try {
            InputStream is = getClass().getResourceAsStream("/data.json");
            if (is != null) {
                db = mapper.readValue(is, new TypeReference<List<Pokemon>>(){});
                System.out.println("✅ Data Loaded: " + db.size() + " pokemons.");
            } else {
                System.err.println("⚠️ Warning: data.json not found in resources.");
            }
        } catch (Exception e) {
            System.err.println("❌ Error loading data: " + e.getMessage());
        }
    }

    public List<Pokemon> search(String keyword) {
        if (db.isEmpty()) return Collections.emptyList();
        if (keyword == null || keyword.isBlank()) return db;
        
        String k = keyword.toLowerCase();
        return db.stream()
                .filter(p -> p.getName().contains(k) || String.valueOf(p.getId()).equals(k))
                .collect(Collectors.toList());
    }
}
""")

    write_file(os.path.join(JAVA_CONTROLLER, "PokemonController.java"), """
package com.omni.pokemon.controller;

import com.omni.pokemon.model.Pokemon;
import com.omni.pokemon.service.PokemonService;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class PokemonController {
    
    private final PokemonService service;

    @GetMapping("/pokemon")
    public List<Pokemon> getPokemons(@RequestParam(required = false) String k) {
        return service.search(k);
    }

    @GetMapping("/health")
    public String health() {
        return "OK";
    }
}
""")

    write_file(os.path.join(JAVA_PKG, "OmniDexApp.java"), """
package com.omni.pokemon;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OmniDexApp {
    public static void main(String[] args) {
        SpringApplication.run(OmniDexApp.class, args);
    }
}
""")

# ==============================================================================
# 3. ⚙️ [FIX] POM.xml (의존성 충돌 방지)
# ==============================================================================
def fix_pom():
    write_file(os.path.join(PROJECT_ROOT, "pom.xml"), """
<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.omni</groupId>
    <artifactId>omni-pokemon-web</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/> 
    </parent>

    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
""")

# ==============================================================================
# 4. 🧪 [NEW] Test Code (빌드 검증용)
# ==============================================================================
def generate_tests():
    test_path = os.path.join(SRC_MAIN, "../test/java/com/omni/pokemon")
    write_file(os.path.join(test_path, "OmniDexAppTests.java"), """
package com.omni.pokemon;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class OmniDexAppTests {
    @Test
    void contextLoads() {
        // Context loading test to ensure build integrity
    }
}
""")

# ==============================================================================
# 5. 🚀 Git Push Script
# ==============================================================================
def generate_push_script():
    write_file(os.path.join(BASE_DIR, "push_fix.sh"), """
#!/bin/bash
echo "🔧 Fixing Compile Errors & Pushing..."

# 1. Config Check
git config --global user.email "bot@omni.com"
git config --global user.name "Omni Bot"

# 2. Add fixes
git add .
git commit -m "Fix: Resolve Maven compilation error in Pokemon.java"

# 3. Push
git push
echo "✅ Pushed to GitHub. Check Actions tab now."
""")
    if os.name != 'nt':
        os.chmod(os.path.join(BASE_DIR, "push_fix.sh"), 0o755)

# ==============================================================================
# Main Execution
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Repairing Project Files...")
    fix_java_model()
    fix_java_service()
    fix_pom()
    generate_tests()
    generate_push_script()
    print("\n🎉 모든 파일이 복구되었습니다.")
    print("👉 아래 명령어를 실행하여 GitHub에 수정사항을 반영하세요:\n")
    print("    ./push_fix.sh")
