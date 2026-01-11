package com.costdata.filemanagement.controller;

import com.costdata.filemanagement.dto.ApiResponse;
import com.costdata.filemanagement.dto.SecurityNewsRequest;
import com.costdata.filemanagement.dto.SecurityNewsResponse;
import com.costdata.filemanagement.service.SecurityNewsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/security-news")
@RequiredArgsConstructor
public class SecurityNewsController {
    
    private final SecurityNewsService securityNewsService;
    
    /**
     * Create a new security news item
     * Requires authentication
     */
    @PostMapping("/create")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> createNews(@Valid @RequestBody SecurityNewsRequest request) {
        try {
            SecurityNewsResponse response = securityNewsService.createNews(request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Security news created successfully", response));
        } catch (Exception e) {
            log.error("Error creating security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to create security news: " + e.getMessage()));
        }
    }
    
    /**
     * Generate automated security news
     * Requires authentication
     */
    @PostMapping("/generate")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> generateNews(@RequestParam(defaultValue = "ALERT") String type) {
        try {
            SecurityNewsResponse response = securityNewsService.generateNews(type);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Security news generated successfully", response));
        } catch (Exception e) {
            log.error("Error generating security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to generate security news: " + e.getMessage()));
        }
    }
    
    /**
     * Get all security news items
     * Requires authentication
     */
    @GetMapping("/list")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> getAllNews() {
        try {
            List<SecurityNewsResponse> newsList = securityNewsService.getAllNews();
            return ResponseEntity.ok(ApiResponse.success("Security news retrieved successfully", newsList));
        } catch (Exception e) {
            log.error("Error retrieving security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to retrieve security news: " + e.getMessage()));
        }
    }
    
    /**
     * Get security news by ID
     * Requires authentication
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> getNewsById(@PathVariable String id) {
        try {
            return securityNewsService.getNewsById(id)
                    .map(news -> ResponseEntity.ok(ApiResponse.success("Security news retrieved successfully", news)))
                    .orElse(ResponseEntity.status(HttpStatus.NOT_FOUND)
                            .body(ApiResponse.error("Security news not found with ID: " + id)));
        } catch (Exception e) {
            log.error("Error retrieving security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to retrieve security news: " + e.getMessage()));
        }
    }
    
    /**
     * Get security news by severity
     * Requires authentication
     */
    @GetMapping("/severity/{severity}")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> getNewsBySeverity(@PathVariable String severity) {
        try {
            List<SecurityNewsResponse> newsList = securityNewsService.getNewsBySeverity(severity);
            return ResponseEntity.ok(ApiResponse.success("Security news retrieved successfully", newsList));
        } catch (Exception e) {
            log.error("Error retrieving security news by severity: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to retrieve security news: " + e.getMessage()));
        }
    }
    
    /**
     * Get security news by category
     * Requires authentication
     */
    @GetMapping("/category/{category}")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> getNewsByCategory(@PathVariable String category) {
        try {
            List<SecurityNewsResponse> newsList = securityNewsService.getNewsByCategory(category);
            return ResponseEntity.ok(ApiResponse.success("Security news retrieved successfully", newsList));
        } catch (Exception e) {
            log.error("Error retrieving security news by category: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to retrieve security news: " + e.getMessage()));
        }
    }
    
    /**
     * Update security news
     * Requires authentication
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> updateNews(@PathVariable String id, @Valid @RequestBody SecurityNewsRequest request) {
        try {
            return securityNewsService.updateNews(id, request)
                    .map(news -> ResponseEntity.ok(ApiResponse.success("Security news updated successfully", news)))
                    .orElse(ResponseEntity.status(HttpStatus.NOT_FOUND)
                            .body(ApiResponse.error("Security news not found with ID: " + id)));
        } catch (Exception e) {
            log.error("Error updating security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to update security news: " + e.getMessage()));
        }
    }
    
    /**
     * Delete security news
     * Requires admin role
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> deleteNews(@PathVariable String id) {
        try {
            boolean deleted = securityNewsService.deleteNews(id);
            if (deleted) {
                return ResponseEntity.ok(ApiResponse.success("Security news deleted successfully"));
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(ApiResponse.error("Security news not found with ID: " + id));
            }
        } catch (Exception e) {
            log.error("Error deleting security news: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("Failed to delete security news: " + e.getMessage()));
        }
    }
}
