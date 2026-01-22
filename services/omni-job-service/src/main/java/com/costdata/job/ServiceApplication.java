package com.costdata.job;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.annotation.PostConstruct;
import java.util.Map;
import java.io.File;

@SpringBootApplication @RestController
public class ServiceApplication {
    public static void main(String[] args) { SpringApplication.run(ServiceApplication.class, args); }
    
    @PostConstruct public void init() { 
        System.out.println("🚀 job Service Starting...");
        File dataDir = new File("src/main/resources/data");
        if(dataDir.exists()) {
            System.out.println("📦 Data Loaded: " + dataDir.list().length + " files");
        }
    }
    
    @GetMapping("/") public Map<String, String> status() { return Map.of("service", "job", "status", "active", "data", "loaded"); }
}
