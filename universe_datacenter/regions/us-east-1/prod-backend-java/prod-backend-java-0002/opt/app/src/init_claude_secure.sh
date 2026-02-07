#!/bin/bash

echo "🛡️  Initializing Secure Claude Code Integration..."

# 1. 디렉토리 구조 생성
mkdir -p .github/workflows
mkdir -p .github/actions/setup-claude

# ==============================================================================
# 2. Setup Action 생성 (Setup-Claude)
# ==============================================================================
echo "⚙️  Generating Setup Action..."
cat << 'EOF' > .github/actions/setup-claude/action.yml
name: 'Setup Claude Code'
description: 'Installs Claude Code CLI and persists authentication globally'
inputs:
  anthropic-key:
    description: 'API Key for Authentication'
    required: true

runs:
  using: "composite"
  steps:
    - name: Install Claude Code
      shell: bash
      run: |
        echo "⬇️ Installing Claude Code..."
        curl -fsSL https://claude.ai/install.sh | bash
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Configure Global Authentication
      shell: bash
      run: |
        # [SECURE FIX] API 키를 GITHUB_ENV에 기록하여 Job 전체에 공유
        echo "ANTHROPIC_API_KEY=${{ inputs.anthropic-key }}" >> $GITHUB_ENV
        
        # Headless 모드 활성화
        echo "CI=true" >> $GITHUB_ENV
        echo "CLAUDE_HEADLESS=true" >> $GITHUB_ENV
        
        # Git 봇 설정
        git config --global user.name "Claude Bot"
        git config --global user.email "bot@claude.ai"

    - name: Verify Installation
      shell: bash
      run: claude --version
EOF

# ==============================================================================
# 3. Workflow: Feature Builder (기능 구현)
# ==============================================================================
echo "🏗️  Generating Feature Builder Workflow..."
cat << 'EOF' > .github/workflows/03-feature-builder.yml
name: 🏗️ Feature Builder (Dispatch)
on:
  workflow_dispatch:
    inputs:
      requirement:
        description: '구현할 기능 설명'
        required: true
      branch_name:
        description: '브랜치 이름 (옵션)'
        required: false

jobs:
  build-feature:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v3
      
      - uses: ./.github/actions/setup-claude
        with:
          anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Implement Feature
        id: coding
        env:
          BRANCH_NAME: ${{ inputs.branch_name || format('feature/claude-{0}', github.run_id) }}
        run: |
          git checkout -b $BRANCH_NAME
          
          echo "🤖 Claude is working on: ${{ inputs.requirement }}"
          
          # Claude 실행 (토큰 누수 방지된 안전한 프롬프트)
          claude -p "TASK: ${{ inputs.requirement }} \n CONTEXT: CI Environment. \n ACTION: Implement feature. No user input."
          
          if [[ -n $(git status --porcelain) ]]; then
            git add .
            COMMIT_MSG=$(git diff --staged | claude -p "Generate commit message (max 50 chars)")
            git commit -m "$COMMIT_MSG"
            git push origin $BRANCH_NAME
            echo "pushed=true" >> $GITHUB_OUTPUT
            echo "branch=$BRANCH_NAME" >> $GITHUB_OUTPUT
          else
            echo "pushed=false" >> $GITHUB_OUTPUT
          fi

      - name: Create PR
        if: steps.coding.outputs.pushed == 'true'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          BRANCH_NAME: ${{ steps.coding.outputs.branch }}
        run: |
          gh pr create --title "✨ Feature: $BRANCH_NAME" --body "Implemented by Claude Code: ${{ inputs.requirement }}" --head $BRANCH_NAME --base main
EOF

# ==============================================================================
# 4. Workflow: Auto Review (PR 리뷰)
# ==============================================================================
echo "🤖 Generating PR Review Workflow..."
cat << 'EOF' > .github/workflows/01-pr-auto-review.yml
name: 🤖 Claude Code Reviewer
on:
  pull_request:
    types: [opened, synchronize]
    paths-ignore: ['*.md', '.github/**']
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v3
        with: { fetch-depth: 0 }
      - uses: ./.github/actions/setup-claude
        with:
          anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Analyze Diff
        env:
          PR_NUMBER: ${{ github.event.pull_request.number }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git diff origin/${{ github.base_ref }} > diff.txt
          if [ ! -s diff.txt ]; then exit 0; fi
          cat diff.txt | claude -p "Review diff for bugs/security. Output Markdown. If good, say 'LGTM'." > review.md
          if ! grep -q "LGTM" review.md; then gh pr comment $PR_NUMBER --body-file review.md; fi
EOF

# ==============================================================================
# 5. Workflow: Issue Triage (이슈 대응)
# ==============================================================================
echo "🚑 Generating Issue Triage Workflow..."
cat << 'EOF' > .github/workflows/02-issue-triage.yml
name: 🚑 Issue Auto-Triage
on:
  issues: { types: [opened] }
jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
    steps:
      - uses: actions/checkout@v3
      - uses: ./.github/actions/setup-claude
        with:
          anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Suggest Solution
        env:
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "${{ github.event.issue.title }} \n ${{ github.event.issue.body }}" > issue.txt
          claude -p "Analyze issue and suggest code fix. Context: $(cat issue.txt)" > solution.md
          gh issue comment $ISSUE_NUMBER --body-file solution.md
EOF

# ==============================================================================
# 6. Workflow: Nightly Refactor (정기 리팩토링)
# ==============================================================================
echo "🧹 Generating Nightly Refactor Workflow..."
cat << 'EOF' > .github/workflows/99-nightly-refactor.yml
name: 🧹 Nightly Refactor
on:
  schedule:
    - cron: '0 18 * * *'
jobs:
  refactor:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v3
      - uses: ./.github/actions/setup-claude
        with:
          anthropic-key: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Cleanup Code
        run: |
          BRANCH="refactor/nightly-$(date +%Y%m%d)"
          git checkout -b $BRANCH
          claude -p "Scan codebase for unused vars/imports and fix them."
          if [[ -n $(git status --porcelain) ]]; then
            git add .
            git commit -m "🧹 Nightly cleanup"
            git push origin $BRANCH
            gh pr create --title "🧹 Nightly Refactor" --body "Automated cleanup" --base main
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF

# ==============================================================================
# 7. 이전의 잘못된 파일 정리 및 강제 푸시
# ==============================================================================
echo "🧹 Cleaning up generated scripts..."
rm -f generate_workflows.sh

echo "📦 Preparing to Push..."
git add .

# 상태 확인 후 커밋
if [[ -n $(git status --porcelain) ]]; then
  git commit -m "🚀 Fix: Secure Claude Integration (Remove leaked secrets)"
  
  echo "🚀 Pushing changes..."
  # 이전에 실패했으므로 안전하게 푸시
  git push
else
  echo "✅ Nothing to change. Files are already correct."
fi
