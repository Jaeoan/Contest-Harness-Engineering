# Public-Data Agency Harness

공공데이터 공모전/서비스 프로젝트를 **기획 → 데이터 분석 → 디자인 → 웹 → 제출 문서**까지 Claude Code 에이전트 팀으로 돌리는 하네스.
프로젝트가 끝나면 `/retro`로 교훈을 규칙에 반영한다. 자동으로 실행되는 작업은 없다.

자세한 사용법은 **USAGE.md**.

## 빠른 시작
```bash
# 하네스 저장소에서 새 프로젝트 폴더를 만든다 (산출물을 하네스에 섞지 않는다)
mkdir ../my-contest && git archive main | tar -x -C ../my-contest
cd ../my-contest
bash scripts/install-external.sh          # 외부 스킬·MCP 설치 (vendor/는 git 제외)
claude                                    # Claude Code 실행 후:
> /kickoff docs/내기획서.md                 # 전체 파이프라인
> /analyze-plan docs/내기획서.md            # 기획서 → 데이터 분석 계획만
> /find-problem 경기도 안양시, 보행 안전     # Well-known problem 발굴
> /retro                                  # 프로젝트 끝나고 교훈을 규칙으로
```

## 구조
```
CLAUDE.md                       오케스트레이터: 절대 규칙, 팀 표, 파이프라인, 게이트
.claude/agents/ (14)            기획3 · 디자인2 · 프론트2 · 백엔드2 · 데이터3 · 게이트1 · 큐레이터1
.claude/skills/ (10 + ext-*)    기획서 · 양식 문서(Word) · 데이터소스 · 뉴스 신호 · 분석계획 · 공간위험도 · RAG · 정적 웹·AI · 프론트고정 · Spring
.claude/commands/ (4)           /kickoff /analyze-plan /find-problem /retro
.claude/hooks/guard_stack.py    금지 패키지·.js/.jsx 차단 (PreToolUse)
harness/                        protected.txt · CHANGELOG · learning-log · proposals
scripts/                        validate_harness.py · install-external.sh
examples/anyang-case.md         기준 사례 + 교훈
```

## 하네스 개선 방법
```
프로젝트 종료 → /retro → 게이트 FAIL·사용자 수정 요청·반복 작업 수집
     ▼
규칙 한 줄 + 넣을 파일을 사용자에게 제시 → 승인된 것만 하네스 저장소에 반영
     ▼
validate_harness.py 통과 → 커밋
```
지역명·프로젝트 수치는 규칙에 넣지 않는다. 구체적인 사례는 `examples/`에만 둔다.

## 고정 규칙 (사용자 승인 없이 변경 금지)
- 프론트: TypeScript + React + Tailwind CSS (Vite 기본) — 훅이 강제
- 백엔드(필요할 때만): Spring Boot 3.x + Java 21 + PostgreSQL. 공간 문제면 PostGIS
- 데이터: Python. RAG를 백엔드에 두면 pgvector
- 검증 안 된 링크·수치 금지, 상관≠인과, 사용/미사용 데이터 구분
- 하네스와 프로젝트 분리, 외부 연락·제출·배포는 사용자 승인 후

## 참고한 레포
- 에이전트 구조: msitarzewski/agency-agents (정체성·미션·규칙·산출물·지표 형식)
- 프론트/디자인: anthropics/skills(frontend-design), Leonxlnx/taste-skill, pbakaus/impeccable, microsoft/playwright-mcp
- 백엔드: piomin/claude-ai-spring-boot, rrezartprebreza/spring-boot-skills
- 데이터: nimrodfisher/data-analytics-skills, K-Dense-AI/claude-scientific-skills, probabl-ai/skills
- RAG: HKUDS/LightRAG, infiniflow/ragflow, explodinggradients/ragas
