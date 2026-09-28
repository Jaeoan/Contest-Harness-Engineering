---
name: spring-api-conventions
description: Spring Boot 3.x + Java 21 백엔드 규약 — 기능별 패키지, record DTO, ProblemDetail 에러, springdoc OpenAPI 계약 우선, PostGIS/Hibernate Spatial, Flyway, Testcontainers, 분석 결과 적재. 백엔드·API·Spring·JPA·DB·PostGIS 작업 시 반드시 사용.
---
# Spring API 규약

## 스택
Spring Boot 3.x · Java 21 · Gradle(Kotlin DSL) · Spring Web · Spring Data JPA · PostgreSQL (+ 공간 문제면 PostGIS·Hibernate Spatial, RAG면 pgvector) · Flyway · springdoc-openapi · Testcontainers · Actuator
(Boot 4 전환 여부는 harness-curator가 생태계 성숙도를 보고 `harness/proposals.md`에 제안만 한다.)

## 패키지 (기능별)
```
com.<org>.<app>/
  risk/        RiskController, RiskService, RiskGridRepository, dto/, domain/
  zone/
  facility/
  common/      error/(GlobalExceptionHandler), config/, util/
```

## 규칙
- 계약 우선: `api/openapi.yaml`이 진실. 구현 후 `/v3/api-docs`와 diff 0.
- DTO = `record`. 엔티티를 응답으로 노출 금지.
- 에러 = `ProblemDetail`(RFC 9457), `@RestControllerAdvice` 한 곳.
- 검증 = `@Valid` + Jakarta Validation. 좌표 범위·페이지 크기 상한 검증.
- (공간 유형일 때) 공간 조회 예시:
```java
@Query(value = """
  SELECT g.* FROM risk_grid g
  WHERE ST_Intersects(g.geom, ST_MakeEnvelope(:minLon, :minLat, :maxLon, :maxLat, 4326))
  AND g.model_version = :version
  """, nativeQuery = true)
List<RiskGrid> findInBbox(double minLon, double minLat, double maxLon, double maxLat, String version);
```
- 지도 bbox 조회는 결과 상한(예: 5,000 격자) + GeoJSON 응답.
- 분석 결과 적재: `data/export/*.parquet|csv` → 배치(Spring Batch) 또는 Python에서 직접 COPY. `model_version`으로 교체, 이전 버전 보존.
- 테스트: Testcontainers로 실제 DB 검증 (공간이면 `postgis/postgis` 이미지).

## 참고 레포 (변경 감시 대상)
piomin/claude-ai-spring-boot (Claude Code용 Spring 템플릿: agents·skills 구성), rrezartprebreza/spring-boot-skills (REST·JPA 규약 스킬, Boot 3/4 분리).
