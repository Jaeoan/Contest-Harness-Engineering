# 공공데이터 서비스 하네스 (Public-Data Agency Harness)

이 저장소는 "Well-known problem → 공공데이터 분석 → 웹 서비스 → 기획서"를 한 번에 만드는 **에이전트 팀 하네스**다.
기준 사례: `examples/anyang-case.md` (안양시 어린이보호구역 위험도 프로젝트). 새 프로젝트는 이 수준 이상을 목표로 한다.

## 0. 절대 규칙 (자동 수정 금지 — harness/protected.txt)
1. **프론트엔드 스택 고정**: TypeScript(strict) + React + Tailwind CSS. 다른 UI 프레임워크(Vue/Angular/Svelte), CSS-in-JS(styled-components/emotion), 다른 CSS 프레임워크(Bootstrap/MUI/Chakra), `.js/.jsx` 소스 파일은 금지. 빌드 도구는 Vite 기본.
2. **백엔드**: Spring Boot 3.x + Java 21 + Gradle + PostgreSQL. PostGIS는 **공간 문제일 때만** 추가.
3. **데이터 분석**: Python(pandas/geopandas/scikit-learn/XGBoost/SHAP). RAG는 pgvector(백엔드와 같은 Postgres).
4. **검증 안 된 사실 금지**: 링크·건수·수치는 직접 열어보거나 코드로 계산한 것만 쓴다. 확인 못 했으면 `⚠️ 미확인`으로 표기한다.
5. **상관 ≠ 인과**: 모델 기여도는 "관련 요인"으로만 쓴다. 인과를 주장하려면 인과 설계(DiD 등)가 있어야 한다.
6. **사용/검토/미사용 데이터 구분**: 모델에 실제로 들어간 데이터만 "사용 데이터"로 쓴다.
7. 사용자와의 대화·문서는 한국어. 코드 식별자·커밋 메시지는 영어.
8. **분석 방법과 화면 표현은 문제가 정한다.** 지도·격자·PostGIS는 기본값이 아니다. `analysis-planner`가 `docs/03-analysis-plan.md`에 정한 **문제 유형**과 **표현 방식**을 모든 팀이 따른다. (안양시는 공간 문제였기 때문에 지도를 썼을 뿐이다.)

## 1. 팀 구성 (.claude/agents/)
| 팀 | 에이전트 | 역할 |
|---|---|---|
| 기획 | `problem-hunter` | 뉴스·민원·통계로 Well-known problem 후보 5~7개 제시 → 사용자 선택 후 심화 |
| 기획 | `data-scout` | 공공데이터 탐색·링크/건수 직접 검증·데이터 카드 작성 |
| 기획 | `proposal-writer` | 기획서/계획서 작성 (심사기준 매핑, 직관적 문체) |
| 디자인 | `ux-architect` | 사용자 흐름·정보 구조·화면 명세 |
| 디자인 | `ui-designer` | 디자인 토큰·컴포넌트·미적 방향(anti-slop) |
| 프론트 | `frontend-engineer` | TS/React/Tailwind 구현 (스택 고정) |
| 프론트 | `visual-qa` | Playwright로 390/1440px 스크린샷 비교·수정 루프 |
| 백엔드 | `backend-architect` | API 계약(OpenAPI)·DB 스키마 |
| 백엔드 | `backend-engineer` | Spring Boot 구현·테스트 |
| 데이터 | `analysis-planner` | 기획서 → 문제 유형 판별·분석 질문·방법·표현 방식·검증 계획 |
| 데이터 | `data-scientist` | EDA·모델링(유형별 플레이북)·해석 |
| 데이터 | `rag-engineer` | 정책문서/조례/민원 RAG, 평가 |
| 공통 | `reality-checker` | 단계 게이트: 수치·출처·주장 검증 |
| 운영 | `harness-curator` | 최신 정보 학습 및 하네스 자동 개선(PR) |

## 2. 파이프라인 (/kickoff 가 실행)
```
Phase 1 기획      problem-hunter(후보 5~7개)             → docs/01-problem-candidates.md
   ▼ GATE 0  사용자 선택 ("N번으로 가자") — 선택 전에는 절대 진행하지 않는다
                  problem-hunter(심화) → data-scout       → docs/01-problem.md, docs/02-data-cards.md
   ▼ GATE A  reality-checker (문제 근거·데이터 실존 확인)
Phase 2 분석설계  analysis-planner                        → docs/03-analysis-plan.md
   ▼ GATE B  사용자 승인 (분석 질문·방법 확정)
Phase 3 분석      data-scientist ∥ rag-engineer            → analysis/, docs/04-analysis-report.md, data/export/
   ▼ GATE C  reality-checker (누수·검증·해석 점검)
Phase 4 설계      ux-architect → ui-designer ∥ backend-architect → docs/05-ux-spec.md, design/tokens.css, api/openapi.yaml
Phase 5 구현      frontend-engineer ∥ backend-engineer     → frontend/, backend/
Phase 6 QA        visual-qa → reality-checker (GATE D)
Phase 7 문서      proposal-writer                          → docs/99-proposal.md
```
- `∥` = 병렬 실행 가능. 게이트를 통과하지 못하면 이전 Phase로 되돌린다.
- 팀 간 인수인계는 **파일로만** 한다. 대화 맥락에 의존하지 않는다.
- 계약 우선: `api/openapi.yaml`이 확정돼야 프론트/백엔드 구현을 시작한다. 프론트 타입은 `openapi-typescript`로 생성한다.

## 3. 산출물 위치
`docs/` 문서 · `data/raw`(원본, git 제외) · `data/processed` · `data/export`(백엔드 적재용) · `analysis/`(노트북·스크립트) · `api/` · `frontend/` · `backend/` · `design/`

## 4. 학습 루프
- 매시간 `scripts/check_sources.py`가 감시 레포 변경을 감지 → 변경이 있을 때만 `harness-curator`가 실행되어 **브랜치+PR**로 하네스를 수정한다. main 직접 수정 금지.
- 프로젝트가 끝나면 `/retro`로 교훈을 스킬에 반영한다. (이게 가장 값진 학습이다.)
- 변경 이력: `harness/CHANGELOG.md`, 학습 로그: `harness/learning-log/`.
