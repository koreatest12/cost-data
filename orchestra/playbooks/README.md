# Ansible Playbooks for AWX Orchestra

이 디렉토리에는 AWX에서 사용할 수 있는 예제 Ansible 플레이북들이 포함되어 있습니다.

## 플레이북 목록

### 1. deploy-webservers.yml
웹 서버에 Nginx를 설치하고 설정하는 플레이북입니다.

**대상 호스트:**
- `web_servers` 그룹: Nginx 설치 및 설정
- `deploy_server` 그룹: 배포 환경 설정

**주요 작업:**
- Nginx 설치
- 커스텀 index.html 배포
- 서비스 시작 및 활성화

**실행 방법:**
```bash
ansible-playbook -i ../../inventory.ini deploy-webservers.yml
```

### 2. health-check.yml
모든 서버의 시스템 상태를 확인하는 플레이북입니다.

**대상 호스트:**
- `all` (모든 서버)

**확인 항목:**
- 디스크 사용량
- 메모리 사용량
- 시스템 업타임
- 기본 시스템 정보

**실행 방법:**
```bash
ansible-playbook -i ../../inventory.ini health-check.yml
```

## AWX에서 사용하기

### 1. Git 저장소로 프로젝트 추가

AWX에서 이 플레이북을 사용하려면:

1. AWX 웹 UI에 로그인
2. **Projects** → **Add** 클릭
3. 다음 정보 입력:
   - Name: `Cost Data Playbooks`
   - SCM Type: `Git`
   - SCM URL: `https://github.com/koreatest12/cost-data.git`
   - SCM Branch: `main` (또는 해당 브랜치)
4. **Save** 클릭

### 2. Job Template 생성

1. **Templates** → **Add** → **Add job template** 클릭
2. 다음 정보 입력:
   - Name: `Deploy Web Servers`
   - Job Type: `Run`
   - Inventory: 생성한 인벤토리 선택
   - Project: `Cost Data Playbooks`
   - Playbook: `orchestra/playbooks/deploy-webservers.yml`
3. **Save** 클릭

### 3. Job 실행

1. 생성한 Job Template 선택
2. **Launch** 버튼 클릭
3. 실행 진행 상황을 실시간으로 확인

## 플레이북 커스터마이징

### Variables 변경

각 플레이북의 `vars` 섹션을 수정하여 설정을 변경할 수 있습니다:

```yaml
vars:
  nginx_port: 80
  server_name: example.com
```

AWX에서는 Job Template의 Extra Variables에서 이러한 변수를 오버라이드할 수 있습니다.

### 추가 플레이북 작성

새로운 플레이북을 작성할 때는 다음 구조를 따르세요:

```yaml
---
- name: Playbook Description
  hosts: target_group
  become: yes  # sudo 권한이 필요한 경우
  
  vars:
    # 변수 정의
  
  tasks:
    - name: Task description
      module_name:
        parameter: value
```

## 참고 자료

- [Ansible 문서](https://docs.ansible.com/)
- [Ansible 모듈 인덱스](https://docs.ansible.com/ansible/latest/collections/index_module.html)
- [AWX 사용자 가이드](https://github.com/ansible/awx)
