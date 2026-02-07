package com.costdata.filemanagement.service;

import com.costdata.filemanagement.dto.FileResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

@Service
public class FileManagementService {

    @Value("${file.storage.location:uploads}")
    private String storageLocation;

    public void init() throws IOException {
        Files.createDirectories(Paths.get(storageLocation));
    }

    public FileResponse createFile(String filePath, String content) throws IOException {
        Path fullPath = Paths.get(storageLocation, filePath);
        
        // Create parent directories if they don't exist
        Files.createDirectories(fullPath.getParent());
        
        // Write content to file
        if (content != null) {
            Files.writeString(fullPath, content);
        } else {
            Files.createFile(fullPath);
        }
        
        return buildFileResponse(fullPath);
    }

    public FileResponse createDirectory(String dirPath) throws IOException {
        Path fullPath = Paths.get(storageLocation, dirPath);
        Files.createDirectories(fullPath);
        return buildFileResponse(fullPath);
    }

    public List<FileResponse> listFiles(String dirPath) throws IOException {
        Path fullPath = dirPath == null || dirPath.isEmpty() 
            ? Paths.get(storageLocation) 
            : Paths.get(storageLocation, dirPath);
        
        List<FileResponse> files = new ArrayList<>();
        
        if (!Files.exists(fullPath)) {
            throw new IOException("Directory does not exist: " + dirPath);
        }
        
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(fullPath)) {
            for (Path entry : stream) {
                files.add(buildFileResponse(entry));
            }
        }
        
        return files;
    }

    public FileResponse getFileInfo(String filePath) throws IOException {
        Path fullPath = Paths.get(storageLocation, filePath);
        
        if (!Files.exists(fullPath)) {
            throw new IOException("File or directory does not exist: " + filePath);
        }
        
        return buildFileResponse(fullPath);
    }

    public String readFile(String filePath) throws IOException {
        Path fullPath = Paths.get(storageLocation, filePath);
        
        if (!Files.exists(fullPath)) {
            throw new IOException("File does not exist: " + filePath);
        }
        
        if (Files.isDirectory(fullPath)) {
            throw new IOException("Path is a directory, not a file: " + filePath);
        }
        
        return Files.readString(fullPath);
    }

    public void deleteFile(String filePath) throws IOException {
        Path fullPath = Paths.get(storageLocation, filePath);
        
        if (!Files.exists(fullPath)) {
            throw new IOException("File or directory does not exist: " + filePath);
        }
        
        if (Files.isDirectory(fullPath)) {
            // Delete directory and all contents recursively
            Files.walkFileTree(fullPath, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    Files.delete(file);
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                    Files.delete(dir);
                    return FileVisitResult.CONTINUE;
                }
            });
        } else {
            Files.delete(fullPath);
        }
    }

    private FileResponse buildFileResponse(Path path) throws IOException {
        BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);
        
        return FileResponse.builder()
            .name(path.getFileName().toString())
            .path(Paths.get(storageLocation).relativize(path).toString())
            .type(Files.isDirectory(path) ? "directory" : getFileExtension(path.getFileName().toString()))
            .size(attrs.size())
            .lastModified(LocalDateTime.ofInstant(attrs.lastModifiedTime().toInstant(), ZoneId.systemDefault()))
            .isDirectory(Files.isDirectory(path))
            .build();
    }

    private String getFileExtension(String fileName) {
        int lastIndexOf = fileName.lastIndexOf(".");
        if (lastIndexOf == -1) {
            return "file";
        }
        return fileName.substring(lastIndexOf + 1);
    }
}
