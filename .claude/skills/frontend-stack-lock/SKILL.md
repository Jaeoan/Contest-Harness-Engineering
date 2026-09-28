---
name: frontend-stack-lock
description: 프론트엔드 고정 스택(TypeScript + React + Tailwind CSS) 규칙, 폴더 구조, 지도·차트 라이브러리 선택, anti-slop 디자인 규칙, 금지 목록. 프론트엔드 코드를 만들거나 고치거나 패키지를 추가할 때 반드시 사용.
---
# 프론트엔드 스택 고정 (자동 수정 금지 파일)

## 고정 (변경 불가)
- **TypeScript** (`strict: true`, `noUncheckedIndexedAccess: true`)
- **React** (함수 컴포넌트 + hooks)
- **Tailwind CSS** (v4, `@theme`로 토큰 연결)

## 기본값 (합리적 이유가 있으면 변경 가능, 이유를 docs에 기록)
- 빌드: Vite · 라우팅: React Router · 서버 상태: TanStack Query · 폼: react-hook-form + zod
- 지도(**분석 계획에서 지도 사용일 때만 설치**): MapLibre GL(`react-map-gl/maplibre`) + V-World/OSM 타일, 또는 Kakao Maps SDK(`react-kakao-maps-sdk`) — 국내 주소 검색이 핵심이면 Kakao
- 차트: Recharts (간단), visx/D3 (커스텀)
- 아이콘: lucide-react · API 타입: openapi-typescript + openapi-fetch
- 테스트: Vitest + Testing Library, E2E는 Playwright

## 금지
Vue/Angular/Svelte/Solid, styled-components/emotion/CSS Modules 남용, Bootstrap/MUI/Chakra/Ant Design, jQuery, `.js/.jsx` 소스, 인라인 hex 색상, `any` 남발.
(`.claude/hooks/guard-stack.sh`가 package.json과 파일 확장자를 검사해 차단한다.)

## 폴더 구조
```
frontend/src/
  app/            # 라우터, 프로바이더
  pages/          # 화면 단위
  features/<도메인>/  # components, hooks, api (기능별)
  components/ui/  # 공용 원자 컴포넌트
  api/            # schema.d.ts(생성), client.ts
  styles/         # index.css (@import "tailwindcss"; @theme ← design/tokens.css)
```

## 토큰 연결 예시 (index.css)
```css
@import "tailwindcss";
@theme {
  --color-surface: var(--surface);
  --color-ink: var(--ink);
  --color-risk-1: var(--risk-1);
  --font-sans: "Pretendard Variable", Pretendard, system-ui, sans-serif;
}
```

## Anti-slop 체크
- 방향 1개를 정하고(design/brief.md) 끝까지 유지. 보라 그라디언트·같은 크기 카드 4열·장식용 이모지 금지.
- 한국어: `word-break: keep-all`, 숫자는 `tabular-nums`, 날짜 `YYYY.MM.DD`.
- 위험도 색: 색각이상 안전 순차 팔레트 + 텍스트 라벨 병기.
- 반응형: 390px 먼저. (지도 화면이 있을 때) 바텀시트 패턴.
