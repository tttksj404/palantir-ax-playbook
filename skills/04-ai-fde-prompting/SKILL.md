---
name: ax-ai-fde-prompting
description: AI FDE·개발자·현업이 최소 맥락과 검증 가능한 출력 계약으로 협업하도록 작업 지시를 만든다.
---

# AI FDE 프롬프트·작업 계약

## 목적

좋은 문장보다 재현 가능한 작업 지시를 만든다. 프롬프트는 업무 목표, 사용할 객체·도구, 권한, 출력 스키마, 검증 절차, 실패 시 중단 조건을 포함해야 한다.

## 작업 지시 형식

```markdown
# 동사 + 대상 + 결과

## 목표
## 최소 업무 맥락
- use_case:
- object_types:
- current_state:
- data_as_of:

## 사용 가능한 도구
- name / read-or-write / required-permission / side-effect

## 제약
- 금지된 데이터·행동
- 불확실할 때의 질문·거절 조건

## 출력 계약
- schema 또는 표 형식
- 근거 ID와 기준 시각
- confidence를 수치처럼 과장하지 않는 표현 규칙

## 검증 체크리스트
## 알려진 실패 모드
```

## 절차

1. 작업의 동사와 대상 객체를 제목에 포함한다.
2. AI가 추론할 수 있는 최소 맥락만 제공하고, 권한 없는 원문을 넣지 않는다.
3. 도구마다 읽기·쓰기·외부 부작용을 표시한다.
4. 답변이 아니라 소비 가능한 스키마를 먼저 정의한다.
5. 근거가 부족하거나 데이터가 오래되었을 때의 질문·거절·이관을 명시한다.
6. 정상·경계·권한·적대적 케이스를 검증 체크리스트에 연결한다.
7. 프롬프트·도구 설명·모델·정책 버전을 함께 기록한다.

## 산출물

```yaml
prompt_id:
task_type:
version:
owner:
minimum_context: []
allowed_tools: []
forbidden_actions: []
output_schema:
evidence_requirements: []
refusal_or_escalation_rules: []
verification_cases: []
known_failure_modes: []
```

## 완료 게이트

- 작업 지시만 읽어도 입력·도구·출력·검증 범위를 알 수 있다.
- 사용자의 권한보다 넓은 도구나 데이터가 지정되지 않았다.
- 모델이 만든 사실과 원천 근거가 구분된다.
- 출력 파싱 실패와 불확실성 처리 방식이 있다.
- 프롬프트 변경이 평가·릴리스 추적 대상이다.

## 관련 자료

- [Palantir AI FDE Library](https://github.com/s-andthat/palantir-ai-fde-library)
- [Palantir OSDK TypeScript](https://github.com/palantir/osdk-ts)
- [AIP Community Registry](https://github.com/palantir/aip-community-registry)
- [평가 루브릭](../../docs/EVALUATION-RUBRIC.md)

## 주의

이 스킬은 모델의 숨은 능력을 늘리는 프롬프트가 아닙니다. 계약·도구 경계·평가 증거를 명시해 작업 품질을 재현하려는 절차입니다.
