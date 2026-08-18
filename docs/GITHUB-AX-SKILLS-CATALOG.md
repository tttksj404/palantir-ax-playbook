# GitHub 기반 AX 스킬 카탈로그

> 이 문서는 GitHub에서 확인한 팔란티어·AI FDE·에이전트 운영 자료를 이 저장소의 AX 파이프라인에 적용하기 위한 선별 기록입니다.
>
> 기존 자료 확인 기준일: **2026-08-14** · 그래프 엔지니어링 자료 추가 확인일: **2026-08-18**

## 1. 결론

팔란티어 AX를 위한 단일 공식 `SKILL.md` 패키지는 확인하지 못했습니다. 대신 다음 네 종류의 자료를 조합하는 것이 현실적입니다.

1. **팔란티어 공식 코드·사례**로 Ontology SDK, Foundry API, AIP 평가·이벤트·배포 패턴을 확인한다.
2. **커뮤니티 AI FDE 자료**에서 현장 문제 정의, 프롬프트 계약, Ontology 편집, 거버넌스 작업 방식을 가져온다.
3. **벤더 중립 스킬 팩**에서 데이터 계약, 재처리, 보안, 평가, 운영 게이트를 보강한다.
4. **그래프 오케스트레이션 레퍼런스**에서 상태 전이, 분기, 병렬·join, checkpoint, resume, retry·escalation을 보강한다.
5. 이 자료를 그대로 설치하지 않고, 이 저장소의 `skills/` 아래에 **검증 가능한 내부 절차**로 재작성한다.

현재 적용한 내부 스킬의 실행 순서는 다음과 같습니다.

```mermaid
flowchart LR
    A[01 유스케이스 발견] --> B[02 Ontology·업무 상태]
    B --> C[03 데이터 계약·파이프라인]
    C --> D[04 AI FDE 프롬프트]
    D --> I[09 그래프 엔지니어링]
    I --> E[05 행동·승인·권한]
    E --> F[06 평가·피드백 루프]
    F --> G[07 관찰성·배포·롤백]
    G --> H[08 FDE 현장 전달·확장]
    H --> A
```

## 2. 우선순위별 선별 결과

| 우선순위 | 자료 | 성격 | 이 레포에 적용한 부분 | 주의점 |
|---|---|---|---|---|
| P0 | [Palantir AI FDE Library](https://github.com/s-andthat/palantir-ai-fde-library) | 커뮤니티 | 프롬프트 표준, 역할 분리, 데이터·Ontology·거버넌스 작업 체크리스트 | Palantir 공식 지원 자료가 아님. README의 제품·벤치마크 주장은 별도 검증 |
| P0 | [AIP Community Registry](https://github.com/palantir/aip-community-registry) | Palantir GitHub의 커뮤니티 레지스트리 | Evals 피드백, DevOps, Push-Based Events, OSDK 예제의 적용 지점 | 레지스트리 설명상 커뮤니티 프로젝트이며 공식 지원을 보장하지 않음 |
| P0 | [Data Engineering Agent Skills](https://github.com/vaquarkhan/data-engineering-agent-skills) | 벤더 중립 커뮤니티 스킬 팩 | spec-first, 데이터 계약, 품질·계보, replay/backfill, release gate | Foundry 전용이 아니므로 제품 API로 오해하지 않음 |
| P0 | [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook) | OWASP 보안 플레이북 | 프롬프트 인젝션, MCP·툴 경계, 위협모델, 증거 기반 보안 게이트 | 조직의 법적·산업별 통제를 대체하지 않음 |
| P1 | [Palantir OSDK TypeScript](https://github.com/palantir/osdk-ts) | Palantir 공식 SDK | Ontology Object·Action 연동을 설계할 때의 실제 코드 기준 | 계정·Developer Console·생성 SDK 설정은 실제 환경에서 확인 |
| P1 | [Foundry Platform Python SDK](https://github.com/palantir/foundry-platform-python) | Palantir 공식 SDK | Foundry API·AIP Agent·데이터·관리 API 연동 경계 | Ontology 중심 앱은 해당 저장소 README의 SDK 선택 지침을 따름 |
| P1 | [Palantir Ontology Strategy](https://github.com/Leading-AI-IO/palantir-ontology-strategy) | 커뮤니티 학습 자료 | 업무 객체·관계·행동·조직 도입의 학습 프레임 | 공식 Palantir 문서가 아닌 해석·교육 자료 |
| P1 | [Agents Towards Production](https://github.com/NirDiamant/agents-towards-production) | 벤더 중립 코드 학습 자료 | 에이전트 평가·관찰성·보안·배포 학습 범위 | 예제 기술을 Foundry 구성요소로 자동 치환하지 않음 |
| P1 | [Awesome FDE Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap) | FDE 역량 로드맵 | FDE 역할, 현장 전달, 데이터·AI·컨설팅 역량 체계 | Palantir 전용 구현 가이드가 아님 |
| P1 | [LangGraph](https://github.com/langchain-ai/langgraph) | 상태 보존형 그래프 오케스트레이션 | node/edge, 조건부 경로, checkpoint·resume을 학습하는 구현 레퍼런스 | LangGraph를 Palantir 구현으로 간주하지 않음 |
| P1 | [Temporal](https://github.com/temporalio/temporal) | 내구성 있는 워크플로 오케스트레이션 | 장기 실행, 재개, timeout, retry·보상 흐름의 일반 레퍼런스 | LLM·Foundry 전용이 아니며 제품 치환 근거가 아님 |
| P1 | [Prefect](https://github.com/PrefectHQ/prefect) | 데이터·업무 흐름 오케스트레이션 | 실행 상태, 재시도, 일정, 운영 관찰성의 참고 | Foundry Pipelines·AIP를 대체하라는 의미가 아님 |
| P2 | [NetworkX](https://github.com/networkx/networkx) | 그래프 분석 라이브러리 | topology 검사, reachability·cycle 분석, 정적 검증 아이디어 | 실행·내구성 런타임이 아님 |
| 조건부 | [Astronomer Agents](https://github.com/astronomer/agents) | Airflow·데이터 오케스트레이션 스킬 | Airflow를 쓰는 조직의 이벤트·워크플로 참고 | Foundry Pipelines를 Airflow로 대체하라는 의미가 아님 |
| 조건부 | [OpenCode Palantir](https://github.com/anandpant/opencode-palantir) | 커뮤니티 OpenCode 플러그인 | Palantir 문서 탐색·MCP 부트스트랩 아이디어 | 네이티브 Windows 미지원. WSL2에서도 토큰·툴 권한 검토 필요 |

## 3. 내부 스킬과 외부 자료의 매핑

| 내부 스킬 | 먼저 읽을 외부 자료 | 적용한 핵심 |
|---|---|---|
| [`01-discovery-and-usecase`](../skills/01-discovery-and-usecase/SKILL.md) | FDE Library, FDE Roadmap | 기술이 아니라 업무 결과·현장 제약·기준선을 먼저 고정 |
| [`02-ontology-modeling`](../skills/02-ontology-modeling/SKILL.md) | OSDK, Ontology Strategy, AIP Registry | 객체·관계·상태·행동을 업무 언어로 모델링 |
| [`03-data-contract-and-pipeline`](../skills/03-data-contract-and-pipeline/SKILL.md) | Data Engineering Agent Skills, Push-Based Events | 계약 우선, 품질 게이트, idempotency, replay/backfill, lineage |
| [`04-ai-fde-prompting`](../skills/04-ai-fde-prompting/SKILL.md) | FDE Library, OSDK | 최소 맥락·도구·예상 출력·검증 체크리스트를 프롬프트에 포함 |
| [`09-graph-engineering`](../skills/09-graph-engineering/SKILL.md) | [@0xwhrrari graph/harness/loop framing](https://x.com/0xwhrrari/status/2086784668003598356?s=46), LangGraph, Temporal, NetworkX | trace first, node/edge contract, 상태 전이, 병렬·join, checkpoint·resume, bounded retry·escalation |
| [`05-action-and-approval-governance`](../skills/05-action-and-approval-governance/SKILL.md) | OSDK, OWASP, AIP Registry | 모델 출력과 업무 변경을 분리하고 권한·정책·승인·감사를 강제 |
| [`06-evals-and-feedback-loop`](../skills/06-evals-and-feedback-loop/SKILL.md) | AIP Evals Registry, Agents Towards Production | 실제 사용자 피드백을 회귀 평가 케이스로 승격 |
| [`07-observability-release-rollback`](../skills/07-observability-release-rollback/SKILL.md) | DevOps Registry, Agents Towards Production, OWASP | 코드뿐 아니라 프롬프트·정책·데이터 계약을 릴리스 단위로 관리 |
| [`08-fde-adoption-and-field-delivery`](../skills/08-fde-adoption-and-field-delivery/SKILL.md) | Ontology Strategy, FDE Roadmap, FDE Library | 현업 공동 설계, 채택, 운영 책임, 확장 조건을 제품 범위에 포함 |

## 3-1. 그래프 엔지니어링 자료의 출처 경계

사용자가 제공한 [@0xwhrrari X 게시물](https://x.com/0xwhrrari/status/2086784668003598356?s=46)은 그래프 엔지니어링 적용의 출발점으로 기록했다. 다만 현재 작업 환경에서는 해당 X 페이지 본문을 직접 추출하지 못했으므로, 게시물의 문장을 직접 인용하지 않고 공개적으로 확인 가능한 관련 정리와 구현 레퍼런스를 교차 확인해 내부 절차로 재작성했다.

그래프 관련 핵심 적용은 다음과 같다.

1. **Harness**는 도구·권한·메모리·격리·trace 등 환경과 결과의 영향 범위를 담당한다.
2. **Loop**는 반복·검증·피드백·예산·종료를 담당하며, 같은 호출을 무한 재시도하지 않는다.
3. **Graph**는 node·edge·state·branch·parallel·join·approval·checkpoint·recovery를 담당한다.
4. 실제 trace를 관찰한 뒤 안정적인 경로만 그래프로 고정하며, 단순 업무에는 그래프를 강제하지 않는다.

상세한 설계와 Palantir AX 매핑은 [AX 그래프 엔지니어링 플레이북](GRAPH-ENGINEERING-PLAYBOOK.md), 실행 절차는 [09 그래프 엔지니어링 스킬](../skills/09-graph-engineering/SKILL.md)에 있다.

## 4. 적용하지 않은 자료

검색 결과에 포함됐지만 이 카탈로그의 팔란티어 AX 후보로는 사용하지 않은 자료도 구분합니다.

| 자료군 | 제외 이유 |
|---|---|
| Microsoft Agent 365, Azure AI Foundry 관련 저장소 | Microsoft Foundry와 Palantir Foundry는 다른 제품·플랫폼이므로 직접 근거로 사용할 수 없음 |
| 일반 `awesome-skills` 모음 | 스킬 형식 참고에는 쓸 수 있지만 팔란티어 AX의 업무·권한·Ontology 근거가 부족함 |
| Palantir와 이름만 유사한 독립 Ontology 플랫폼 | 개념 비교용일 뿐 Palantir 제품·고객 적용 근거가 아님 |

## 5. 출처를 사용할 때의 규칙

### 공식성과 커뮤니티를 분리한다

- `palantir/*`의 SDK·공식 문서는 제품 API의 기준으로 사용한다.
- `palantir/aip-community-registry`의 예제는 구현 아이디어로 사용하되, 운영 보증이나 공식 지원으로 표현하지 않는다.
- `s-andthat/*`, `Leading-AI-IO/*`, `vaquarkhan/*` 등은 커뮤니티 학습 자료로 표시한다.
- 외부 자료의 성능 수치·GA 여부·MCP 지원 여부는 실제 공식 문서와 계정 환경에서 다시 확인한다.

### 복사보다 내부 검증을 우선한다

외부 스킬을 그대로 설치하거나 프롬프트를 복사하지 않는다. 내부 스킬은 다음을 반드시 포함해야 합니다.

1. 입력과 선행 조건
2. 수행 절차와 변경 가능한 범위
3. 구조화된 산출물 형식
4. 자동·사람 검증 체크리스트
5. 실패·중단·수동 이관 조건
6. 사용한 출처와 아직 검증하지 않은 주장

### 라이선스와 비밀값을 확인한다

외부 저장소의 코드를 가져올 때는 해당 저장소의 `LICENSE`, 의존성, 서비스 약관을 다시 확인한다. Foundry URL·토큰·고객 데이터는 스킬 문서나 예제에 기록하지 않는다.

## 6. 다음 확장 순서

이 카탈로그의 다음 작업은 실제 Palantir 계정이나 테스트 가능한 대체 시스템에서 각 스킬의 검증 증거를 채우는 것입니다.

1. 한 개의 읽기 전용 업무 객체를 선택한다.
2. 데이터·객체·권한 계약을 작성한다.
3. 실제 케이스 20개 이상으로 정상·경계·권한·실패 평가를 만든다.
4. 행동은 sandbox와 사람 승인부터 시작한다.
5. 스킬별 `검증일`, `환경`, `실행 명령`, `결과 아티팩트`를 기록한다.

현재 이 저장소에 추가한 스킬은 **설계·학습용 내부 절차**이며, Palantir 계정에서 실행되었다는 뜻은 아닙니다. 그래프 런타임 레퍼런스를 추가했다고 실제 AX 실행 그래프가 운영 중이라는 뜻도 아닙니다.
