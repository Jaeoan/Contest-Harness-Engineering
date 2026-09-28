---
description: 뉴스·민원·통계를 근거로 Well-known problem 후보 5~7개를 제시하고 사용자 선택을 받는다
argument-hint: <관심 분야 / 지역 / 공모전 요강 URL>
---
조건: $ARGUMENTS

1. `problem-hunter` 단계 1을 실행한다 (`news-signal-scan` 스킬 필수). 결과: `docs/01-problem-candidates.md`.
2. 사용자에게 보여줄 것:
   - 요약 표: 번호 · 문제 · 분석 유형 · 뉴스 추이 · 데이터 확인 여부 · 점수
   - 후보별 3줄: 누가 겪나 / 대표 기사 1건(매체·날짜·제목) / 공공데이터로 할 수 있는 것
   - (선택) 추천 1개와 이유 한 줄
3. **여기서 멈추고** "몇 번으로 갈까요? 섞거나 다른 방향으로 다시 찾을 수도 있어요."라고 묻는다.
4. 사용자가 고르면 `problem-hunter` 단계 2(심화) → `data-scout` 순으로 진행하고, 끝나면 `/analyze-plan`을 제안한다.
