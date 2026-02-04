# 📘 Claude Code & Omni-Server 운영 매뉴얼

## 🌟 핵심 기능
1. **🏗️ 대량 스캐폴딩**: `./scripts/scaffold_services.sh` 실행 시 4개 마이크로서비스(Controller, Service, DTO 등) 자동 생성.
2. **🤖 자율 에이전트**: `04-claude-autonomous.yml`이 6시간마다 실행되어 `TODO: Claude` 주석을 찾아 자동으로 코드를 구현.
3. **🏗️ 기능 빌더**: 수동으로 기능을 요청하면 브랜치 생성부터 PR까지 자동화.

## 🚀 필수 설정
- Secrets에 `ANTHROPIC_API_KEY` 등록 필수.
- Settings > Actions > General > "Read and write permissions" 허용.

## 🆘 문제 해결
Git 충돌 에러 시, 이 부트스트랩 워크플로우를 다시 실행하면 자동으로 병합 및 복구됩니다.
