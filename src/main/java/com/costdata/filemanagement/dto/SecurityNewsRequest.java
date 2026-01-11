package com.costdata.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SecurityNewsRequest {
    
    @NotBlank(message = "Title is required")
    private String title;
    
    @NotBlank(message = "Content is required")
    private String content;
    
    private String severity; // LOW, MEDIUM, HIGH, CRITICAL
    
    private String category; // VULNERABILITY, PATCH, THREAT, ALERT
    
    private String source;
}
