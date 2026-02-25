"""
Mini Git CLI - 커밋 그래프 REPL 인터페이스

지원 명령어:
- INIT <name>                    → 저장소 초기화
- COMMIT "<message>"             → 커밋 생성
- BRANCH <name>                  → 브랜치 생성
- SWITCH <name>                  → 브랜치 전환
- LOG [--sort-by=date|author]    → 커밋 로그 출력
- PATH <hash1> <hash2>          → 최단 경로 탐색
- ANCESTORS <hash>               → 조상 커밋 목록
- SEARCH <keyword>               → 키워드 검색
- SEARCH --author=<name>         → 작성자 검색
- EXIT / QUIT                    → 종료
"""
import shlex

from mini_git import (
    CommitGraph, InvertedIndex,
    merge_sort, find_path, find_ancestors,
)


def main():
    graph = None
    index = InvertedIndex()

    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            break

        line = line.strip()
        if not line:
            continue

        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()

        if not tokens:
            continue

        cmd = tokens[0].upper()

        if cmd in ("EXIT", "QUIT"):
            break

        elif cmd == "INIT":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            graph = CommitGraph()
            graph.init(tokens[1])
            index = InvertedIndex()
            print("Initialized repository.")
            print(f"Current branch: main")
            print(f"Current user: {tokens[1]}")

        elif cmd == "COMMIT":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            message = tokens[1]
            commit = graph.commit(message)
            index.add_commit(commit)
            print(f"[{commit.branch} {commit.hash}] {commit.message}")

        elif cmd == "BRANCH":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            name = tokens[1]
            if name in graph.branches:
                print(f"(error) ERR branch '{name}' already exists")
            else:
                graph.branch(name)
                print(f"Created branch: {name}")

        elif cmd == "SWITCH":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            name = tokens[1]
            if name not in graph.branches:
                print(f"(error) ERR branch '{name}' not found")
            else:
                graph.switch(name)
                print(f"Switched to branch: {name}")

        elif cmd == "LOG":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue

            sort_by = None
            for t in tokens[1:]:
                if t.startswith("--sort-by="):
                    sort_by = t.split("=", 1)[1]

            all_commits = list(graph.commits.values())

            if sort_by == "date":
                ordered = merge_sort(all_commits, key=lambda c: c.timestamp)
                for c in ordered:
                    print(f"commit {c.hash} ({c.author}, {c.timestamp})")
                    print(f"    {c.message}")
            elif sort_by == "author":
                ordered = merge_sort(all_commits, key=lambda c: c.author)
                for c in ordered:
                    print(f"commit {c.hash} ({c.author}, {c.timestamp})")
                    print(f"    {c.message}")
            else:
                # 모든 브랜치의 모든 커밋을 시간 역순으로 출력
                ordered = merge_sort(all_commits, key=lambda c: c.timestamp)
                ordered = ordered[::-1]
                for c in ordered:
                    print(f"commit {c.hash} ({c.author}, {c.timestamp}) [{c.branch}]")
                    print(f"    {c.message}")

        elif cmd == "PATH":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 3:
                print("(error) ERR wrong number of arguments")
                continue
            h1, h2 = tokens[1], tokens[2]
            path = find_path(graph, h1, h2)
            if path is None:
                print("No path found.")
            else:
                print("Path: " + " -> ".join(path))

        elif cmd == "ANCESTORS":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            h = tokens[1]
            if h not in graph.commits:
                print(f"(error) ERR commit '{h}' not found")
                continue
            ancestors = find_ancestors(graph, h)
            print(f"Ancestors of {h}:")
            if not ancestors:
                print("(none)")
            else:
                for a in ancestors:
                    print(f"- {a}")

        elif cmd == "SEARCH":
            if graph is None:
                print("(error) ERR repository not initialized")
                continue
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue

            query = tokens[1]
            if query.startswith("--author="):
                author = query.split("=", 1)[1]
                matching_hashes = index.search_by_author(author)
            else:
                matching_hashes = index.search_by_keyword(query)

            matching_commits = [
                graph.commits[h] for h in matching_hashes
                if h in graph.commits
            ]
            matching_commits = merge_sort(
                matching_commits, key=lambda c: c.timestamp
            )
            print(f"Found {len(matching_commits)} commit(s):")
            for c in matching_commits:
                print(f"- {c.hash}: {c.message}")

        else:
            print(f"(error) ERR unknown command '{tokens[0]}'")


if __name__ == "__main__":
    main()
