# Python 도서 관리 시스템 코딩 시험

## 시험 개요

- **시간**: 15분
- **합격 기준**: 100점 만점 중 70점 이상
- **제출물**: 4개의 Python 파일 (models.py, filters.py, storage.py, cli.py)

PBL 과정에서 배운 개념(dataclass, 제너레이터, 데코레이터, 파일 I/O, CLI)을 **도서 관리 시스템**이라는 새로운 도메인에 적용하는 시험입니다.

---

## 스켈레톤 파일 설명

배포된 `template/` 디렉토리에 4개의 스켈레톤 파일이 있습니다. 각 파일의 `TODO` 부분을 구현하세요.

| 파일 | 역할 | 배점 |
|------|------|------|
| `models.py` | Book 데이터 모델 정의 | 25점 |
| `filters.py` | 검색/필터링 (제너레이터, 데코레이터) | 25점 |
| `storage.py` | 파일 저장/로드 | 20점 |
| `cli.py` | CLI 인터페이스 | 30점 |

---

## 문제 1: 데이터 모델 (25점)

`models.py`에 `Book` 클래스를 구현하세요.

### 요구사항
1. `@dataclass` 데코레이터 사용 (7점)
2. 필수 필드와 타입 힌트 (6점):
   - `isbn: str` — 국제 표준 도서 번호
   - `title: str` — 도서 제목
   - `author: str` — 저자
   - `price: int` — 가격 (원)
   - `is_available: bool` — 대출 가능 여부 (기본값: `True`)
3. 필드 타입 힌트 (5점)
4. `__post_init__` 유효성 검증 (7점): `price < 0`이면 `ValueError` 발생

### 추가 구현 (채점 외)
- `to_dict()`: Book → 딕셔너리 변환
- `from_dict(data)`: 딕셔너리 → Book 변환 (클래스 메서드)

---

## 문제 2: 코딩 패턴 (25점)

`filters.py`에 검색/필터링 함수를 구현하세요.

### 요구사항
1. **`search_books` 제너레이터** (8점, ⚠️ AI 함정):
   - `yield`를 사용하여 검색 결과를 반환하세요
   - ❌ 리스트를 만들어 반환하면 **0점**
   - ✅ `yield`로 하나씩 반환해야 합니다
2. **사용자 정의 데코레이터** (7점):
   - `validate_args` 데코레이터를 직접 정의하세요
   - `functools.wraps`를 사용하세요
3. **타입 힌트** (5점): 3개 이상의 함수에 타입 힌트 적용
4. **Any 미사용** (5점, ⚠️ AI 함정):
   - ❌ `Any` 타입을 30% 이상 사용하면 **0점**
   - ✅ `str`, `int`, `List[Book]` 등 구체적인 타입을 사용하세요

---

## 문제 3: CLI 인터페이스 (30점)

`cli.py`에 명령줄 인터페이스를 구현하세요.

### 요구사항
1. **cli.py 존재** (5점): 파일이 있어야 합니다
2. **--help 옵션** (5점, ⚠️ AI 함정):
   - `python cli.py --help` 실행 시 도움말 출력
   - ❌ argparse 없이 구현하면 **0점**
3. **add 서브커맨드** (8점):
   - `python cli.py add --isbn "978-..." --title "제목" --author "저자" --price 10000`
4. **list 서브커맨드** (7점):
   - `python cli.py list`
5. **크래시 방지** (5점): 잘못된 입력에 Traceback 미출력

---

## 문제 4: 데이터 저장 (20점)

`storage.py`에 파일 저장/로드 함수를 구현하세요.

### 요구사항
1. **왕복 무결성** (7점): `save_books()` → `load_books()`로 데이터 완전 복원
2. **파일 형식** (3점): JSONL, JSON, 또는 CSV 형식 사용
3. **pickle 미사용** (5점, ⚠️ AI 함정):
   - ❌ `import pickle` 사용 시 **0점**
   - ❌ `.pkl`/`.pickle` 파일 생성 시 **0점**
   - ✅ `json`/`csv` 등 텍스트 기반 직렬화 사용
4. **필수 필드 포함** (5점): 저장 데이터에 isbn, title, author, price 포함

---

## ⚠️ AI 함정 경고 (4개)

AI 도구를 사용하면 다음 항목에서 감점될 수 있습니다:

| # | 항목 | AI가 흔히 하는 실수 | 올바른 구현 |
|---|------|-------------------|------------|
| 1 | search_books | 리스트 반환 (`return [...]`) | `yield`로 하나씩 반환 |
| 2 | Any 타입 | `Any` 남용 | 구체적 타입 사용 |
| 3 | --help | argparse 미사용 | `argparse` 사용 |
| 4 | pickle | `import pickle` 사용 | `json`/`csv` 사용 |

---

## 평가 기준

| 영역 | 배점 | AI 함정 |
|------|------|---------|
| 데이터 모델 | 25점 | 0개 |
| 코딩 패턴 | 25점 | 2개 |
| CLI 동작 | 30점 | 1개 |
| 데이터 저장 | 20점 | 1개 |
| **합계** | **100점** | **4개** |

---

## 제출 및 채점

```bash
# 채점 실행
python3 scripts/run_grading.py \
  --student-id <학생ID> \
  --mission-id python_level1_mission01 \
  --submission-dir /path/to/your/submission
```

---

**제출 기한**: 15분
**참고**: AI 어시스턴트를 활용할 수 있지만, AI 함정 항목은 반드시 직접 검증하세요.
