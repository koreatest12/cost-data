package com.costdata.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SecurityNewsResponse {
    
    private String id;
    private String title;
    private String content;
    private String severity;
    private String category;
    private String source;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
