---
name: ax-data-contract-and-pipeline
description: 원천 데이터와 이벤트를 계약·품질·계보·재처리 가능한 파이프라인으로 연결한다.
---

# 데이터 계약·파이프라인

## 목적

AI가 최신이 아닌 데이터, 중복 이벤트, 권한 없는 필드, 재현할 수 없는 파생 결과를 근거로 업무를 변경하지 않도록 데이터 평면을 먼저 고정한다.

## 입력

- Ontology 객체·필드·상태 계약
- 원천 시스템과 추출 방식(batch, CDC, stream, webhook)
- 신선도·완전성·정확성·중복 허용 기준
- 개인정보·민감정보 분류와 접근 정책
- 재처리·backfill·보존·삭제 요구사항

## 절차

1. 원천별 소유자, schema version, 데이터 기준 시각, SLA를 등록한다.
2. raw 입력을 보존하고 curated 변환과 업무 객체 projection을 분리한다.
3. 필수 필드·타입·범위·참조 무결성·중복·신선도 검사를 계약으로 만든다.
4. 이벤트는 event id, producer, occurred_at, observed_at, schema version을 갖게 한다.
5. 소비자는 idempotency key와 처리 상태를 기록하고 재시도해도 부작용이 없게 한다.
6. 실패 레코드는 quarantine으로 보내고 원천·규칙·오류 코드를 남긴다.
7. replay/backfill이 가능한 입력 범위와 영향받는 projection을 명시한다.
8. 계약·파이프라인·projection 변경은 샘플 데이터와 회귀 검증 후 승격한다.

## 산출물

```yaml
dataset_or_event:
owner:
source_of_truth:
schema_version:
data_as_of:
freshness_sla:
quality_rules: []
lineage:
  upstream: []
  downstream: []
delivery_mode: batch | cdc | stream | webhook
idempotency_key:
replay_window:
backfill_plan:
quarantine:
privacy_class:
publish_gate:
```

## 완료 게이트

- 품질 실패가 조용히 통과하지 않고 격리·알림으로 이어진다.
- 같은 입력을 다시 처리해도 중복 write가 발생하지 않는다.
- 특정 시점의 입력과 파생 결과를 재현할 수 있다.
- `data_as_of`, source, schema version이 AI 맥락에 전달된다.
- 개인정보·민감 필드가 허용된 소비자에게만 노출된다.
- contract 변경 시 downstream 영향과 rollback/backfill 절차가 있다.

데이터 품질·신선도·권한 증거가 없으면 추천·행동 단계로 데이터를 승격하지 않는다.

## 팔란티어 매핑

- Foundry Data Operations: 원천 연결·변환·품질·계보
- Push-Based Events: 외부 webhook과 이벤트 입력
- Ontology projection: 정제 데이터에서 업무 객체·상태를 제공하는 계층
- Platform SDK: 자동화·관리·데이터 API 연동 경계

## 관련 자료

- [Data Engineering Agent Skills](https://github.com/vaquarkhan/data-engineering-agent-skills)
- [Push-Based Events](https://github.com/palantir/aip-community-registry/tree/develop/Push-Based%20Events)
- [Foundry Platform Python SDK](https://github.com/palantir/foundry-platform-python)
- [AX 기술 파이프라인](../../docs/AX-TECHNICAL-PIPELINE.md)
