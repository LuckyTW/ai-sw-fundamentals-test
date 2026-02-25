## 문항 3: Mini Git 커밋 그래프 시뮬레이터

### 시험 정보
- 과정: AI 올인원
- 단계: AI·SW 기초
- 난이도: 2
- 권장 시간: 25분
- Pass 기준: 정답 체크리스트 16개 중 70점 이상 충족

### 문제

여러분은 Mini Git을 구현합니다. 커밋을 **DAG(방향 비순환 그래프)**로 관리하고, 브랜치 분기/전환, BFS 경로 탐색, 역색인 검색, 직접 구현한 정렬 알고리즘을 제공하는 대화형 CLI를 만들어야 합니다.

#### 핵심 요구사항

1. **커밋 그래프 (`mini_git.py`)**
   - `Commit` 클래스: `hash`, `message`, `author`, `timestamp`, `parents`, `branch` 속성
   - `CommitGraph` 클래스: `dict` 기반 커밋 저장소 + 브랜치 관리
     - `init(author)` → 저장소 초기화, main 브랜치 생성
     - `commit(message)` → **HEAD 브랜치의 최신 커밋을 부모로** 새 커밋 생성
     - `branch(name)` → 현재 커밋을 가리키는 새 브랜치 생성
     - `switch(name)` → HEAD를 다른 브랜치로 이동
   - `InvertedIndex` 클래스: 단어/작성자 역색인
     - `add_commit(commit)` → 메시지 단어와 작성자 인덱싱
     - `search_by_keyword(keyword)` → 키워드 포함 커밋 해시 반환
     - `search_by_author(author)` → 작성자의 커밋 해시 반환
   - `merge_sort(arr, key)` → **정렬 알고리즘 직접 구현**
   - `find_path(graph, h1, h2)` → **BFS로 두 커밋 간 최단 경로** (무방향!)
   - `find_ancestors(graph, hash)` → BFS로 모든 조상 탐색 (부모 방향만)

2. **CLI (`cli.py`)**
   - `mini-git> ` 프롬프트로 대화형 REPL (템플릿에 기본 구조 제공됨)
   - 9개 명령어 처리 (아래 출력 형식 참조)

#### 해시 함수

해시 함수는 템플릿에 제공되어 있습니다. **이 함수를 수정하지 마세요:**

```python
import hashlib

def generate_hash(message: str, seq: int) -> str:
    """커밋 해시 생성 (이 함수를 수정하지 마세요)"""
    return hashlib.sha256(f"{message}:{seq}".encode()).hexdigest()[:7]
```

- `seq` = 커밋 생성 순서 (1부터 시작, 저장소 전체에서 고유)

### 제약 사항
- **정렬 알고리즘은 직접 구현** (merge sort 권장). `sorted()`, `list.sort()`, `heapq` 사용 **금지**
- **PATH 탐색은 무방향 BFS**: 부모→자식, 자식→부모 양방향으로 탐색해야 다른 브랜치 간 경로를 찾을 수 있습니다
- **LOG는 모든 브랜치의 모든 커밋을 출력**: 현재 브랜치만이 아닌, 저장소 전체의 커밋을 출력합니다
- 외부 패키지 설치 금지 (표준 라이브러리만 사용)
- `collections.deque`는 사용 가능 (큐 용도)

### 출력 형식

| 명령어 | 출력 형식 |
|--------|---------|
| `INIT <name>` | `Initialized repository.` / `Current branch: main` / `Current user: <name>` |
| `COMMIT "<msg>"` | `[<branch> <hash>] <message>` |
| `BRANCH <name>` | `Created branch: <name>` |
| `SWITCH <name>` | `Switched to branch: <name>` |
| `LOG` | 아래 참조 (모든 브랜치, 시간 역순, 브랜치 라벨 포함) |
| `LOG --sort-by=date` | 아래 참조 (시간순, 브랜치 라벨 없음) |
| `LOG --sort-by=author` | 아래 참조 (작성자순, 브랜치 라벨 없음) |
| `PATH <h1> <h2>` | `Path: <h1> -> <h2> -> ...` 또는 `No path found.` |
| `ANCESTORS <hash>` | `Ancestors of <hash>:` / `- <hash1>` 또는 `(none)` |
| `SEARCH <keyword>` | `Found N commit(s):` / `- <hash>: <message>` |
| `SEARCH --author=<name>` | 동일 |

#### LOG 기본 형식 (브랜치 라벨 포함)
```
commit <hash> (<author>, <YYYY-MM-DD HH:MM:SS>) [<branch>]
    <message>
```

#### LOG --sort-by 형식 (브랜치 라벨 없음)
```
commit <hash> (<author>, <YYYY-MM-DD HH:MM:SS>)
    <message>
```

#### 에러 형식
```
(error) ERR unknown command '<cmd>'
(error) ERR wrong number of arguments
(error) ERR branch '<name>' already exists
(error) ERR branch '<name>' not found
```

### 실행 예시

```
mini-git> INIT Alice
Initialized repository.
Current branch: main
Current user: Alice
mini-git> COMMIT "Initial commit"
[main 4574868] Initial commit
mini-git> COMMIT "Add feature"
[main 3b63dc5] Add feature
mini-git> BRANCH dev
Created branch: dev
mini-git> SWITCH dev
Switched to branch: dev
mini-git> COMMIT "Dev work"
[dev 6536d0e] Dev work
mini-git> LOG
commit 6536d0e (Alice, 2026-02-25 14:30:00) [dev]
    Dev work
commit 3b63dc5 (Alice, 2026-02-25 14:30:00) [main]
    Add feature
commit 4574868 (Alice, 2026-02-25 14:30:00) [main]
    Initial commit
mini-git> EXIT
```

### 제출 방식

`mini_git.py`와 `cli.py` 2개 파일을 제출합니다.
- 템플릿 파일의 TODO 부분을 구현하세요.
- `cli.py`는 `from mini_git import ...`로 임포트합니다.
- `generate_hash` 함수는 수정하지 마세요.
