## 문항 1: Python 도서 관리 시스템

### 시험 정보
- 과정: AI 올인원
- 단계: AI·SW 기초
- 난이도: 1
- 권장 시간: 15분
- Pass 기준: 총 100점 중 70점 이상

### 문제

PBL 과정에서 배운 개념(dataclass, 제너레이터, 데코레이터, 파일 I/O, CLI)을 **도서 관리 시스템**이라는 새로운 도메인에 적용하는 시험입니다.

배포된 `template/` 디렉토리에 4개의 스켈레톤 파일이 있습니다. 각 파일의 `TODO` 부분을 구현하세요.

| 파일 | 역할 | 배점 |
|------|------|------|
| `models.py` | Book 데이터 모델 정의 | 25점 |
| `filters.py` | 검색/필터링 (제너레이터, 데코레이터) | 25점 |
| `storage.py` | 파일 저장/로드 | 20점 |
| `cli.py` | CLI 인터페이스 | 30점 |

#### 1. 데이터 모델 — `models.py` (25점)

`Book` 클래스를 구현하세요.

- `@dataclass` 데코레이터 사용 (7점)
- 필수 필드와 타입 힌트 (6점):
  - `isbn: str` — 국제 표준 도서 번호
  - `title: str` — 도서 제목
  - `author: str` — 저자
  - `price: int` — 가격 (원)
  - `is_available: bool` — 대출 가능 여부 (기본값: `True`)
- 필드 타입 힌트 (5점)
- `__post_init__` 유효성 검증 (7점): `price < 0`이면 `ValueError` 발생
- 추가 구현 (채점 외): `to_dict()`, `from_dict(data)` 클래스 메서드

#### 2. 코딩 패턴 — `filters.py` (25점)

검색/필터링 함수를 구현하세요.

- **`search_books` 제너레이터** (8점, ⚠️ AI 함정):
  - `yield`를 사용하여 검색 결과를 반환하세요
  - ❌ 리스트를 만들어 반환하면 **0점**
  - ✅ `yield`로 하나씩 반환해야 합니다
- **사용자 정의 데코레이터** (7점):
  - `validate_args` 데코레이터를 직접 정의하세요
  - `functools.wraps`를 사용하세요
- **타입 힌트** (5점): 3개 이상의 함수에 타입 힌트 적용
- **Any 미사용** (5점, ⚠️ AI 함정):
  - ❌ `Any` 타입을 30% 이상 사용하면 **0점**
  - ✅ `str`, `int`, `List[Book]` 등 구체적인 타입을 사용하세요

#### 3. CLI 인터페이스 — `cli.py` (30점)

명령줄 인터페이스를 구현하세요.

- **cli.py 존재** (5점): 파일이 있어야 합니다
- **--help 옵션** (5점, ⚠️ AI 함정):
  - `python cli.py --help` 실행 시 도움말 출력
  - ❌ argparse 없이 구현하면 **0점**
- **add 서브커맨드** (8점):
  - `python cli.py add --isbn "978-..." --title "제목" --author "저자" --price 10000`
- **list 서브커맨드** (7점):
  - `python cli.py list`
- **크래시 방지** (5점): 잘못된 입력에 Traceback 미출력

#### 4. 데이터 저장 — `storage.py` (20점)

파일 저장/로드 함수를 구현하세요.

- **왕복 무결성** (7점): `save_books()` → `load_books()`로 데이터 완전 복원
- **파일 형식** (3점): JSONL, JSON, 또는 CSV 형식 사용
- **pickle 미사용** (5점, ⚠️ AI 함정):
  - ❌ `import pickle` 사용 시 **0점**
  - ❌ `.pkl`/`.pickle` 파일 생성 시 **0점**
  - ✅ `json`/`csv` 등 텍스트 기반 직렬화 사용
- **필수 필드 포함** (5점): 저장 데이터에 isbn, title, author, price 포함

### 제약 사항
- `yield` 제너레이터로 검색 결과를 반환해야 합니다 (리스트 반환 금지)
- `typing.Any` 타입 사용 비율을 30% 미만으로 유지하세요
- `argparse`를 사용하여 `--help` 옵션을 지원해야 합니다
- `pickle` 모듈 사용 금지 — `json`/`csv` 등 텍스트 기반 직렬화만 허용
- 외부 패키지 설치 금지 (표준 라이브러리만 사용)

### 제출 방식

`models.py`, `filters.py`, `storage.py`, `cli.py` 4개 파일을 제출합니다.
- 템플릿 파일의 `TODO` 부분을 구현하세요.
