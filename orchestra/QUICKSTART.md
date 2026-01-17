# 🎭 Ansible AWX Orchestra Server - 빠른 시작 가이드

이 가이드는 Ansible AWX Orchestra 서버를 최대한 빠르게 설치하고 사용하는 방법을 안내합니다.

## ⚡ 5분 안에 시작하기

### 1단계: 설치 (2분)

```bash
# 저장소 클론 (이미 클론했다면 건너뛰기)
git clone https://github.com/koreatest12/cost-data.git
cd cost-data

# Orchestra 디렉토리로 이동
cd orchestra

# 설치 스크립트 실행
chmod +x install-awx.sh
./install-awx.sh
```

설치 스크립트가 자동으로:
- ✅ Docker 설치 확인 (없으면 설치)
- ✅ Docker Compose 설치 확인 (없으면 설치)
- ✅ AWX 컨테이너 시작
- ✅ 서비스 상태 확인

### 2단계: 웹 UI 접속 (1분)

설치가 완료되면 (약 2-3분 소요):

1. 웹 브라우저 열기
2. 다음 URL 접속: **http://localhost:8080**
3. 로그인:
   - **사용자명**: `admin`
   - **비밀번호**: `admin`

### 3단계: 첫 번째 인벤토리 생성 (2분)

1. 좌측 메뉴에서 **Inventories** 클릭
2. **Add** 버튼 클릭 → **Add inventory** 선택
3. 인벤토리 이름 입력: `Production Servers`
4. **Save** 클릭

**호스트 추가:**

1. 생성한 인벤토리 클릭
2. **Hosts** 탭 선택
3. **Add** 클릭
4. 호스트 정보 입력:
   ```
   Name: 192.168.1.101
   ```
5. **Variables** 섹션에 다음 입력:
   ```yaml
   ansible_user: ubuntu
   ansible_connection: ssh
   ```
6. **Save** 클릭

## 🎯 기본 사용 예제

### 예제 1: 시스템 상태 확인

이 저장소에 포함된 헬스 체크 플레이북을 사용하여 서버 상태를 확인할 수 있습니다.

#### 프로젝트 생성:

1. **Projects** → **Add** 클릭
2. 정보 입력:
   - **Name**: `Cost Data Playbooks`
   - **Organization**: Default
   - **SCM Type**: Git
   - **SCM URL**: `https://github.com/koreatest12/cost-data.git`
   - **SCM Branch/Tag/Commit**: `main`
3. **Save** 클릭
4. 프로젝트 동기화 완료 대기 (🔄 아이콘이 ✅로 변경)

#### Job Template 생성:

1. **Templates** → **Add** → **Add job template** 클릭
2. 정보 입력:
   - **Name**: `System Health Check`
   - **Job Type**: Run
   - **Inventory**: `Production Servers` (앞에서 생성한 인벤토리)
   - **Project**: `Cost Data Playbooks`
   - **Playbook**: `orchestra/playbooks/health-check.yml`
3. **Save** 클릭

#### Job 실행:

1. 생성한 `System Health Check` 템플릿 클릭
2. 우측 상단 **Launch** 버튼 클릭
3. 실행 로그를 실시간으로 확인

### 예제 2: Nginx 웹 서버 배포

1. Job Template 생성 (위와 동일한 방법):
   - **Name**: `Deploy Web Servers`
   - **Playbook**: `orchestra/playbooks/deploy-webservers.yml`
2. **Launch** 버튼으로 실행

## 📋 체크리스트

설치 및 설정이 완료되었는지 확인하세요:

- [ ] AWX 웹 UI에 접속할 수 있음 (http://localhost:8080)
- [ ] `admin` 계정으로 로그인 성공
- [ ] 인벤토리 생성 완료
- [ ] 최소 1개 이상의 호스트 추가
- [ ] 프로젝트 생성 및 동기화 완료
- [ ] Job Template 생성 완료
- [ ] 첫 번째 Job 실행 성공

## 🔧 자주 사용하는 명령어

### AWX 관리

```bash
# AWX 상태 확인
cd orchestra
docker-compose ps

# AWX 로그 확인
docker logs -f awx_web

# AWX 재시작
docker-compose restart

# AWX 중지
docker-compose stop

# AWX 시작
docker-compose start

# AWX 완전 제거 (데이터 포함)
docker-compose down -v
```

### Ansible 직접 실행 (AWX 없이)

```bash
# 인벤토리의 모든 서버에 핑 테스트
ansible all -i inventory.ini -m ping

# 헬스 체크 플레이북 직접 실행
ansible-playbook -i inventory.ini orchestra/playbooks/health-check.yml

# Nginx 배포 플레이북 실행
ansible-playbook -i inventory.ini orchestra/playbooks/deploy-webservers.yml
```

## 🚨 문제 해결

### AWX 웹 UI에 접속할 수 없음

```bash
# 컨테이너 상태 확인
docker ps

# AWX 웹 로그 확인
docker logs awx_web

# 포트 8080이 사용 중인지 확인
sudo netstat -tulpn | grep 8080

# 방화벽 허용 (필요시)
sudo ufw allow 8080
```

### 로그인 실패

기본 계정 정보 확인:
- 사용자명: `admin`
- 비밀번호: `admin`

컨테이너를 재시작해 보세요:
```bash
docker-compose restart awx_web
```

### Job 실행 실패

1. **호스트 연결 확인**:
   - SSH 키가 올바르게 설정되었는지 확인
   - 호스트 Variables에 `ansible_user`가 설정되었는지 확인

2. **Credential 추가**:
   - **Resources** → **Credentials** → **Add**
   - **Credential Type**: Machine
   - SSH 키 또는 비밀번호 입력

3. **Job Template에 Credential 연결**:
   - Job Template 편집
   - **Credentials** 섹션에서 생성한 Credential 선택

## 📚 다음 단계

기본 설정이 완료되었다면:

1. **보안 강화**:
   - [orchestra/README.md](README.md#보안-설정) 참조
   - 관리자 비밀번호 변경
   - HTTPS 설정

2. **고급 기능**:
   - 추가 플레이북 작성
   - 스케줄된 작업 설정
   - 사용자 및 팀 관리
   - 알림 설정

3. **상세 문서**:
   - [전체 설치 가이드](README.md)
   - [플레이북 예제](playbooks/README.md)
   - [Ansible 공식 문서](https://docs.ansible.com/)

## 💡 팁

- **프로젝트 동기화**: Git 저장소를 업데이트한 후 AWX 프로젝트를 동기화하세요
- **Variables 활용**: Job Template에서 Extra Variables로 설정을 오버라이드할 수 있습니다
- **로그 저장**: Job 실행 결과는 AWX에 자동으로 저장되며 언제든지 확인 가능합니다
- **API 활용**: AWX는 RESTful API를 제공하므로 외부 시스템과 통합 가능합니다

## 🆘 도움말

문제가 발생하면:

1. [전체 문서](README.md) 확인
2. [문제 해결 섹션](README.md#문제-해결) 참조
3. GitHub 이슈 생성
4. [Ansible AWX 공식 문서](https://github.com/ansible/awx) 참조

---

**축하합니다! 🎉** 
이제 Ansible AWX Orchestra 서버를 사용할 준비가 되었습니다!
