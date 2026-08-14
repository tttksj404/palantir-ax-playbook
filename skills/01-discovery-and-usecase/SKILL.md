---
name: ax-discovery-and-usecase
description: 업무 병목과 측정 가능한 결과를 기준으로 AX 유스케이스를 고르고 파일럿 범위를 고정한다.
---

# AX 유스케이스 발견

## 목적

“AI를 도입하자”를 실행 가능한 업무 문제로 바꾼다. 모델·제품·벤더를 먼저 고르지 않고, 현재 업무의 병목·기준선·위험·책임자를 확인한다.

## 입력

- 업무 프로세스와 실제 사용자
- 현재 처리 시간·오류·재작업·대기 시간의 기준선
- 사용하는 원천 시스템과 문서
- 변경할 수 있는 업무 상태와 변경할 수 없는 상태
- 규제·보안·개인정보·현업 제약

## 절차

1. 업무의 시작 이벤트와 완료 상태를 한 문장으로 쓴다.
2. 사용자가 반복적으로 검색·복사·판단·승인·전달하는 단계를 관찰한다.
3. 각 병목에 대해 빈도, 소요 시간, 오류 비용, 의사결정 지연을 기록한다.
4. AI 역할을 `조회`, `요약`, `분류`, `예측`, `추천`, `행동 초안`, `제한 실행` 중 하나 이상으로 구분한다.
5. 읽기 전용 파일럿으로 검증 가능한 최소 수직 슬라이스를 선택한다.
6. 성공 기준, 중단 조건, 업무 오너, 데이터 오너, 보안 오너를 확정한다.

## 산출물

```yaml
use_case_id:
problem_statement:
actor:
trigger:
current_workflow:
target_workflow:
baseline:
ai_role: read | summarize | classify | predict | recommend | propose | execute
business_objects: []
source_systems: []
success_metrics: []
stop_conditions: []
owners:
  business:
  data:
  security:
  operations:
risk_level: low | medium | high | critical
pilot_scope:
out_of_scope: []
```

## 완료 게이트

- 기준선이 숫자 또는 재현 가능한 관찰 기록으로 존재한다.
- 유스케이스가 하나의 업무 상태와 책임자를 가진다.
- AI가 할 수 있는 일과 할 수 없는 일이 분리되어 있다.
- 성공 지표와 중단 조건이 모두 있다.
- 읽기 전용으로 시작할 수 있는 최소 범위가 있다.

게이트를 충족하지 못하면 `NEEDS_FIX`로 남기고 Ontology·모델링 단계로 넘어가지 않는다.

## 관련 자료

- [Palantir AI FDE Library](https://github.com/s-andthat/palantir-ai-fde-library)
- [Awesome FDE Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap)
- [AX 유스케이스 캔버스](../../docs/AX-USE-CASE-CANVAS.md)
- [AX 전환 가이드](../../docs/AX-TRANSFORMATION-GUIDE.md)

## 주의

파일럿 목표나 예상 절감률을 측정 결과처럼 쓰지 않는다. 실제 전후 비교가 없으면 `target`, `hypothesis`, `not measured`로 표시한다.
