"""DB 미션 검증용 CSV 데이터 상수 + 헬퍼"""
import os

AUTHORS_CSV = """\
author_id,name,email,team
1,김민수,minsoo@dev.com,backend
2,이지혜,jihye@dev.com,frontend
3,박동현,donghyun@dev.com,backend
4,최유나,yuna@dev.com,frontend
5,황서진,seojin@dev.com,backend
6,정태환,taehwan@dev.com,devops
"""

COMMITS_CSV = """\
hash,message,author_id,parent_hash,branch_name,created_at
a1b2c3d,Initial project setup,1,,main,2026-01-10 09:00:00
b2c3d4e,Add README and gitignore,1,a1b2c3d,main,2026-01-10 09:30:00
c3d4e5f,Setup CI/CD pipeline,6,b2c3d4e,main,2026-01-10 10:00:00
d4e5f6a,Add login page,2,c3d4e5f,feature/login,2026-01-11 09:00:00
e5f6a7b,Add auth middleware,2,d4e5f6a,feature/login,2026-01-11 10:00:00
f6a7b8c,Fix build configuration,6,c3d4e5f,main,2026-01-11 11:00:00
a7b8c9d,Add session management,3,e5f6a7b,feature/login,2026-01-12 09:00:00
b8c9d0e,Update dependencies,1,f6a7b8c,main,2026-01-12 10:00:00
c9d0e1f,Add dashboard layout,4,a7b8c9d,feature/dashboard,2026-01-13 09:00:00
d0e1f2a,Refactor API endpoints,3,b8c9d0e,main,2026-01-13 10:00:00
e1f2a3b,Add chart components,4,c9d0e1f,feature/dashboard,2026-01-13 11:00:00
f2a3b4c,Release v1.0,1,d0e1f2a,main,2026-01-14 09:00:00
"""

BRANCHES_CSV = """\
name,head_hash,created_at
main,f2a3b4c,2026-01-10 09:00:00
feature/login,a7b8c9d,2026-01-11 09:00:00
feature/dashboard,e1f2a3b,2026-01-13 09:00:00
hotfix/urgent,c3d4e5f,2026-01-11 14:00:00
"""

COMMIT_FILES_CSV = """\
id,commit_hash,file_path
1,a1b2c3d,src/main.py
2,a1b2c3d,requirements.txt
3,b2c3d4e,README.md
4,b2c3d4e,.gitignore
5,c3d4e5f,.github/workflows/ci.yml
6,c3d4e5f,Dockerfile
7,c3d4e5f,requirements.txt
8,d4e5f6a,src/pages/login.html
9,d4e5f6a,src/auth/login.py
10,e5f6a7b,src/auth/middleware.py
11,e5f6a7b,src/auth/login.py
12,f6a7b8c,Dockerfile
13,f6a7b8c,requirements.txt
14,a7b8c9d,src/auth/session.py
15,a7b8c9d,src/auth/middleware.py
16,b8c9d0e,requirements.txt
17,c9d0e1f,src/pages/dashboard.html
18,c9d0e1f,src/dashboard/layout.py
19,d0e1f2a,src/api/endpoints.py
20,d0e1f2a,src/api/routes.py
21,e1f2a3b,src/dashboard/charts.py
22,e1f2a3b,src/dashboard/layout.py
23,f2a3b4c,CHANGELOG.md
24,f2a3b4c,src/main.py
25,f2a3b4c,requirements.txt
"""

# 기대 정답값
EXPECTED_AUTHOR_COUNTS = {
    "김민수": 4, "이지혜": 2, "박동현": 2,
    "최유나": 2, "황서진": 0, "정태환": 2,
}
EXPECTED_DISTINCT_FILES = {
    "김민수": 5, "이지혜": 3, "박동현": 4,
    "최유나": 3, "황서진": 0, "정태환": 3,
}
EXPECTED_BRANCH_COUNTS = {
    "main": 7, "feature/login": 3,
    "feature/dashboard": 2, "hotfix/urgent": 0,
}
EXPECTED_MAIN_HISTORY = [
    "f2a3b4c", "d0e1f2a", "b8c9d0e",
    "f6a7b8c", "c3d4e5f", "b2c3d4e", "a1b2c3d",
]


def write_csv_files(data_dir: str) -> None:
    """CSV 4개를 data_dir에 쓰기"""
    files = {
        "authors.csv": AUTHORS_CSV,
        "commits.csv": COMMITS_CSV,
        "branches.csv": BRANCHES_CSV,
        "commit_files.csv": COMMIT_FILES_CSV,
    }
    for filename, content in files.items():
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
