package com.costdata.filemanagement.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SecurityNews {
    
    private String id;
    private String title;
    private String content;
    private String severity; // LOW, MEDIUM, HIGH, CRITICAL
    private String category; // VULNERABILITY, PATCH, THREAT, ALERT
    private String source;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
