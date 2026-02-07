package com.costdata.filemanagement.controller;

import com.costdata.filemanagement.dto.ApiResponse;
import com.costdata.filemanagement.dto.DirectoryRequest;
import com.costdata.filemanagement.dto.FileRequest;
import com.costdata.filemanagement.dto.FileResponse;
import com.costdata.filemanagement.service.FileManagementService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileManagementController {

    private final FileManagementService fileManagementService;

    @PostMapping("/create")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> createFile(@Valid @RequestBody FileRequest request) {
        try {
            FileResponse response = fileManagementService.createFile(request.getPath(), request.getContent());
            return ResponseEntity.ok(ApiResponse.success("File created successfully", response));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Failed to create file: " + e.getMessage()));
        }
    }

    @PostMapping("/directory/create")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> createDirectory(@Valid @RequestBody DirectoryRequest request) {
        try {
            FileResponse response = fileManagementService.createDirectory(request.getPath());
            return ResponseEntity.ok(ApiResponse.success("Directory created successfully", response));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Failed to create directory: " + e.getMessage()));
        }
    }

    @GetMapping("/list")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> listFiles(@RequestParam(required = false) String path) {
        try {
            List<FileResponse> files = fileManagementService.listFiles(path);
            return ResponseEntity.ok(ApiResponse.success("Files retrieved successfully", files));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Failed to list files: " + e.getMessage()));
        }
    }

    @GetMapping("/info")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> getFileInfo(@RequestParam String path) {
        try {
            FileResponse response = fileManagementService.getFileInfo(path);
            return ResponseEntity.ok(ApiResponse.success("File info retrieved successfully", response));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error("File not found: " + e.getMessage()));
        }
    }

    @GetMapping("/read")
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public ResponseEntity<ApiResponse> readFile(@RequestParam String path) {
        try {
            String content = fileManagementService.readFile(path);
            return ResponseEntity.ok(ApiResponse.success("File read successfully", content));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Failed to read file: " + e.getMessage()));
        }
    }

    @DeleteMapping("/delete")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> deleteFile(@RequestParam String path) {
        try {
            fileManagementService.deleteFile(path);
            return ResponseEntity.ok(ApiResponse.success("File or directory deleted successfully"));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Failed to delete: " + e.getMessage()));
        }
    }
}
