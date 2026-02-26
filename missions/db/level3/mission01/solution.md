## 문항 5 정답지

### 정답 체크리스트

| 번호 | 체크 항목 | 배점 | AI 트랩 | 검증 방법 |
|------|----------|------|---------|----------|
| 1 | `db_created` — analysis.db 생성 + 4개 테이블 존재 | 4 | - | sqlite_master 쿼리 |
| 2 | `foreign_keys` — commits에 FK 제약조건 존재 | 4 | - | PRAGMA foreign_key_list |
| 3 | `root_commit_null` — parent_hash NULL 허용 + root commit 존재 | 5 | **Yes** | SELECT COUNT(*) WHERE parent_hash IS NULL = 1 |
| 4 | `data_loaded` — 테이블별 행 수 (6, 12, 4, 25) | 4 | - | SELECT COUNT(*) per table |
| 5 | `index_exists` — 최소 1개 사용자 정의 인덱스 | 3 | - | sqlite_master WHERE type='index' |
| 6 | `author_commit_count` — 김민수 4 commits 확인 | 5 | - | 라인에 "김민수"+"4 commits" |
| 7 | `author_left_join` — 황서진(0 commits) 포함 확인 | 8 | **Yes** | 라인에 "황서진"+"0 commits" |
| 8 | `branch_commit_count` — main 7 commits 확인 | 5 | - | 라인에 "main"+"7 commits" |
| 9 | `branch_no_commits` — hotfix/urgent 0 commits 포함 | 6 | **Yes** | 라인에 "hotfix/urgent"+"0 commits" |
| 10 | `distinct_file_count` — 김민수 5 files changed 확인 | 6 | **Yes** | 라인에 "김민수"+"5 files" |
| 11 | `most_changed_files` — requirements.txt 5 commits | 6 | - | 라인에 "requirements.txt"+"5 commits" |
| 12 | `self_join_parent` — 커밋 히스토리에 root(a1b2c3d) 포함 | 8 | **Yes** | History 섹션에 "a1b2c3d" 존재 |
| 13 | `history_count` — main 히스토리 7개 커밋 전부 | 2 | - | History 섹션에 7개 해시 전부 |
| 14 | `report_created` — 리포트 파일 생성 확인 | 3 | - | 파일 존재 + 비어있지 않음 |
| 15 | `report_sections` — 5개 섹션 헤더 존재 | 4 | - | 문자열 매칭 |
| 16 | `top_author` — Most Active Author = 김민수(4) | 7 | - | 라인 매칭 |
| 17 | `commit_total` — Total Commits: 12 확인 | 6 | - | 라인 매칭 |
| 18 | `summary_stats` — 요약 3항목 (Author/Branch/File) 존재 | 8 | - | 문자열 매칭 |
| 19 | `file_ranking_order` — requirements.txt가 1위 | 7 | - | 섹션 내 순위 확인 |

- Pass 기준: 총 100점 중 70점 이상

### AI 트랩 분석

| 트랩 ID | AI 실수 패턴 | 올바른 구현 | 배점 |
|---------|------------|----------|------|
| `root_commit_null` | parent_hash NOT NULL 정의 → root commit INSERT 실패 | parent_hash는 NULL 허용 | 5 |
| `author_left_join` | INNER JOIN으로 커밋 없는 작성자(황서진) 제외 | LEFT JOIN으로 0-commit 작성자 포함 | 8 |
| `branch_no_commits` | INNER JOIN으로 커밋 없는 브랜치(hotfix/urgent) 제외 | LEFT JOIN으로 0-commit 브랜치 포함 | 6 |
| `distinct_file_count` | COUNT(*)로 중복 파일을 별도 카운트 | COUNT(DISTINCT file_path)로 고유 파일 수 | 6 |
| `self_join_parent` | INNER JOIN self-reference → parent=NULL인 root 제외 | Recursive CTE 또는 LEFT JOIN으로 root 포함 | 8 |

**트랩 합계**: 33점 → 전부 걸리면 67점 (Fail), 1개만 수정하면 72점 이상 (Pass)

### 핵심 SQL 쿼리

#### 작성자별 기여 (LEFT JOIN + COUNT DISTINCT)

```sql
SELECT a.name,
       COUNT(DISTINCT c.hash) AS commit_count,
       COUNT(DISTINCT cf.file_path) AS file_count
FROM authors a
LEFT JOIN commits c ON a.author_id = c.author_id
LEFT JOIN commit_files cf ON c.hash = cf.commit_hash
GROUP BY a.author_id
ORDER BY commit_count DESC, a.author_id ASC
```

#### 브랜치별 커밋 수 (LEFT JOIN)

```sql
SELECT b.name,
       COUNT(c.hash) AS commit_count,
       b.head_hash
FROM branches b
LEFT JOIN commits c ON b.name = c.branch_name
GROUP BY b.name
ORDER BY commit_count DESC, b.name ASC
```

#### main 커밋 히스토리 (Recursive CTE)

```sql
WITH RECURSIVE history(hash, message, parent_hash) AS (
    SELECT c.hash, c.message, c.parent_hash
    FROM branches b
    JOIN commits c ON b.head_hash = c.hash
    WHERE b.name = 'main'
    UNION ALL
    SELECT c.hash, c.message, c.parent_hash
    FROM history h
    JOIN commits c ON h.parent_hash = c.hash
)
SELECT hash, message FROM history
```

#### 파일 변경 횟수

```sql
SELECT file_path,
       COUNT(DISTINCT commit_hash) AS change_count
FROM commit_files
GROUP BY file_path
HAVING change_count >= 2
ORDER BY change_count DESC, file_path ASC
```

### 정답 코드

정답 코드는 `sample_submission_db/commit_analyzer.py`를 참조하세요.
