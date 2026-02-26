#!/usr/bin/env python3
"""
커밋 이력 DB 분석기 — 모범 답안

CSV 데이터를 SQLite DB로 적재한 뒤,
SQL 쿼리로 커밋 이력을 분석하고 텍스트 리포트를 생성한다.
"""
import argparse
import csv
import os
import sqlite3


# ── DB 스키마 생성 ──

def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS authors (
            author_id INTEGER PRIMARY KEY,
            name      TEXT NOT NULL,
            email     TEXT NOT NULL,
            team      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS commits (
            hash        TEXT PRIMARY KEY,
            message     TEXT NOT NULL,
            author_id   INTEGER NOT NULL,
            parent_hash TEXT,
            branch_name TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (author_id)   REFERENCES authors(author_id),
            FOREIGN KEY (parent_hash) REFERENCES commits(hash)
        );

        CREATE TABLE IF NOT EXISTS branches (
            name        TEXT PRIMARY KEY,
            head_hash   TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (head_hash) REFERENCES commits(hash)
        );

        CREATE TABLE IF NOT EXISTS commit_files (
            id          INTEGER PRIMARY KEY,
            commit_hash TEXT NOT NULL,
            file_path   TEXT NOT NULL,
            FOREIGN KEY (commit_hash) REFERENCES commits(hash)
        );

        CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author_id);
        CREATE INDEX IF NOT EXISTS idx_commits_branch ON commits(branch_name);
        CREATE INDEX IF NOT EXISTS idx_commit_files_hash ON commit_files(commit_hash);
    """)
    conn.commit()


# ── CSV 로드 ──

def load_csv(conn: sqlite3.Connection, data_dir: str) -> None:
    cur = conn.cursor()

    # authors
    with open(os.path.join(data_dir, "authors.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO authors VALUES (?,?,?,?)",
                (int(row["author_id"]), row["name"], row["email"], row["team"]),
            )

    # commits (parent_hash 빈 문자열 → NULL 변환)
    with open(os.path.join(data_dir, "commits.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parent = row["parent_hash"] if row["parent_hash"] else None
            cur.execute(
                "INSERT INTO commits VALUES (?,?,?,?,?,?)",
                (row["hash"], row["message"], int(row["author_id"]),
                 parent, row["branch_name"], row["created_at"]),
            )

    # branches
    with open(os.path.join(data_dir, "branches.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO branches VALUES (?,?,?)",
                (row["name"], row["head_hash"], row["created_at"]),
            )

    # commit_files
    with open(os.path.join(data_dir, "commit_files.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO commit_files VALUES (?,?,?)",
                (int(row["id"]), row["commit_hash"], row["file_path"]),
            )

    conn.commit()


# ── 분석 쿼리 ──

def author_contributions(conn: sqlite3.Connection):
    """작성자별 커밋 수 + 고유 파일 수 (LEFT JOIN)"""
    sql = """
        SELECT a.name,
               COUNT(DISTINCT c.hash) AS commit_count,
               COUNT(DISTINCT cf.file_path) AS file_count
        FROM authors a
        LEFT JOIN commits c ON a.author_id = c.author_id
        LEFT JOIN commit_files cf ON c.hash = cf.commit_hash
        GROUP BY a.author_id
        ORDER BY commit_count DESC, a.author_id ASC
    """
    return conn.execute(sql).fetchall()


def branch_analysis(conn: sqlite3.Connection):
    """브랜치별 커밋 수 (LEFT JOIN)"""
    sql = """
        SELECT b.name,
               COUNT(c.hash) AS commit_count,
               b.head_hash
        FROM branches b
        LEFT JOIN commits c ON b.name = c.branch_name
        GROUP BY b.name
        ORDER BY commit_count DESC, b.name ASC
    """
    return conn.execute(sql).fetchall()


def commit_history_main(conn: sqlite3.Connection):
    """main 브랜치 커밋 히스토리 (head → root, Recursive CTE)"""
    sql = """
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
    """
    return conn.execute(sql).fetchall()


def most_changed_files(conn: sqlite3.Connection):
    """파일별 변경 횟수 (커밋 수 기준)"""
    sql = """
        SELECT file_path,
               COUNT(DISTINCT commit_hash) AS change_count
        FROM commit_files
        GROUP BY file_path
        HAVING change_count >= 2
        ORDER BY change_count DESC, file_path ASC
    """
    return conn.execute(sql).fetchall()


def total_stats(conn: sqlite3.Connection):
    """전체 통계"""
    total_commits = conn.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
    total_authors = conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0]
    total_branches = conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0]
    return total_commits, total_authors, total_branches


# ── 리포트 생성 ──

def generate_report(conn: sqlite3.Connection) -> str:
    lines = []

    # 전체 통계
    t_commits, t_authors, t_branches = total_stats(conn)
    lines.append("=== Commit Statistics ===")
    lines.append(f"Total Commits: {t_commits}")
    lines.append(f"Total Authors: {t_authors}")
    lines.append(f"Total Branches: {t_branches}")
    lines.append("")

    # 작성자별 기여
    contribs = author_contributions(conn)
    lines.append("Author Contributions (commits, files changed):")
    for i, (name, commits, files) in enumerate(contribs, 1):
        lines.append(f"  {i}. {name}: {commits} commits, {files} files changed")
    lines.append("")

    # 브랜치 분석
    lines.append("=== Branch Analysis ===")
    branches = branch_analysis(conn)
    for name, count, head in branches:
        lines.append(f"  {name}: {count} commits (head: {head})")
    lines.append("")

    # 커밋 히스토리 (main)
    lines.append("=== Commit History (main) ===")
    history = commit_history_main(conn)
    for h, msg in history:
        lines.append(f"  {h} {msg}")
    lines.append("")

    # 파일 변경 분석
    lines.append("=== File Change Analysis ===")
    lines.append("Most Changed Files:")
    files = most_changed_files(conn)
    for i, (fp, cnt) in enumerate(files, 1):
        lines.append(f"  {i}. {fp}: {cnt} commits")
    lines.append("")

    # 요약
    lines.append("=== Summary ===")
    # 최다 커밋 작성자
    top_author = contribs[0] if contribs else ("N/A", 0, 0)
    lines.append(f"Most Active Author: {top_author[0]} ({top_author[1]} commits)")
    # 최대 브랜치
    top_branch = branches[0] if branches else ("N/A", 0, "")
    lines.append(f"Largest Branch: {top_branch[0]} ({top_branch[1]} commits)")
    # 최다 변경 파일
    top_file = files[0] if files else ("N/A", 0)
    lines.append(f"Most Changed File: {top_file[0]} ({top_file[1]} commits)")

    return "\n".join(lines)


# ── 메인 ──

def main():
    parser = argparse.ArgumentParser(description="커밋 이력 DB 분석기")
    parser.add_argument("--data-dir", required=True, help="CSV 데이터 디렉토리")
    parser.add_argument("--output", required=True, help="리포트 출력 경로")
    parser.add_argument("--db", required=True, help="SQLite DB 파일 경로")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys = ON")

    create_tables(conn)
    load_csv(conn, args.data_dir)

    report = generate_report(conn)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    conn.close()


if __name__ == "__main__":
    main()
