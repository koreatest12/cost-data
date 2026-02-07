# Claude Code 완벽 가이드 (한국어)

> Anthropic의 AI 코딩 어시스턴트 - 터미널에서 작동하는 에이전틱 개발 환경

---

## 📑 목차

1. [Claude Code란?](#1-claude-code란)
2. [설치 및 시작하기](#2-설치-및-시작하기)
3. [기본 사용법](#3-기본-사용법)
4. [주요 기능](#4-주요-기능)
5. [고급 기능](#5-고급-기능)
6. [모범 사례](#6-모범-사례)
7. [자주 사용하는 워크플로우](#7-자주-사용하는-워크플로우)
8. [문제 해결](#8-문제-해결)
9. [핵심 요약](#9-핵심-요약)

---

## 1. Claude Code란?

**Claude Code**는 Anthropic이 개발한 최고 성능의 AI 코딩 어시스턴트로, 터미널에서 직접 작동하는 에이전틱(agentic) 코딩 환경입니다.

### 1.1 주요 특징

전통적인 챗봇과 달리 Claude Code는:
- 🔍 파일을 직접 읽고 분석
- ✏️ 코드를 수정하고 작성
- ⚙️ 터미널 명령어 실행
- 🔄 Git 커밋 생성 및 관리
- 🧪 테스트 작성 및 실행
- 🐛 코드 디버깅 및 최적화

### 1.2 지원 플랫폼

- 💻 **터미널** (CLI) - 핵심 경험
- 🌐 **웹 버전** - claude.ai/code
- 🎨 **VS Code** - 확장 프로그램
- 🛠️ **JetBrains IDE** - 플러그인
- 🤖 **CI/CD** - GitHub Actions, GitLab CI
- 💬 **Slack** - 팀 협업
- 🌍 **Chrome** - 브라우저 확장

### 1.3 개발자들이 선호하는 이유

- ⚡ Unix 철학에 따른 구성 가능한 설계
- 🎯 직접 작업을 수행하여 생산성 극대화
- 🔌 MCP를 통한 외부 도구 통합
- 🔒 엔터프라이즈급 보안 및 프라이버시

---

## 2. 설치 및 시작하기

### 2.1 시스템 요구사항

| 항목 | 요구사항 |
|------|----------|
| **운영체제** | macOS 13.0+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+ |
| **하드웨어** | 4GB 이상 RAM |
| **네트워크** | 인터넷 연결 필수 |
| **쉘** | Bash 또는 Zsh 권장 |

### 2.2 설치 방법

#### 옵션 1: 원시 설치 (권장)

**macOS / Linux / WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

#### 옵션 2: Homebrew (macOS)

```bash
brew install --cask claude-code
```

#### 옵션 3: WinGet (Windows)

```powershell
winget install Anthropic.ClaudeCode
```

### 2.3 인증 설정

#### 개인 사용자
- Claude Pro 구독 (권장)
- Claude Max 구독
- Claude Console 계정

#### 팀/조직
- Claude for Teams
- Claude for Enterprise
- Amazon Bedrock
- Google Vertex AI
- Microsoft Foundry

### 2.4 첫 실행

```bash
# 프로젝트 디렉토리로 이동
cd your-project

# Claude Code 시작
claude
```

---

## 3. 기본 사용법

### 3.1 핵심 CLI 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `claude` | 대화형 모드 시작 | `claude` |
| `claude "작업"` | 일회성 작업 실행 | `claude "add hello world function"` |
| `claude -p "쿼리"` | 쿼리만 실행 후 종료 | `claude -p "explain this code"` |
| `claude -c` | 최근 대화 계속 | `claude --continue` |
| `claude -r` | 세션 선택 및 재개 | `claude --resume` |
| `claude --help` | 도움말 표시 | `claude --help` |

### 3.2 첫 세션 시작하기

**1단계: 로그인**
```bash
# Claude Code 시작
claude

# 로그인 명령어 실행
/login
```

**2단계: 프로젝트 이해하기**
```
what does this project do?
```

**3단계: 코드 변경하기**
```
add a hello world function to the main file
```

**4단계: Git 작업**
```
commit my changes with a descriptive message
```

### 3.3 대화형 모드 키보드 단축키

| 단축키 | 기능 | 설명 |
|--------|------|------|
| `Ctrl+C` | 현재 작업 취소 | Claude의 현재 작업을 중단 |
| `Ctrl+D` | 종료 | Claude Code 종료 |
| `Ctrl+O` | 상세 출력 토글 | 자세한 로그 표시/숨김 |
| `Ctrl+R` | 명령 기록 검색 | 이전 명령어 검색 |
| `Esc + Esc` | 되돌리기 | 코드/대화 이전 상태로 복원 |
| `Shift+Tab` | 권한 모드 전환 | 권한 설정 모드 변경 |
| `?` | 단축키 표시 | 사용 가능한 모든 단축키 확인 |

---

## 4. 주요 기능

### 4.1 슬래시 명령어

Claude Code는 다양한 슬래시 명령어를 제공합니다:

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `/help` | 도움말 표시 | `/help` |
| `/clear` | 대화 기록 초기화 | `/clear` |
| `/model` | AI 모델 선택 | `/model` → sonnet/opus/haiku 선택 |
| `/permissions` | 권한 설정 | `/permissions` |
| `/config` | 설정 파일 열기 | `/config` |
| `/memory` | CLAUDE.md 편집 | `/memory` |
| `/hooks` | 훅 관리 | `/hooks` |
| `/mcp` | MCP 서버 관리 | `/mcp` |
| `/cost` | 토큰 사용량 확인 | `/cost` |
| `/context` | 컨텍스트 시각화 | `/context` |
| `/rename` | 세션 이름 변경 | `/rename my-feature` |
| `/rewind` | 이전 상태로 되돌리기 | `/rewind` |
| `/init` | CLAUDE.md 초기화 | `/init` |
| `/theme` | 색상 테마 변경 | `/theme` |
| `/vim` | Vim 모드 활성화 | `/vim` |

### 4.2 훅 (Hooks)

훅은 Claude Code의 특정 이벤트에서 자동으로 실행되는 셸 명령어입니다.

#### 주요 훅 이벤트

| 이벤트 | 실행 시점 | 차단 가능 여부 |
|--------|----------|---------------|
| `SessionStart` | 세션 시작 시 | ❌ |
| `PreToolUse` | 도구 사용 전 | ✅ |
| `PostToolUse` | 도구 사용 후 | ❌ |
| `Notification` | 알림 필요 시 | ❌ |
| `UserPromptSubmit` | 사용자 프롬프트 제출 시 | ✅ |
| `Stop` | Claude 응답 완료 시 | ❌ |
| `PreCompact` | 컨텍스트 압축 전 | ✅ |

#### 훅 설정 예시

**자동 코드 포맷팅:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

**Git 커밋 전 테스트 실행:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "npm test",
            "blockOnFailure": true
          }
        ]
      }
    ]
  }
}
```

#### 훅 설정 위치

- `~/.claude/settings.json` - 모든 프로젝트에 적용
- `.claude/settings.json` - 특정 프로젝트에만 적용
- `/hooks` 명령으로 대화형 설정

### 4.3 MCP (Model Context Protocol) 서버

MCP는 Claude Code를 외부 도구, 데이터베이스, API에 연결하는 프로토콜입니다.

#### 인기 있는 MCP 서버

| 서버 | 기능 | 사용 사례 |
|------|------|-----------|
| **GitHub** | PR 리뷰, 이슈 관리 | 코드 리뷰 자동화 |
| **Sentry** | 에러 모니터링 | 버그 추적 및 수정 |
| **PostgreSQL** | 데이터베이스 쿼리 | 스키마 분석, 쿼리 최적화 |
| **Notion** | 문서 관리 | 설계 문서 참조 |
| **Figma** | 디자인 파일 | UI 구현 |
| **Slack** | 메시지 관리 | 팀 커뮤니케이션 |

#### MCP 서버 추가

**HTTP 서버 추가:**
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

**로컬 stdio 서버 추가:**
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub
```

#### MCP 서버 관리

```bash
# MCP 서버 목록 확인
claude mcp list

# MCP 서버 제거
claude mcp remove github

# MCP 서버 상태 확인
claude mcp status
```

#### MCP 설정 범위

| 범위 | 위치 | 적용 대상 |
|------|------|-----------|
| `local` | `~/.claude.json` | 현재 프로젝트만 |
| `project` | `.mcp.json` | 모든 팀원 (git 커밋) |
| `user` | `~/.claude.json` | 모든 프로젝트 |

#### MCP 인증

```bash
# Claude Code 내에서
/mcp

# OAuth 인증 진행
# 브라우저에서 인증 완료
```

### 4.4 스킬 (Skills)

스킬은 Claude Code의 기능을 확장하는 재사용 가능한 지시사항입니다.

#### 스킬 생성

**1단계: 디렉토리 생성**
```bash
mkdir -p ~/.claude/skills/my-skill
```

**2단계: SKILL.md 작성**
```yaml
---
name: my-skill
description: 스킬이 하는 일에 대한 설명
disable-model-invocation: false
allowed-tools: Read, Grep, Glob
---

스킬의 구체적인 지시사항을 여기에 작성합니다.

예시:
1. 프로젝트의 모든 TODO 코멘트 찾기
2. 우선순위별로 정리
3. 마크다운 리포트 생성
```

#### 스킬 호출

```bash
/my-skill [인자]
```

#### 스킬 설정 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `name` | 스킬 이름 | 필수 |
| `description` | Claude가 사용 시기를 판단하는 설명 | 필수 |
| `disable-model-invocation` | 자동 호출 비활성화 | false |
| `user-invocable` | 사용자 메뉴에 표시 | true |
| `allowed-tools` | 스킬이 사용 가능한 도구 | 모든 도구 |
| `context: fork` | 격리된 서브에이전트에서 실행 | - |

#### 스킬 위치

- `~/.claude/skills/` - 모든 프로젝트
- `.claude/skills/` - 특정 프로젝트
- 플러그인에 포함된 스킬

#### 유용한 스킬 예시

**코드 리뷰 스킬:**
```yaml
---
name: code-review
description: 코드 보안 및 품질 검토
allowed-tools: Read, Grep, Glob
---

다음 항목을 검토하세요:
1. 보안 취약점 (SQL 주입, XSS, CSRF)
2. 코드 중복 및 복잡도
3. 테스트 커버리지
4. 성능 이슈
5. 문서화 상태

마크다운 형식으로 리포트를 작성하세요.
```

**린팅 자동 수정 스킬:**
```yaml
---
name: fix-linting
description: Linting 문제 자동 수정
disable-model-invocation: true
---

1. Run linter: `npm run lint`
2. Fix any issues automatically
3. Run lint again to verify all fixed
4. Create a commit "fix: resolve linting issues"
```

### 4.5 설정 (Settings)

#### 설정 파일 계층 구조

설정은 다음 순서로 적용됩니다 (위가 높은 우선순위):

1. **관리됨(Managed)** - 조직 정책 (최고 우선순위)
2. **로컬** - `.claude/*.local.json` (gitignored)
3. **프로젝트** - `.claude/settings.json` (git 커밋)
4. **사용자** - `~/.claude/settings.json`

#### 주요 설정 옵션

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git *)",
      "Read",
      "Edit(src/**)",
      "Write"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(.env*)",
      "Read(secrets/**)"
    ]
  },

  "env": {
    "NODE_ENV": "development",
    "DEBUG": "app:*"
  },

  "model": "claude-sonnet-4-5-20250929",

  "sandbox": {
    "enabled": true
  },

  "hooks": {
    // 훅 설정
  }
}
```

#### 권한 규칙 패턴

| 패턴 | 설명 | 예시 |
|------|------|------|
| `Bash` | 모든 bash 명령어 | `Bash` |
| `Bash(cmd*)` | 특정 명령어로 시작 | `Bash(npm run *)` |
| `Read(path)` | 특정 파일 읽기 | `Read(.env)` |
| `Edit(glob)` | Glob 패턴으로 편집 | `Edit(src/**)` |
| `Write` | 파일 쓰기 전체 | `Write` |

### 4.6 IDE 통합

#### VS Code 확장

**설치 방법:**
1. VS Code 확장 마켓플레이스 열기
2. "Claude Code" 검색
3. 설치 클릭

**주요 기능:**
- 📝 인라인 diff 보기
- 🔗 @ 멘션으로 파일 참조
- 📚 대화 기록 접근
- 🎭 여러 탭에서 동시 대화
- 🎨 코드 하이라이팅

**중요 단축키:**

| 단축키 (Mac) | 단축키 (Windows/Linux) | 기능 |
|-------------|----------------------|------|
| `Cmd+P` | `Ctrl+P` | 모델 선택 |
| `Option+K` | `Alt+K` | @ 멘션 참조 추가 |
| `Cmd+N` | `Ctrl+N` | 새 대화 시작 |
| `Cmd+Enter` | `Ctrl+Enter` | 프롬프트 제출 |

#### JetBrains IDE 플러그인

**설치 방법:**
1. Settings → Plugins
2. Marketplace 탭에서 "Claude Code" 검색
3. Install 클릭

**지원 IDE:**
- IntelliJ IDEA
- PyCharm
- WebStorm
- PhpStorm
- GoLand
- RubyMine

### 4.7 키보드 단축키 커스터마이제이션

#### 설정 파일 위치
```bash
~/.claude/keybindings.json
```

#### 커스텀 바인딩 예시

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+s": "chat:stash",
        "ctrl+u": null,
        "alt+c": "chat:clear"
      }
    },
    {
      "context": "Global",
      "bindings": {
        "ctrl+t": "tabs:new",
        "ctrl+w": "tabs:close"
      }
    }
  ]
}
```

#### 주요 컨텍스트

| 컨텍스트 | 설명 |
|----------|------|
| `Global` | 모든 화면 |
| `Chat` | 채팅 입력 |
| `Autocomplete` | 자동완성 |
| `Settings` | 설정 화면 |
| `Confirmation` | 확인 대화상자 |
| `Transcript` | 대화 기록 |
| `HistorySearch` | 기록 검색 |
| `Task` | 작업 실행 중 |
| `ThemePicker` | 테마 선택 |
| `Tabs` | 탭 관리 |
| `DiffDialog` | Diff 보기 |
| `ModelPicker` | 모델 선택 |

---

## 5. 고급 기능

### 5.1 계획 모드 (Plan Mode)

코드 변경 전에 Claude가 계획을 수립하고 검토할 수 있도록 합니다.

#### 사용 방법

```bash
/plan
```

그 후 작업 요청:
```
refactor the authentication system to use OAuth2
```

#### 계획 모드의 장점

- ✅ Claude가 먼저 분석하고 계획 수립
- ✅ 변경 전에 검토 및 승인 기회
- ✅ 큰 변경사항에 권장
- ⚠️ 일반 모드보다 느림

#### 언제 사용할까?

| 상황 | 계획 모드 | 일반 모드 |
|------|----------|----------|
| 대규모 리팩토링 | ✅ | ❌ |
| 새로운 기능 추가 | ✅ | △ |
| 아키텍처 변경 | ✅ | ❌ |
| 버그 수정 | △ | ✅ |
| 간단한 수정 | ❌ | ✅ |

### 5.2 확장된 사고 모드 (Extended Thinking)

복잡한 문제에 대해 더 깊은 분석을 제공합니다.

#### 활성화 방법

**방법 1: 모델 선택 시**
```bash
/model
# "Extended thinking" 옵션 활성화
```

**방법 2: 스킬에서**
```yaml
---
name: complex-analysis
description: 복잡한 분석 ultrathink
---

다음을 심층 분석하세요:
- 아키텍처 문제
- 성능 병목 지점
- 보안 취약점
```

#### 언제 사용할까?

- 🧩 복잡한 알고리즘 설계
- 🏗️ 아키텍처 결정
- 🔍 심층 디버깅
- 📊 성능 최적화

### 5.3 체크포인팅 (Checkpointing)

이전 상태로 되돌리기 기능입니다.

#### 되돌리기 방법

**키보드 단축키:**
```
Esc + Esc
```

**슬래시 명령어:**
```
/rewind
```

#### 되돌리기 옵션

1. **특정 메시지 시점으로 대화 되돌리기**
   - 선택한 메시지 이후 대화 삭제

2. **코드만 되돌리기 (대화 유지)**
   - 파일 변경사항만 복원

3. **둘 다 되돌리기**
   - 대화와 코드 모두 복원

#### 사용 예시

```bash
# 잘못된 변경사항 적용 후
Esc + Esc

# 원하는 시점 선택
# → 코드 복원 완료
```

### 5.4 서브에이전트 (Subagents)

특정 작업을 격리된 컨텍스트에서 실행합니다.

#### 서브에이전트 생성

**1단계: 디렉토리 생성**
```bash
mkdir -p .claude/agents
```

**2단계: 에이전트 파일 작성**

`.claude/agents/security-reviewer.md`:
```yaml
---
name: security-reviewer
description: 코드 보안 취약점 검토
tools: Read, Grep, Glob, Bash
model: opus
---

보안 전문가로서 다음을 검토하세요:

## 검토 항목
1. SQL 주입 및 XSS 취약점
2. 인증/권한 결함
3. 비밀키 및 토큰 노출
4. 안전하지 않은 직렬화
5. CSRF 보호

## 출력 형식
- 발견된 취약점 목록
- 심각도 등급 (Critical/High/Medium/Low)
- 수정 방법 제안
```

#### 서브에이전트 호출

```bash
use a subagent to review this code for security issues
```

#### 서브에이전트의 장점

- 🎯 메인 대화 컨텍스트를 깨끗하게 유지
- 📝 조사 결과만 요약으로 받음
- ⚡ 병렬 처리 가능
- 🔒 격리된 환경에서 안전하게 실행

### 5.5 헤드리스 모드 (Headless Mode)

CI/CD, 스크립트에서 Claude를 사용할 수 있습니다.

#### 기본 사용법

**간단한 쿼리:**
```bash
claude -p "Explain this project"
```

**JSON 출력:**
```bash
claude -p "List all API endpoints" --output-format json
```

**스트리밍 JSON:**
```bash
claude -p "Analyze logs" --output-format stream-json
```

#### CI/CD 통합 예시

**GitHub Actions:**
```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Claude
        run: curl -fsSL https://claude.ai/install.sh | bash
      - name: Review PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p "Review this PR for security issues and code quality" \
            --output-format json > review.json
      - name: Post Comment
        uses: actions/github-script@v6
        with:
          script: |
            const review = require('./review.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review.content
            });
```

### 5.6 세션 관리

#### 세션 재개

```bash
# 최근 세션 계속
claude --continue
claude -c

# 선택 가능한 목록
claude --resume
claude -r

# 이름으로 재개
claude -r "auth-refactor"
```

#### 세션 이름 지정

```bash
# 대화 중에
/rename my-feature-branch

# 또는 시작할 때
claude --session "bugfix-login"
```

#### 세션 목록 확인

```bash
# 모든 세션 보기
claude --list-sessions

# 특정 세션 정보
claude --session-info "my-feature"
```

### 5.7 병렬 세션

여러 Claude 인스턴스를 동시에 실행할 수 있습니다.

#### Git Worktree 활용

```bash
# 새 worktree 생성
git worktree add ../project-feature -b feature-branch

# 해당 디렉토리로 이동
cd ../project-feature

# 별도의 Claude 세션 시작
claude
```

#### Desktop 앱 활용

- 여러 탭에서 동시 작업
- 각 탭은 독립적인 세션
- 프로젝트 간 전환 용이

#### 사용 사례

| 작업 | 세션 1 | 세션 2 |
|------|--------|--------|
| **개발** | 새 기능 구현 | 버그 수정 |
| **리팩토링** | 백엔드 수정 | 프론트엔드 수정 |
| **테스트** | 유닛 테스트 작성 | E2E 테스트 작성 |

### 5.8 Vim 모드

Vim 키 바인딩을 사용할 수 있습니다.

#### 활성화

```bash
/vim
```

#### 기본 명령어

| 모드 | 명령어 | 설명 |
|------|--------|------|
| **일반** | `i` | 삽입 모드 |
| **일반** | `Esc` | 일반 모드로 복귀 |
| **일반** | `h/j/k/l` | 커서 이동 (←/↓/↑/→) |
| **일반** | `dd` | 줄 삭제 |
| **일반** | `yy` | 줄 복사 |
| **일반** | `p` | 붙여넣기 |
| **명령** | `:w` | 저장 |
| **명령** | `:q` | 종료 |
| **명령** | `:wq` | 저장 후 종료 |

---

## 6. 모범 사례

### 6.1 Claude가 작업을 검증하도록 하기

**가장 중요한 습관:** Claude가 자신의 작업을 확인하도록 요청하세요.

#### 좋은 예시 ✅

```
add input validation to the login form.
write tests that verify the validation works correctly.
run the tests and fix any failures.
```

#### 나쁜 예시 ❌

```
add input validation to the login form
```

#### 검증 방법

- 🧪 **테스트 작성 및 실행**
- 📸 **스크린샷으로 UI 확인**
- 🔍 **Linting 및 타입 체크**
- 🚀 **빌드 및 배포 테스트**

### 6.2 탐색 → 계획 → 구현 → 커밋

효과적인 개발 워크플로우:

#### Step 1: 탐색 (Plan Mode)

```
/plan
read the authentication system and understand how sessions are handled
```

#### Step 2: 계획

```
create a detailed implementation plan for adding OAuth2 support
```

#### Step 3: 구현

```
implement the OAuth2 flow following the plan.
write comprehensive tests and ensure they all pass.
```

#### Step 4: 커밋

```
commit the changes with a descriptive message and create a pull request
```

### 6.3 효과적인 CLAUDE.md 작성

CLAUDE.md는 프로젝트별 지식을 Claude에게 전달하는 파일입니다.

#### 포함해야 할 항목 ✅

```markdown
# CLAUDE.md

## 코드 스타일
- ES 모듈 사용 (require 금지)
- 함수형 프로그래밍 패러다임 선호
- TypeScript 타입 주석 필수

## 빌드 및 테스트
- 변경 후 항상 타입 체크: `npm run type-check`
- 개별 테스트 실행 권장: `npm test -- file.test.ts`
- 커밋 전 linting 필수: `npm run lint`

## 프로젝트 구조
- `/src` - 소스 코드
- `/tests` - 테스트 파일
- `/public` - 정적 파일

## 워크플로우
- 기능 브랜치에서 개발
- PR 전 모든 테스트 통과 필수
- 커밋 메시지는 Conventional Commits 형식

## 배포
- Vercel을 통한 자동 배포
- 환경변수는 .env.local 사용
```

#### 제외해야 할 항목 ❌

- ❌ 표준 언어 규칙 (예: JavaScript 기본 문법)
- ❌ 일반적인 API 문서
- ❌ 자주 변경되는 정보
- ❌ 과도하게 상세한 설명

### 6.4 권한 설정으로 중단 줄이기

반복적인 수동 승인을 줄이세요.

#### 권장 설정

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Read",
      "Edit(src/**)",
      "Edit(tests/**)",
      "Write(tests/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Read(.env*)",
      "Read(secrets/**)",
      "Edit(.env*)"
    ]
  }
}
```

#### 권한 설정 팁

1. ✅ **안전한 명령어는 허용**
   - `npm run`, `git status`, `git diff`

2. ⚠️ **위험한 명령어는 거부**
   - `rm -rf`, `git push --force`

3. 🔒 **민감한 파일 보호**
   - `.env`, `secrets/`, `credentials.json`

### 6.5 스킬로 재사용 가능한 워크플로우 만들기

반복 작업을 스킬로 자동화하세요.

#### 린팅 수정 스킬

`~/.claude/skills/fix-linting/SKILL.md`:
```yaml
---
name: fix-linting
description: Linting 문제 자동 수정
disable-model-invocation: true
---

1. Run linter: `npm run lint`
2. Automatically fix all fixable issues
3. Run lint again to verify all issues resolved
4. If any issues remain, fix them manually
5. Create a commit: "fix: resolve linting issues"
```

사용: `/fix-linting`

#### 코드 리뷰 스킬

`~/.claude/skills/review-pr/SKILL.md`:
```yaml
---
name: review-pr
description: Pull Request 종합 검토
allowed-tools: Read, Grep, Glob, Bash
---

다음 항목을 검토하고 리포트를 작성하세요:

1. **코드 품질**
   - 중복 코드 확인
   - 복잡도 분석
   - 명명 규칙 준수

2. **보안**
   - 취약점 검사
   - 입력 검증
   - 인증/권한 확인

3. **테스트**
   - 테스트 커버리지
   - Edge case 처리

4. **문서화**
   - 코드 주석
   - README 업데이트
```

사용: `/review-pr`

### 6.6 컨텍스트 적극 관리

컨텍스트 크기는 성능과 정확도에 영향을 미칩니다.

#### 언제 `/clear` 사용할까?

- 🔄 완전히 새로운 작업 시작
- 🔁 같은 문제를 반복해서 수정
- 📚 대화가 매우 길어졌을 때
- 🎯 관련 없는 정보가 많을 때

#### `/compact` 사용

```bash
/compact Keep the API changes and database schema discussion
```

**장점:**
- 중요한 정보만 유지
- 컨텍스트 크기 감소
- 성능 향상

#### 컨텍스트 확인

```bash
/context
# 현재 사용 중인 컨텍스트 시각화
```

### 6.7 서브에이전트로 조사 분리

탐색 작업은 서브에이전트를 활용하세요.

#### 예시

```bash
use subagents to investigate:
1. how our authentication handles token refresh
2. what OAuth utilities already exist in the codebase
3. how other services integrate with OAuth providers
```

**장점:**
- 🎯 메인 대화가 깨끗하게 유지됨
- 📊 조사 결과만 요약으로 받음
- ⚡ 여러 조사를 병렬로 수행
- 🔍 각 조사가 독립적으로 진행

### 6.8 기능 선택 가이드

어떤 기능을 사용할지 판단하세요.

| 상황 | 권장 기능 | 이유 |
|------|----------|------|
| 프로젝트 전반 규칙 | **CLAUDE.md** | 모든 세션에 자동 로드 |
| 자동 코드 포맷팅 | **훅 (Hooks)** | 결정적이고 보장된 실행 |
| 선택적 워크플로우 | **스킬 (Skills)** | 필요할 때만 로드 |
| 외부 도구 연동 | **MCP** | DB, API 직접 접근 |
| 격리된 조사 | **서브에이전트** | 컨텍스트 분리 |
| 사전 검증 | **계획 모드** | 큰 변경 전 검토 |

---

## 7. 자주 사용하는 워크플로우

### 7.1 버그 수정

```
Step 1 (Plan Mode):
Read the error message and find the relevant code that's causing the issue.

Step 2 (Normal):
Write a failing test that reproduces the bug.

Step 3 (Normal):
Fix the code to make the test pass.

Step 4 (Normal):
Run the full test suite to verify no regressions.

Step 5 (Normal):
Commit with a descriptive message following conventional commits format.
```

#### 예시

```
/plan
The login form shows "undefined" error when username is empty.
Find the code handling form validation.

[Claude 분석 후]

write a test that reproduces the "undefined" error when username is empty.
fix the validation logic to show proper error message.
run all tests and verify they pass.
commit the fix with message "fix(auth): handle empty username validation"
```

### 7.2 새 기능 추가

```
Step 1 (Plan Mode):
Create a detailed implementation plan for the new feature.

Step 2 (Normal):
Write example tests demonstrating the feature's behavior.

Step 3 (Normal):
Implement the feature to pass the tests.

Step 4 (Normal):
Add tests for edge cases and error handling.

Step 5 (Normal):
Create a PR with detailed description and test plan.
```

#### 예시

```
/plan
Add a "Remember Me" checkbox to the login form that keeps users logged in for 30 days.

[Claude의 계획 검토 후]

write tests for the remember me functionality.
implement the remember me feature with secure cookie handling.
test the feature manually and verify it works correctly.
commit and create a PR with description of the feature.
```

### 7.3 코드 리팩토링

```
Step 1 (Plan Mode):
Identify refactoring opportunities and potential risks.

Step 2 (Normal):
Create comprehensive tests for current behavior.

Step 3 (Normal):
Refactor the code while maintaining test pass status.

Step 4 (Normal):
Verify all tests still pass and no features are broken.

Step 5 (Normal):
Commit the refactoring with clear explanation.
```

#### 예시

```
/plan
The user authentication code is duplicated across multiple controllers.
Refactor to use a shared authentication middleware.

[계획 승인 후]

write tests for the current authentication behavior in all controllers.
create a shared authentication middleware.
update controllers to use the new middleware.
verify all tests pass and authentication still works.
commit with message "refactor(auth): extract shared middleware"
```

### 7.4 PR 리뷰

```bash
# GitHub CLI 사용
gh pr view 456 | claude -p "Review this PR for:
1. Security vulnerabilities
2. Code quality issues
3. Missing test coverage
4. Documentation gaps"
```

#### 또는 대화형

```
/review-pr

# GitHub URL 제공
https://github.com/org/repo/pull/456

# Claude가 PR을 분석하고 리뷰 제공
```

### 7.5 데이터베이스 마이그레이션

```
Step 1 (Plan Mode):
Review the database schema and plan the migration strategy.

Step 2 (Normal):
Write the migration script with rollback support.

Step 3 (Normal):
Test the migration on a local database.

Step 4 (Normal):
Verify data integrity and application compatibility.

Step 5 (Normal):
Document the migration process and commit.
```

### 7.6 성능 최적화

```
Step 1 (Plan Mode):
Profile the application and identify performance bottlenecks.

Step 2 (Normal):
Establish baseline metrics with benchmarks.

Step 3 (Normal):
Implement optimizations one at a time.

Step 4 (Normal):
Measure improvements and verify no regressions.

Step 5 (Normal):
Document the optimizations and results.
```

---

## 8. 문제 해결

### 8.1 설치 문제

#### "claude: command not found"

**해결 방법:**
```bash
# 설치 확인
claude --version

# 재설치
curl -fsSL https://claude.ai/install.sh | bash

# 경로 확인
which claude

# 쉘 재시작
source ~/.bashrc  # 또는 source ~/.zshrc
```

#### WSL에서 Git Bash 필요

**문제:**
Windows Subsystem for Linux에서 Git Bash 경로 설정 필요

**해결 방법:**
```bash
# 환경변수 설정
export CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"

# .bashrc 또는 .zshrc에 추가
echo 'export CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"' >> ~/.bashrc
```

### 8.2 권한 관련 문제

#### 반복적인 권한 요청

**해결 방법:**
```bash
# 설정 파일 열기
/config

# 또는 직접 편집
nano ~/.claude/settings.json
```

**권장 설정:**
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git *)",
      "Read",
      "Edit(src/**)"
    ]
  }
}
```

#### 모든 권한 요청 건너뛰기 (위험)

```bash
claude --dangerously-skip-permissions
```

**⚠️ 경고:** 보안 위험이 있으므로 신뢰할 수 있는 환경에서만 사용하세요.

### 8.3 성능 문제

#### 느린 응답 속도

**진단:**
```bash
# 컨텍스트 사용량 확인
/context

# 비용 및 토큰 사용량 확인
/cost
```

**해결 방법:**
```bash
# 컨텍스트 초기화
/clear

# 또는 컨텍스트 압축
/compact Keep only the important parts about the API implementation
```

#### 높은 CPU/메모리 사용

**해결 방법:**
1. VS Code 확장 재시작
2. 백그라운드 프로세스 확인: `/tasks`
3. Claude Code 재시작
4. 시스템 재부팅

### 8.4 세션 문제

#### 세션을 찾을 수 없음

**해결 방법:**
```bash
# 사용 가능한 세션 목록 보기
claude -r

# 특정 세션 검색
claude --list-sessions | grep "feature"
```

#### 원격 세션 문제

**웹에서 터미널로 전환:**
```bash
claude --teleport
```

**터미널에서 웹으로 전환:**
```
/teleport
```

### 8.5 MCP 연결 문제

#### MCP 서버 연결 실패

**진단:**
```bash
# MCP 서버 상태 확인
claude mcp status

# MCP 서버 목록
claude mcp list
```

**해결 방법:**
```bash
# MCP 서버 제거 후 재추가
claude mcp remove problematic-server
claude mcp add --transport http problematic-server https://api.example.com/mcp/

# 또는 OAuth 재인증
/mcp
# OAuth 재인증 진행
```

### 8.6 Git 관련 문제

#### 커밋 실패

**문제:**
Pre-commit 훅 실패로 커밋이 안 됨

**해결 방법:**
```
fix the linting issues that are preventing the commit.
run the linter manually to see what needs to be fixed.
once fixed, create the commit again.
```

#### Push 실패

**문제:**
Remote branch와 충돌

**해결 방법:**
```
pull the latest changes from the remote branch.
resolve any merge conflicts.
push the changes again.
```

---

## 9. 핵심 요약

### 9.1 Claude Code의 3가지 철칙

1. **검증 가능하도록 만들기**
   - 테스트 작성 및 실행
   - 스크린샷으로 UI 확인
   - Linting 및 빌드 검증

2. **컨텍스트를 적극 관리하기**
   - 주기적으로 `/clear` 사용
   - 관련 없는 정보 제거
   - 컨텍스트 크기 모니터링

3. **명확하고 구체적으로 요청하기**
   - 원하는 결과를 상세히 설명
   - 테스트 및 검증 방법 명시
   - 제약 조건 명확히 전달

### 9.2 시작하기 좋은 작업

| 작업 유형 | 난이도 | 권장 이유 |
|----------|--------|-----------|
| **버그 수정** | ⭐ | 명확한 목표, 검증 가능 |
| **테스트 작성** | ⭐ | 코드 이해도 향상 |
| **Linting 문제 해결** | ⭐ | 간단하고 자동화 가능 |
| **리팩토링** | ⭐⭐ | 기존 테스트로 검증 |
| **문서화** | ⭐⭐ | 프로젝트 이해 필요 |
| **새 기능 추가** | ⭐⭐⭐ | 계획과 설계 필요 |

### 9.3 피해야 할 패턴

| 안티패턴 | 문제점 | 해결책 |
|---------|--------|--------|
| **컨텍스트 과다 축적** | 느린 응답, 낮은 정확도 | 주기적으로 `/clear` |
| **같은 실수 반복** | 비효율적 | 프롬프트 개선, CLAUDE.md 업데이트 |
| **과도하게 긴 CLAUDE.md** | 컨텍스트 낭비 | 핵심만 간결하게 |
| **불명확한 요청** | 원치 않는 결과 | 구체적이고 명확하게 |
| **검증 없이 진행** | 오류 누적 | 단계별 테스트 |

### 9.4 효과적인 프롬프트 작성

#### 좋은 프롬프트 ✅

```
Add input validation to the registration form:
1. Email must be valid format
2. Password must be at least 8 characters
3. Username must be alphanumeric only

Write tests for each validation rule.
Run the tests and ensure they all pass.
Update the form UI to show validation errors inline.
```

#### 나쁜 프롬프트 ❌

```
add validation
```

### 9.5 빠른 참조

#### 자주 사용하는 명령어

```bash
# 대화형 모드 시작
claude

# 계획 모드
/plan

# 컨텍스트 초기화
/clear

# 모델 선택
/model

# 설정 열기
/config

# 권한 관리
/permissions

# 세션 이름 변경
/rename feature-name

# 되돌리기
Esc + Esc
```

#### 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl+C` | 작업 취소 |
| `Ctrl+D` | 종료 |
| `Ctrl+R` | 기록 검색 |
| `Esc Esc` | 되돌리기 |
| `Shift+Tab` | 권한 모드 |

---

## 10. 추가 리소스

### 10.1 공식 문서

- **메인 문서:** https://code.claude.com/docs/en/overview.md
- **시작 가이드:** https://code.claude.com/docs/en/quickstart.md
- **CLI 참조:** https://code.claude.com/docs/en/cli-reference.md
- **모범 사례:** https://code.claude.com/docs/en/best-practices.md

### 10.2 주요 가이드

- **MCP 가이드:** https://code.claude.com/docs/en/mcp.md
- **스킬 가이드:** https://code.claude.com/docs/en/skills.md
- **훅 가이드:** https://code.claude.com/docs/en/hooks-guide.md
- **설정 가이드:** https://code.claude.com/docs/en/settings.md

### 10.3 IDE 통합

- **VS Code:** https://code.claude.com/docs/en/vs-code.md
- **JetBrains:** https://code.claude.com/docs/en/jetbrains.md
- **대화형 모드:** https://code.claude.com/docs/en/interactive-mode.md

### 10.4 커뮤니티 및 지원

- **GitHub:** https://github.com/anthropics/claude-code
- **Discord:** Anthropic 공식 Discord
- **포럼:** https://discuss.anthropic.com

---

## 부록 A: 설정 예시

### A.1 프로젝트별 설정

`.claude/settings.json`:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Read",
      "Edit(src/**)",
      "Write(tests/**)"
    ],
    "deny": [
      "Bash(rm *)",
      "Read(.env*)"
    ]
  },

  "env": {
    "NODE_ENV": "development"
  },

  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $(jq -r '.tool_input.file_path')"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "npm run lint",
            "blockOnFailure": true
          }
        ]
      }
    ]
  }
}
```

### A.2 사용자 전역 설정

`~/.claude/settings.json`:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  "model": "claude-sonnet-4-5-20250929",

  "permissions": {
    "allow": [
      "Read",
      "Bash(git *)"
    ]
  },

  "theme": "dark"
}
```

---

## 부록 B: 유용한 스킬 모음

### B.1 테스트 실행 스킬

`~/.claude/skills/run-tests/SKILL.md`:
```yaml
---
name: run-tests
description: 테스트 실행 및 실패 분석
allowed-tools: Bash, Read
---

1. Run all tests: `npm test`
2. If any tests fail:
   - Identify the failing tests
   - Read the relevant test files
   - Analyze the failure reasons
   - Fix the code or tests
   - Re-run tests to verify fixes
3. Report summary of test results
```

### B.2 보안 검사 스킬

`~/.claude/skills/security-check/SKILL.md`:
```yaml
---
name: security-check
description: 보안 취약점 검사
allowed-tools: Grep, Read, Bash
---

다음 보안 취약점을 검사하세요:

1. **하드코딩된 비밀키**
   - API 키, 토큰, 비밀번호 검색

2. **SQL 주입 가능성**
   - 동적 쿼리 구성 확인
   - Prepared statements 사용 여부

3. **XSS 취약점**
   - 사용자 입력의 이스케이프 처리
   - innerHTML 사용 검토

4. **CSRF 보호**
   - CSRF 토큰 사용 확인

5. **인증/권한**
   - 인증 체크 누락
   - 권한 우회 가능성

마크다운 리포트로 결과 제공
```

### B.3 코드 커버리지 스킬

`~/.claude/skills/check-coverage/SKILL.md`:
```yaml
---
name: check-coverage
description: 테스트 커버리지 확인 및 개선
allowed-tools: Bash, Read, Write
---

1. Run coverage: `npm run test:coverage`
2. Identify uncovered code:
   - Functions without tests
   - Branches not covered
   - Critical paths missing tests
3. For each uncovered area:
   - Write appropriate tests
   - Verify tests pass
   - Update coverage report
4. Report final coverage percentage
```

---

**문서 버전:** 1.0
**최종 업데이트:** 2026-02-04
**작성자:** Claude Code Agent

---

이 문서는 Claude Code 사용을 시작하는 모든 개발자를 위한 포괄적인 가이드입니다. 추가 질문이나 문제가 있다면 공식 문서를 참조하거나 커뮤니티에 문의하세요.
