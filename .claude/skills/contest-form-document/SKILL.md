---
name: contest-form-document
description: 공모전 요강 양식대로 보고서·요약서·신청서를 Word로 만들고 통합 제출본과 PDF까지 내는 절차와 재사용 코드(docx-js). 양식 표 재현, 개조식 칸, 아주 작은 출처 줄, 쪽수 확인, 이전 판 정리. 보고서 양식, 요약서, 참가신청서, 제출본, Word 생성, 양식에 맞춰줘 요청 시 반드시 사용.
---
# 공모전 양식 문서 스킬

## 준비
프로젝트 폴더에서:
1. `docs/report/build/`를 만들고 이 스킬의 `scripts/lib.js`, `scripts/render.ps1`을 복사한다.
2. 그 폴더에서 `npm init -y && npm i docx`를 실행한다.

## 절차
1. **양식 먼저 읽기**: 요강과 양식에서 제출 서류·순서, 목차, 칸 이름, 분량, 파일명·제목 규칙을 `docs/00-brief.md`에 옮긴다.
2. **양식 표 재현**: 칸 이름과 순서를 그대로 쓴다. 본문은 표 칸 안에 넣는다. 양식이 표 형식이면 본문도 표 밖으로 나가지 않는다.
3. **문서마다 스크립트 하나**: `application.js`, `report.js`, `summary.js`처럼 나누고 각 파일이 `children`을 내보낸다.
4. **수치는 파일에서 읽는다**: 분석 결과는 `data/processed/`, `frontend/public/data/`의 파일을 코드로 읽어 넣는다. 본문에 손으로 치면 재분석 때 어긋난다.
5. **출처는 한곳에서**: `references.json`(cite, title, source, date, url)에 모으고 `cite()`로 칸 안에 작게 단다.
6. **통합 제출본**: `docMulti([{children, pageNumbers}, ...], 제목)`로 요강의 제출 서류 순서대로 합친다. 문서마다 쪽 번호가 1부터 시작한다.
7. **렌더 확인**: `powershell -ExecutionPolicy Bypass -File render.ps1 <파일.docx>`로 PDF와 쪽수를 얻는다(Windows, Microsoft Word 필요). Word가 없으면 LibreOffice로 PDF를 만들되 쪽 나눔이 다를 수 있다고 알린다. PDF를 이미지로 바꿔 쪽마다 눈으로 본다: 표 넘침, 빈 쪽, 잘린 그림, 범례가 가린 내용.

## lib.js 주요 함수
| 함수 | 쓰임 |
|---|---|
| `formTitle(kind, contest)` | 양식 머리 상자 (공모전명 필수) |
| `formTable(rows, pct, o)` | 칸 합치기가 되는 양식 표. 칸은 문자열 또는 `{t, span, head, sub, band}`, 본문 칸은 `{body: [...], span, cont, more}` |
| `formBoxes(boxes)` | 요약서처럼 ▢ 칸을 한 표로 묶기 |
| `sq`, `P`, `note`, `table`, `figure` | □ 소제목, 문단, 작은 주석, 일반 표, 그림+캡션 |
| `cite(refs, keys)` | 아주 작은 출처 줄 |
| `doc`, `docMulti`, `save` | 단일 문서, 통합본, 저장 |

## 제출 전
- [ ] `public-data-proposal` 스킬의 제출 전 체크 통과, reality-checker 제출 점검 통과
- [ ] 제출 폴더에 이전 판 Word·PDF가 남아 있지 않고, Word와 PDF가 같은 판이다 (사용자 확인 후 정리)
- [ ] `[작성자 기입]` 칸을 사용자에게 알렸다
- [ ] 메일 제목·파일명이 요강 규칙과 같다. 제출은 사용자가 직접 한다
