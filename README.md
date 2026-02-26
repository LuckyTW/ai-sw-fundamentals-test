# 코디세이 시험 자동 채점 시스템

PBL 교육 후 학습 성취도를 측정하는 **플러그인 기반 코드 채점 프레임워크**

---

## 개요

이 시스템은 **코디세이** PBL 교육 과정을 완료한 학습자의 실습 성취도를 자동으로 채점합니다.
리눅스 시스템 관리, Python 코딩, 자료구조, 알고리즘, 데이터베이스 등 다양한 미션 카테고리를 지원하며,
새로운 도메인으로 자유롭게 확장할 수 있습니다.

### 주요 특징

- **플러그인 아키텍처** — `BaseValidator`를 상속하면 어떤 유형의 미션이든 검증기를 추가할 수 있음
- **체크리스트 기반 채점** — 항목별 배점·힌트·AI 함정 플래그로 명확한 평가 기준 제공
- **AI 함정 요소** — 학습자가 AI 도구에 의존하지 않고 핵심 개념을 이해했는지 검증
- **자동 결과 리포팅** — JSON + Markdown 형식의 상세 채점 리포트 자동 생성
- **크로스 플랫폼** — 모든 미션이 macOS/Linux에서 동작 (subprocess + tmpdir 기반)
- **최소 의존성** — PyYAML 외 Python 표준 라이브러리만 사용

### 프로젝트 현황

| 구분 | 수치 |
|------|------|
| 총 미션 수 | 6개 (Linux 1, Python 2, DS 1, Algo 1, DB 1) |
| 총 Validator 클래스 | 17개 |
| 총 CheckItem 수 | 81개 |
| 총 AI 트랩 항목 | 24개 |

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
│   ├── linux/validators/              #   리눅스 미션용 (1개)
│   │   └── linux_auditor_validator.py #     보안 감사 도구 (subprocess+tmpdir 기반)
│   ├── python/validators/             #   Python 미션용 (5개 + 헬퍼)
│   │   ├── _helpers.py                #     공통 유틸 (import_student_module 등)
│   │   ├── model_validator.py
│   │   ├── pattern_validator.py
│   │   ├── cli_validator.py
│   │   ├── persistence_validator.py
│   │   └── log_analyzer_validator.py
│   ├── ds/validators/                 #   자료구조 미션용 (4개)
│   │   ├── structure_validator.py     #     AST 분석형
│   │   ├── basic_command_validator.py #     subprocess형
│   │   ├── lru_validator.py           #     subprocess형
│   │   └── ttl_validator.py           #     Popen형
│   ├── algo/validators/               #   알고리즘 미션용 (4개 + 헬퍼)
│   │   ├── _helpers.py                #     공통 유틸 (generate_hash, parse_responses)
│   │   ├── structure_validator.py
│   │   ├── basic_command_validator.py
│   │   ├── graph_algorithm_validator.py
│   │   └── search_sort_validator.py
│   └── db/validators/                 #   데이터베이스 미션용 (3개 + 데이터)
│       ├── _data.py                   #     CSV 데이터 상수 + write_csv_files() 헬퍼
│       ├── schema_validator.py        #     DB 스키마 검증
│       ├── analysis_validator.py      #     리포트 분석 섹션 검증
│       └── report_validator.py        #     리포트 형식/요약 검증
│
├── missions/                          # 미션 정의 (config.yaml + problem.md + solution.md)
│   ├── linux/level2/mission01/        #   리눅스 서버 보안 감사 도구
│   ├── python/level1/mission01/       #   Python 도서 관리 시스템
│   │   └── template/
│   ├── python/level1/mission02/       #   서버 접근 로그 분석기
│   │   └── template/
│   ├── ds/level1/mission01/           #   Mini LRU 캐시
│   │   └── template/
│   ├── algo/level2/mission01/         #   Mini Git 커밋 그래프 시뮬레이터
│   │   └── template/
│   └── db/level3/mission01/           #   커밋 이력 DB 분석기
│       └── template/
│
├── sample_submission/                 # python_level1_mission01 정답 예시
├── sample_submission_python02/        # python_level1_mission02 정답 예시
├── sample_submission_linux/           # linux_level2_mission01 정답 예시
├── sample_submission_ds/              # ds_level1_mission01 정답 예시
├── sample_submission_algo/            # algo_level2_mission01 정답 예시
├── sample_submission_db/              # db_level3_mission01 정답 예시
│
├── scripts/
│   └── run_grading.py                 # 메인 실행 스크립트 (CLI 진입점)
├── utils/
│   └── config_loader.py               # 미션 설정 YAML 로더
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
# 공통 형식
python3 scripts/run_grading.py \
  --student-id <학생ID> \
  --mission-id <미션ID> \
  --submission-dir /path/to/submission
```

### 3. 샘플 정답으로 테스트

```bash
# Python 도서 관리 시스템 (난이도 1)
python3 scripts/run_grading.py --student-id sample --mission-id python_level1_mission01 --submission-dir sample_submission

# Python 서버 로그 분석기 (난이도 1)
python3 scripts/run_grading.py --student-id sample --mission-id python_level1_mission02 --submission-dir sample_submission_python02

# 리눅스 보안 감사 도구 (난이도 2)
python3 scripts/run_grading.py --student-id sample --mission-id linux_level2_mission01 --submission-dir sample_submission_linux

# Mini LRU 캐시 (난이도 1)
python3 scripts/run_grading.py --student-id sample --mission-id ds_level1_mission01 --submission-dir sample_submission_ds

# Mini Git 커밋 그래프 시뮬레이터 (난이도 2)
python3 scripts/run_grading.py --student-id sample --mission-id algo_level2_mission01 --submission-dir sample_submission_algo

# 커밋 이력 DB 분석기 (난이도 3)
python3 scripts/run_grading.py --student-id sample --mission-id db_level3_mission01 --submission-dir sample_submission_db
```

### 4. 결과 확인

```bash
# results/ 디렉토리에 JSON + Markdown 자동 저장
cat results/sample_python_level1_mission01_*.md
```

---

## 구현된 미션 목록

### 미션 총괄

| 미션 ID | 카테고리 | 난이도 | 시간 | CheckItems | AI 트랩 | 제출물 |
|---------|---------|--------|------|-----------|---------|--------|
| `python_level1_mission01` | Python | 1 | 15분 | 17 | 4 | models.py, filters.py, storage.py, cli.py |
| `python_level1_mission02` | Python | 1 | 15분 | 7 | 3 | log_analyzer.py |
| `linux_level2_mission01` | Linux | 2 | 25분 | 7 | 4 | auditor.py |
| `ds_level1_mission01` | 자료구조 | 1 | 15분 | 15 | 4 | lru_cache.py, cli.py |
| `algo_level2_mission01` | 알고리즘 | 2 | 25분 | 16 | 4 | mini_git.py, cli.py |
| `db_level3_mission01` | 데이터베이스 | 3 | 40분 | 19 | 5 | commit_analyzer.py |

---

### 1. Python Level 1 — 도서 관리 시스템 (`python_level1_mission01`)

> PBL에서 배운 dataclass, 제너레이터, 데코레이터, 파일 I/O, CLI를 새로운 도메인에 적용하는 코딩 시험

**검증 구조**: 4개 Validator, 17개 CheckItem

| Validator | 가중치 | 검증 방식 | 핵심 항목 |
|-----------|--------|----------|----------|
| `ModelValidator` | 25 | AST + import | @dataclass, 필드, 타입 힌트, __post_init__ |
| `PatternValidator` | 25 | AST + inspect | yield 제너레이터, 데코레이터, Any 비율 |
| `CLIValidator` | 30 | subprocess | --help, add/list, 크래시 방지 |
| `PersistenceValidator` | 20 | import + 파일 | save/load 왕복, pickle 미사용 |

**AI 트랩** (4개):
- `pattern_yield` — yield 없이 리스트 반환
- `pattern_no_any` — Any 타입 30% 이상 남용
- `cli_help` — --help 옵션 미구현
- `persist_no_pickle` — pickle 사용 (보안 취약)

---

### 2. Python Level 1 — 서버 접근 로그 분석기 (`python_level1_mission02`)

> CSV 로그 데이터를 파싱하여 IP 통계, 상태코드 비율, 느린 엔드포인트를 분석하는 리포트 생성

**검증 구조**: 1개 Validator, 7개 CheckItem

| Validator | 가중치 | 핵심 항목 |
|-----------|--------|----------|
| `LogAnalyzerValidator` | 100 | CSV 파싱, Top IP, 상태코드 비율, 느린 엔드포인트, 리포트 |

**AI 트랩** (3개, 합계 25점):
- `ip_order` — 동점 IP를 오름차순이 아닌 **내림차순**으로 정렬
- `status_ratio` — 1xx 상태코드를 포함하여 비율 계산
- `slow_values` — response_time 소수점(33.7)을 정확히 처리

---

### 3. Linux Level 2 — 리눅스 서버 보안 감사 도구 (`linux_level2_mission01`)

> 6개의 리눅스 설정 파일 스냅샷을 분석하여 보안 취약점을 탐지하는 감사 리포트 생성

**검증 구조**: 1개 Validator, 7개 CheckItem

| Validator | 가중치 | 핵심 항목 |
|-----------|--------|----------|
| `LinuxAuditorValidator` | 100 | 설정 파싱, SSH/방화벽/계정/권한 감사, 로그 통계, 리포트 |

**AI 트랩** (4개, 합계 60점):
- `ssh_audit` — PermitRootLogin `prohibit-password`를 "안전"으로 오판 (정답: `no`만 안전)
- `firewall_audit` — 23/tcp(Telnet) 위험 포트 미탐지
- `account_audit` — agent-test의 agent-core 그룹 RBAC 위반 미탐지
- `permission_audit` — api_keys 775+agent-common 권한 위반 미탐지

---

### 4. DS Level 1 — Mini LRU 캐시 (`ds_level1_mission01`)

> 이중 연결 리스트 + 해시맵으로 LRU 캐시를 직접 구현하고, TTL 만료 관리와 Redis 스타일 CLI 구현

**검증 구조**: 4개 Validator, 15개 CheckItem

| Validator | 가중치 | 검증 방식 | 핵심 항목 |
|-----------|--------|----------|----------|
| `StructureValidator` | 25 | AST 분석 | Node 클래스, 금지 import, 연결 리스트 메서드 |
| `BasicCommandValidator` | 25 | subprocess | SET/GET/DEL/EXISTS/DBSIZE |
| `LRUValidator` | 30 | subprocess | LRU 제거, GET 갱신, INFO |
| `TTLValidator` | 20 | Popen | EXPIRE/TTL, lazy deletion |

**AI 트랩** (4개):
- `no_builtin_cache` — OrderedDict/deque/functools.lru_cache 사용 금지
- `output_format` — Python `True`/`None` 대신 Redis `OK`/`(nil)` 형식
- `lru_get_refresh` — GET도 LRU 접근 시간 갱신 필수 (move_to_front)
- `ttl_expired_get` — GET 시 만료 확인 후 삭제 (lazy deletion)

---

### 5. Algo Level 2 — Mini Git 커밋 그래프 시뮬레이터 (`algo_level2_mission01`)

> 커밋 DAG 자료구조를 구현하고, BFS 경로 탐색·merge sort 정렬·역 인덱스 검색 기능을 갖춘 Git 시뮬레이터

**검증 구조**: 4개 Validator, 16개 CheckItem

| Validator | 가중치 | 검증 방식 | 핵심 항목 |
|-----------|--------|----------|----------|
| `StructureValidator` | 20 | AST 분석 | Commit 클래스, sort 함수 금지, dict 저장소 |
| `BasicCommandValidator` | 20 | subprocess | INIT/COMMIT/BRANCH/SWITCH |
| `GraphAlgorithmValidator` | 35 | subprocess | PATH/ANCESTORS/LOG, 독립 세션 |
| `SearchSortValidator` | 25 | subprocess | SEARCH/LOG --sort-by |

**AI 트랩** (4개):
- `no_builtin_sort` — sorted()/list.sort() 금지 → merge sort 직접 구현
- `commit_parent_after_switch` — SWITCH 후 HEAD 브랜치의 최신 커밋이 부모
- `log_all_branches` — 저장소의 **모든** 커밋을 시간순 출력
- `path_cross_branch` — DAG를 **무방향 그래프**로 취급하여 BFS

---

### 6. DB Level 3 — 커밋 이력 DB 분석기 (`db_level3_mission01`)

> CSV 커밋 데이터를 SQLite DB로 적재하고, SQL 쿼리(JOIN, GROUP BY, Recursive CTE)로 분석하여 텍스트 리포트 생성. DB·Algo·Python 미션을 융합한 난이도 3 심화 통합 문제.

**검증 구조**: 3개 Validator, 19개 CheckItem

| Validator | 가중치 | 검증 방식 | 핵심 항목 |
|-----------|--------|----------|----------|
| `SchemaValidator` | 20 | DB 쿼리 | 테이블 생성, FK, root commit NULL, 데이터 적재, 인덱스 |
| `AnalysisValidator` | 45 | 라인 매칭 | 작성자/브랜치 집계, LEFT JOIN, DISTINCT, 히스토리 |
| `ReportValidator` | 35 | 라인 매칭 | 섹션 구조, 요약 통계, 파일 순위 |

**AI 트랩** (5개, 합계 33점):
- `root_commit_null` — parent_hash NOT NULL 정의 → root commit INSERT 실패
- `author_left_join` — INNER JOIN으로 커밋 없는 작성자(황서진) 제외
- `branch_no_commits` — INNER JOIN으로 커밋 없는 브랜치(hotfix/urgent) 제외
- `distinct_file_count` — COUNT(*)로 중복 파일 별도 카운트 → COUNT(DISTINCT) 필요
- `self_join_parent` — INNER JOIN self-reference → parent=NULL인 root commit 제외

**미션 융합 매핑**:
- **DB 미션** (핵심): 4테이블 스키마, PK/FK, JOIN, GROUP BY, Recursive CTE, 인덱스
- **Algo M1** (Mini Git): 커밋 그래프 DAG, 브랜치, self-referencing FK
- **Python M2** (로그 분석): CSV 파싱, 집계, Top-N, 텍스트 리포트

---

## AI 트랩 설계 철학

AI 트랩은 **AI가 흔히 범하는 실수를 의도적으로 유도하는 채점 항목**입니다.
학습자가 AI 도구의 출력물을 그대로 제출하면 Fail, 검토·수정하면 Pass되도록 설계됩니다.

### 트랩 유형

| 유형 | 설명 | 예시 |
|------|------|------|
| **엣지 케이스** | 빈 값·경계값·소수점 등 AI가 간과 | 소수점 응답시간, 0건 작성자 |
| **정렬/순서** | AI가 기본 정렬을 사용하지만 문제는 역순 요구 | 동점 IP 내림차순 |
| **보안/관례** | AI가 '일반적'인 답을 주지만 문제는 엄격한 답 요구 | `prohibit-password` vs `no` |
| **패턴 강제** | 특정 구현 패턴 요구 vs AI의 다른 패턴 사용 | yield 강제, pickle 금지 |
| **JOIN/집계** | SQL JOIN 유형이나 집계 함수 오용 | INNER→LEFT JOIN, COUNT(*)→DISTINCT |

### 배치 원칙

- 난이도 2~3 문항에 집중 배치 (문항당 2~5개)
- 트랩 전부 걸려도 Fail, 1~2개만 수정하면 Pass 경계
- `CheckItem`의 `ai_trap=True` 플래그로 코드에서 명시
- `config.yaml`의 `ai_traps` 섹션에 ID와 설명 등록

---

## 새 미션 추가 방법

### 1. 미션 디렉토리 생성

```bash
mkdir -p missions/{category}/level{N}/mission{NN}/template
```

### 2. 미션 파일 작성

| 파일 | 용도 |
|------|------|
| `config.yaml` | 미션 메타데이터 + 사용할 Validator 목록 등록 |
| `problem.md` | 학생용 문제지 |
| `solution.md` | 모범 답안 |
| `template/` | (선택) 학생 배포용 스켈레톤 코드 |

### 3. 검증기 작성

`plugins/{category}/validators/`에 `BaseValidator`를 상속하는 클래스를 구현합니다:

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
            ai_trap=False,
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
level: 1
category: "python"
time_limit: 900
passing_score: 70

validators:
  - module: "plugins.python.validators.my_validator"
    class: "MyValidator"
    weight: 100

ai_traps:
  - item: "trap_id"
    trap_description: "AI가 흔히 틀리는 포인트"
    correct_answer: "올바른 구현 방법"
```

### 5. 정답으로 검증

```bash
python3 scripts/run_grading.py \
  --student-id sample \
  --mission-id {category}_level{N}_mission{NN} \
  --submission-dir sample_submission_{category}
# → 100점 확인
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

## Validator 패턴 분류

| 패턴 | 설명 | 사용 미션 |
|------|------|---------|
| **AST 분석형** | `ast` 모듈로 소스코드 구문 분석 + 런타임 검증 | Python M1, DS, Algo |
| **subprocess 실행형** | `subprocess.run()`으로 학생 코드 실행 후 출력 검증 | Python M1/M2, Linux, DS, Algo, DB |
| **파일 I/O형** | `tempfile.TemporaryDirectory()`로 임시 환경 구성 | Python M1/M2, Linux, DB |
| **Popen형** | `subprocess.Popen()` + `time.sleep()`으로 시간 의존 테스트 | DS (TTL 만료) |
| **DB 쿼리형** | `sqlite3` 직접 연결하여 메타데이터 쿼리 | DB |
| **라인 매칭형** | subprocess 실행 후 리포트 파일 라인 기반 매칭 | Linux, DB |

---

## 채점 결과 예시

### JSON 출력

```json
{
  "student_id": "sample",
  "mission_id": "db_level3_mission01",
  "timestamp": "2026-02-26T17:08:28.812786",
  "overall_passed": true,
  "overall_score": 100.0,
  "results": [
    {
      "validator": "SchemaValidator",
      "result": {
        "earned_points": 20,
        "total_points": 20,
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

- **학습자 ID**: sample
- **최종 결과**: ✅ PASS
- **종합 점수**: 100.0점

## 1. SchemaValidator — 20 / 20
✅ [4점] analysis.db 생성 + 4개 테이블 존재
✅ [4점] commits 테이블에 FK 제약조건 존재
✅ [5점] parent_hash NULL 허용 + root commit 존재 ⚠️ AI Trap
✅ [4점] 테이블별 행 수 정확성 (6, 12, 4, 25)
✅ [3점] 최소 1개 사용자 정의 인덱스 존재
```

---

## 문제 해결

### ImportError 발생 시

반드시 **프로젝트 루트 디렉토리**에서 실행하세요.

```bash
cd /path/to/linux-test
python3 scripts/run_grading.py ...
```

### 학생 코드 관련 오류

`--submission-dir` 경로가 절대 경로인지, 해당 디렉토리에 제출 파일이 존재하는지 확인하세요.

```bash
ls /path/to/submission/
# 미션별 필요 파일이 있어야 함
```

---

## 기술 스택

| 항목 | 상세 |
|------|------|
| 언어 | Python 3.8+ |
| 외부 의존성 | PyYAML (설정 파싱) |
| 표준 라이브러리 | `ast`, `subprocess`, `importlib`, `os`, `json`, `csv`, `pathlib`, `dataclasses`, `abc`, `inspect`, `tempfile`, `sqlite3`, `re`, `hashlib` |
| 코딩 컨벤션 | 변수/함수: 영어 snake_case, 문서/주석/커밋: 한국어 |

---

## 향후 계획

- [ ] Docker 샌드박스 통합 (학생 코드 격리 실행)
- [ ] 웹 기반 채점 대시보드
- [ ] 실시간 채점 API
- [ ] `tests/` 유닛 테스트 구현
- [ ] 추가 도메인 미션 확장 (웹, 네트워크 등)

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
