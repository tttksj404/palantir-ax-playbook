---
name: ax-fde-adoption-and-field-delivery
description: 현업과 함께 AX 제품을 설계·운영하고 채택·가치·확장 조건을 증거로 관리한다.
---

# FDE 현장 전달·채택·확장

## 목적

AX를 플랫폼 설치 프로젝트가 아니라 현업의 실제 업무 루프를 바꾸는 제품 전달 과정으로 운영한다. FDE는 요구사항 수집자에 머물지 않고 문제 정의, 데이터·Ontology 설계, 수직 슬라이스 구현, 교육, 운영 피드백을 연결한다.

## 역할 구조

| 역할 | 책임 |
|---|---|
| Business owner | 문제·우선순위·업무 KPI·최종 가치 판단 |
| Domain SME | 예외·정답·승인 기준·현업 채택 판단 |
| FDE/AI engineer | 현장 맥락을 데이터·객체·AI·행동 계약으로 구현 |
| Data/Ontology owner | 원천·의미 모델·품질·계보·권한 |
| Security/platform owner | 접근·정책·배포·관찰성·사고 대응 |
| Operations/on-call | 운영 지표·장애·fallback·릴리스 승인 |

## 현장 루프

```text
업무 관찰
  → 병목·기준선 합의
  → 객체·데이터·권한 계약
  → 읽기 전용 수직 슬라이스
  → 현업 사용·수정·거절 기록
  → 평가·업무 KPI 비교
  → 승인된 행동과 운영 책임 추가
  → 다음 업무로 확장
```

## 절차

1. 첫 1~2주에 업무 shadowing과 기준선 측정을 끝낸다.
2. 한 업무 오너와 한 현업 SME를 지정하고 의사결정 지연을 없앤다.
3. 기존 도구를 없애기 전에 읽기 전용 보조 흐름을 운영한다.
4. 사용자의 수정·거절·수동 우회를 숨기지 않고 피드백으로 수집한다.
5. 교육은 제품 기능 설명이 아니라 “언제 믿고, 언제 확인하고, 언제 이관하는가”를 중심으로 한다.
6. 채택률만 보지 말고 처리 시간·재작업·오류·승인 품질·업무 중단을 기준선과 비교한다.
7. 공통 플랫폼 기능과 도메인별 예외를 분리한 뒤 다음 업무로 확장한다.

## 완료 게이트

- 현업이 문제·정답·예외·중단 조건을 함께 정의했다.
- 사용자별 채택과 비채택 이유가 기록되어 있다.
- 운영 책임자와 수동 fallback이 있다.
- 개선 수치가 측정 결과인지 목표인지 구분되어 있다.
- 다음 확장이 공통화할 것과 도메인에 남길 것을 구분한다.

## 관련 자료

- [Palantir AI FDE Library](https://github.com/s-andthat/palantir-ai-fde-library)
- [Palantir Ontology Strategy](https://github.com/Leading-AI-IO/palantir-ontology-strategy)
- [Awesome FDE Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap)
- [AX 전환 가이드](../../docs/AX-TRANSFORMATION-GUIDE.md)
- [AX 프로그램 캔버스](../../docs/AX-PROGRAM-CANVAS.md)

## 주의

FDE 역할을 “고객 옆에서 빨리 코딩하는 사람”으로 축소하지 않는다. 업무 책임·데이터 책임·보안 책임·운영 책임이 문서와 실제 운영에서 분리되어 있어야 한다.
