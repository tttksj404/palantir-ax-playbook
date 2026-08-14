# 참고자료와 근거 범위

자료 확인 기준일: **2026-08-14**

이 문서는 1차적으로 팔란티어 공식 문서·공식 고객 사례·공시를 사용하고, AI 위험관리의 일반 원칙은 NIST AI RMF를 사용했습니다. 링크의 내용·제품 명칭·공개 상태는 변경될 수 있으므로, 실제 도입·구매·법무 판단 전 원문을 다시 확인해야 합니다.

## 팔란티어 플랫폼·아키텍처

| 자료 | 이 문서에서 사용한 근거 | 한계·주의 |
|---|---|---|
| [Architecture Center overview](https://www.palantir.com/docs/foundry/architecture-center/overview) | Foundry·AIP·Apollo의 관계, Ontology 중심 구조, FDE 방식 | 팔란티어가 설명하는 참조 아키텍처 |
| [AIP architecture](https://www.palantir.com/docs/foundry/architecture-center/aip-architecture) | AIP의 컨텍스트·보안·에이전트·평가·배포 범주 | 제품 문서의 기능 설명 |
| [AIP overview](https://www.palantir.com/docs/foundry/aip) | AIP가 데이터·업무 운영·모델을 연결하는 방식 | 제품 문서의 벤더 관점 |
| [Ontology overview](https://www.palantir.com/docs/foundry/ontology/overview) | 객체·속성·링크·행동을 포함한 운영 계층 | Ontology의 실제 범위는 도입 환경에 따라 달라짐 |
| [Ontology system](https://www.palantir.com/docs/foundry/architecture-center/ontology-system) | 데이터 표현을 넘어 의사결정·운영을 모델링한다는 설명 | 팔란티어의 개념적 설명 |
| [Foundry platform summary for LLMs](https://www.palantir.com/docs/foundry/getting-started/foundry-platform-summary-llm) | AIP 구성요소, 도구 유형, 모델·사용량 관리 | 페이지 자체가 LLM 생성 및 엔지니어 검토 자료임을 밝힘 |
| [Agents overview](https://www.palantir.com/docs/foundry/agents/overview) | pro-code Agents, 도구 호출, Ontology binding, 권한 연결 | 해당 문서에 표시된 베타 상태를 실제 계정·버전에서 확인해야 함 |
| [AIP Chatbot Studio](https://www.palantir.com/docs/foundry/chatbot-studio/overview) | 기업별 정보·도구를 쓰는 챗봇, 배포 방식, 현재 명칭 | 과거 AIP Agent Studio 명칭과 혼동 주의 |

## 행동·평가·관찰성·보안

| 자료 | 이 문서에서 사용한 근거 | 한계·주의 |
|---|---|---|
| [Action types overview](https://www.palantir.com/docs/foundry/action-types/overview) | 객체·속성·링크를 변경하는 행동, 검증·부작용·알림 | 제품의 행동 모델 설명 |
| [Action permissions](https://www.palantir.com/docs/foundry/action-types/permissions) | 행동 제출 시 권한·조건·객체 접근 검사가 필요하다는 설명 | 실제 권한 설정은 조직별 검토 필요 |
| [Object permissioning](https://www.palantir.com/docs/foundry/object-permissioning/overview) | 객체·링크·Ontology 리소스의 세밀한 권한 | 제품 권한 체계의 개요 |
| [AIP Evals overview](https://www.palantir.com/docs/foundry/aip-evals/overview) | 테스트 케이스·평가 기준·평가 함수, 버전 비교·디버깅 | 평가 품질은 조직이 구성하는 케이스에 좌우됨 |
| [AIP Observability overview](https://www.palantir.com/docs/foundry/aip-observability/overview) | 로그·추적·실행 이력·P95·토큰·오류 관찰 | 관찰 항목과 실제 보존 정책은 환경별 확인 필요 |
| [AI FDE security and governance](https://www.palantir.com/docs/foundry/ai-fde/security-and-governance) | 사용자 신원·권한에 따른 실행, 승인·감사·거버넌스 | 팔란티어가 제시하는 제품 보안 모델이며 조직의 전체 통제를 대체하지 않음 |
| [Machinery overview](https://www.palantir.com/docs/foundry/machinery/overview) | 프로세스·다단계 워크플로·에이전트·자동화·사람 개입 | 제품 기능을 AX 일반 원칙으로 해석한 부분은 분석임 |

## 공개 고객 사례·기업 적용

| 자료 | 이 문서에서 사용한 근거 | 한계·주의 |
|---|---|---|
| [Palantir Impact](https://www.palantir.com/impact) | Wendy’s, Heineken, Panasonic Energy 등 공개 적용 흐름과 성과 수치 | 팔란티어 또는 고객이 제공한 사례·수치이며 독립 검증으로 보지 않음 |
| [General Mills case study PDF](https://www.palantir.com/assets/xrfr7uokpv1b/1aLBn65y83vdytjpXJKZcO/16989b788b34cb677f6d763d56a72349/Building_an_Intelligent_AI-Driven_Supply_Chain_at_General_Mills_-_AIPCon_March_-24_Impact_Study.pdf) | 공급망 의사결정·제약조건·사람의 추천 수용·공개 성과 | 고객·벤더 공동 사례의 자기보고 수치 |
| [Beyond Meat AIPCon one-pager](https://www.palantir.com/assets/xrfr7uokpv1b/4rM2L8TANQGcPsLKOzdMJ0/6795f2b89327a87361743319836f0c42/AIPCon_Mar_-24_-_Bootcamp_One-Pager_-_Beyond_Meat.pdf) | 여러 데이터 소스를 통합한 재고·공급망 가시성 | 공식 고객 사례 자료, 외부 감사 자료 아님 |
| [Food and beverage offerings](https://www.palantir.com/offerings/food-and-beverage/) | Beyond Meat·Wendy’s 등 식음료 적용 맥락 | 마케팅·고객 사례 페이지 |
| [Supply-chain use case](https://www.palantir.com/docs/foundry/use-case-examples/optimizing-production-with-erp-data-across-the-supply-chain) | ERP 데이터 통합·디지털 트윈·생산 의사결정 | 익명 Fortune 100 사례의 추정 효과 |
| [AIPCon](https://www.palantir.com/aipcon/) | 다양한 산업·기관의 공개 데모·고객 사례 범위 | 행사·마케팅 자료가 포함됨 |

## 회사·제품의 공개 설명

| 자료 | 이 문서에서 사용한 근거 | 한계·주의 |
|---|---|---|
| [Our new platform — Palantir CEO letter](https://www.palantir.com/newsroom/letters/our-new-platform/) | 2023년 AIP 소개, 생성형 AI를 운영 데이터·행동과 연결한다는 방향 | 경영진의 공개 설명·제품 포지셔닝 |
| [Palantir FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm) | AIP의 출시 시점과 회사가 공개한 사업·고객 맥락 | 회사가 SEC에 제출한 자기보고 공시; 투자 판단 자료로 사용하지 않음 |
| [DevCon 5](https://www.palantir.com/devcon5/) | AI FDE, 평가·디버깅·오케스트레이션을 보여주는 공개 발표 | 행사 데모·제품 방향 설명 |

## AI 위험관리

| 자료 | 이 문서에서 사용한 근거 | 한계·주의 |
|---|---|---|
| [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | 자발적·권리 보존형·부문 중립적 AI 위험관리 프레임워크 | 법적 의무나 특정 산업 규정을 자동 충족하지 않음 |
| [NIST AI RMF Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook) | Govern·Map·Measure·Manage 구조 | 조직 상황에 맞게 조정해야 하는 참고 가이드 |
| [NIST AI RMF FAQ](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook-faqs) | 일률적인 순서의 체크리스트가 아니라 유연한 동반 자료라는 성격 | 구체적인 법률·보안 통제는 별도 검토 필요 |
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | 조직의 AI 관리시스템을 수립·구현·유지·지속 개선하기 위한 국제표준의 범위 | 인증 또는 표준 활용이 특정 법률·규제 준수를 자동 보장하지 않음 |
| [ISO AI management systems guide](https://www.iso.org/artificial-intelligence/ai-management-systems) | AI 관리시스템을 Plan-Do-Check-Act 방식의 지속 개선으로 해석하는 관점 | ISO의 설명 자료이며 실제 인증·심사 요구사항은 표준 원문과 심사기관 확인 필요 |
| [OECD AI Principles](https://www.oecd.org/en/topics/ai-principles.html) | 인간 중심·권리·투명성·안전·책임성 관점의 국제 원칙 | 법률이 아니라 정책·설계 원칙이며 산업·국가별 의무를 대체하지 않음 |
| [OECD 2024 AI Principles update](https://www.oecd.org/en/about/news/press-releases/2024/05/oecd-updates-ai-principles-to-stay-abreast-of-rapid-technological-developments.html) | 2024년 업데이트에서 생성형 AI, 안전, 정보 무결성, 책임 있는 사업 수행을 강조한 배경 | OECD의 정책 발표 자료 |

## 자료 사용 규칙

이 저장소의 문장 중 다음은 원문을 그대로 옮긴 것이 아니라 요약·분석입니다.

- 제품 기능·아키텍처: 공식 문서의 설명을 짧게 재구성
- 고객 성과: 원 출처의 주장 범위를 넘지 않도록 사례로만 사용
- AX 로드맵·평가 임계값·조직 모델: 이 저장소의 권고안

새로 추가한 AX 전환 가이드는 NIST·ISO·OECD의 원칙을 기업 실행 언어로 번역한 분석 문서입니다. NIST Playbook은 일률적인 순서의 체크리스트가 아니며, ISO/IEC 42001은 AI 관리시스템 표준이고, OECD AI Principles는 정책·설계 원칙입니다. 세 자료 어느 것도 특정 기업의 AX 성공이나 규제 준수를 자동 보장하지 않습니다.

따라서 제안서나 면접에서 수치를 사용할 때에는 반드시 `누가`, `언제`, `어떤 기준선과 정의로`, `독립 검증 여부`를 함께 말해야 합니다.

