# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

PBL(Problem-Based Learning) 교육 후 학습자의 학습 성취도를 자동 채점하는 **플러그인 기반 검증 프레임워크**. 현재 리눅스 시스템 관리 미션을 지원하며, 알고리즘/자료구조/데이터베이스 등으로 확장 가능한 구조.

## 실행 명령어

```bash
# 의존성 설치
pip3 install -r requirements.txt

# 채점 실행
python3 scripts/run_grading.py --student-id <학생ID> --mission-id linux_level1_mission01 --output-dir results
```

테스트 디렉토리(`tests/`)는 존재하나 아직 구현된 테스트 없음.

## 아키텍처

**핵심 흐름**: CLI → Grader → 동적 Validator 로딩 → CheckItem 실행 → ValidationResult (JSON/Markdown 리포트)

### core/
- `base_validator.py` — 모든 Validator의 추상 기반 클래스. `setup()`, `build_checklist()`, `teardown()`, `validate()` 인터페이스 정의
- `check_item.py` — 개별 채점 항목. `validator: Callable[[], bool]` 함수로 pass/fail 판정
- `checklist.py` — CheckItem 컬렉션. 전체 점수 집계
- `grader.py` — 메인 채점 엔진. `importlib`로 config.yaml에 정의된 Validator를 동적 로딩
- `validation_result.py` — 결과 집계 및 JSON/Markdown 리포트 생성

### plugins/
미션 유형별 Validator 구현체. 현재 `plugins/linux/validators/`에 SSH, Firewall, Account, Script 검증기 구현.

### missions/
미션 정의 디렉토리. 각 미션은 `config.yaml`(메타데이터 + Validator 설정), `problem.md`(학생용 문제), `solution.md`(모범답안)으로 구성.
경로 패턴: `missions/{category}/level{N}/mission{NN}/`

### 결과물
`results/` 디렉토리에 `{student_id}_{mission_id}_{timestamp}.json`과 `.md` 파일 생성. 70점 이상 Pass.

## 새 미션/Validator 추가 방법

1. `missions/{category}/level{N}/mission{NN}/` 디렉토리에 `config.yaml`, `problem.md`, `solution.md` 생성
2. `plugins/{category}/validators/`에 `BaseValidator`를 상속하는 Validator 클래스 구현
3. `config.yaml`의 `validators` 목록에 모듈 경로와 클래스명 등록

## 코딩 컨벤션

- **언어**: 코드 변수/함수명은 영어(snake_case), 문서/주석/커밋은 한국어
- **의존성**: PyYAML 외에는 Python 표준 라이브러리만 사용 (subprocess, os, re, json, pathlib, dataclasses, abc)
- **AI 트랩**: `CheckItem`의 `ai_trap=True` 플래그로 AI가 흔히 틀리는 항목 표시 (예: PermitRootLogin `prohibit-password` vs `no`, 파일 권한 `644` vs `755`)
- **subprocess 호출**: 5초 타임아웃 적용
- **리눅스 미션 검증은 실제 리눅스 환경 필요** (macOS에서는 프레임워크 동작만 확인 가능)
