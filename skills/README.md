# AX 실행 스킬

이 디렉터리는 GitHub에서 조사한 팔란티어·AI FDE·데이터 엔지니어링·에이전트 보안 자료를 이 저장소에 맞는 실행 절차로 재작성한 것입니다.

이 파일들은 Palantir 공식 스킬 패키지가 아닙니다. 각 스킬은 **업무 정의 → 계약 → 구현 → 검증 → 운영**의 순서를 강제하기 위한 학습·설계 템플릿입니다.

## 실행 순서

```text
01 유스케이스 발견
  → 02 업무 객체·Ontology 모델링
  → 03 데이터 계약·파이프라인
  → 04 AI FDE 프롬프트·작업 지시
  → 05 행동·승인·권한
  → 06 평가·피드백
  → 07 관찰성·배포·롤백
  → 08 현장 전달·채택·확장
```

각 단계는 앞 단계의 산출물을 입력으로 사용합니다. 앞 단계의 계약이 없는 상태에서 다음 스킬로 건너뛰면 `NEEDS_FIX`로 판정합니다.

## 스킬 목록

| 번호 | 파일 | 사용 시점 |
|---:|---|---|
| 01 | [`discovery-and-usecase/SKILL.md`](01-discovery-and-usecase/SKILL.md) | AX 후보를 기술이 아니라 업무 결과와 기준선으로 정의할 때 |
| 02 | [`ontology-modeling/SKILL.md`](02-ontology-modeling/SKILL.md) | 업무 객체·관계·상태·행동을 모델링할 때 |
| 03 | [`data-contract-and-pipeline/SKILL.md`](03-data-contract-and-pipeline/SKILL.md) | 원천 연결, 데이터 품질, 이벤트, 재처리, 계보를 설계할 때 |
| 04 | [`ai-fde-prompting/SKILL.md`](04-ai-fde-prompting/SKILL.md) | AI FDE·개발자·현업이 같은 작업 계약으로 협업할 때 |
| 05 | [`action-and-approval-governance/SKILL.md`](05-action-and-approval-governance/SKILL.md) | AI 추천을 업무 시스템 변경으로 연결할 때 |
| 06 | [`evals-and-feedback-loop/SKILL.md`](06-evals-and-feedback-loop/SKILL.md) | 출시 전후 평가와 사용자 피드백을 회귀 테스트로 만들 때 |
| 07 | [`observability-release-rollback/SKILL.md`](07-observability-release-rollback/SKILL.md) | 프롬프트·정책·데이터·코드의 배포와 운영을 관리할 때 |
| 08 | [`fde-adoption-and-field-delivery/SKILL.md`](08-fde-adoption-and-field-delivery/SKILL.md) | 현업 채택, 교육, 운영 책임, 다음 업무 확장을 설계할 때 |

## 공통 산출물 계약

모든 스킬 실행 결과에는 아래 항목을 남깁니다.

```yaml
skill:
version:
owner:
use_case:
inputs: []
assumptions: []
decisions: []
artifacts: []
verification:
  checks: []
  evidence: []
  status: PASS | NEEDS_FIX | BLOCKED
failure_modes: []
next_action:
```

`PASS`는 문서가 존재한다는 뜻이 아니라, 해당 스킬의 완료 게이트와 증거가 충족되었다는 뜻입니다. Palantir 계정이나 실제 업무 시스템에 연결하지 않은 경우에는 `design-only` 또는 `not-run`을 명시합니다.

## 공통 프롬프트 골격

AI 에이전트에게 스킬을 사용할 때는 다음 맥락을 먼저 제공합니다.

1. **업무 목표**: 무엇을 개선하려는가?
2. **업무 객체**: 어떤 객체·상태·관계가 대상인가?
3. **권한과 금지 범위**: 읽기·추천·초안·실행 중 어디까지 가능한가?
4. **사용 가능한 도구**: 실제 연결된 도구만 나열한다.
5. **출력 계약**: JSON·표·결정 기록 등 소비 가능한 형태를 지정한다.
6. **검증 방법**: 성공·실패·중단 조건과 증거 위치를 지정한다.

## 가져온 자료의 사용 원칙

- Palantir 공식 SDK는 API와 코드 경계의 참고로만 사용한다.
- AIP Community Registry는 구현 패턴의 참고로 사용하며 공식 지원으로 표현하지 않는다.
- 커뮤니티 스킬 팩은 이 디렉터리의 절차로 재작성하고, 제품·성능 주장은 별도 검증한다.
- 외부 저장소의 비밀값, 고객 데이터, 토큰, 약관상 제한된 코드를 이 레포에 넣지 않는다.

## 관련 문서

- [GitHub 기반 AX 스킬 카탈로그](../docs/GITHUB-AX-SKILLS-CATALOG.md)
- [AX 기술 파이프라인](../docs/AX-TECHNICAL-PIPELINE.md)
- [평가 루브릭](../docs/EVALUATION-RUBRIC.md)
- [AX 유스케이스 캔버스](../docs/AX-USE-CASE-CANVAS.md)
