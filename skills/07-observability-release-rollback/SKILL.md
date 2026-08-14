---
name: ax-observability-release-rollback
description: 코드·프롬프트·모델·정책·데이터 계약을 함께 릴리스하고 관찰·카나리·롤백 가능한 운영 흐름을 만든다.
---

# 관찰성·배포·롤백

## 목적

AI 시스템의 변경 대상은 코드만이 아니다. prompt, tool description, Ontology 계약, 모델, 정책, 평가 세트, 데이터 projection을 한 릴리스의 증거 단위로 묶고 문제가 생기면 원인을 좁혀 되돌린다.

## 릴리스 절차

1. 변경 manifest에 모든 artifact version, owner, 영향 use case를 기록한다.
2. lint·schema·contract·unit 검사를 실행한다.
3. 고정 평가 세트와 보안·권한·적대적 테스트를 실행한다.
4. immutable artifact를 만들고 staging의 비식별 데이터로 통합 검증한다.
5. shadow/replay에서 실제 요청을 복제하되 외부 write를 차단한다.
6. 제한된 사용자·케이스로 canary를 실행하고 quality·risk·SLO를 확인한다.
7. 통과 시 승격하고, 실패 시 자동 중단·rollback·원인 분석으로 전환한다.
8. 운영 피드백과 incident를 다음 평가 세트·runbook에 반영한다.

## 최소 trace 스키마

```yaml
trace_id:
request_id:
use_case:
actor_hash:
policy_version:
ontology_or_context_version:
data_as_of:
retrieved_evidence_ids: []
model_version:
prompt_version:
tool_calls: []
approval_state:
result_state:
latency_ms:
token_usage:
cost:
error_code:
```

개인정보·비밀·원문 전체를 무조건 로그에 남기지 않는다. 필요한 추적성은 마스킹·참조 ID·보존 정책으로 확보한다.

## 롤백 기준

- 권한 우회·민감정보 노출·허용되지 않은 행동: 즉시 기능 차단
- schema/contract incompatibility: 이전 artifact와 projection으로 복귀
- 평가 하드 게이트 실패: production 승격 금지
- 품질·지연·비용 SLO 초과: canary 중단 후 원인별 rollback
- 데이터 오류: source correction과 영향 projection을 분리해 재처리

## 완료 게이트

- 어떤 버전이 어떤 결과를 만들었는지 trace로 재구성할 수 있다.
- staging·shadow·canary·production의 권한과 데이터 범위가 구분된다.
- prompt·policy·data contract도 코드와 같은 승인 흐름을 탄다.
- rollback을 실행할 사람·명령·대상·복구 후 검증이 문서화되어 있다.
- 대시보드에 품질·권한·행동·지연·비용·채택 지표가 분리되어 있다.

## 팔란티어 매핑

- DevOps for AI Products: 개발·운영 환경 승격과 패키지 관리 패턴
- AIP Observability: 실행 이력·trace·운영 지표
- Apollo: 여러 환경에 승인 artifact를 배포하는 제품 개념
- AIP Evals: 승격 전 품질 게이트

## 관련 자료

- [DevOps for AI Products](https://github.com/palantir/aip-community-registry/tree/develop/DevOps%20for%20AI%20Products)
- [Agents Towards Production](https://github.com/NirDiamant/agents-towards-production)
- [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook)
- [AX 기술 파이프라인](../../docs/AX-TECHNICAL-PIPELINE.md)
