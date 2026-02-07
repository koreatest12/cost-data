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
public class FileResponse {
    
    private String name;
    private String path;
    private String type;
    private Long size;
    private LocalDateTime lastModified;
    private Boolean isDirectory;
}
