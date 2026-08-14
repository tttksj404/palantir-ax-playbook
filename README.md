# Palantir AX Playbook

팔란티어가 공개한 Foundry·AIP·Apollo·Ontology와 기업 고객 사례를 바탕으로, 기업이 AI를 실제 업무와 의사결정에 연결하는 방법을 정리한 AI Study 저장소입니다.

## 한 줄 결론

기업 AX의 핵심은 챗봇을 하나 더 만드는 것이 아니라, **업무 객체와 데이터의 의미를 통합하고, AI가 할 수 있는 행동을 권한·검증·감사 가능한 도구로 제한한 뒤, 사람의 승인과 운영 지표를 포함한 업무 루프로 배포하는 것**입니다.

```mermaid
flowchart LR
    U[사용자·현장 이벤트] --> I[신원·권한·정책]
    I --> O[업무 객체 모델 / Ontology]
    O --> C[문서·데이터·실시간 맥락]
    C --> M[LLM·규칙·최적화 모델]
    M --> T[조회·추천·행동 도구]
    T --> H{사람 승인}
    H -->|승인| S[업무 시스템에 반영]
    H -->|거절·수정| F[피드백·재평가]
    S --> L[로그·평가·성과 지표]
    F --> L
    L --> M
```

## 이 저장소에서 답하는 질문

- 팔란티어의 AI는 단순한 질의응답과 무엇이 다른가?
- Foundry, Ontology, AIP, Apollo, FDE가 기업 운영에서 어떤 역할을 하는가?
- AI가 추천을 넘어 실제 업무를 변경할 때 어떤 안전장치가 필요한가?
- 우리 회사가 90일 안에 검증 가능한 AX 파일럿을 시작하려면 무엇을 준비해야 하는가?
- 조직 전체의 AX 전환은 전략·업무·데이터·조직·거버넌스·KPI를 어떤 순서로 바꾸는가?
- 우리 조직의 AX 성숙도와 다음 투자 우선순위를 어떻게 진단하는가?
- 실제 AX 구축에서 데이터·온라인 추론·행동·평가·CI/CD 파이프라인은 어떻게 연결하는가?
- 모델 정확도 외에 어떤 평가·운영·변화관리 지표를 봐야 하는가?
- GitHub의 AI FDE·데이터·보안 스킬을 AX 구축 절차에 어떻게 재사용하는가?

## 문서 구성

1. [팔란티어 AI·AX 플레이북](docs/PALANTIR-AI-AX-PLAYBOOK.md) — 팔란티어 구조·사례와 기업 AI 업무 제품의 기술·조직·거버넌스
2. [AX 전환 가이드](docs/AX-TRANSFORMATION-GUIDE.md) — 전략부터 업무 재설계·조직·KPI·90일/1년 로드맵까지
3. [AX 기술 파이프라인·시스템 설계](docs/AX-TECHNICAL-PIPELINE.md) — 데이터·온라인 실행·행동·평가·CI/CD·LLMOps·서비스 경계
4. [AX 성숙도 평가](docs/AX-MATURITY-ASSESSMENT.md) — 7개 축을 증거 기반으로 진단하고 다음 투자 순서를 정하는 표
5. [AX 프로그램 캔버스](docs/AX-PROGRAM-CANVAS.md) — 전사 AX North Star·포트폴리오·조직·거버넌스·로드맵 템플릿
6. [AX 유스케이스 캔버스](docs/AX-USE-CASE-CANVAS.md) — 개별 후보 업무와 파일럿 범위를 정의하는 템플릿
7. [평가 루브릭](docs/EVALUATION-RUBRIC.md) — 답변·추천·행동형 AI를 출시 전에 검증하는 기준과 테스트 케이스 형식
8. [GitHub AX 스킬 카탈로그](docs/GITHUB-AX-SKILLS-CATALOG.md) — 조사한 외부 저장소의 공식성·적용 단계·주의점과 내부 스킬 매핑
9. [AX 실행 스킬](skills/README.md) — 유스케이스부터 FDE 현장 전달까지 재사용하는 8개 내부 `SKILL.md`
10. [참고자료](docs/REFERENCES.md) — 공식 문서·고객 사례·GitHub 자료, 각 자료가 뒷받침하는 주장과 한계

## GitHub 참고자료와 적용 지도

아래 자료를 그대로 복사하지 않고, 팔란티어 공식 SDK·사례와 커뮤니티·벤더 중립 자료를 구분해 내부 AX 스킬로 재작성했습니다. 각 자료의 공식성·주의점·전체 매핑은 [GitHub AX 스킬 카탈로그](docs/GITHUB-AX-SKILLS-CATALOG.md)에 기록했습니다.

```mermaid
flowchart LR
    subgraph Sources["GitHub 참고자료"]
        FDE["AI FDE Library"]
        REG["AIP Community Registry"]
        OSDK["Palantir OSDK"]
        DATA["Data Engineering Agent Skills"]
        SEC["OWASP Secure Agent Playbook"]
        ROAD["Ontology Strategy · FDE Roadmap"]
    end

    subgraph Skills["이 레포의 내부 AX 스킬"]
        S1["01 발견"]
        S2["02 Ontology"]
        S3["03 데이터 계약"]
        S4["04 AI FDE 프롬프트"]
        S5["05 행동·승인"]
        S6["06 평가·피드백"]
        S7["07 운영·롤백"]
        S8["08 FDE 전달"]
    end

    subgraph Pipeline["AX 기술 파이프라인"]
        P1["Data · Semantic"]
        P2["Online Decision"]
        P3["Action · Write-back"]
        P4["Evaluation"]
        P5["Delivery · Operations"]
    end

    FDE --> S1
    FDE --> S4
    FDE --> S8
    REG --> S2
    REG --> S3
    REG --> S6
    OSDK --> S2
    OSDK --> S5
    DATA --> S3
    DATA --> S7
    SEC --> S5
    SEC --> S7
    ROAD --> S1
    ROAD --> S8

    S1 --> P1
    S2 --> P1
    S3 --> P1
    S4 --> P2
    S5 --> P3
    S6 --> P4
    S7 --> P5
    S8 --> P5
```

| 자료 | 분류 | 이 저장소에 반영한 내용 |
|---|---|---|
| [Palantir AI FDE Library](https://github.com/s-andthat/palantir-ai-fde-library) | 커뮤니티 | AI FDE 작업 지시, 최소 맥락, 도구·출력·검증 계약 |
| [AIP Community Registry](https://github.com/palantir/aip-community-registry) | Palantir GitHub의 커뮤니티 레지스트리 | AIP Evals 피드백, 이벤트 입력, DevOps, OSDK 예제 적용 위치 |
| [Palantir OSDK TypeScript](https://github.com/palantir/osdk-ts) | Palantir 공식 SDK | Ontology Object·Action 연동 경계 |
| [Foundry Platform Python SDK](https://github.com/palantir/foundry-platform-python) | Palantir 공식 SDK | Foundry API·AIP Agent·플랫폼 연동 경계 |
| [Data Engineering Agent Skills](https://github.com/vaquarkhan/data-engineering-agent-skills) | 벤더 중립 커뮤니티 | 데이터 계약, 품질, 계보, replay/backfill, 릴리스 게이트 |
| [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook) | 보안 플레이북 | 툴·MCP 경계, 프롬프트 인젝션, 권한·감사 점검 |
| [Ontology Strategy](https://github.com/Leading-AI-IO/palantir-ontology-strategy) · [FDE Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap) | 커뮤니티 학습 자료 | 업무 객체 중심 설계, FDE 현장 전달·채택·확장 |

> 참고자료는 Palantir 공식 지원이나 성능 보증을 의미하지 않습니다. 실제 계정·데이터·권한 환경에서 실행하지 않은 내용은 `설계·학습용 적용본`으로 표시합니다.

## 먼저 읽는 법

- **경영진·기획자**: [AX 전환 가이드](docs/AX-TRANSFORMATION-GUIDE.md) 1~5장 → 30·60·90일 로드맵 → [프로그램 캔버스](docs/AX-PROGRAM-CANVAS.md)
- **AX/DT 담당자**: [성숙도 평가](docs/AX-MATURITY-ASSESSMENT.md) → [전환 가이드](docs/AX-TRANSFORMATION-GUIDE.md) → 포트폴리오·가치 실현 보드
- **개발자·데이터 엔지니어**: [기술 파이프라인](docs/AX-TECHNICAL-PIPELINE.md) → [AX 실행 스킬](skills/README.md) → 평가 루브릭 → 캔버스의 데이터·행동 계약
- **AI FDE·플랫폼팀**: [GitHub AX 스킬 카탈로그](docs/GITHUB-AX-SKILLS-CATALOG.md) → 01~08 스킬을 실제 유스케이스에 순서대로 적용
- **보안·법무·감사**: 본문 7장 권한·거버넌스 → 8장 실패 설계 → 참고자료의 근거 범위
- **면접·스터디**: 본문 2장 핵심 구조 → 사례 표 → 마지막 학습 과제

## 근거를 읽는 규칙

문서 안에서 다음 표기를 구분합니다.

- **[공식 사실]**: 팔란티어 공식 제품 문서·공시·공식 고객 사례에 직접 기술된 내용
- **[사례]**: 팔란티어 또는 고객이 공개한 사례. 수치와 성과는 별도 독립 검증이 없으면 `vendor/customer-reported`로 표시
- **[분석]**: 공개 자료를 기업 AX 관점에서 해석한 내용
- **[권고]**: 특정 기업에 그대로 복사하기 위한 명령이 아니라, 이 저장소가 제안하는 실행 원칙

공개 자료만으로 팔란티어 내부의 모든 사내 AI 사용 방식을 확인할 수는 없습니다. 따라서 이 저장소의 표현은 “팔란티어가 기업 고객의 운영에 AI를 연결하는 공개 방식”을 중심으로 하며, 팔란티어 내부 운영을 단정하지 않습니다. 자료 확인 기준일은 **2026-08-14**입니다.

## 핵심 학습 산출물

이 저장소를 읽은 뒤 아래 네 문장을 자신의 조직 업무에 맞게 말할 수 있으면 1차 학습이 끝난 것입니다.

1. “우리 AI가 읽고 판단해야 하는 업무 객체는 무엇이고, 각 객체의 출처·상태·소유자는 무엇인가?”
2. “AI가 할 수 있는 행동과 할 수 없는 행동을 어떻게 권한·스키마·승인으로 제한할 것인가?”
3. “출시 전에 어떤 정상·경계·적대적 테스트를 통과해야 하는가?”
4. “파일럿이 실제 업무 성과를 냈다고 말할 수 있는 비교 기준과 운영 책임자는 누구인가?”

## 라이선스와 사용 범위

이 저장소는 학습·검토용 공개 문서입니다. 팔란티어의 상표·제품명·원문 자료의 권리는 각 권리자에게 있으며, 사례 수치는 원 출처의 조건과 한계를 함께 확인해야 합니다.

