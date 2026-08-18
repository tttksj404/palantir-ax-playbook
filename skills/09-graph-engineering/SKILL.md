---
name: ax-graph-engineering
description: AX 에이전트의 실행 흐름을 노드·엣지·상태·분기·병렬·승인·복구가 있는 검증 가능한 그래프로 설계한다.
---

# 그래프 엔지니어링

## 목적

에이전트가 “무엇을 할까?”를 매번 모델의 암묵적 판단에 맡기지 않고, **어느 노드가 다음에 실행되며 어떤 상태와 근거가 이동하는지**를 검증 가능한 계약으로 만든다.

이 스킬에서 그래프는 실행·제어 그래프를 뜻한다. 업무 객체와 관계를 정의하는 Ontology/지식 그래프, 데이터 계보 그래프, GNN/Graph ML과 혼동하지 않는다.

## 적용 순서

### 0. 먼저 trace를 관찰한다

그래프를 먼저 크게 그리지 않는다.

1. 대표 업무 케이스를 최소 권한·최소 도구 harness에서 실행한다.
2. `model_call`, `tool_call`, `observation`, `decision`, `human_intervention`을 기록한다.
3. 반복되는 경계·분기·병렬 후보·실패·승인 지점을 표시한다.
4. 실제 trace에서 반복되는 경로만 node와 edge로 승격한다.
5. 아직 불확실한 계획은 모델의 동적 계획으로 남기고, 확정된 제어 흐름과 구분한다.

### 1. 그래프 도입 여부를 판정한다

다음 중 두 개 이상이 있으면 그래프 후보로 분류한다.

- 전문 역할 또는 agent가 정해진 순서로 실행된다.
- 서로 독립된 조사·검증을 병렬로 수행할 수 있다.
- 상태·정책·근거에 따라 경로가 갈린다.
- 사람 승인, 외부 이벤트, timeout 후 resume이 필요하다.
- 실패를 특정 checkpoint부터 재개해야 한다.
- retry와 escalation이 서로 다른 경로다.

단순 단일 에이전트·소수의 읽기 도구·계속 새 계획을 발명하는 탐색 작업이면 먼저 bounded loop를 설계한다. 그래프가 실제 복잡도를 낮추는지 trace로 확인하기 전에는 formalization을 보류한다.

### 2. 노드 경계를 정한다

각 노드는 아래 타입 중 하나로 명시한다.

| `node_type` | 용도 | 기본 side effect |
|---|---|---|
| `deterministic` | schema·권한·품질·계산·멱등성 검사 | read |
| `agent` | 제한된 업무 판단·도구 선택 | read 또는 draft |
| `reviewer` | 원 작업과 분리된 독립 검증 | read |
| `router` | 상태·정책·근거에 따른 경로 선택 | read |
| `approval` | 사람의 승인·거절·수정·이관 | external decision |
| `event` | webhook·스케줄·새 데이터로 실행 시작 | read |
| `recovery` | 보상·재처리·수동 이관 | 명시된 범위 |
| `terminal` | 성공·실패·취소·에스컬레이션 종료 | none |

각 노드에 다음을 기록한다.

```yaml
node:
  node_id:
  node_type:
  owner:
  input_schema: {}
  output_schema: {}
  reads: []
  writes: []
  allowed_tools: []
  side_effect: read | draft | write | external
  evidence_required: []
  timeout_seconds:
  max_attempts:
  on_error: retry | route | escalate | fail
```

LLM 호출 자체를 node로 만들더라도 결과를 자유 텍스트로 다음 노드에 넘기지 않는다. 구조화 출력, 근거 ID, 기준 시각, 거절·불확실성 상태를 포함한다.

### 3. 엣지와 조건을 정의한다

```yaml
edge:
  edge_id:
  from:
  to:
  edge_type: success | failure | retry | escalate | parallel | join | interrupt | compensate
  predicate:
  required_evidence: []
  max_traversals:
  state_mapping: {}
```

규칙:

- `success`는 schema·필수 evidence·권한 검사를 모두 통과할 때만 사용한다.
- `retry`는 매번 새 evidence를 얻을 수 있을 때만 허용하고 `max_traversals`를 둔다.
- `escalate`는 max attempt, 권한 부족, 정책 위반, 불확실성, irrecoverable error를 수용한다.
- `parallel`은 branch 간 write 충돌이 없거나 명시된 merge 규칙이 있을 때만 사용한다.
- `join`은 필수 branch의 종료·결과·오류 처리를 확인한 뒤 실행한다.
- `interrupt`와 `resume`은 pending 상태, actor, 만료 시각, 승인·거절 사유를 저장한다.
- 외부 변경 이후에는 중복을 막을 idempotency key와 compensate/수동복구 경로를 갖는다.

### 4. 공유 상태를 최소화하고 버전으로 묶는다

모든 원문 대화나 고객 데이터를 모든 노드에 복사하지 않는다. node가 필요한 상태만 전달하고 나머지는 접근 통제가 있는 참조로 둔다.

```yaml
graph_run:
  graph_id:
  graph_version:
  run_id:
  actor_id:
  state: running | waiting_approval | succeeded | failed | escalated | cancelled
  data_as_of:
  policy_version:
  budget:
    max_total_attempts:
    max_total_seconds:
    max_external_writes:
  checkpoint:
    last_completed_node:
    state_ref:
  evidence_refs: []

node_run:
  node_id:
  node_run_id:
  attempt:
  status: running | succeeded | failed | waiting | skipped
  input_ref:
  output_ref:
  evidence_refs: []
  tool_call_refs: []
```

`graph_version`, `prompt_version`, `model_version`, `policy_version`, `data_version`을 같은 trace에서 조회할 수 있어야 replay·비교·rollback이 가능하다.

### 5. loop를 graph 안에 배치한다

그래프는 흐름을, loop는 반복을 담당한다. 다음 네 loop를 필요할 때 분리한다.

| loop | 그래프에 넣을 위치 | 종료 증거 |
|---|---|---|
| Agent loop | 한 `agent` node 내부 | 실제 tool observation 또는 결정적 결과 |
| Verification loop | `reviewer → repair → reviewer` 사이 | schema·근거·테스트·SME 결과 |
| Event loop | `event` node에서 새 run 또는 resume | event ID·dedup·freshness |
| Improvement loop | 운영 trace에서 새 graph/prompt/policy 후보로 | 동일 케이스 전후 평가 |

모든 반복은 `goal`, `feedback`, `fresh_evidence`, `attempt`, `budget`, `stop_rule`을 기록한다. 모델의 “완료” 선언은 단독 종료 조건으로 쓰지 않는다.

### 6. 독립 reviewer와 사람 gate를 분리한다

- maker가 생성한 결과를 같은 context에서 자기 자신이 승인하지 않도록 한다.
- reviewer는 최소한 원 작업의 숨은 chain-of-thought가 아니라 결과·근거·계약·diff만 받는다.
- 결정적 검사로 대체할 수 있는 것은 먼저 코드·schema·권한·테스트로 검사한다.
- 고위험 write는 reviewer 통과만으로 실행하지 않고 사람 승인 또는 조직이 승인한 통제를 추가한다.
- 승인·거절·수정은 graph state에 남기고, 사람의 identity·시각·사유를 audit record로 보존한다.

### 7. Palantir AX 경계에 연결한다

제품 내부 구현을 단정하지 않고 공개 개념을 다음처럼 대응시킨다.

| 그래프 구성 | AX 연결점 |
|---|---|
| 상태·context | Ontology 객체·링크·속성·업무 상태 |
| read/agent node | Foundry 데이터·Ontology 조회, AIP Agent/Logic 등 |
| router/condition | 업무 상태·정책·평가 evidence 기반 분기 |
| action node | Action type·Workflow·허용된 write-back |
| approval/interrupt | 사람 승인·거절·이관·resume |
| reviewer/evidence | AIP Evals·실행 trace·업무 검토 |
| checkpoint/release | Observability·DevOps·Apollo 방향의 버전·운영 관리 |

실제 제품명·API·권한·베타 상태는 계정의 공식 문서와 Developer Console에서 다시 확인한다. 이 스킬의 결과는 계정 연결 전 `design-only`다.

## 산출물 계약

```yaml
skill: ax-graph-engineering
version: 1.0.0
owner:
use_case:
inputs:
  - trace_refs: []
  - object_and_data_contracts: []
  - policy_and_permission_contracts: []
decisions:
  graph_required: true | false | needs_more_trace
  rationale:
  topology:
    nodes: []
    edges: []
    joins: []
    checkpoints: []
  loop_policy:
    max_attempts:
    fresh_evidence_required: true
    escalation_path:
verification:
  checks: []
  evidence: []
  status: PASS | NEEDS_FIX | BLOCKED
failure_modes: []
next_action:
```

## 완료 게이트

- [ ] 그래프 도입 결정이 실제 trace 또는 `needs_more_trace` 근거에 연결되어 있다.
- [ ] 모든 node에 타입·owner·입출력 schema·tool·side effect가 있다.
- [ ] 모든 edge에 타입·predicate·max traversal·상태 매핑이 있다.
- [ ] parallel branch의 독립성·join·merge 규칙이 검증되었다.
- [ ] 모든 cycle에 fresh evidence·attempt·budget·stop·escalation이 있다.
- [ ] reviewer가 maker와 별도 context·trace를 사용한다.
- [ ] approval·resume·checkpoint·idempotency·compensation이 필요한 위치에 있다.
- [ ] graph/prompt/model/policy/data 버전을 replay할 수 있다.
- [ ] 실제 계정·대체 실행 환경에서 돌리지 않았다면 `design-only`로 표시했다.

## 중단·이관 조건

다음이면 그래프 설계를 `NEEDS_FIX` 또는 `BLOCKED`로 남기고 write-back으로 진행하지 않는다.

- 실제 업무 trace 없이 상상한 노드만 늘어나고 있다.
- branch가 공유 상태를 덮어쓰지만 merge 규칙이 없다.
- retry가 새 evidence 없이 동일 호출을 반복한다.
- reviewer가 maker와 같은 context·권한으로만 동작한다.
- actor/object/action 권한을 실행 시 재검증할 수 없다.
- 중단 후 재개 지점과 외부 side effect 중복 방지 수단이 없다.
- graph가 해결하려는 문제가 harness 또는 loop 문제인데 graph 복잡도만 증가하고 있다.

## 관련 자료

- [@0xwhrrari 원문 X 게시물](https://x.com/0xwhrrari/status/2086784668003598356?s=46)
- [Agentic Engineering 정리](https://www.coldmountain.ai/wiki/tools/agentic-engineering)
- [Harness·Loop·Graph 비교](https://todayforai.com/en/guides/20260726-guide-three-agent-engineering-architectures)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Temporal](https://github.com/temporalio/temporal)
- [NetworkX](https://github.com/networkx/networkx)
- [AX 기술 파이프라인](../../docs/AX-TECHNICAL-PIPELINE.md)
- [AX 그래프 엔지니어링 플레이북](../../docs/GRAPH-ENGINEERING-PLAYBOOK.md)

## 주의

그래프는 복잡도를 없애지 않고 밖으로 드러낸다. 노드 수·branch 수·retry 수·reviewer 수가 늘면 비용·지연·운영 부담도 늘어난다. 따라서 가장 작은 그래프로 시작하고, 실제 실패 trace가 증명한 경우에만 분기·병렬·자동 write를 추가한다.
