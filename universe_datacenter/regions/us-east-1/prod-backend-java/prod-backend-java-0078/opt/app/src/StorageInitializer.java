package com.costdata.filemanagement.config;

import com.costdata.filemanagement.service.FileManagementService;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class StorageInitializer implements CommandLineRunner {

    private final FileManagementService fileManagementService;

    @Override
    public void run(String... args) throws Exception {
        fileManagementService.init();
    }
}
