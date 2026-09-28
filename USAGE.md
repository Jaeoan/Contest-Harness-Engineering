# 사용방법

## 1. 처음 한 번 설치 (10분)
```bash
unzip public-data-harness.zip && cd public-data-harness
git init && git add -A && git commit -m "init harness"
bash scripts/install-external.sh      # 외부 스킬·Playwright MCP 설치
python3 scripts/check_sources.py      # 매시간 감시 기준점 기록 (BASELINE)
pip install pandas geopandas scikit-learn xgboost shap   # 분석팀용
```
매시간 자동 업데이트를 쓰려면 GitHub에 올리고 저장소 Settings → Secrets → `ANTHROPIC_API_KEY` 추가. (Actions가 알아서 매시 7분에 돈다)

## 2. 프로젝트 시작 — 상황별로 명령어 하나
Claude Code를 이 폴더에서 실행(`claude`)한 뒤:

| 지금 내 상황 | 입력 | 결과 |
|---|---|---|
| 주제도 없음, 공모전 요강만 있음 | `/find-problem <요강 URL 또는 분야·지역>` | 뉴스·민원·통계 근거가 붙은 후보 5~7개 → **내가 번호를 고르면** 그 문제로 심화 |
| 기획서(초안) 있음, 분석 뭐 할지 모름 | `/analyze-plan docs/기획서.md` | 문제 유형 · 분석 질문 · 방법 · 화면 표현 · 첫날 할 일 |
| 처음부터 끝까지 다 | `/kickoff docs/기획서.md` | 7단계 자동 진행 (분석 계획에서 한 번 멈추고 승인 요청) |
| 프로젝트 끝남 | `/retro` | 이번 교훈을 스킬 규칙으로 저장 |

특정 팀만 부르고 싶으면 그냥 말하면 된다: "reality-checker로 기획서 수치 검사해줘", "visual-qa로 화면 검수해줘".

## 2-1. 문제 고르기 (GATE 0)
`/find-problem` 또는 `/kickoff`(문제 미정일 때)는 후보 5~7개를 보여주고 **멈춘다.** 이렇게 답하면 된다:
- "3번으로 가자" → 3번 심화 (근거 수치 확정, 뉴스 타임라인, 데이터 검증)
- "2번이랑 5번 섞어서" / "다 별로, 복지 쪽으로 다시" → 후보를 다시 만든다
후보마다 뉴스 신호(최근 3년 보도 추이 + 대표 기사 3건), 공식 수치, 쓸 수 있는 공공데이터, 분석 유형, 점수가 붙는다.
네이버 뉴스 API 키(`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`)를 환경변수로 넣으면 기사 목록을 CSV로 더 많이 모은다. 없어도 웹 검색으로 동작한다.

## 3. 지도는 언제 쓰나 — 문제가 정한다
`analysis-planner`가 가장 먼저 **문제 유형**을 판별하고, 그에 따라 **화면의 주인공**을 정한다. 모든 팀이 이 결정(`docs/03-analysis-plan.md` 0절)을 따른다.

| 결정이 걸린 곳 | 유형 | 화면의 주인공 | 지도 |
|---|---|---|---|
| 어디에? (안양시: 어느 구역이 위험) | 공간 | 위험 지도 | 사용 |
| 누구부터? (복지 사각지대 가구) | 개체 | 우선순위 리스트 | 보조 또는 없음 |
| 언제·얼마나? (응급실 혼잡) | 시계열 | 추세 차트 + 알림 | 없음 |
| 사람들이 뭐라고? (반복 민원) | 텍스트 | 토픽 추이 + 원문 근거 | 없음 |
| 나한테 맞는 건? (청년 정책) | 매칭 | 맞춤 결과 카드 | 없음 |
| 어떻게 이동? (통학 흐름) | 네트워크 | 흐름 지도 | 사용 |

지도가 아니면 PostGIS·지도 라이브러리·격자 분석도 설치하지 않는다. 판단이 마음에 안 들면 GATE B(승인 단계)에서 "지도 빼고 리스트로" 처럼 말하면 된다.

## 4. 진행 중 확인할 파일
`docs/03-analysis-plan.md`(분석 방향) → `docs/04-analysis-report.md`(결과 수치) → `qa/gate-*.md`(검증 판정) → `docs/99-proposal.md`(기획서)

## 5. 하네스 자동 업데이트 관리
- 매시간 변경이 감지되면 `harness-auto` 라벨 PR이 올라온다 → 읽고 머지/닫기만 하면 된다.
- 감시 레포 추가·삭제: `harness/sources.json`
- 봇이 못 고치는 파일(스택 규칙 등)에 대한 제안: `harness/proposals.md`
- 무엇을 배웠는지: `harness/learning-log/`, `harness/CHANGELOG.md`
