# On-prem Agentic MAS 실행 예제

이 디렉터리는 저장소의 [온프레미스 Agentic MAS 구현 레퍼런스](../../docs/ONPREM-AGENTIC-MAS-REFERENCE.md)를 실제 Python 코드로 옮긴 최소 수직 슬라이스다. 기본 demo는 클라우드 모델이나 외부 업무 시스템을 호출하지 않으며, 고위험 요청을 사람 승인 대기 상태로 끝낸다.

~~~powershell
uv sync
uv run python -m onprem_agentic_mas
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
~~~

구성은 다음과 같다.

| 모듈 | 책임 |
|---|---|
| workflow.py | LangGraph orchestration, verified evidence → proposal → policy → authorized action 경계 |
| contracts.py | Case, VerifiedEvidence, Proposal, Approval, AuthorizedAction의 검증 계약 |
| evidence.py | tenant·case·ACL·source version/hash·freshness를 확인하는 EvidenceResolver |
| proposal.py | deterministic/local model candidate를 typed proposal으로 변환하고 digest를 계산 |
| policy.py | server-owned risk와 proposal-bound approval을 판정하는 PolicyAuthority |
| actions.py | AuthorizedAction만 받아 side effect를 수행하는 ActionGateway |
| memory.py | SQLite 기반 tenant-isolated memory |
| etl.py | schema version·중복 ID·drift를 quarantine하는 replay 가능한 ETL 진입점 |
| layout.py | bbox 검증 및 document/block/model provenance를 보존하는 ETL 변환 |
| local_model.py | HTTPS/host allowlist와 응답 크기 제한이 있는 내부 모델 gateway client |
| improvement.py | immutable evaluation artifact와 release approval을 요구하는 promotion gate |

실제 업무 시스템을 연결할 때는 InMemoryActionGateway를 production adapter로 교체한다. 모델 출력은 항상 proposal까지만 허용하고, policy·승인·idempotency를 건너뛰어 직접 write-back하지 않는다. API 인증 adapter는 `CaseRequest`의 tenant ID와 actor ID를 JSON body가 아니라 인증된 principal에서 설정해야 한다. `CaseRequest`는 호출자가 보낸 위험도·승인 boolean·근거 본문을 받지 않는다. 서버 측 `EvidenceResolver`가 tenant·case·ACL·source version/hash·freshness를 확인한 `VerifiedEvidence`만 전달하고, `PolicyAuthority`는 위험도를 소유한다. 승인 시스템에서 이미 검증한 `VerifiedApproval`은 request·proposal digest·tenant·case·action·policy version·승인 시각·만료·revocation에 모두 결합돼야 한다. `ActionGateway`는 이 과정을 통과한 `AuthorizedAction`만 받고, 같은 idempotency key가 다른 proposal digest를 재사용하면 conflict로 차단한다.

SQLite 예제는 복합키 `(tenant_id, memory_id)`를 가진 `agent_memory_v2`만 사용한다. 이전 단일 `memory_id` 키 테이블이 있다면 그대로 재사용하지 않으므로, 운영 전환에서는 데이터 보존·롤백 계획을 포함한 별도 마이그레이션을 검토한다.

이 예제의 Agent Card는 contracts/agent-card.example.json에 있다. 이는 정적 계약 예시이며, 실제 A2A server는 별도의 인증·discovery·timeout·callback 테스트와 함께 구현해야 한다.
