# Codex 스킬·지침 가이드 — palantir-ax-playbook

> 생성일 2026-11-23. Codex 작업 폴더 `~/Desktop/2학기/palantir-ax-playbook`에서 이 레포를 다룰 때 적용되는 지침과 자주 쓰는 스킬이다.
> 전체 목록(사용자 스킬 66개, 플러그인 스킬, 모든 작업 폴더 맵)은 `tttksj404/codex-global-skills`의 `docs/codex-skill-usage-guide.md`에 있다.

## 적용 지침

| 지침 | 언제 | 내용 |
|---|---|---|
| 전역 `~/.codex/AGENTS.md` | 모든 작업 | 한국어 답변, 직접 수행·검증, 결과/검증/남은 리스크 보고, 복잡한 작업은 `codex-fablize` 자동 승격 |
| 로컬 `skills/` 8개 | AX 도입 단계별 산출물 작성 | 01 발굴 → 02 온톨로지 → 03 데이터 계약 → 04 프롬프팅 → 05 승인 거버넌스 → 06 평가 → 07 관측·롤백 → 08 현장 배포 |

## 레포 로컬 스킬

| 스킬 | 언제 쓰나 (SKILL.md description) |
|---|---|
| `ax-discovery-and-usecase` | 업무 병목과 측정 가능한 결과를 기준으로 AX 유스케이스를 고르고 파일럿 범위를 고정한다. |
| `ax-ontology-modeling` | 업무 데이터를 객체·관계·상태·행동·권한 모델로 바꾸고 AI가 사용할 의미 경계를 고정한다. |
| `ax-data-contract-and-pipeline` | 원천 데이터와 이벤트를 계약·품질·계보·재처리 가능한 파이프라인으로 연결한다. |
| `ax-ai-fde-prompting` | AI FDE·개발자·현업이 최소 맥락과 검증 가능한 출력 계약으로 협업하도록 작업 지시를 만든다. |
| `ax-action-and-approval-governance` | AI의 추천·행동 계획을 권한·정책·승인·idempotency·감사가 가능한 업무 변경으로 제한한다. |
| `ax-evals-and-feedback-loop` | 실제 업무 케이스와 사용자 피드백을 평가 데이터·회귀 게이트·개선 작업으로 전환한다. |
| `ax-observability-release-rollback` | 코드·프롬프트·모델·정책·데이터 계약을 함께 릴리스하고 관찰·카나리·롤백 가능한 운영 흐름을 만든다. |
| `ax-fde-adoption-and-field-delivery` | 현업과 함께 AX 제품을 설계·운영하고 채택·가치·확장 조건을 증거로 관리한다. |

## 이 레포에서 주로 쓰는 스킬

"언제 쓰나"는 각 `SKILL.md`의 description 원문이다.

| 스킬 | 언제 쓰나 (SKILL.md description) |
|---|---|
| `writing-principles` | What fiction readers want (reader reward channels) and the specific ways LLM training damages them. Load when drafting prose, critiquing, or diagnosing why a passage feels flat. |
| `information-hierarchy` | Load for large human-facing outputs: reports, docs, multi-section explanations, artifacts. Choose the right form for each beat (prose, diagram, table, mockup) and put the answer first, depth behind it. If the medium allows, use progressive disclosure. |
| `presentation-design` | Visual design guidance for bold, minimal presentations. Provides layout patterns, typography hierarchy, color specifications, and slide composition rules. Use when asking "how should this slide look?", "design guidance for...", "what layout for this slide?", or when translating content into visual structure for a presentation. |
| `slide-deck-builder` | Structure a persuasive slide deck - narrative arc, one-idea-per-slide discipline, and headlines written as takeaways not labels. Use when building any presentation that must move an audience to a decision. |
| `notion-spec-to-implementation` | Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them. |
