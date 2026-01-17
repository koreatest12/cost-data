# 디렉토리별 기능 구성 (Directory-Specific Feature Configuration)

이 문서는 Cost Data 프로젝트의 각 디렉토리가 어떤 기능을 담당하는지 설명합니다.

## 디렉토리 구조 및 기능

### `/` (루트 디렉토리)
**기능:** 프로젝트 메인 설정 및 실행 스크립트
- `pom.xml` - Maven 프로젝트 설정
- `requirements.txt` - Python 의존성
- `inventory.ini` - Ansible 배포 설정
- `README.md` - 프로젝트 설명서
- `DEPLOYMENT.md` - 배포 가이드
- `quick-start.sh` - 빠른 시작 스크립트

### `/src/main/java` 디렉토리
**기능:** Spring Boot Java 애플리케이션 소스 코드

#### `/src/main/java/com/costdata/filemanagement/`
**기능:** 파일 관리 애플리케이션 메인 패키지

- **`FileManagementApplication.java`**
  - 기능: Spring Boot 애플리케이션 진입점
  - 포트: 9999
  - 용도: 애플리케이션 시작 및 초기화

#### `/src/main/java/com/costdata/filemanagement/controller/`
**기능:** REST API 컨트롤러

- **`FileManagementController.java`**
  - 기능: 파일 및 디렉토리 관리 REST API
  - 엔드포인트:
    - POST `/api/files/create` - 파일 생성
    - POST `/api/files/directory/create` - 디렉토리 생성
    - GET `/api/files/list` - 파일 목록
    - GET `/api/files/read` - 파일 읽기
    - GET `/api/files/info` - 파일 정보
    - DELETE `/api/files/delete` - 파일 삭제

#### `/src/main/java/com/costdata/filemanagement/service/`
**기능:** 비즈니스 로직 처리

- **`FileManagementService.java`**
  - 기능: 파일 시스템 작업 처리
  - 용도: 파일 생성, 읽기, 삭제, 목록 조회

#### `/src/main/java/com/costdata/filemanagement/config/`
**기능:** 애플리케이션 설정

- **`SecurityConfig.java`**
  - 기능: Spring Security 설정
  - 사용자: user/password, admin/admin
  - 권한: USER, ADMIN

- **`StorageInitializer.java`**
  - 기능: 파일 저장소 초기화
  - 용도: uploads 디렉토리 생성

#### `/src/main/java/com/costdata/filemanagement/dto/`
**기능:** 데이터 전송 객체 (DTO)

- **`FileRequest.java`** - 파일 생성 요청
- **`DirectoryRequest.java`** - 디렉토리 생성 요청
- **`FileResponse.java`** - 파일 정보 응답
- **`ApiResponse.java`** - 일반 API 응답

### `/src/main/resources` 디렉토리
**기능:** 애플리케이션 리소스 및 설정

- **`application.properties`**
  - 기능: Spring Boot 설정
  - 포트: 9999
  - 파일 저장 위치: uploads

### `/src/test/java` 디렉토리
**기능:** 테스트 코드
- 단위 테스트
- 통합 테스트

### `/deploy` 디렉토리
**기능:** 배포 스크립트 및 설정

- **`deploy.sh`**
  - 기능: 자동 배포 스크립트
  - 용도: 서버 설치 및 구성

- **`cost-data.service`**
  - 기능: systemd 서비스 파일
  - 용도: 시스템 서비스로 실행

- **`playbook.yml`**
  - 기능: Ansible 배포 플레이북
  - 용도: 다중 서버 배포

- **`templates/`**
  - `cost-data.service.j2` - systemd 서비스 템플릿
  - `deployment-info.txt.j2` - 배포 정보 템플릿

### `/uploads` 디렉토리
**기능:** 사용자 업로드 파일 저장소
- 용도: API를 통해 업로드된 파일 저장
- 권한: 읽기/쓰기
- 관리: FileManagementService

### `/data` 디렉토리
**기능:** 애플리케이션 데이터 저장

- **`server_config.json`**
  - 기능: 서버 관리 시스템 구성
  - 용도: 서버 정보, 업그레이드 이력 저장

### `/DB` 디렉토리
**기능:** 데이터베이스 및 지식 베이스

- **`knowledge_base.md`**
  - 기능: 지식 베이스 문서
  - 용도: 시스템 정보 및 가이드

- **`neural_memory.json.gz`**
  - 기능: 신경망 메모리 데이터
  - 용도: 학습 데이터 저장

- **`total_news_history.md`**
  - 기능: 보안 뉴스 히스토리
  - 용도: 보안 뉴스 기록

### Python 스크립트
**위치:** 루트 디렉토리

#### `server_manager.py`
**기능:** 서버 관리 시스템
- 서버 추가/업그레이드
- 용량 체크 및 증설
- 디스크 설치 및 관리
- CLI 인터페이스

**사용 예시:**
```bash
python3 server_manager.py add --server-id web-1 --cpu 4 --memory 8
python3 server_manager.py upgrade --server-id web-1 --cpu 8 --memory 16
python3 server_manager.py check-capacity --server-id web-1
python3 server_manager.py install-disk --server-id web-1 --disk-size 500 --disk-type SSD
```

#### `demo.py`
**기능:** 시스템 데모 스크립트
- 기능 시연
- 예제 실행

#### `security_news.py`
**기능:** 보안 뉴스 시스템
- 보안 뉴스 수집
- DB 디렉토리에 저장

#### `test_server_manager.py`
**기능:** 서버 관리 시스템 테스트
- 단위 테스트
- 기능 검증

## 포트 9999 사용

모든 웹 서비스는 **포트 9999**에서 실행됩니다:
- Spring Boot 애플리케이션: `http://localhost:9999`
- REST API: `http://localhost:9999/api/*`
- Health Check: `http://localhost:9999/actuator/health`

## 배포 시 각 디렉토리 역할

배포 시 각 디렉토리는 다음과 같이 구성됩니다:

1. **소스 코드** (`/src`) → JAR 파일로 빌드 → `/opt/cost-data/cost-data.jar`
2. **Python 스크립트** → `/opt/cost-data/`로 복사
3. **업로드 디렉토리** → `/opt/cost-data/uploads` 생성
4. **데이터 디렉토리** → `/opt/cost-data/data` 생성
5. **DB 디렉토리** → `/opt/cost-data/DB`로 복사
6. **배포 스크립트** → 시스템 서비스 설치

## 통합 운영

모든 컴포넌트는 포트 9999에서 통합 운영됩니다:

1. **파일 관리 API** - 포트 9999에서 REST API 제공
2. **서버 관리** - Python CLI로 서버 구성 관리
3. **보안 뉴스** - 백그라운드 데이터 수집
4. **데모** - 시스템 기능 시연

자세한 내용은 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.
