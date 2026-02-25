## 문항 3 정답지

### 정답 코드

모범 답안은 `sample_submission_algo/` 디렉토리에 위치합니다:
- `sample_submission_algo/mini_git.py` — Commit + CommitGraph + InvertedIndex + merge_sort + BFS
- `sample_submission_algo/cli.py` — REPL + 명령어 파싱 + Git 스타일 출력

### 핵심 구현 포인트

1. **Commit 클래스**: hash, message, author, timestamp, parents, branch 6개 속성
2. **CommitGraph.commit()**: `self.branches[self.head_branch]`를 부모로 설정 (트랩!)
3. **LOG**: `list(graph.commits.values())`로 모든 커밋 수집 → 모든 브랜치 출력 (트랩!)
4. **find_path()**: 무방향 인접 리스트 구축 → BFS (트랩!)
5. **merge_sort()**: 분할 + 병합 직접 구현, `sorted()`/`.sort()` 사용 금지 (트랩!)
6. **InvertedIndex**: 단어/작성자를 lowercase로 인덱싱 → 대소문자 무관 검색

### 정답 체크리스트

| 번호 | 체크 항목 | 배점 | 검증 방법 | AI 트랩 |
|------|----------|------|----------|---------|
| 1 | Commit 클래스에 hash/message/author/timestamp/parents 존재 | 8 | AST 분석 | - |
| 2 | sorted()/list.sort()/heapq 미사용 | 7 | AST Import/Call 검사 | **Yes** |
| 3 | dict 기반 커밋 저장소 | 5 | AST 분석 | - |
| 4 | cli.py 실행 + 프롬프트 출력 | 3 | subprocess | - |
| 5 | INIT 명령어 정상 동작 | 5 | subprocess | - |
| 6 | COMMIT 출력 형식 정확 | 6 | subprocess | - |
| 7 | BRANCH/SWITCH 정상 동작 | 6 | subprocess | - |
| 8 | SWITCH 후 COMMIT 올바른 부모 설정 | 7 | subprocess (ANCESTORS) | **Yes** |
| 9 | LOG가 모든 브랜치 커밋 출력 | 8 | subprocess (LOG) | **Yes** |
| 10 | 같은 브랜치 내 PATH (독립 세션) | 5 | subprocess (PATH) | - |
| 11 | 다른 브랜치 간 PATH (무방향 BFS) | 10 | subprocess (PATH) | **Yes** |
| 12 | ANCESTORS 모든 조상 출력 | 5 | subprocess (ANCESTORS) | - |
| 13 | SEARCH 키워드 검색 | 7 | subprocess | - |
| 14 | 미존재 키워드 SEARCH → 0건 | 5 | subprocess | - |
| 15 | SEARCH --author 작성자 검색 | 6 | subprocess | - |
| 16 | LOG --sort-by=date 날짜순 정렬 | 7 | subprocess | - |

- Pass 기준: 총 100점 중 70점 이상

### AI 트랩 해설

1. **no_builtin_sort** (7점): AI가 `sorted(commits, key=lambda c: c.timestamp)`를 사용. merge sort 또는 quick sort를 직접 구현해야 함.

2. **commit_parent_after_switch** (7점): 브랜치 A에서 커밋 후 SWITCH로 브랜치 B로 이동한 뒤 COMMIT을 하면, 새 커밋의 부모는 브랜치 B의 HEAD여야 함. AI는 "마지막으로 생성된 커밋"을 부모로 설정하는 실수를 범함.

3. **log_all_branches** (8점): 실제 Git의 `git log`는 현재 HEAD에서 도달 가능한 커밋만 출력. AI가 이 패턴을 따라하면, 다른 브랜치에만 존재하는 커밋이 누락됨. Mini Git의 LOG는 저장소의 모든 커밋을 시간순으로 출력해야 함.

4. **path_cross_branch** (10점): 다른 브랜치에 있는 두 커밋 간 PATH를 찾으려면, DAG를 무방향 그래프로 취급하여 BFS를 수행해야 함. AI가 부모 방향으로만 BFS를 구현하면, 공통 조상을 지나 다른 브랜치로 이동하는 경로를 찾을 수 없음.

### AI 트랩 점수 시뮬레이션

| 시나리오 | 감점 | 총점 | 결과 |
|---------|------|------|------|
| 트랩 4개 모두 걸림 | -32 | 68점 | **Fail** |
| 트랩 3개 걸림 (sort만 수정) | -25 | 75점 | Pass |
| 트랩 2개 걸림 | -14~18 | 82~86점 | Pass |
| 트랩 0개 | 0 | 100점 | Pass |

### 테스트 독립성 (조정 1 적용)

연쇄 실패 방지를 위해 GraphAlgorithmValidator는 2개의 독립 세션을 사용:

- **세션 A** (path_same_branch): 선형 체인 `c1→c2→c3` (브랜치 없음)
  - `commit_parent_after_switch` 트랩에 영향받지 않음
- **세션 B** (나머지 4개): 브랜치 분기 시나리오 `c1→c2→c3→c4, c2→c5`
  - `commit_parent`, `log_all`, `path_cross`, `ancestors` 검증
