---
description: 기획서/주제/공모전 요강을 받아 7단계 파이프라인 전체를 실행한다
argument-hint: <기획서 파일 경로 | 주제 | 공모전 요강 URL>
---
입력: $ARGUMENTS

CLAUDE.md의 파이프라인을 실행한다. 너는 오케스트레이터다 — 직접 구현하지 말고 서브에이전트에 위임하고, 산출물 파일로 진행을 판단한다.

1. 입력이 파일이면 읽고, URL이면 WebFetch로 요강을 읽는다. `docs/00-brief.md`에 (목표 · 제약: 지역/데이터/부문/마감 · 심사기준 · 사용자 관심사) 정리.
2. Phase 1:
   - 문제가 정해지지 않았으면 `problem-hunter` 단계 1로 후보 5~7개를 만들고 **GATE 0: 사용자 선택을 받을 때까지 멈춘다.**
   - 기획서에 문제가 이미 있으면 problem-hunter는 뉴스 신호·근거 수치 검증만 한다 (반복 보도가 약하면 사용자에게 알리고 대안 후보 2~3개를 함께 제시).
   - 선택 후 `problem-hunter` 단계 2 → `data-scout`.
3. GATE A: `reality-checker`. FAIL이면 해당 에이전트에 수정 지시 후 재검사(최대 2회).
4. Phase 2: `analysis-planner` → `docs/03-analysis-plan.md`. **여기서 멈추고 사용자에게 분석 질문·방법 요약(5줄 이내)을 보여주고 승인받는다.**
5. 승인 후 Phase 3~7을 CLAUDE.md 순서대로 진행. `∥` 표시 단계는 병렬로 서브에이전트를 띄운다.
6. 각 Phase 종료 시 한 줄 진행 보고: `[Phase N 완료] 산출물: ... / 다음: ...`
7. 마지막에 `/retro` 실행을 제안한다.
