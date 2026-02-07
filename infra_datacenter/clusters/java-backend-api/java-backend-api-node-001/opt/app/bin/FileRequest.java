package com.costdata.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FileRequest {
    
    @NotBlank(message = "File path is required")
    private String path;
    
    private String content;
}
