# 온프레미스 Agentic MAS 구현 레퍼런스

> 상태: 실행 가능한 학습·설계 레퍼런스
> 범위: 특정 산업을 전제하지 않는 규제·문서·업무 시스템 자동화
> 비범위: 이 저장소가 실제 고객 데이터, GPU 서버, 업무 원장 또는 외부 A2A 서비스를 이미 운영한다는 뜻은 아니다.

이 문서는 “에이전트를 만든다”는 말을 실제 시스템 경계와 코드로 번역한다. 목표는 모델에게 자유로운 권한을 주는 것이 아니라, 업무 근거를 읽고 구조화된 제안을 만들게 한 뒤 정책·승인·멱등성·감사 경계를 통과한 경우에만 좁은 업무 행동을 수행하게 만드는 것이다.

팔란티어의 Ontology, AIP, Actions, Evals, Observability 패턴은 여기서 벤더 중립적인 구현 언어로 바꿔 쓴다. 즉, 팔란티어 제품을 복제하거나 연동한 예제가 아니라, 같은 문제를 온프레미스 Python, LangGraph, 로컬 모델 서버, ETL, 데이터 계약으로 구현하는 출발점이다.

## 1. 채용 공고의 업무를 실제 컴포넌트로 바꾸기

| 요구 업무 | 실제 구현물 | 이 저장소의 출발 코드 | 운영에서 추가할 것 |
|---|---|---|---|
| Multi-Agent System과 루프 엔지니어링 | 명시적인 그래프 노드와 상태 전이 | workflow.py | 도메인별 agent, 장기 작업 큐, timeout·재시도 정책 |
| A2A | Agent Card와 별도 원격 서비스 경계 | contracts/agent-card.example.json | 실제 A2A SDK 서버, 인증, 서비스 디스커버리 |
| 에이전트 메모리 | 테넌트 필터가 강제되는 운영 메모리 | memory.py | ACL 연동, 보존 기간, 검색/벡터 인덱스 |
| 자가 개선 | 피드백을 릴리스 후보로 만들되 사람 승인 전 자동 승격 금지 | improvement.py | 평가 세트, SME 라벨링, canary·rollback |
| SLLM/VLM 온프레미스 추론 | 내부 OpenAI 호환 모델 게이트웨이 호출 계약 | local_model.py | vLLM 서버, TLS/mTLS, 모델·GPU 호환성 검증 |
| Document Layout Analysis | 레이아웃 결과를 버전·신뢰도와 함께 ETL 이벤트로 투영 | layout.py | 실제 layout/VLM 서비스, OCR, 표 구조 평가 |
| RAG·규제 지식 | 근거 ID, 출처, 기준 시각을 가진 Evidence 계약 | contracts.py, etl.py | 권한 필터 검색, chunk/index, 지식 그래프 |
| ETL | JSONL 검증·격리·재처리 가능한 최소 경계 | etl.py | CDC/배치 오케스트레이터, raw/curated 저장소, 데이터 계보 |
| 업무 행동 | 정책 통과 후 한 곳에서만 side effect를 수행 | ActionGateway, workflow.py | System of Record adapter, 승인 UI, 보상 행동 |

가장 중요한 설계 선택은 다음 하나다.

~~~text
모델은 "후보 제안"까지만 만든다.
API 인증 adapter는 tenant ID와 actor ID를 client JSON이 아니라 인증된 principal에서 설정한다. 호출자는 근거 본문·위험도·승인 여부를 결정하지 않는다. 인증된 서버 측 `EvidenceResolver`가 tenant·case·ACL·source version/hash·freshness를 확인한 `VerifiedEvidence`만 전달하고, `PolicyAuthority`가 위험 등급을 소유한다. 승인 시스템에서 검증한 승인 ID·승인자·tenant·case·request·action·policy version·proposal digest·승인 시각·만료·revocation을 함께 확인한다.

메모리는 `(tenant_id, memory_id)` 복합키로 저장하고, action receipt의 idempotency key에도 tenant를 포함한다. 같은 key를 재시도할 때는 proposal digest가 같을 때만 이전 receipt를 재사용하고, 다르면 conflict로 차단한다. 기존에 `memory_id` 단독 키를 썼다면 자동으로 같은 테이블을 재사용하지 말고, 접근 통제와 rollback을 검증한 별도 데이터 마이그레이션으로 전환한다.
`AuthorizedAction`만 받는 Action Gateway가 실제 업무 시스템을 변경한다.
~~~

따라서 모델 교체, 프롬프트 변경, 검색 품질 저하가 곧바로 임의의 SQL 실행이나 업무 원장 변경으로 이어지지 않는다.

## 2. 권장 아키텍처

~~~mermaid
flowchart LR
    S[문서·업무 DB·이벤트] --> L[OCR / Layout Analysis]
    S --> E[ETL Ingestion]
    L --> E
    E --> Q[검증·격리·재처리]
    Q --> O[업무 Ontology / Knowledge Graph]
    O --> R[권한 필터 RAG / Context Builder]
    R --> G[LangGraph MAS]
    M[온프레미스 SLLM / VLM] --> G
    G --> P[정책·위험·승인 Gate]
    P -->|허용| A[Action Gateway]
    P -->|차단·대기| H[결과·감사 로그]
    A --> W[System of Record / Task System]
    W --> H
    H --> MEM[테넌트 격리 메모리]
    H --> EV[평가·피드백·릴리스 Gate]
    EV --> G
~~~

이 구조는 세 평면을 분리한다.

- 데이터·의미 평면: 원천, OCR/Layout, ETL, 업무 객체, 문서 인덱스, 지식 그래프
- 실행 평면: LangGraph workflow, 로컬 SLLM/VLM, 검색, tool 선택
- 통제 평면: 권한, 정책, 사람 승인, idempotency, 로그, 평가, 배포 승인

이 분리는 기존 [AX 기술 파이프라인·시스템 설계](AX-TECHNICAL-PIPELINE.md)의 데이터 → 맥락 → 모델 → 행동 → 평가 → 배포 흐름을 구현 단위로 나눈 것이다.

## 3. 지금 바로 실행하는 최소 수직 슬라이스

현재 예제는 클라우드 모델 API나 실제 업무 시스템 없이도 실행된다. 기본 실행은 서버 측 정책이 고위험으로 분류한 요청을 만들고, 검증된 승인 기록이 없으므로 반드시 pending_approval으로 끝난다. 즉, 안전 경로가 정상이라는 것을 먼저 확인하는 예제다.

### 3.1 Windows PowerShell

~~~powershell
# clone한 저장소 루트에서 실행한다.
Set-Location .\examples\onprem-agentic-mas

uv sync --locked --all-extras --dev
uv run python -m onprem_agentic_mas
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
~~~

기대하는 기본 출력은 아래 성질을 가진 JSON이다.

~~~json
{
  "status": "pending_approval",
  "reason": "human_approval_required",
  "action_receipt": null
}
~~~

샘플 ETL 입력도 같은 환경에서 실행할 수 있다.

~~~powershell
uv run python -c "from pathlib import Path; from onprem_agentic_mas.etl import ingest_jsonl; result = ingest_jsonl(Path('data/sample-events.jsonl')); print(len(result.accepted), len(result.quarantined))"
~~~

1 0은 한 건이 수용되고 격리 건이 없다는 뜻이다. 원천 데이터가 손상되었거나 스키마가 다르면 배치 전체를 멈추지 않고, 원문 대신 해시와 사유를 quarantine 결과에 남긴다.

### 3.2 현재 코드가 보장하는 안전 경로

| 경로 | 코드의 동작 | 테스트 |
|---|---|---|
| 근거 없음 | blocked, Action Gateway 호출 없음 | test_workflow.py |
| 확인되지 않은 근거 ID | 저위험 policy여도 blocked, 외부 쓰기 없음 | test_workflow.py |
| 고위험·무승인 | pending_approval, 외부 쓰기 없음 | test_workflow.py, test_cli.py |
| 승인 범위 변경·만료·폐기 | request/evidence digest가 다르거나 만료·폐기되면 pending_approval | test_workflow.py |
| 승인된 요청 재시도 | 동일 idempotency key로 한 번만 commit | test_workflow.py |
| 멱등 key 충돌 | 다른 proposal digest로 같은 key를 쓰면 conflict | test_workflow.py |
| 타 테넌트 메모리 | 검색 결과에서 제외 | test_memory.py |
| ETL drift·중복 ID | 수용 데이터는 유지, schema drift·중복은 quarantine | test_etl.py |
| Layout 모델 결과 | bbox 검증 후 문서·블록·모델 provenance가 이벤트에 보존됨 | test_layout.py |
| 개선 후보 | immutable evaluation artifact와 release approval 없이는 promotion 차단 | test_improvement.py |

InMemoryActionGateway는 테스트용이다. 실제 업무 시스템 연결은 같은 인터페이스를 구현하는 별도 adapter에서만 한다. 모델 코드는 업무 DB, ERP, CRM, 메일, 자유 SQL에 직접 연결하지 않는다.

예제 Action Gateway도 runtime에서 `AuthorizedAction` 이외의 객체를 거부한다. 운영 adapter는 여기에 더해 정책 서비스가 발급한 authorization capsule의 서명 또는 서버 간 인증을 검증해야 하며, 단순한 Python 타입만으로 외부 호출을 신뢰해서는 안 된다.

## 4. LangGraph MAS를 어떻게 실제 업무 흐름으로 확장하는가

이 저장소의 build_system 함수는 아래 고정 순서를 가진다.

~~~text
START
  → retrieve_memory
  → resolve_evidence
  → evidence_agent
  → policy_agent
  → allowed 인 경우 execute
  → record_memory
  → END
~~~

각 노드의 책임은 일부러 좁다.

1. retrieve_memory: 요청의 tenant ID를 필수 필터로 사용한다. 유사한 과거 결과를 가져오되, 다른 테넌트 결과를 넘기지 않는다.
2. resolve_evidence: 요청의 evidence ID를 source-of-record에서 다시 찾아 tenant·case·ACL·source version/hash·freshness가 맞는 `VerifiedEvidence`만 반환한다. 하나라도 누락되면 차단한다.
3. evidence_agent: `ProposalGenerator`가 검증된 근거만 입력으로 받아 `ProposalCandidate`를 만들고, 그 후보·요청·근거의 canonical digest를 가진 `ActionProposal`으로 변환한다. 이 단계는 로컬 모델로 교체할 수 있지만, 여전히 proposal까지만 허용한다.
4. policy_agent: 서버 측 `PolicyAuthority`가 위험 등급과 검증된 승인 기록을 결정론적으로 판정한다. 승인 기록은 tenant·case·request·action·policy version·proposal digest·승인 시각·만료·revocation 모두와 맞지 않으면 허용하지 않는다.
5. execute: 허용 결과에서 생성된 `AuthorizedAction`만 Action Gateway로 넘긴다.
6. record_memory: 모델의 사고 과정이 아니라 요청 요약, 결과 상태, 시간만 기록한다.

새로운 agent를 추가할 때는 “agent 수를 늘리는 것”보다 다음 질문을 먼저 답한다.

| 추가하려는 역할 | 입력 계약 | 출력 계약 | 금지 권한 | 실패 시 |
|---|---|---|---|---|
| 문서 근거 agent | 권한 있는 chunk·metadata | VerifiedEvidence 배열 | 업무 write | 근거 부족으로 차단 |
| 규칙 해석 agent | 규정 조항·기준 시각 | 구조화된 rule candidate | 최종 판정·예외 승인 | SME 이관 |
| 계획 agent | case·evidence·policy hint | ActionProposal 후보 | 직접 tool 호출 | proposal 폐기 |
| 검토 agent | proposal·영향 미리보기 | approve/reject/revise | 정책 우회 | 승인 대기 |
| 실행 agent | AuthorizedAction | action receipt | 임의 endpoint | 보상/수동 복구 |

여러 agent가 서로 자유롭게 대화하는 구조는 감사와 비용을 급격히 어렵게 만든다. 우선은 LangGraph 하나가 orchestration owner가 되고, 각 node의 상태·입력·출력을 명시하는 방식이 더 안전하다.

## 5. 로컬 SLLM을 vLLM과 연결하는 방법

예제의 local_model.py는 내부 OpenAI 호환 endpoint의 chat/completions만 호출한다. 이는 vLLM 같은 온프레미스 서버를 붙일 때, 클라우드 SDK나 벤더 종속 코드 없이 사용할 수 있는 최소 adapter다.

다만 이 client의 출력은 반드시 “제안 후보”로 취급한다. 실제 action으로 바꾸기 전에는 Pydantic 스키마 검증, evidence 재검증, policy gate, 사람 승인을 별도로 통과해야 한다.

### 5.1 GPU 서버에서의 모델 서버 기동

아래는 승인된 모델 파일과 GPU 호환성이 이미 검증된 Linux 서버에서만 쓰는 예시다. <approved-model-path>는 조직이 라이선스·보안·성능 검토를 마친 내부 모델 경로로 바꾼다.

~~~bash
export VLLM_API_KEY='secret-from-internal-secret-manager'

vllm serve <approved-model-path> \
  --served-model-name local-sllm \
  --host 127.0.0.1 \
  --port 8000 \
  --api-key "$VLLM_API_KEY"

curl --fail \
  --header "Authorization: Bearer $VLLM_API_KEY" \
  http://127.0.0.1:8000/v1/models
~~~

운영에서는 vLLM 포트를 외부에 직접 노출하지 않는다. 내부 reverse proxy, TLS 또는 mTLS, 네트워크 정책, 요청 제한, 중앙 비밀 관리, 감사 로그를 앞에 둔다. vLLM의 API key 옵션만으로는 네트워크 경계와 사용자 권한을 완성할 수 없다.

Python adapter 사용 예시는 다음과 같다.

~~~python
from onprem_agentic_mas.local_model import (
    ChatRole,
    LocalChatMessage,
    LocalOpenAICompatibleClient,
)

client = LocalOpenAICompatibleClient(
    base_url="https://gpu-gateway.internal/v1",
    api_key="<read-from-secret-manager>",
    model="local-sllm",
    allowed_hosts=frozenset({"gpu-gateway.internal"}),
)
candidate_text = client.complete(
    (
        LocalChatMessage(
            role=ChatRole.USER,
            content="Return only a JSON action proposal supported by cited evidence.",
        ),
    )
)
~~~

`LocalModelProposalGenerator`를 `build_system(..., proposals=...)`에 주입하면 이 client의 응답은 `ProposalCandidate` JSON으로 검증된 뒤에만 workflow에 들어간다. 예제 테스트는 실제 loopback HTTP fake로 이 경로를 호출하되, 고위험 action은 승인 전 `pending_approval`에서 멈추는 것을 확인한다. 운영 client는 HTTPS와 명시적 host allowlist를 강제하고, HTTP는 `allow_insecure_loopback=True`인 loopback 개발 환경에만 허용한다. API key는 객체 표현에서 숨기며, 응답 바이트도 제한한다.

LangChain을 선호하는 팀은 선택 의존성을 설치해 같은 내부 endpoint를 사용해도 된다.

~~~powershell
uv sync --extra local-model
~~~

그 다음 langchain_openai.ChatOpenAI의 base_url을 내부 /v1 endpoint로 지정한다. LangChain은 모델 adapter와 tool abstraction에 쓰고, LangGraph는 상태 전이와 정책 외부화에 쓴다. 하나의 요청에 LangGraph와 Google ADK를 동시에 orchestration owner로 두지는 않는다.

## 6. VLM과 Document Layout Analysis를 제품 경로에 넣는 방법

Layout Analysis를 단순 OCR 결과로 취급하면 이후 RAG와 규제 근거가 약해진다. 최소한 문서 ID, 페이지, block ID, bounding box, confidence, model version, 처리 시각을 함께 저장한다.

layout.py의 LayoutDocument와 LayoutBlock은 그 경계의 예시다. 실제 Layout/VLM 서비스는 JSON만 반환하고, left < right·top < bottom 검증을 통과한 결과만 layout_document_to_events 함수를 거쳐 ETL로 넘긴다. 변환된 event에는 document ID, model version, page, block kind, bbox, confidence가 typed provenance로 유지된다.

~~~text
PDF/Image
  → OCR 또는 Layout/VLM service
  → LayoutDocument JSON 검증
  → confidence/페이지/block 단위 품질 판단
  → IngestionEvent
  → raw/curated 저장소와 검색 인덱스
~~~

실제 모델 개선은 아래 순서로 한다.

1. 문서 종류, 언어, 표·도장·다단 레이아웃, 스캔 품질별로 고정 평가 세트를 만든다.
2. block detection, reading order, table structure, key-value extraction을 분리해 측정한다.
3. 날짜 기준으로 train/validation/test를 나누고, 같은 문서 또는 변형본이 서로 다른 split에 들어가지 않게 막는다.
4. LoRA 등 경량 튜닝은 baseline과 같은 평가 세트에서 비교한다.
5. 정확도만이 아니라 처리 지연, GPU 메모리, 문서당 비용, confidence calibration, 실패 문서 격리율을 함께 본다.
6. 승인된 artifact만 staging → shadow/replay → 제한된 canary 순서로 올린다.

이 저장소는 임의의 공개 모델이나 회사 문서를 넣어 성능 수치를 주장하지 않는다. 실제 튜닝 명령은 승인된 모델·데이터셋·GPU 수·라이선스가 확정된 뒤 training container와 재현 가능한 manifest에 함께 커밋해야 한다.

## 7. RAG, Ontology, Knowledge Graph를 실제 데이터 계약으로 만들기

RAG는 문서를 벡터화하는 작업만이 아니다. 업무형 시스템에서는 다음 식별자와 조건이 항상 함께 이동해야 한다.

~~~text
chunk_id
source_id
source_version
tenant_id
object_id
data_as_of
ingested_at
permission_scope
rule_or_document_version
extraction_model_version
~~~

권장 Ontology의 시작점은 매우 작아도 된다.

| 객체 | 핵심 속성 | 관계 | 상태/행동 |
|---|---|---|---|
| Case | case ID, owner, risk | Evidence, ReviewTask와 연결 | open, waiting_approval, resolved |
| Evidence | source ID, excerpt, 기준 시각 | Case, Rule과 연결 | active, stale, superseded |
| Rule | version, effective date, jurisdiction | Evidence, Case와 연결 | draft, approved, retired |
| ReviewTask | 담당자, deadline, idempotency key | Case와 연결 | proposed, approved, committed |
| Document | 원본 해시, ACL, layout version | Evidence와 연결 | ingested, quarantined, deleted |

`CaseRequest`는 untrusted evidence ID만 담고, `EvidenceResolver`가 실제 source ID·version·content hash·기준 시각·ACL을 검증한 `VerifiedEvidence`를 반환한다. 모델 프롬프트에만 규정명이나 문서 링크를 넣지 말고, 이 식별자를 proposal digest·응답·로그·행동 proposal에 같이 넣어야 재현할 수 있다.

검색은 두 갈래로 둔다.

- 정확한 현재 상태, 권한, 수치, 상태 전이: 구조화된 Object API 또는 SQL read model
- 유사 규정, 문서 문맥, 과거 사례: tenant/ACL filter가 먼저 적용되는 lexical/vector retrieval

LLM이 수치나 권한을 추측하도록 두기보다, 구조화된 조회와 검색 근거를 Context Builder가 묶고 모델에는 필요한 최소 맥락만 전달한다.

## 8. A2A를 언제 쓰고 어떻게 분리하는가

A2A는 agent가 많아지기 위한 장식이 아니다. 서로 다른 팀·서비스·실행 환경이 독립 배포되고, 각자가 명시적인 capability, input/output mode, 인증, 실패 계약을 가져야 할 때 쓴다.

이 예제의 contracts/agent-card.example.json은 Agent Card에 담아야 할 최소 개념을 보여 준다. 이 파일 하나만으로 실제 A2A 서버가 되는 것은 아니다. 실제 서비스는 A2A SDK 또는 Google ADK의 현재 공식 문서에 맞춰 아래를 구현해야 한다.

1. /.well-known/agent-card.json을 인증 정책과 함께 제공한다.
2. 각 skill의 입력·출력 JSON Schema와 최대 실행 시간을 계약으로 둔다.
3. 요청 ID, tenant, actor, trace ID, idempotency key를 전달한다.
4. 원격 agent의 결과도 local policy/action gate를 다시 통과시킨다.
5. discovery 실패, timeout, 중복 호출, callback 재시도, 권한 거부를 테스트한다.

프레임워크 역할을 겹치지 않게 배치하면 다음과 같다.

| 역할 | 기본 선택 | 쓰는 이유 |
|---|---|---|
| 한 제품 안의 상태 전이·승인 흐름 | LangGraph | 명시적 graph와 conditional routing |
| 모델·retriever·tool adapter | LangChain 또는 직접 adapter | local endpoint·retrieval 구현 교체 |
| 별도 팀/서비스의 원격 agent | A2A + 필요 시 Google ADK | capability discovery와 서비스 간 계약 |

## 9. 자가 개선은 자동 코드 변경이 아니라 릴리스 게이트다

안전한 self-improvement loop는 다음처럼 닫힌다.

~~~text
사용자 수정·거절·실패
  → 원인 분류
  → 익명화·검토된 평가 케이스
  → retrieval/prompt/model/policy 후보 변경
  → offline regression + 권한·행동 평가
  → 사람 승인
  → staging / shadow / canary
  → 관찰성·rollback
~~~

improvement.py는 이를 가장 작게 표현한다. 호출자는 candidate ID만 요청하고, `ReleaseAuthority`가 immutable evaluation artifact를 찾아 최소 한 개 이상의 evaluation case와 blocker failure를 확인한다. 그 artifact ID/hash에 결합되고, artifact 완료 뒤에 승인됐으며, 현재 시각에 유효하고 폐기되지 않은 검증된 release approval이 있어야 candidate가 promotable하다. 자동으로 프롬프트, 정책, 모델 가중치, 업무 데이터를 수정하는 루프는 운영 사고를 재현하기 어렵게 하므로 이 예제의 범위에서 금지한다.

평가 세트에는 적어도 아래를 넣는다.

- 정상 업무 케이스
- 문서 누락·상충·오래된 기준 시각
- 타 테넌트·민감 필드·권한 없는 사용자
- 프롬프트 인젝션과 tool argument 조작
- 중복 요청·부분 성공·timeout·외부 원장 실패
- 과거에 실제로 수정·거절된 회귀 케이스

## 10. 배포와 운영을 실제 제품 수준으로 올리는 순서

처음부터 완전 자동화를 만들지 않는다.

| 단계 | 공개 범위 | 반드시 남길 증거 |
|---|---|---|
| 1. 읽기 전용 | 한 업무 객체와 문서 검색 | 출처·기준 시각·권한 테스트 |
| 2. 제안 | ActionProposal을 UI에 표시 | 근거·정책·평가 결과 |
| 3. 승인 | 담당자가 approve/reject/revise | 승인 이력·영향 미리보기 |
| 4. 제한 실행 | 저위험 action 하나 | idempotency·receipt·rollback |
| 5. 확장 | 여러 source·agent·업무 | SLO·비용·on-call·release gate |

CI는 코드뿐 아니라 data contract, ontology schema, prompt, policy, model version, evaluation set을 모두 변경 단위로 취급해야 한다. production write-back은 local 성공만으로 열지 않고 sandbox, replay/shadow, canary를 거친다.

이 저장소에 추가된 예제의 최소 품질 게이트는 다음 네 개다.

~~~text
ruff format --check
ruff check
basedpyright
pytest
~~~

실제 조직에서는 여기에 dependency scan, secret scan, schema compatibility, offline eval, permission/red-team test, container image scan, staging smoke, canary SLO를 추가한다.

## 11. 처음 30일의 구현 순서

### 1주차: 업무 경계와 데이터 계약

- 한 개의 Case와 한 개의 허용 action을 고른다.
- source owner, ACL, 기준 시각, retention, freshness SLA를 문서화한다.
- Case, Evidence, Rule, ReviewTask의 JSON Schema와 상태 전이를 고정한다.

### 2주차: 읽기 전용 RAG와 문서 파이프라인

- 원천 파일을 raw 영역에 저장하고, validation/quarantine/replay를 만든다.
- Layout 결과를 block 단위로 검증하고 source/version metadata를 붙인다.
- tenant와 ACL 필터가 retrieval보다 먼저 실행되는지 테스트한다.

### 3주차: LangGraph와 승인 UX

- Evidence → Proposal → Policy → Approval 흐름을 구현한다.
- Action Gateway는 sandbox task 생성처럼 되돌릴 수 있는 행동 하나만 연결한다.
- 정상·경계·권한·실패·중복 케이스를 pytest/eval로 고정한다.

### 4주차: 모델과 운영 경계

- GPU 서버의 local model endpoint를 mTLS/secret management 뒤에 둔다.
- 동기화된 모델·프롬프트·retrieval 후보를 shadow에서 비교한다.
- trace, action receipt, 평가 결과, rollback runbook을 확인한 후 작은 canary를 연다.

## 12. 참고한 공식 구현 문서

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)와 [custom workflow 안내](https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow)
- [A2A specification](https://a2a-protocol.org/v0.3.0/specification/)와 [Agent discovery](https://a2a-protocol.org/latest/topics/agent-discovery/)
- [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/)
- [Google ADK Python repository](https://github.com/google/adk-python)와 [A2A guide](https://github.com/google/adk-docs/blob/main/docs/a2a/index.md)

제품과 프로토콜의 버전·명령·보안 기본값은 변할 수 있다. 실제 서버 배포 또는 원격 A2A 연동 직전에는 위 공식 문서와 내부 보안 기준을 다시 확인한다.
