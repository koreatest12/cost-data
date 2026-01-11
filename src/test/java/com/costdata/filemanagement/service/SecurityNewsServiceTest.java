package com.costdata.filemanagement.service;

import com.costdata.filemanagement.dto.SecurityNewsRequest;
import com.costdata.filemanagement.dto.SecurityNewsResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class SecurityNewsServiceTest {
    
    private SecurityNewsService securityNewsService;
    
    @BeforeEach
    void setUp() {
        securityNewsService = new SecurityNewsService();
    }
    
    @Test
    void testCreateNews() {
        // Given
        SecurityNewsRequest request = new SecurityNewsRequest();
        request.setTitle("Test Security News");
        request.setContent("Test content for security news");
        request.setSeverity("HIGH");
        request.setCategory("VULNERABILITY");
        request.setSource("Test Source");
        
        // When
        SecurityNewsResponse response = securityNewsService.createNews(request);
        
        // Then
        assertNotNull(response);
        assertNotNull(response.getId());
        assertEquals("Test Security News", response.getTitle());
        assertEquals("Test content for security news", response.getContent());
        assertEquals("HIGH", response.getSeverity());
        assertEquals("VULNERABILITY", response.getCategory());
        assertEquals("Test Source", response.getSource());
        assertNotNull(response.getCreatedAt());
        assertNotNull(response.getUpdatedAt());
    }
    
    @Test
    void testGenerateNewsVulnerability() {
        // When
        SecurityNewsResponse response = securityNewsService.generateNews("VULNERABILITY");
        
        // Then
        assertNotNull(response);
        assertNotNull(response.getId());
        assertTrue(response.getTitle().contains("보안 취약점"));
        assertEquals("HIGH", response.getSeverity());
        assertEquals("VULNERABILITY", response.getCategory());
    }
    
    @Test
    void testGenerateNewsPatch() {
        // When
        SecurityNewsResponse response = securityNewsService.generateNews("PATCH");
        
        // Then
        assertNotNull(response);
        assertEquals("MEDIUM", response.getSeverity());
        assertEquals("PATCH", response.getCategory());
    }
    
    @Test
    void testGenerateNewsThreat() {
        // When
        SecurityNewsResponse response = securityNewsService.generateNews("THREAT");
        
        // Then
        assertNotNull(response);
        assertEquals("CRITICAL", response.getSeverity());
        assertEquals("THREAT", response.getCategory());
    }
    
    @Test
    void testGenerateNewsDefault() {
        // When
        SecurityNewsResponse response = securityNewsService.generateNews("UNKNOWN");
        
        // Then
        assertNotNull(response);
        assertEquals("LOW", response.getSeverity());
        assertEquals("ALERT", response.getCategory());
    }
    
    @Test
    void testGetAllNews() {
        // Given
        SecurityNewsRequest request1 = new SecurityNewsRequest();
        request1.setTitle("News 1");
        request1.setContent("Content 1");
        
        SecurityNewsRequest request2 = new SecurityNewsRequest();
        request2.setTitle("News 2");
        request2.setContent("Content 2");
        
        securityNewsService.createNews(request1);
        securityNewsService.createNews(request2);
        
        // When
        List<SecurityNewsResponse> allNews = securityNewsService.getAllNews();
        
        // Then
        assertEquals(2, allNews.size());
    }
    
    @Test
    void testGetNewsById() {
        // Given
        SecurityNewsRequest request = new SecurityNewsRequest();
        request.setTitle("Test News");
        request.setContent("Test Content");
        
        SecurityNewsResponse created = securityNewsService.createNews(request);
        
        // When
        Optional<SecurityNewsResponse> found = securityNewsService.getNewsById(created.getId());
        
        // Then
        assertTrue(found.isPresent());
        assertEquals(created.getId(), found.get().getId());
        assertEquals("Test News", found.get().getTitle());
    }
    
    @Test
    void testGetNewsByIdNotFound() {
        // When
        Optional<SecurityNewsResponse> found = securityNewsService.getNewsById("non-existent-id");
        
        // Then
        assertFalse(found.isPresent());
    }
    
    @Test
    void testGetNewsBySeverity() {
        // Given
        SecurityNewsRequest highSeverity = new SecurityNewsRequest();
        highSeverity.setTitle("High Severity News");
        highSeverity.setContent("Content");
        highSeverity.setSeverity("HIGH");
        
        SecurityNewsRequest lowSeverity = new SecurityNewsRequest();
        lowSeverity.setTitle("Low Severity News");
        lowSeverity.setContent("Content");
        lowSeverity.setSeverity("LOW");
        
        securityNewsService.createNews(highSeverity);
        securityNewsService.createNews(lowSeverity);
        
        // When
        List<SecurityNewsResponse> highNews = securityNewsService.getNewsBySeverity("HIGH");
        
        // Then
        assertEquals(1, highNews.size());
        assertEquals("HIGH", highNews.get(0).getSeverity());
    }
    
    @Test
    void testGetNewsByCategory() {
        // Given
        SecurityNewsRequest vulnNews = new SecurityNewsRequest();
        vulnNews.setTitle("Vulnerability News");
        vulnNews.setContent("Content");
        vulnNews.setCategory("VULNERABILITY");
        
        SecurityNewsRequest patchNews = new SecurityNewsRequest();
        patchNews.setTitle("Patch News");
        patchNews.setContent("Content");
        patchNews.setCategory("PATCH");
        
        securityNewsService.createNews(vulnNews);
        securityNewsService.createNews(patchNews);
        
        // When
        List<SecurityNewsResponse> vulnList = securityNewsService.getNewsByCategory("VULNERABILITY");
        
        // Then
        assertEquals(1, vulnList.size());
        assertEquals("VULNERABILITY", vulnList.get(0).getCategory());
    }
    
    @Test
    void testUpdateNews() {
        // Given
        SecurityNewsRequest createRequest = new SecurityNewsRequest();
        createRequest.setTitle("Original Title");
        createRequest.setContent("Original Content");
        
        SecurityNewsResponse created = securityNewsService.createNews(createRequest);
        
        SecurityNewsRequest updateRequest = new SecurityNewsRequest();
        updateRequest.setTitle("Updated Title");
        updateRequest.setContent("Updated Content");
        updateRequest.setSeverity("CRITICAL");
        
        // When
        Optional<SecurityNewsResponse> updated = securityNewsService.updateNews(created.getId(), updateRequest);
        
        // Then
        assertTrue(updated.isPresent());
        assertEquals("Updated Title", updated.get().getTitle());
        assertEquals("Updated Content", updated.get().getContent());
        assertEquals("CRITICAL", updated.get().getSeverity());
    }
    
    @Test
    void testUpdateNewsNotFound() {
        // Given
        SecurityNewsRequest updateRequest = new SecurityNewsRequest();
        updateRequest.setTitle("Updated Title");
        updateRequest.setContent("Updated Content");
        
        // When
        Optional<SecurityNewsResponse> updated = securityNewsService.updateNews("non-existent-id", updateRequest);
        
        // Then
        assertFalse(updated.isPresent());
    }
    
    @Test
    void testDeleteNews() {
        // Given
        SecurityNewsRequest request = new SecurityNewsRequest();
        request.setTitle("Test News");
        request.setContent("Test Content");
        
        SecurityNewsResponse created = securityNewsService.createNews(request);
        
        // When
        boolean deleted = securityNewsService.deleteNews(created.getId());
        
        // Then
        assertTrue(deleted);
        assertFalse(securityNewsService.getNewsById(created.getId()).isPresent());
    }
    
    @Test
    void testDeleteNewsNotFound() {
        // When
        boolean deleted = securityNewsService.deleteNews("non-existent-id");
        
        // Then
        assertFalse(deleted);
    }
}
