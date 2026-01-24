package com.costdata.security;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;
@SpringBootApplication @RestController
public class ServiceApplication {
    public static void main(String[] args) { SpringApplication.run(ServiceApplication.class, args); }
    @GetMapping("/") public Map<String, String> s() { return Map.of("status", "online"); }
}
