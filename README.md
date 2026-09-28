# Public-Data Agency Harness

공공데이터 공모전/서비스 프로젝트를 **기획 → 데이터 분석 → 디자인 → 프론트 → 백엔드 → 기획서**까지 Claude Code 에이전트 팀으로 돌리는 하네스.
매시간 참고 레포의 변경을 감지해 **스스로 규칙을 업데이트(PR)** 한다.

자세한 사용법은 **USAGE.md**.

## 빠른 시작
```bash
git init && git add -A && git commit -m "init harness"
bash scripts/install-external.sh          # 외부 스킬·MCP 설치 (vendor/는 git 제외)
python3 scripts/check_sources.py          # 첫 실행 = 기준점(BASELINE) 기록
claude                                    # Claude Code 실행 후:
> /kickoff docs/내기획서.md                 # 전체 파이프라인
> /analyze-plan docs/내기획서.md            # 기획서 → 데이터 분석 계획만
> /find-problem 경기도 안양시, 보행 안전     # Well-known problem 발굴
> /retro                                  # 프로젝트 끝나고 교훈을 규칙으로
```

## 구조
```
CLAUDE.md                       오케스트레이터: 절대 규칙, 팀 표, 7단계 파이프라인, 게이트
.claude/agents/ (14)            기획3 · 디자인2 · 프론트2 · 백엔드2 · 데이터3 · 게이트1 · 큐레이터1
.claude/skills/ (7 + ext-*)     기획서 · 데이터소스 · 분석계획 · 공간위험도(+grid_features.py) · RAG · 프론트고정 · Spring
.claude/commands/ (5)           /kickoff /analyze-plan /find-problem /harness-update /retro
.claude/hooks/guard_stack.py    금지 패키지·.js/.jsx·보호파일 수정 차단 (PreToolUse)
harness/                        sources.json(감시 목록) · protected.txt · CHANGELOG · learning-log · proposals
scripts/                        check_sources.py · validate_harness.py · harness-update.sh · install-external.sh
examples/anyang-case.md         기준 사례 + 교훈
```

## "매시간 최신 정보 학습"의 실제 동작
LLM 가중치를 학습시키는 게 아니라, **하네스 파일(에이전트·스킬·레퍼런스)을 갱신**하는 것이다.
```
[매시 7분] check_sources.py ── GitHub API로 17개 레포 커밋/릴리스 비교 (LLM 호출 없음, 비용 0)
     │ 변경 없음 → 종료
     ▼ 변경 있음
harness-curator (claude -p, HARNESS_AUTO=1)
     │ 변경 내용 읽기 → 분류(무관/지식/규칙/파괴적) → 최대 5파일 수정 → 출처 기록
     │ 보호 파일은 훅이 차단 → proposals.md에 제안만
     ▼
validate_harness.py 통과 → 브랜치 harness/auto-* → PR (라벨 harness-auto)
     ▼
사람이 리뷰·머지 (열린 자동 PR이 있으면 다음 실행은 건너뜀)
```
실행 방법 3가지 중 택1:
1. **GitHub Actions** (포함됨): `.github/workflows/harness-hourly.yml` — 저장소 Secrets에 `ANTHROPIC_API_KEY` 추가.
2. **로컬 cron**: `7 * * * * cd <repo> && bash scripts/harness-update.sh >> harness/cron.log 2>&1`
3. **Claude Code Routines**(클라우드 스케줄): 매시간, 프롬프트 `bash scripts/harness-update.sh 를 실행하고 결과를 요약해줘`.

감시 대상 추가/삭제는 `harness/sources.json`만 고치면 된다.

## 고정 규칙 (사람만 변경)
- 프론트: TypeScript + React + Tailwind CSS (Vite 기본) — 훅이 강제
- 백엔드: Spring Boot 3.x + Java 21 + PostGIS
- 데이터: Python + pgvector RAG
- 검증 안 된 링크·수치 금지, 상관≠인과, 사용/미사용 데이터 구분

## 참고한 레포 (sources.json에서 계속 감시)
- 에이전트 구조: msitarzewski/agency-agents (정체성·미션·규칙·산출물·지표 형식)
- 프론트/디자인: anthropics/skills(frontend-design), Leonxlnx/taste-skill, pbakaus/impeccable, microsoft/playwright-mcp
- 백엔드: piomin/claude-ai-spring-boot, rrezartprebreza/spring-boot-skills
- 데이터: nimrodfisher/data-analytics-skills, K-Dense-AI/claude-scientific-skills, probabl-ai/skills
- RAG: HKUDS/LightRAG, infiniflow/ragflow, explodinggradients/ragas
