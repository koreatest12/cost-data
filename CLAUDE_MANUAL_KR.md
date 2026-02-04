# 📘 Claude Code 통합 운영 매뉴얼

## 🚀 필수 설정
1. **Secrets**: `ANTHROPIC_API_KEY` 등록 필수.
2. **Permissions**: Settings > Actions > General > "Read and write permissions" 체크.

## 🤖 기능 가이드
1. **🏗️ Feature Builder**: `Actions` 탭에서 수동 실행. 원하는 기능을 한국어로 입력하면 코드 작성 및 PR 생성.
2. **🤖 Auto Reviewer**: PR 생성 시 자동 실행. 코드 변경사항을 분석해 한국어로 리뷰.
3. **🚑 Issue Triage**: 이슈 등록 시 자동 실행. 해결책 제안.
4. **🧹 Nightly Refactor**: 매일 새벽 자동 실행. 코드 정리.

## 🔧 문제 해결
권한 에러 발생 시:
```bash
./scripts/restore_permissions.sh
```
