#!/usr/bin/env bash
# 매시간 실행: 변경 감지(무료) → 변경 있을 때만 Claude 실행 → 검증 → 브랜치 + PR
# 로컬 cron 예:  7 * * * * cd /path/to/repo && bash scripts/harness-update.sh >> harness/cron.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."

status=$(python3 scripts/check_sources.py | head -1)
echo "[check] $status"
case "$status" in
  BASELINE*|NO_CHANGES*|RATE_LIMITED*) exit 0 ;;
esac

branch="harness/auto-$(date -u +%Y%m%d-%H%M)"
git checkout -b "$branch"

HARNESS_AUTO=1 claude -p "/harness-update" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Grep,Glob,WebFetch,WebSearch,Task,Bash(python3 scripts/check_sources.py:*),Bash(python3 scripts/validate_harness.py:*),Bash(git diff:*),Bash(git checkout --:*)" \
  --max-turns 40 | tee harness/last-run.md

python3 scripts/validate_harness.py
python3 scripts/check_sources.py --commit-state

git add -A
if git diff --cached --quiet; then echo "no diff"; exit 0; fi
git commit -m "chore(harness): auto-update $(date -u +%FT%H:%MZ)"
git push -u origin "$branch"
if command -v gh >/dev/null; then
  gh label create harness-auto --color 5319e7 --force >/dev/null 2>&1 || true
  gh pr create --title "harness: auto-update $(date -u +%F\ %H:%M)" --body-file harness/last-run.md --label harness-auto
fi
