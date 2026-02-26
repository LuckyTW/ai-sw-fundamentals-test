## 문항 5: 커밋 이력 DB 분석기

### 시험 정보
- 과정: AI 올인원
- 단계: AI·SW 기초
- 난이도: 3 (심화 통합)
- 권장 시간: 40분
- Pass 기준: 정답 체크리스트 19개 중 70점 이상 충족

### 문제

당신은 Git 저장소의 커밋 이력 데이터를 분석하는 도구를 개발해야 합니다.

4개의 CSV 파일(authors, commits, branches, commit_files)을 SQLite 데이터베이스로 적재한 뒤, SQL 쿼리로 다양한 통계를 분석하고 텍스트 리포트를 생성하세요.

### 입력 데이터

`--data-dir` 디렉토리에 다음 4개 CSV 파일이 주어집니다:

1. **authors.csv** — 작성자 정보 (author_id, name, email, team)
2. **commits.csv** — 커밋 기록 (hash, message, author_id, parent_hash, branch_name, created_at)
3. **branches.csv** — 브랜치 정보 (name, head_hash, created_at)
4. **commit_files.csv** — 커밋별 변경 파일 (id, commit_hash, file_path)

#### 데이터 특징
- 커밋 데이터는 DAG(방향 비순환 그래프) 구조로, 각 커밋은 `parent_hash`로 부모 커밋을 참조합니다
- **최초 커밋(root commit)은 `parent_hash`가 비어 있습니다** (부모 없음)
- 브랜치의 `head_hash`는 해당 브랜치의 최신 커밋을 가리킵니다
- 하나의 파일이 여러 커밋에서 변경될 수 있습니다

### 요구사항

#### 1. DB 스키마 설계 및 데이터 적재
- `authors`, `commits`, `branches`, `commit_files` 4개 테이블 생성
- 적절한 **Primary Key**와 **Foreign Key** 제약조건 설정
  - `commits.author_id` → `authors.author_id`
  - `commits.parent_hash` → `commits.hash` (self-referencing FK)
  - `commit_files.commit_hash` → `commits.hash`
- 최소 **1개 이상의 인덱스** 생성 (쿼리 최적화)
- CSV 데이터를 DB에 적재

#### 2. 분석 쿼리 구현
- **작성자별 기여 분석**: 각 작성자의 커밋 수와 변경한 **고유 파일 수**
- **브랜치별 커밋 수 분석**: 각 브랜치에 속한 커밋 수
- **main 브랜치 커밋 히스토리**: head에서 root까지 parent_hash를 따라가며 역순 추적
- **파일 변경 횟수 분석**: 가장 많이 변경된 파일 순위 (2회 이상)

#### 3. 텍스트 리포트 생성

아래 형식에 맞춰 리포트를 생성하세요:

```
=== Commit Statistics ===
Total Commits: [전체 커밋 수]
Total Authors: [전체 작성자 수]
Total Branches: [전체 브랜치 수]

Author Contributions (commits, files changed):
  1. [이름]: [N] commits, [M] files changed
  ...

=== Branch Analysis ===
  [브랜치명]: [N] commits (head: [해시])
  ...

=== Commit History (main) ===
  [해시] [커밋 메시지]
  ...

=== File Change Analysis ===
Most Changed Files:
  1. [파일명]: [N] commits
  ...

=== Summary ===
Most Active Author: [이름] ([N] commits)
Largest Branch: [브랜치명] ([N] commits)
Most Changed File: [파일명] ([N] commits)
```

### 제약 사항
- **Python 표준 라이브러리만 사용** (sqlite3, csv, argparse, os 등)
- 외부 라이브러리(pandas, sqlalchemy 등) 사용 금지
- DB 엔진은 **SQLite** (`sqlite3` 모듈)만 사용
- `PRAGMA foreign_keys = ON`으로 FK 제약조건 활성화 필수

### 실행 방법

```bash
python commit_analyzer.py --data-dir <CSV디렉토리> --output <리포트경로> --db <DB경로>
```

- `--data-dir`: CSV 4개 파일이 있는 디렉토리
- `--output`: 리포트 텍스트 파일 출력 경로
- `--db`: SQLite DB 파일 경로

### 제출 방식
- `commit_analyzer.py` 파일 1개 제출
- 템플릿(`template/commit_analyzer.py`)의 함수 시그니처를 유지하면서 TODO 부분을 구현
