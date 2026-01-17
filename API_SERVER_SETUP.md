# API 서버 설치 가이드 (API Server Installation Guide)

## 개요 (Overview)

이 문서는 Cost Data File Management API 서버의 설치 및 실행 방법을 안내합니다.

This document provides instructions for installing and running the Cost Data File Management API server.

## 시스템 요구사항 (System Requirements)

- **Java**: JDK 17 이상 (JDK 17 or higher)
- **Maven**: 3.6 이상 (3.6 or higher)
- **운영체제 (OS)**: Windows, Linux, or macOS

## 설치 방법 (Installation Instructions)

### 1. Java 설치 확인 (Verify Java Installation)

```bash
java -version
```

JDK 17 이상이 설치되어 있어야 합니다.
(JDK 17 or higher must be installed)

### 2. Maven 설치 확인 (Verify Maven Installation)

```bash
mvn -version
```

### 3. API 서버 시작 (Start API Server)

#### Linux/MacOS:

```bash
./start-api-server.sh
```

#### Windows:

```batch
start-api-server.bat
```

또는 수동으로 시작 (Or start manually):

```bash
mvn spring-boot:run
```

## 서버 접속 정보 (Server Access Information)

- **URL**: http://localhost:8080
- **포트 (Port)**: 8080

### 기본 계정 (Default Credentials)

#### 일반 사용자 (Regular User):
- Username: `user`
- Password: `password`
- 권한 (Permissions): 파일/디렉토리 생성, 조회, 읽기 (Create, Read, List files/directories)

#### 관리자 (Administrator):
- Username: `admin`
- Password: `admin`
- 권한 (Permissions): 모든 기능 + 삭제 (All functions + Delete)

## API 엔드포인트 (API Endpoints)

### 1. 파일 생성 (Create File)
```bash
POST /api/files/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test.txt",
  "content": "파일 내용"
}
```

### 2. 디렉토리 생성 (Create Directory)
```bash
POST /api/files/directory/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test-directory"
}
```

### 3. 파일 목록 조회 (List Files)
```bash
GET /api/files/list?path=directory-path
Authorization: Basic Auth (user/admin)
```

### 4. 파일 정보 조회 (Get File Info)
```bash
GET /api/files/info?path=file-path
Authorization: Basic Auth (user/admin)
```

### 5. 파일 읽기 (Read File)
```bash
GET /api/files/read?path=file-path
Authorization: Basic Auth (user/admin)
```

### 6. 파일/디렉토리 삭제 (Delete File/Directory)
```bash
DELETE /api/files/delete?path=file-or-directory-path
Authorization: Basic Auth (admin only)
```

## 사용 예시 (Usage Examples)

### 파일 생성 (Create a File)
```bash
curl -u user:password -X POST http://localhost:8080/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"example.txt","content":"Hello World"}'
```

### 디렉토리 생성 (Create a Directory)
```bash
curl -u user:password -X POST http://localhost:8080/api/files/directory/create \
  -H "Content-Type: application/json" \
  -d '{"path":"my-directory"}'
```

### 파일 목록 조회 (List Files)
```bash
curl -u user:password http://localhost:8080/api/files/list
```

### 파일 읽기 (Read a File)
```bash
curl -u user:password http://localhost:8080/api/files/read?path=example.txt
```

### 파일 삭제 (Delete a File) - 관리자만 가능 (Admin only)
```bash
curl -u admin:admin -X DELETE http://localhost:8080/api/files/delete?path=example.txt
```

## 빌드 및 패키징 (Build and Package)

### JAR 파일 생성 (Create JAR file)
```bash
mvn clean package
```

생성된 JAR 파일 위치 (Generated JAR location):
```
target/file-management-1.0.0.jar
```

### JAR 파일로 실행 (Run with JAR)
```bash
java -jar target/file-management-1.0.0.jar
```

## 설정 변경 (Configuration Changes)

설정 파일 위치 (Configuration file location):
```
src/main/resources/application.properties
```

### 포트 변경 (Change Port)
```properties
server.port=8081
```

### 파일 저장 위치 변경 (Change File Storage Location)
```properties
file.storage.location=custom-uploads
```

## 서버 중지 (Stop Server)

서버를 중지하려면 터미널에서 `Ctrl+C`를 누르세요.

To stop the server, press `Ctrl+C` in the terminal.

## 문제 해결 (Troubleshooting)

### 포트가 이미 사용 중인 경우 (Port Already in Use)
```
Error: Port 8080 is already in use
```

해결 방법 (Solution):
1. `application.properties`에서 포트 번호 변경 (Change port number in application.properties)
2. 또는 다른 프로세스가 8080 포트를 사용 중이면 종료 (Or terminate process using port 8080)

### Java 버전 오류 (Java Version Error)
```
Error: Unsupported Java version
```

해결 방법 (Solution):
- JDK 17 이상을 설치하세요 (Install JDK 17 or higher)

## 추가 정보 (Additional Information)

- API 문서는 README.md 파일을 참조하세요 (See README.md for API documentation)
- 기술 스택 (Tech Stack): Spring Boot 3.2.1, Spring Security, Java 17
- 저장소 (Repository): https://github.com/koreatest12/cost-data

## 라이선스 (License)

이 프로젝트는 LICENSE 파일에 명시된 라이선스를 따릅니다.

This project follows the license specified in the LICENSE file.
