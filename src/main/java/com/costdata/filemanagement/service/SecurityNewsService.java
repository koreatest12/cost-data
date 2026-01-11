package com.costdata.filemanagement.service;

import com.costdata.filemanagement.dto.SecurityNewsRequest;
import com.costdata.filemanagement.dto.SecurityNewsResponse;
import com.costdata.filemanagement.model.SecurityNews;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Slf4j
@Service
public class SecurityNewsService {
    
    private final Map<String, SecurityNews> newsStore = new ConcurrentHashMap<>();
    
    /**
     * Create a new security news item
     */
    public SecurityNewsResponse createNews(SecurityNewsRequest request) {
        String id = UUID.randomUUID().toString();
        LocalDateTime now = LocalDateTime.now();
        
        SecurityNews news = SecurityNews.builder()
                .id(id)
                .title(request.getTitle())
                .content(request.getContent())
                .severity(request.getSeverity() != null ? request.getSeverity() : "MEDIUM")
                .category(request.getCategory() != null ? request.getCategory() : "ALERT")
                .source(request.getSource())
                .createdAt(now)
                .updatedAt(now)
                .build();
        
        newsStore.put(id, news);
        log.info("Created security news with ID: {}", id);
        
        return mapToResponse(news);
    }
    
    /**
     * Generate automated security news based on predefined templates
     */
    public SecurityNewsResponse generateNews(String type) {
        SecurityNewsRequest request = new SecurityNewsRequest();
        LocalDateTime now = LocalDateTime.now();
        
        switch (type.toUpperCase()) {
            case "VULNERABILITY":
                request.setTitle("새로운 보안 취약점 발견: CVE-" + now.getYear() + "-" + generateRandomNumber());
                request.setContent("새로운 보안 취약점이 발견되었습니다. 해당 취약점은 원격 코드 실행이 가능하며, 즉시 패치를 적용하시기 바랍니다.");
                request.setSeverity("HIGH");
                request.setCategory("VULNERABILITY");
                request.setSource("GitHub Copilot Security Scanner");
                break;
                
            case "PATCH":
                request.setTitle("보안 패치 업데이트 안내");
                request.setContent("최신 보안 패치가 릴리스되었습니다. 시스템 보안을 위해 최신 버전으로 업데이트하시기 바랍니다.");
                request.setSeverity("MEDIUM");
                request.setCategory("PATCH");
                request.setSource("GitHub Copilot Patch Monitor");
                break;
                
            case "THREAT":
                request.setTitle("새로운 보안 위협 탐지");
                request.setContent("새로운 악성코드 및 보안 위협이 탐지되었습니다. 방화벽 규칙을 업데이트하고 시스템을 점검하시기 바랍니다.");
                request.setSeverity("CRITICAL");
                request.setCategory("THREAT");
                request.setSource("GitHub Copilot Threat Intelligence");
                break;
                
            default:
                request.setTitle("보안 알림: 시스템 보안 점검 권고");
                request.setContent("정기적인 보안 점검을 수행하시기 바랍니다. 최신 보안 정책을 확인하고 시스템을 업데이트하세요.");
                request.setSeverity("LOW");
                request.setCategory("ALERT");
                request.setSource("GitHub Copilot Security Monitor");
        }
        
        return createNews(request);
    }
    
    /**
     * Get all security news items
     */
    public List<SecurityNewsResponse> getAllNews() {
        return newsStore.values().stream()
                .sorted(Comparator.comparing(SecurityNews::getCreatedAt).reversed())
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }
    
    /**
     * Get security news by ID
     */
    public Optional<SecurityNewsResponse> getNewsById(String id) {
        return Optional.ofNullable(newsStore.get(id))
                .map(this::mapToResponse);
    }
    
    /**
     * Get security news by severity
     */
    public List<SecurityNewsResponse> getNewsBySeverity(String severity) {
        return newsStore.values().stream()
                .filter(news -> news.getSeverity().equalsIgnoreCase(severity))
                .sorted(Comparator.comparing(SecurityNews::getCreatedAt).reversed())
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }
    
    /**
     * Get security news by category
     */
    public List<SecurityNewsResponse> getNewsByCategory(String category) {
        return newsStore.values().stream()
                .filter(news -> news.getCategory().equalsIgnoreCase(category))
                .sorted(Comparator.comparing(SecurityNews::getCreatedAt).reversed())
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }
    
    /**
     * Update security news
     */
    public Optional<SecurityNewsResponse> updateNews(String id, SecurityNewsRequest request) {
        SecurityNews news = newsStore.get(id);
        if (news == null) {
            return Optional.empty();
        }
        
        news.setTitle(request.getTitle());
        news.setContent(request.getContent());
        news.setSeverity(request.getSeverity() != null ? request.getSeverity() : news.getSeverity());
        news.setCategory(request.getCategory() != null ? request.getCategory() : news.getCategory());
        news.setSource(request.getSource() != null ? request.getSource() : news.getSource());
        news.setUpdatedAt(LocalDateTime.now());
        
        log.info("Updated security news with ID: {}", id);
        return Optional.of(mapToResponse(news));
    }
    
    /**
     * Delete security news by ID
     */
    public boolean deleteNews(String id) {
        SecurityNews removed = newsStore.remove(id);
        if (removed != null) {
            log.info("Deleted security news with ID: {}", id);
            return true;
        }
        return false;
    }
    
    /**
     * Map SecurityNews entity to SecurityNewsResponse DTO
     */
    private SecurityNewsResponse mapToResponse(SecurityNews news) {
        return SecurityNewsResponse.builder()
                .id(news.getId())
                .title(news.getTitle())
                .content(news.getContent())
                .severity(news.getSeverity())
                .category(news.getCategory())
                .source(news.getSource())
                .createdAt(news.getCreatedAt())
                .updatedAt(news.getUpdatedAt())
                .build();
    }
    
    /**
     * Generate random number for CVE IDs
     */
    private String generateRandomNumber() {
        return String.format("%05d", new Random().nextInt(100000));
    }
}
