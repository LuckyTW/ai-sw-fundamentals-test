# QA 테스트 보고서: python_level1_mission03

- 일시: 2026-03-03
- 대상: python_level1_mission03 (프롬프트 관리 프로그램)
- 방법: 모범 답안 안정성(3회 반복), AI 트랩 시나리오 시뮬레이션, Pass/Fail 경계값 분석, 커스텀 구현 엣지 케이스, 코드 레벨 버그 탐색

---

## 1. 미션 개요

| 항목 | 값 |
|------|-----|
| 난이도 | 1 (기본기 확인) |
| 제한시간 | 900초 (15분) |
| 합격 기준 | 70점 이상 (Validator별 AND 조건) |
| 제출물 | `prompt_manager.py` (1개 파일) |
| Validator 수 | 3개 (PMStructure 25, PMCLI 45, PMInteraction 30) |
| CheckItem 수 | 16개 |
| AI 트랩 수 | 3개 (17점) |

---

## 2. 전체 결과 요약

| 항목 | 결과 |
|------|------|
| 모범 답안 안정성 | 100점 x3 ✅ |
| 발견된 버그 | 3건 (3건 모두 수정 완료) |
| 미수정 이슈 | 0건 |
| 알려진 제한사항 | 1건 (문서화) |

---

## 3. 모범 답안 재현성 (3회 반복)

```
Run 1: 100.00점 ✅ PASS
Run 2: 100.00점 ✅ PASS
Run 3: 100.00점 ✅ PASS
```

16개 CheckItem 모두 PASS, 3개 Validator 모두 100%. 결정적(deterministic) 실행 확인.

---

## 4. AI 트랩 시뮬레이션

### 4-1. 테스트 제출물 구성

| 시나리오 | 디렉토리 | 트랩 내용 |
|---------|---------|----------|
| trap_search_content | `/tmp/ds_qa_tests/trap_search_content/` | 제목만 검색, content 미포함 |
| trap_add_validation | `/tmp/ds_qa_tests/trap_add_validation/` | 빈 제목 검증 없이 바로 추가 |
| trap_favorite_toggle | `/tmp/ds_qa_tests/trap_favorite_toggle/` | `p["favorite"] = True` (토글 아님) |
| trap_all_fail | `/tmp/ds_qa_tests/trap_all_fail/` | 3개 트랩 모두 포함 |
| template_only | `/tmp/ds_qa_tests/template_only/` | 템플릿 그대로 제출 (TODO 미구현) |
| custom_menu | `/tmp/ds_qa_tests/custom_menu/` | 정상 구현이나 "===" 없는 커스텀 메뉴 |
| custom_menu_trap | `/tmp/ds_qa_tests/custom_menu_trap/` | 커스텀 메뉴 + favorite_toggle 트랩 |

### 4-2. 트랩 시뮬레이션 결과 (최종, 버그 수정 후)

| 시나리오 | 점수 | 결과 | 실패 항목 |
|---------|------|------|----------|
| 모범 답안 | 100점 | ✅ PASS | 없음 |
| search_content 트랩 | 95점 | ✅ PASS | search_content (5점) |
| add_validation 트랩 | 95점 | ✅ PASS | add_validation (5점) |
| favorite_toggle 트랩 | 93점 | ✅ PASS | favorite_toggle (7점) |
| 3개 트랩 모두 실패 | 83점 | ✅ PASS | search_content(5) + add_validation(5) + favorite_toggle(7) |
| 템플릿 그대로 | 50점 | ❌ FAIL | 7개 항목 |
| 커스텀 메뉴 (정상) | 100점 | ✅ PASS | 없음 |
| 커스텀 메뉴 + fav 트랩 | 93점 | ✅ PASS | favorite_toggle (7점) |

### 4-3. 30% 규칙 검증

AI 트랩이 해당 Validator 총점의 30% 미만이어야 단독 FAIL을 방지합니다.

| Validator | 총점 | 트랩 배점 | 비율 | 트랩 실패 시 Validator 점수 |
|-----------|------|---------|------|---------------------------|
| PMCLIValidator | 45 | search_content(5) + add_validation(5) = 10 | 22.2% ✅ | 77.8% (>70%) |
| PMInteractionValidator | 30 | favorite_toggle(7) = 7 | 23.3% ✅ | 76.7% (>70%) |
| PMStructureValidator | 25 | 없음 | 0% ✅ | 100% |

모든 Validator에서 30% 규칙을 만족합니다. 3개 트랩이 모두 실패해도 83점으로 PASS 가능 (난이도 1 특성).

### 4-4. Validator별 상세 점수 (3개 트랩 모두 실패 시)

| Validator | 점수 | 결과 |
|-----------|------|------|
| PMStructureValidator | 100.0% (25/25) | ✅ PASS |
| PMCLIValidator | 77.78% (35/45) | ✅ PASS |
| PMInteractionValidator | 76.67% (23/30) | ✅ PASS |
| **overall** | **83점** | **✅ PASS** |

---

## 5. 발견 및 수정된 버그 (3건)

### Bug 1: favorite_toggle 초기 구현 — 메뉴 텍스트 간섭 [HIGH, 수정 완료]

- **발견 시점**: 모범 답안 채점 (초기 구현 직후)
- **증상**: 모범 답안이 93점 (favorite_toggle FAIL)
- **원인**: 라인 기반 스캔에서 메뉴 항목 "7. 즐겨찾기 목록"이 `in_favorites_section=True` 트리거. 이후 manage_favorite 확인 메시지에서 "블로그 글 작성 도우미" 탐지 → 거짓 양성
- **수정**: `output.split("=== ")` 섹션 파싱 방식으로 변경
- **수정 파일**: `pm_interaction_validator.py`

### Bug 2: add_validation stdin 부족 — 트랩 미작동 [HIGH, 수정 완료]

- **발견 시점**: QA 트랩 시뮬레이션
- **증상**: `trap_add_validation` 제출물이 100점 (트랩 미탐지)
- **원인**: 초기 stdin `"1\n\n2\n0\n"` (4줄)에서:
  - **정상 구현**: 빈 제목 → `return` → 메뉴2(목록) → 종료 (3줄 소비)
  - **트랩 구현**: 빈 제목 → 내용("2") → 카테고리("0") → 메뉴(EOF!) → `EOFError`
  - 트랩 구현이 `list_prompts`를 실행하기 전에 EOF 발생하여 "4." 패턴이 출력되지 않음
- **수정**: stdin을 `"1\n\n2\n0\n2\n0\n"` (6줄)으로 변경. 충분한 입력 제공으로 트랩 구현도 `list_prompts`까지 도달
  - **정상**: 빈 제목(return) → 메뉴2(목록: 3개) → 종료. extra "2\n0\n" 미소비
  - **트랩**: 빈 제목 → 내용("2") → 카테고리("0") → 메뉴2(목록: **4개**!) → 종료. "4. [기타] " 패턴 탐지
- **수정 파일**: `pm_cli_validator.py`

### Bug 3: favorite_toggle fallback — 커스텀 메뉴 미지원 [MEDIUM, 수정 완료]

- **발견 시점**: QA 커스텀 메뉴 엣지 테스트
- **증상**: "===" 없는 커스텀 메뉴 + favorite_toggle 트랩 조합이 100점 (트랩 미탐지)
- **원인**: `output.split("=== ")` 결과가 1개 요소만 존재. fallback으로 "마지막 1/3" 검사를 수행하나, 메뉴 3회 출력(~27줄)에 비해 `show_favorites` 출력(1-2줄)이 전체 출력의 중간 1/3에 위치하여 마지막 1/3에 포함되지 않음
- **수정**: 전체 접근 방식 변경. `show_favorites`는 `"제목 ⭐"` 형식으로 출력하지만 `manage_favorite` 확인 메시지는 `⭐`를 포함하지 않는 점을 활용. 모든 줄에서 "블로그 글 작성 도우미" + "⭐" 동시 존재 여부를 검사:
  ```python
  for line in output.split("\n"):
      if "블로그 글 작성 도우미" in line and "⭐" in line:
          return False  # 토글 실패 (즐겨찾기가 해제되지 않음)
  return True
  ```
- **장점**: 메뉴 형식(===, [, 커스텀 헤더 등)에 완전히 독립적. 출력 위치나 줄 수에 무관
- **잠재 리스크**: 학생이 `manage_favorite` 함수에서 "블로그 글 작성 도우미 ⭐"를 포함하는 확인 메시지를 출력하면 거짓 양성. 하지만 이는 매우 비현실적 (확인 메시지에 ⭐를 붙이는 관례가 없음)
- **수정 파일**: `pm_interaction_validator.py`

---

## 6. 알려진 제한사항 (1건)

### 6-1. [LOW] list_prompts의 ⭐와 favorite_toggle 검사 간 이론적 충돌

- **시나리오**: 학생이 `manage_favorite` 후 바로 `list_prompts`를 호출하는 커스텀 플로우를 구현한 경우
- **현재 상태**: `favorite_toggle` 검사의 stdin은 `"6\n1\n7\n0\n"` (관리→즐겨찾기목록→종료)이므로 `list_prompts`는 호출되지 않아 문제 없음
- **위험도**: 매우 낮음. stdin 기반 테스트이므로 학생 코드가 예상 외 메뉴를 추가하지 않는 한 영향 없음

---

## 7. 템플릿 안전성 검증

템플릿(TODO 미구현)을 그대로 제출했을 때의 결과:

| Validator | 점수 | 결과 |
|-----------|------|------|
| PMStructureValidator | 100.0% (25/25) | ✅ PASS |
| PMCLIValidator | 22.22% (10/45) | ❌ FAIL |
| PMInteractionValidator | 26.67% (8/30) | ❌ FAIL |
| **overall** | **50점** | **❌ FAIL** |

- PMStructureValidator가 PASS하는 이유: 템플릿에 이미 `def` 5개 이상, list+dict 초기 데이터 포함
- 전체적으로 50점 FAIL → 템플릿 그대로 제출로는 합격 불가 ✅

---

## 8. 트랩 독립성 검증

각 트랩의 실패가 다른 CheckItem에 연쇄 영향을 주지 않는지 확인합니다.

| 트랩 | 영향받는 항목 | 독립성 |
|------|------------|--------|
| search_content | search_content만 FAIL | ✅ 독립 |
| add_validation | add_validation만 FAIL | ✅ 독립 |
| favorite_toggle | favorite_toggle만 FAIL | ✅ 독립 |

- `search_content` 트랩 (content 미검색)은 `search_title` 검사와 독립 (별도 키워드 "블로그" vs "SEO")
- `add_validation` 트랩 (빈 제목 미검증)은 `add_prompt` 검사와 독립 (별도 세션, 정상 제목 사용)
- `favorite_toggle` 트랩 (True 고정)은 `favorite_list` 검사와 독립 (별도 세션, 초기 상태에서만 검사)

---

## 9. 커스텀 구현 엣지 케이스

### 9-1. 커스텀 메뉴 헤더 ("===" 미사용)

- **테스트**: `"[ 프롬프트 관리 ]"` 형식의 커스텀 메뉴
- **정상 구현**: 100점 ✅ (Bug 3 수정 후)
- **트랩 포함**: 93점 ✅ (favorite_toggle 정상 탐지)

### 9-2. 추가 확인 메시지 유무

- 일부 구현에서 `add_prompt` 후 "추가되었습니다" 메시지를 출력하거나 생략할 수 있음
- 모든 검사가 결과 데이터(목록 항목, 키워드 존재 여부)를 확인하므로 메시지 유무에 무관하게 동작 ✅

---

## 10. 수정 커밋 내역

| 수정 시점 | 파일 | 설명 |
|----------|------|------|
| 초기 구현 후 즉시 | `pm_interaction_validator.py` | Bug 1: favorite_toggle 메뉴 텍스트 간섭 수정 |
| QA 중 | `pm_cli_validator.py` | Bug 2: add_validation stdin 부족 수정 |
| QA 중 | `pm_interaction_validator.py` | Bug 3: favorite_toggle fallback 커스텀 메뉴 대응 |

---

## 11. 최종 QA 테스트 매트릭스

| # | 테스트 시나리오 | 기대값 | 실제값 | 결과 |
|---|---------------|--------|--------|------|
| 1 | 모범 답안 (Run 1) | 100 PASS | 100 PASS | ✅ |
| 2 | 모범 답안 (Run 2) | 100 PASS | 100 PASS | ✅ |
| 3 | 모범 답안 (Run 3) | 100 PASS | 100 PASS | ✅ |
| 4 | search_content 트랩 | 95 PASS | 95 PASS | ✅ |
| 5 | add_validation 트랩 | 95 PASS | 95 PASS | ✅ |
| 6 | favorite_toggle 트랩 | 93 PASS | 93 PASS | ✅ |
| 7 | 3개 트랩 모두 실패 | 83 PASS | 83 PASS | ✅ |
| 8 | 템플릿 그대로 제출 | FAIL | 50 FAIL | ✅ |
| 9 | 커스텀 메뉴 (정상) | 100 PASS | 100 PASS | ✅ |
| 10 | 커스텀 메뉴 + fav 트랩 | 93 PASS | 93 PASS | ✅ |

**10/10 테스트 통과. QA 완료.**
