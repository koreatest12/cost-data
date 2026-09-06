"""
워크플로우 용량 정리 (Workflow Capacity Cleanup)
GitHub Actions 워크플로우 실행 기록을 정리하여 저장 용량을 확보합니다.

- 오래된 워크플로우 실행 기록 삭제
- 완료/실패/취소된 실행 기록 정리
- 보존 기간(기본 7일) 이전의 기록만 삭제
"""

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

GITHUB_API = "https://api.github.com"
RETRY_MAX = 3
RETRY_DELAY = 5


def get_env():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    retention_days = int(os.environ.get("RETENTION_DAYS", "7"))
    if not token:
        print("❌ GITHUB_TOKEN 또는 GH_TOKEN 환경변수가 필요합니다.")
        sys.exit(1)
    if not repo:
        print("❌ GITHUB_REPOSITORY 환경변수가 필요합니다.")
        sys.exit(1)
    return token, repo, retention_days


def api_request(method, url, token):
    """GitHub API 요청 (재시도 포함)"""
    for attempt in range(1, RETRY_MAX + 1):
        try:
            req = Request(url, method=method)
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            resp = urlopen(req, timeout=30)
            if method == "DELETE":
                return None
            return json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode()
            if e.code == 403 and "rate limit" in body.lower():
                wait = 60 * attempt
                print(f"⏳ API 속도 제한. {wait}초 대기 중... (시도 {attempt}/{RETRY_MAX})")
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                print(f"⚠️ API 오류 ({e.code}): {url} (시도 {attempt}/{RETRY_MAX})")
                time.sleep(RETRY_DELAY * attempt)
        except URLError as e:
            print(f"⚠️ 네트워크 오류: {e.reason} (시도 {attempt}/{RETRY_MAX})")
            time.sleep(RETRY_DELAY * attempt)
    return None


def list_workflows(token, repo):
    """리포지토리의 모든 워크플로우 목록 조회"""
    url = f"{GITHUB_API}/repos/{repo}/actions/workflows?per_page=100"
    data = api_request("GET", url, token)
    if data and "workflows" in data:
        return data["workflows"]
    return []


def list_workflow_runs(token, repo, workflow_id, page=1):
    """특정 워크플로우의 실행 기록 조회"""
    url = (
        f"{GITHUB_API}/repos/{repo}/actions/workflows/{workflow_id}"
        f"/runs?per_page=100&page={page}&status=completed"
    )
    data = api_request("GET", url, token)
    if data and "workflow_runs" in data:
        return data["workflow_runs"], data.get("total_count", 0)
    return [], 0


def delete_workflow_run(token, repo, run_id):
    """워크플로우 실행 기록 삭제"""
    url = f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}"
    api_request("DELETE", url, token)


def run():
    token, repo, retention_days = get_env()
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 60)
    print("🧹 워크플로우 용량 정리 시작")
    print(f"📦 리포지토리: {repo}")
    print(f"📅 보존 기간: {retention_days}일 (기준: {cutoff_str})")
    print("=" * 60)

    workflows = list_workflows(token, repo)
    if not workflows:
        print("⚠️ 워크플로우를 찾을 수 없습니다.")
        return

    print(f"\n📋 발견된 워크플로우: {len(workflows)}개\n")

    total_deleted = 0
    total_checked = 0

    for wf in workflows:
        wf_name = wf["name"]
        wf_id = wf["id"]
        print(f"🔍 [{wf_name}] 검사 중...")

        page = 1
        wf_deleted = 0
        while True:
            runs, total_count = list_workflow_runs(token, repo, wf_id, page)
            if not runs:
                break

            for run in runs:
                total_checked += 1
                created = run.get("created_at", "")
                run_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if run_date < cutoff:
                    delete_workflow_run(token, repo, run["id"])
                    wf_deleted += 1
                    total_deleted += 1

            if len(runs) < 100:
                break
            page += 1

        if wf_deleted > 0:
            print(f"   🗑️  {wf_deleted}개 실행 기록 삭제 완료")
        else:
            print(f"   ✅ 정리할 기록 없음")

    print("\n" + "=" * 60)
    print("📊 정리 결과 요약")
    print(f"   - 검사한 실행 기록: {total_checked}개")
    print(f"   - 삭제한 실행 기록: {total_deleted}개")
    print(f"   - 보존된 실행 기록: {total_checked - total_deleted}개")
    print("=" * 60)
    print("✅ 워크플로우 용량 정리 완료!")


if __name__ == "__main__":
    run()
