#!/usr/bin/env bash
# 참고 레포의 스킬/에이전트/MCP를 설치한다. 외부 경로가 바뀌면 경고만 내고 계속 진행한다.
# 사용: bash scripts/install-external.sh [--with-agency-global]
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p vendor .claude/skills
warn(){ echo "⚠️  $*"; echo "- $(date -u +%F) install 경고: $*" >> harness/proposals.md; }
clone(){ [ -d "vendor/$2" ] && git -C "vendor/$2" pull -q || git clone -q --depth 1 "https://github.com/$1.git" "vendor/$2" || warn "clone 실패 $1"; }
copy_skill(){ # $1=vendor 하위 검색 루트, $2=찾을 폴더명, $3=설치 이름
  local src; src=$(find "vendor/$1" -type d -name "$2" -exec test -f '{}/SKILL.md' \; -print 2>/dev/null | head -1)
  if [ -n "$src" ]; then rm -rf ".claude/skills/$3"; cp -r "$src" ".claude/skills/$3"; echo "✓ $3 ← $src"; else warn "스킬 못 찾음: $1/$2"; fi
}

echo "== 레포 가져오기 =="
clone msitarzewski/agency-agents agency-agents
clone anthropics/skills anthropic-skills
clone Leonxlnx/taste-skill taste-skill
clone piomin/claude-ai-spring-boot spring-template
clone rrezartprebreza/spring-boot-skills spring-boot-skills
clone nimrodfisher/data-analytics-skills data-analytics-skills
clone K-Dense-AI/claude-scientific-skills scientific-skills

echo "== 디자인/프론트 =="
copy_skill anthropic-skills frontend-design ext-frontend-design
copy_skill taste-skill taste-skill ext-taste-skill
command -v claude >/dev/null && claude mcp add playwright -s project -- npx @playwright/mcp@latest || warn "playwright MCP 수동 설치 필요"

echo "== 백엔드 =="
copy_skill spring-boot-skills rest-api-conventions ext-spring-rest   # Boot3/4 중 먼저 찾은 것 → 확인 필요
copy_skill spring-boot-skills spring-data-jpa ext-spring-jpa
copy_skill spring-template spring-boot ext-spring-boot-template
copy_skill spring-template logging-patterns ext-spring-logging

echo "== 데이터 =="
copy_skill data-analytics-skills programmatic-eda ext-programmatic-eda
for s in geopandas shap scikit-learn statsmodels; do copy_skill scientific-skills "$s" "ext-$s"; done
echo "ℹ️  ML 파이프라인 방법론(선택): Claude Code 안에서 /plugin marketplace add probabl-ai/skills"

if [ "${1:-}" = "--with-agency-global" ]; then
  echo "== agency-agents (전역 ~/.claude/agents) =="
  (cd vendor/agency-agents && ./scripts/install.sh --tool claude-code \
     --agent rag-pipeline-engineer,data-visualization-engineer,ui-finish-gate-reviewer,evidence-collector,trend-researcher) \
     || warn "agency-agents 설치 스크립트 옵션 변경 가능성 — README 확인"
fi

echo "== 검증 =="
python3 scripts/validate_harness.py
echo "완료. vendor/는 git에 올리지 않는다(.gitignore)."
