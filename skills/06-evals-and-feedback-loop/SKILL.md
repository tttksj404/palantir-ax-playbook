---
name: ax-evals-and-feedback-loop
description: 실제 업무 케이스와 사용자 피드백을 평가 데이터·회귀 게이트·개선 작업으로 전환한다.
---

# 평가·피드백 루프

## 목적

“답변이 그럴듯하다”를 출시 판정으로 사용하지 않는다. 검색·근거·구조화 출력·행동·권한·운영·업무 가치의 평가를 분리하고, 사용자 수정·거절·실패를 다음 회귀 세트에 편입한다.

## 절차

1. 실제 업무에서 대표·경계·권한·실패·회귀 케이스를 수집한다.
2. 개인정보와 비밀값을 제거하고 입력 시점·정답·허용 행동·근거를 고정한다.
3. 평가 함수를 규칙, 프로그램, LLM grader, SME 판단으로 구분한다.
4. 최소한 schema, evidence, retrieval/context, answer, action, permission, operations 평가를 만든다.
5. 동일한 prompt/model/policy/data version으로 기준 결과를 생성한다.
6. 사용자 피드백을 `wrong_source`, `stale_data`, `missing_context`, `wrong_reasoning`, `wrong_action`, `workflow_mismatch` 등으로 분류한다.
7. 반복되는 피드백을 회귀 케이스로 승격하고 원인·수정·재실행을 연결한다.
8. 하드 게이트 실패 시 평균 점수와 무관하게 출시를 막는다.

## 케이스 형식

```yaml
case_id:
use_case:
input:
as_of:
actor_role:
expected_evidence_ids: []
expected_output:
allowed_actions: []
forbidden_actions: []
graders: []
severity: blocker | high | medium | low
source: representative | boundary | permission | failure | user_feedback
```

## 출시 게이트 예시

| 영역 | 하드 게이트 예시 |
|---|---|
| 출력 | 필수 필드·타입·enum 파싱 성공 |
| 근거 | 근거 ID가 실제 입력과 연결되고 기준 시각이 존재 |
| 권한 | 권한 없는 객체·필드·행동을 노출하거나 실행하지 않음 |
| 행동 | 허용되지 않은 action type·중복 side effect가 0건 |
| 운영 | timeout·오류·비용·P95 기준이 정의된 범위 안에 있음 |
| 사람 | 고위험 케이스가 승인·거절·이관 상태를 남김 |

## 완료 게이트

- 평가 세트에 정상·경계·권한·실패 케이스가 모두 있다.
- 테스트 결과가 prompt/model/policy/data 버전과 함께 저장된다.
- 사용자 피드백이 단순 코멘트로 소멸하지 않고 분류·회귀화된다.
- 개선 전후 비교의 동일성 조건이 기록되어 있다.
- 점수만으로 업무 가치나 생산성 향상을 주장하지 않는다.

## 팔란티어 매핑

- AIP Evals: 테스트 케이스·평가 기준·버전 비교·디버깅
- Feedback Loop with AIP Evals: 사용자 플래그를 평가 케이스로 승격하는 패턴
- AIP Observability: 실행 trace와 운영 신호를 평가 입력으로 연결

## 관련 자료

- [Feedback Loop with AIP Evals](https://github.com/palantir/aip-community-registry/tree/develop/Feedback%20Loop%20with%20AIP%20Evals)
- [Agents Towards Production](https://github.com/NirDiamant/agents-towards-production)
- [평가 루브릭](../../docs/EVALUATION-RUBRIC.md)
- [AX 유스케이스 캔버스](../../docs/AX-USE-CASE-CANVAS.md)

## 주의

평가 케이스가 실제 업무 분포를 대표하지 않거나 정답 라벨의 기준이 불명확하면 결과는 `design-only`입니다. 측정하지 않은 정확도·recall·ROI를 만들어내지 않는다.
