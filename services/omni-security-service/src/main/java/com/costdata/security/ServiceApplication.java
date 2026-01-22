package com.costdata.security;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.annotation.PostConstruct;
import java.util.Map;
@SpringBootApplication @RestController
public class ServiceApplication {
    public static void main(String[] args) { SpringApplication.run(ServiceApplication.class, args); }
    @PostConstruct public void init() { System.out.println("🚀 security Service Started"); }
    @GetMapping("/") public Map<String, String> status() { return Map.of("service", "security", "status", "active"); }
}
