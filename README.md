# 코디세이 시험 자동 채점 시스템

PBL 교육 후 학습 성취도를 측정하는 **플러그인 기반 코드 채점 프레임워크**

---

## 개요

이 시스템은 **코디세이** PBL 교육 과정을 완료한 학습자의 실습 성취도를 자동으로 채점합니다.
현재 **리눅스 시스템 관리**와 **Python 코딩 시험** 두 가지 미션 카테고리를 지원하며,
새로운 도메인(알고리즘, 데이터베이스, 웹 등)으로 자유롭게 확장할 수 있습니다.

### 주요 특징

- **플러그인 아키텍처** — `BaseValidator`를 상속하면 어떤 유형의 미션이든 검증기를 추가할 수 있음
- **체크리스트 기반 채점** — 항목별 배점·힌트·AI 함정 플래그로 명확한 평가 기준 제공
- **AI 함정 요소** — 학습자가 AI 도구에 의존하지 않고 핵심 개념을 이해했는지 검증
- **자동 결과 리포팅** — JSON + Markdown 형식의 상세 채점 리포트 자동 생성
- **최소 의존성** — PyYAML 외 Python 표준 라이브러리만 사용

---

## 시스템 아키텍처

### 핵심 채점 흐름

```
CLI (run_grading.py)
  │
  ▼
config.yaml 로드 (미션 설정)
  │
  ▼
Grader (채점 엔진)
  │  importlib로 Validator 동적 로딩
  ▼
┌──────────────────────────────────────┐
│  Validator.validate()                │
│    ├── setup()         초기화        │
│    ├── build_checklist()  항목 구성  │
│    ├── checklist.execute_all()  실행 │
│    └── teardown()      정리          │
└──────────────────────────────────────┘
  │  각 CheckItem의 validator() 함수 실행
  │  → pass/fail + 점수 집계
  ▼
ValidationResult
  ├── .json  (기계 처리용)
  └── .md    (사람 열람용)
```

### 디렉토리 구조

```
linux-test/
│
├── core/                              # 프레임워크 코어 (미션 무관)
│   ├── base_validator.py              #   추상 검증기 — 모든 플러그인의 부모 클래스
│   ├── check_item.py                  #   개별 채점 항목 (id, 배점, 검증 함수, AI 트랩 플래그)
│   ├── checklist.py                   #   CheckItem 컬렉션 — 전체 점수 집계
│   ├── grader.py                      #   채점 엔진 — config.yaml 기반 Validator 동적 로딩
│   └── validation_result.py           #   결과 집계 + JSON/Markdown 리포트 생성
│
├── plugins/                           # 미션별 검증 플러그인
│   ├── linux/validators/              #   리눅스 시스템 관리 검증기
│   │   ├── ssh_validator.py           #     SSH 보안 설정 검증
│   │   ├── firewall_validator.py      #     방화벽 설정 검증
│   │   ├── account_validator.py       #     계정/그룹 관리 검증
│   │   └── script_validator.py        #     관제 스크립트 검증
│   │
│   └── python/validators/             #   Python 코딩 시험 검증기
│       ├── _helpers.py                #     공통 유틸 (학생 모듈 import, AST 파싱)
│       ├── model_validator.py         #     데이터 모델 검증 (25점)
│       ├── pattern_validator.py       #     코딩 패턴 검증 (25점)
│       ├── cli_validator.py           #     CLI 동작 검증 (30점)
│       └── persistence_validator.py   #     데이터 저장 검증 (20점)
│
├── missions/                          # 미션 정의
│   ├── linux/level1/mission01/        #   리눅스 Level 1 미션
│   │   ├── config.yaml                #     검증기 목록 + 실행 설정
│   │   ├── problem.md                 #     학생용 문제지
│   │   └── solution.md                #     모범 답안
│   │
│   └── python/level1/mission01/       #   Python Level 1 미션 (도서 관리 시스템)
│       ├── config.yaml                #     검증기 목록 + AI 함정 정의
│       ├── problem.md                 #     시험 문제지
│       ├── solution.md                #     모범 답안 (코드 포함)
│       └── template/                  #     학생 배포용 스켈레톤
│           ├── models.py              #       Book dataclass 스켈레톤
│           ├── filters.py             #       제너레이터/데코레이터 스켈레톤
│           ├── storage.py             #       파일 I/O 스켈레톤
│           └── cli.py                 #       argparse CLI 스켈레톤
│
├── scripts/
│   └── run_grading.py                 # 메인 실행 스크립트 (CLI 진입점)
│
├── utils/
│   └── config_loader.py               # 미션 설정 YAML 로더
│
├── results/                           # 채점 결과 저장 디렉토리 (자동 생성)
├── submissions/                       # 학생 제출물 디렉토리
├── tests/                             # 테스트 (구현 예정)
└── requirements.txt                   # 의존성: PyYAML
```

---

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 채점 실행

```bash
# 리눅스 미션 (실제 리눅스 환경에서만 동작)
python3 scripts/run_grading.py \
  --student-id student_001 \
  --mission-id linux_level1_mission01

# Python 미션 (--submission-dir로 학생 제출물 경로 지정)
python3 scripts/run_grading.py \
  --student-id student_001 \
  --mission-id python_level1_mission01 \
  --submission-dir /path/to/student/submission
```

### 3. 결과 확인

```bash
# results/ 디렉토리에 자동 저장
cat results/student_001_python_level1_mission01_*.md
```

---

## 현재 구현된 미션

### 리눅스 Level 1 — 시스템 보안 기초 설정

> 실제 리눅스 환경에서 시스템 명령어를 실행하여 검증합니다.

| 영역 | 배점 | 주요 검증 항목 |
|------|------|---------------|
| SSH 보안 설정 | 30점 | 포트 20022 변경, Root 로그인 차단 |
| 방화벽 설정 | 20점 | UFW 활성화, 포트 허용 |
| 계정 관리 | 20점 | 계정/그룹 생성 |
| 관제 스크립트 | 30점 | 스크립트 존재 + 실행 권한 |

---

### Python Level 1 — 도서 관리 시스템 코딩 시험

> PBL에서 배운 개념(dataclass, 제너레이터, 데코레이터, 파일 I/O, CLI)을 **새로운 도메인**에 적용하는 코딩 시험입니다.

**시험 흐름**:
1. 교사가 `template/` 디렉토리의 스켈레톤 파일을 학생에게 배포
2. 학생이 15분 내에 TODO 부분을 구현하여 제출
3. 자동 채점기가 학생 코드를 분석 (AST 정적 분석 + import 동적 테스트 + subprocess CLI 검증)

#### 채점 항목 (총 100점, 합격 70점 이상)

| Validator | 배점 | 검증 항목 | 검증 방식 |
|-----------|------|----------|----------|
| **ModelValidator** | 25점 | `@dataclass` 사용, 필수 필드, 타입 힌트, `__post_init__` 유효성 | AST + import |
| **PatternValidator** | 25점 | yield 제너레이터, 사용자 정의 데코레이터, 타입 힌트, Any 비율 | AST + import + inspect |
| **CLIValidator** | 30점 | cli.py 존재, `--help`, add/list 서브커맨드, 크래시 방지 | subprocess |
| **PersistenceValidator** | 20점 | save/load 왕복 무결성, 파일 형식, pickle 미사용, 필수 필드 | import + 파일 파싱 |

#### AI 함정 요소 (4개)

학습자가 AI 도구에 의존하면 흔히 틀리는 항목을 의도적으로 포함합니다:

| 항목 | AI가 흔히 하는 실수 | 올바른 구현 |
|------|-------------------|------------|
| `pattern_yield` | `return [...]` 리스트 반환 | `yield`로 하나씩 반환 |
| `pattern_no_any` | `Any` 타입 남용 | `str`, `int`, `List[Book]` 등 구체적 타입 |
| `cli_help` | argparse 미사용 (sys.argv 파싱) | `argparse.ArgumentParser` 사용 |
| `persist_no_pickle` | `import pickle` 사용 | `json`/`csv` 텍스트 기반 직렬화 |

#### 시험 템플릿 구조

학생에게 배포하는 `template/` 디렉토리:

```
template/
├── models.py    # Book dataclass — TODO: 필드 정의, __post_init__, to_dict/from_dict
├── filters.py   # 검색/필터링 — TODO: yield 제너레이터, 데코레이터 구현
├── storage.py   # 파일 I/O — TODO: JSONL save/load (pickle 금지)
└── cli.py       # CLI — TODO: argparse 서브커맨드 (add, list, search)
```

---

## 새 미션 추가 방법

### 1. 미션 디렉토리 생성

```bash
mkdir -p missions/{category}/level{N}/mission{NN}
```

### 2. 미션 파일 작성

| 파일 | 용도 |
|------|------|
| `config.yaml` | 미션 메타데이터 + 사용할 Validator 목록 등록 |
| `problem.md` | 학생용 문제지 |
| `solution.md` | 모범 답안 |
| `template/` | (선택) 학생 배포용 스켈레톤 코드 |

### 3. 검증기 작성

`plugins/{category}/validators/` 아래에 `BaseValidator`를 상속하는 클래스를 구현합니다:

```python
from core.base_validator import BaseValidator
from core.check_item import CheckItem

class MyValidator(BaseValidator):
    def setup(self) -> None:
        """검증 전 초기화 (학생 코드 import, 파일 수집 등)"""
        self.submission_dir = self.config.get("submission_dir", "")

    def build_checklist(self) -> None:
        """채점 항목 등록"""
        self.checklist.add_item(CheckItem(
            id="my_check",
            description="검증 설명",
            points=10,
            validator=self._my_check,
            hint="실패 시 표시할 힌트",
            ai_trap=False,  # AI 함정 여부
        ))

    def teardown(self) -> None:
        """정리 작업"""
        pass

    def _my_check(self) -> bool:
        """실제 검증 로직 — True면 통과, False면 실패"""
        return True
```

### 4. config.yaml에 등록

```yaml
name: "미션 이름"
passing_score: 70

validators:
  - module: "plugins.{category}.validators.my_validator"
    class: "MyValidator"
    weight: 100
```

---

## 코어 프레임워크 API

### BaseValidator (추상 클래스)

모든 검증기가 반드시 상속해야 하는 기반 클래스입니다.

```python
class BaseValidator(ABC):
    def __init__(self, mission_config: Dict[str, Any])  # config.yaml 데이터 수신
    def setup(self) -> None           # 추상 — 초기화
    def build_checklist(self) -> None  # 추상 — CheckItem 등록
    def teardown(self) -> None         # 추상 — 정리
    def validate(self) -> Dict         # 실행: setup → build → execute_all → teardown
```

### CheckItem (데이터클래스)

개별 채점 항목을 표현합니다.

```python
@dataclass
class CheckItem:
    id: str                          # 고유 ID (예: "model_dataclass")
    description: str                 # 설명 (예: "Book이 @dataclass인지 확인")
    points: int                      # 배점
    validator: Callable[[], bool]    # 검증 함수 — True면 통과
    hint: Optional[str] = None       # 실패 시 힌트 메시지
    ai_trap: bool = False            # AI 함정 플래그
```

### Grader (채점 엔진)

`config.yaml`의 `validators` 목록을 읽어 `importlib`로 동적 로딩 후 순차 실행합니다.

```python
grader = Grader(student_id="test", mission_id="python_level1_mission01", mission_config=config)
result = grader.execute()  # ValidationResult 반환
```

### ValidationResult (결과 집계)

모든 Validator 결과를 모아서 최종 점수와 합격 여부를 계산합니다.

- `to_json()` → JSON 문자열 (기계 처리용)
- `to_markdown()` → Markdown 리포트 (사람 열람용)
- 합격 조건: **모든** Validator가 개별 합격선(기본 70점)을 넘어야 최종 PASS

---

## 채점 결과 예시

### JSON 출력

```json
{
  "student_id": "student_001",
  "mission_id": "python_level1_mission01",
  "timestamp": "2026-02-23T13:15:00.000000",
  "overall_passed": true,
  "overall_score": 100.0,
  "results": [
    {
      "validator": "ModelValidator",
      "result": {
        "earned_points": 25,
        "total_points": 25,
        "score": 100.0,
        "is_passed": true,
        "items": [...]
      }
    }
  ]
}
```

### Markdown 리포트

```
# 채점 결과 리포트

- **학습자 ID**: student_001
- **최종 결과**: ✅ PASS
- **종합 점수**: 100.0점

## 1. ModelValidator — 25 / 25
✅ [7점] Book 클래스가 @dataclass로 정의되어 있는지 확인
✅ [6점] Book에 필수 필드가 있는지 확인
✅ [5점] Book 필드에 타입 힌트가 적용되어 있는지 확인
✅ [7점] price < 0일 때 ValueError가 발생하는지 확인
```

---

## 문제 해결

### ImportError 발생 시

반드시 **프로젝트 루트 디렉토리**에서 실행하세요. `run_grading.py`가 프로젝트 루트를 `sys.path`에 추가합니다.

```bash
cd /path/to/linux-test
python3 scripts/run_grading.py ...
```

### Python 미션에서 학생 코드 import 오류

`--submission-dir` 경로가 절대 경로인지, 해당 디렉토리에 학생 파일(`models.py` 등)이 존재하는지 확인하세요.

```bash
ls /path/to/submission/
# models.py  filters.py  storage.py  cli.py 가 있어야 함
```

### 리눅스 미션이 macOS에서 실패

리눅스 미션 검증기(`ssh_validator`, `firewall_validator` 등)는 `subprocess`로 `sshd`, `ufw` 등 리눅스 시스템 명령어를 호출합니다. macOS에서는 프레임워크 구조만 확인 가능하며, 실제 검증은 리눅스 환경에서 수행해야 합니다.

---

## 기술 스택

| 항목 | 상세 |
|------|------|
| 언어 | Python 3.8+ |
| 외부 의존성 | PyYAML (설정 파싱) |
| 표준 라이브러리 | `ast`, `subprocess`, `importlib`, `os`, `json`, `csv`, `pathlib`, `dataclasses`, `abc`, `inspect`, `tempfile`, `glob` |
| 코딩 컨벤션 | 변수/함수: 영어 snake_case, 문서/주석/커밋: 한국어 |

---

## 향후 계획

- [ ] Python Level 2 미션 추가 (웹 API, 데이터베이스 등)
- [ ] 알고리즘/자료구조 미션 카테고리
- [ ] Docker 샌드박스 통합 (학생 코드 격리 실행)
- [ ] 웹 기반 채점 대시보드
- [ ] 실시간 채점 API
- [ ] `tests/` 유닛 테스트 구현

---

## 기여 가이드

새로운 미션이나 검증기를 추가하려면:

1. `plugins/{category}/validators/`에 `BaseValidator`를 상속하는 검증기 작성
2. `missions/{category}/level{N}/mission{NN}/`에 `config.yaml`, `problem.md`, `solution.md` 작성
3. config.yaml의 `validators` 목록에 모듈 경로와 클래스명 등록
4. 모범 답안으로 채점 실행하여 100점 확인
5. 스켈레톤 제출로 낮은 점수 확인
6. Pull Request 제출

---

## 라이선스

MIT License
