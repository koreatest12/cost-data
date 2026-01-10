# Cost Data - File Management System

Spring Boot 애플리케이션으로 파일 및 디렉토리 관리 기능과 권한 인증을 제공합니다.

## 기능

- 파일 생성 및 관리
- 디렉토리 생성 및 관리
- 파일 목록 조회
- 파일 읽기
- 파일/디렉토리 삭제 (관리자 권한 필요)
- Spring Security를 통한 권한 관리

## 기술 스택

- Java 17
- Spring Boot 3.2.1
- Spring Security
- Maven
- Lombok

## 빌드 및 실행

### 필수 요구사항
- JDK 17 이상
- Maven 3.6 이상

### 빌드
```bash
mvn clean install
```

### 실행
```bash
mvn spring-boot:run
```

애플리케이션은 기본적으로 `http://localhost:8080`에서 실행됩니다.

## 사용자 인증

애플리케이션은 두 가지 사용자 계정을 제공합니다:

### 일반 사용자
- Username: `user`
- Password: `password`
- 권한: 파일/디렉토리 생성, 조회, 읽기

### 관리자
- Username: `admin`
- Password: `admin`
- 권한: 모든 기능 + 삭제

## API 엔드포인트

### 1. 파일 생성
```
POST /api/files/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test.txt",
  "content": "파일 내용"
}
```

### 2. 디렉토리 생성
```
POST /api/files/directory/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test-directory"
}
```

### 3. 파일 목록 조회
```
GET /api/files/list?path=directory-path
Authorization: Basic Auth (user/admin)
```

### 4. 파일 정보 조회
```
GET /api/files/info?path=file-path
Authorization: Basic Auth (user/admin)
```

### 5. 파일 읽기
```
GET /api/files/read?path=file-path
Authorization: Basic Auth (user/admin)
```

### 6. 파일/디렉토리 삭제
```
DELETE /api/files/delete?path=file-or-directory-path
Authorization: Basic Auth (admin only)
```

## 사용 예시 (curl)

### 파일 생성
```bash
curl -u user:password -X POST http://localhost:8080/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"example.txt","content":"Hello World"}'
```

### 디렉토리 생성
```bash
curl -u user:password -X POST http://localhost:8080/api/files/directory/create \
  -H "Content-Type: application/json" \
  -d '{"path":"my-directory"}'
```

### 파일 목록 조회
```bash
curl -u user:password http://localhost:8080/api/files/list
```

### 파일 읽기
```bash
curl -u user:password http://localhost:8080/api/files/read?path=example.txt
```

### 파일 삭제 (관리자만 가능)
```bash
curl -u admin:admin -X DELETE http://localhost:8080/api/files/delete?path=example.txt
```

## 파일 저장 위치

파일은 기본적으로 `uploads/` 디렉토리에 저장됩니다. 이는 `application.properties`에서 변경할 수 있습니다:

```properties
file.storage.location=uploads
```

## 테스트

```bash
mvn test
```

## 라이센스

이 프로젝트는 LICENSE 파일에 명시된 라이센스를 따릅니다.
