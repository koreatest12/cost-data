package com.costdata.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DirectoryRequest {
    
    @NotBlank(message = "Directory path is required")
    private String path;
}
