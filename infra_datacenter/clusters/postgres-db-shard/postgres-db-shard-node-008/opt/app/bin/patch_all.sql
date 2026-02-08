
    content TEXT NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN DEFAULT TRUE
    target_path VARCHAR(255) NOT NULL,
('AppConfig.java', 'src/main/java/com/costdata/filemanagement/config/', 'package com.costdata.filemanagement.config; ...'),
('DirectoryRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'package com.costdata.filemanagement.dto; ...'),
('FileRequest.java', 'src/main/java/com/costdata/filemanagement/dto/', 'package com.costdata.filemanagement.dto; ...'),
('GlobalExceptionHandler.java', 'src/main/java/com/costdata/filemanagement/exception/', 'package com.costdata.filemanagement.exception; ...');
('pom.xml', './', '<project>...</project>'), -- 빌드 설정
);
-- 대량 데이터 삽입 (기존 DTO 및 추가 파일들)
-- 추가로 필요한 파일들을 여기에 계속 나열 (대량 반영)
-- 테이블 초기화 및 생성
CREATE TABLE IF NOT EXISTS infra_config_management (
INSERT INTO infra_config_management (file_name, target_path, content)
TRUNCATE TABLE infra_config_management RESTART IDENTITY;
VALUES 
