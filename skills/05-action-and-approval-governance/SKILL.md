---
name: ax-action-and-approval-governance
description: AI의 추천·행동 계획을 권한·정책·승인·idempotency·감사가 가능한 업무 변경으로 제한한다.
---

# 행동·승인·권한 거버넌스

## 목적

모델이 자유롭게 API나 SQL을 호출하지 못하게 하고, 모든 업무 변경을 타입이 있는 `ActionProposal`과 검증 가능한 gateway를 통과시킨다. 기본값은 거부이며, 사람이 승인하지 않은 고위험 변경은 실행하지 않는다.

## 행동 계약

```yaml
action_id:
action_type:
actor:
target:
target_version:
arguments: {}
evidence_ids: []
preconditions: []
policy_version:
impact_preview:
requires_approval: true
idempotency_key:
expires_at:
```

## 검증 순서

1. 요청자·세션·trace ID와 제안 서명을 확인한다.
2. action type이 allowlist에 있는지 확인한다.
3. 대상 객체와 버전이 현재 상태와 일치하는지 확인한다.
4. 요청자의 조직·역할·객체·필드·행동 권한을 확인한다.
5. 입력 타입·범위·민감 필드·업무 선행 조건을 검증한다.
6. 부작용·외부 통지·금액·영향 범위를 미리 계산한다.
7. 위험 등급에 따라 자동 허용·사람 승인·차단을 결정한다.
8. idempotency key로 중복 실행을 차단한다.
9. 승인 후에만 typed adapter가 System of Record에 write-back한다.
10. 결과·실패·부분 성공·보상 행동을 감사 이벤트로 기록한다.

## 상태 모델

```text
PROPOSED → APPROVAL_PENDING → APPROVED → EXECUTING → COMMITTED
                     │              │          ├→ RETRYABLE_FAILURE → RETRYING
                     │              │          └→ COMPENSATION_REQUIRED
                     ├→ REJECTED    └→ EXPIRED
                     └→ CANCELLED
```

## 완료 게이트

- 모델이 직접 임의 endpoint·SQL·shell을 호출하지 않는다.
- 권한 검사가 UI가 아니라 서버·gateway에서 다시 수행된다.
- 승인 전에 영향 미리보기와 근거가 보인다.
- 재시도·중복·timeout·부분 성공의 상태가 정의되어 있다.
- 모든 실행에 actor, target version, policy version, idempotency key가 남는다.
- 실패 시 수동 fallback과 보상 행동이 있다.
- prompt injection, tool confusion, 권한 상승, 데이터 유출 케이스를 시험했다.

## 팔란티어 매핑

- Ontology Action: 객체 상태 변경의 타입·조건·권한 경계
- Functions/Workflow: 다단계 실행과 외부 시스템 adapter
- AIP Agent tool: gateway가 허용한 도구만 노출
- Object/action permissioning: 사용자 맥락에 따른 재검증

## 관련 자료

- [Palantir OSDK TypeScript](https://github.com/palantir/osdk-ts)
- [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook)
- [DevOps for AI Products](https://github.com/palantir/aip-community-registry/tree/develop/DevOps%20for%20AI%20Products)
- [AX 기술 파이프라인](../../docs/AX-TECHNICAL-PIPELINE.md)

## 중단 조건

권한·대상 버전·근거·영향 범위를 확인할 수 없거나, 승인 서비스·감사 기록이 unavailable이면 실행하지 않고 `BLOCKED` 또는 사람 이관으로 끝낸다.
