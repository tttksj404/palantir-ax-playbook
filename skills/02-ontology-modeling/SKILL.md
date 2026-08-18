---
name: ax-ontology-modeling
description: 업무 데이터를 객체·관계·상태·행동·권한 모델로 바꾸고 AI가 사용할 의미 경계를 고정한다.
---

# Ontology·업무 객체 모델링

## 목적

여러 시스템의 테이블과 문서를 AI가 임의로 해석하지 않도록, 업무에서 실제로 추적하는 객체·관계·상태·행동을 명시한다. Palantir Ontology를 사용하는 경우에도 제품 설정이 완료되었다고 가정하지 않고 계약부터 만든다.

## 입력

- [유스케이스 발견 스킬](../01-discovery-and-usecase/SKILL.md)의 산출물
- 원천 시스템 스키마와 키
- 업무 용어·상태 정의·예외 규칙
- 객체·필드·행동별 권한
- 과거·현재·예정 시점의 의미

## 절차

1. 업무에서 식별 가능한 핵심 객체를 명사로 추출한다.
2. 각 객체의 canonical key, 출처, 소유자, 현재 상태, 유효 시점을 정의한다.
3. 객체 사이의 링크와 cardinality, 삭제·병합·분할 규칙을 기록한다.
4. 상태 전이와 전이 주체, 전이 조건, 금지 전이를 표로 만든다.
5. AI가 조회할 속성과 근거 필드를 분리한다.
6. AI가 제안·실행할 행동을 객체·조건·권한·부작용과 함께 정의한다.
7. 샘플 레코드로 객체 연결·상태 전이·권한 필터를 검증한다.

## 산출물

```yaml
object_type:
canonical_key:
source_of_truth:
owner:
properties:
  - name:
    type:
    meaning:
    source:
    freshness_sla:
links:
  - target:
    relationship:
    cardinality:
states:
  - name:
    entry_condition:
    allowed_transitions: []
actions:
  - name:
    preconditions: []
    required_role:
    side_effects: []
    audit_fields: []
permission_boundary:
unknowns: []
```

## 완료 게이트

- 같은 업무 대상을 가리키는 시스템별 키 매핑이 있다.
- 상태와 상태 전이가 정의되어 있고 암묵적인 전이가 없다.
- 사실·추정·생성 요약 필드가 구분된다.
- 객체·속성·행동 권한을 사용자·조직 단위로 시험할 수 있다.
- 행동의 선행 조건과 부작용이 문서화되어 있다.

객체의 canonical key 또는 권한 경계가 없으면 AI 행동을 연결하지 않는다.

## 팔란티어 매핑

- Ontology Object/Property/Link: 업무 객체·속성·관계
- Ontology Action/Function: 상태 변경과 검증된 행동
- OSDK: 생성된 객체·행동 API를 사용하는 애플리케이션 경계
- AIP Context: 현재 사용자 권한으로 제공되는 객체·문서·관계 맥락

## 관련 자료

- [Palantir OSDK TypeScript](https://github.com/palantir/osdk-ts)
- [Palantir Ontology Strategy](https://github.com/Leading-AI-IO/palantir-ontology-strategy)
- [OSDK Hello World](https://github.com/palantir/aip-community-registry/tree/develop/OSDK%20%27Hello%20World%27%20Project)
- [AX 기술 파이프라인](../../docs/AX-TECHNICAL-PIPELINE.md)
