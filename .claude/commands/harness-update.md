---
description: 감시 소스의 최신 변경을 학습해 하네스를 개선한다 (스케줄 실행용)
---
1. `harness/pending_changes.json`이 없으면 `python3 scripts/check_sources.py`를 실행한다. 출력이 `NO_CHANGES`/`BASELINE`/`RATE_LIMITED`면 `harness/learning-log/`에 한 줄 기록하고 종료한다.
2. 변경이 있으면 `harness-curator` 서브에이전트에 `harness/pending_changes.json`을 넘겨 처리한다.
3. `python3 scripts/validate_harness.py` 통과를 확인한다. 실패하면 수정을 되돌린다(`git checkout -- <file>`).
4. (수동 실행일 때만) `python3 scripts/check_sources.py --commit-state` 로 상태를 확정한다. 스케줄 스크립트는 이 단계를 직접 한다.
5. 변경 요약(파일 · 이유 · 출처)을 5줄 이내로 출력한다. 이 출력이 PR 본문이 된다.
