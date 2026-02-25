"""
Mini Git CLI - 커밋 그래프 REPL 인터페이스

## 지원 명령어
- INIT <name>                    → 저장소 초기화
- COMMIT "<message>"             → 커밋 생성
- BRANCH <name>                  → 브랜치 생성
- SWITCH <name>                  → 브랜치 전환
- LOG [--sort-by=date|author]    → 커밋 로그 출력 (모든 브랜치!)
- PATH <hash1> <hash2>          → 최단 경로 탐색 (무방향 BFS!)
- ANCESTORS <hash>               → 조상 커밋 목록
- SEARCH <keyword>               → 키워드 검색
- SEARCH --author=<name>         → 작성자 검색
- EXIT / QUIT                    → 종료

## 출력 형식
- INIT:      Initialized repository. / Current branch: main / Current user: <name>
- COMMIT:    [<branch> <hash>] <message>
- BRANCH:    Created branch: <name>
- SWITCH:    Switched to branch: <name>
- LOG:       commit <hash> (<author>, <timestamp>) [<branch>] (기본)
             commit <hash> (<author>, <timestamp>) (--sort-by 옵션 시 브랜치 라벨 없음)
                 <message>
- PATH:      Path: <h1> -> <h2> -> ... 또는 No path found.
- ANCESTORS: Ancestors of <hash>: / - <ancestor> 또는 (none)
- SEARCH:    Found N commit(s): / - <hash>: <message>
- 에러:      (error) ERR unknown command '<cmd>'
             (error) ERR wrong number of arguments
             (error) ERR branch '<name>' already exists
             (error) ERR branch '<name>' not found

## 프롬프트
- mini-git>

TODO: 각 명령어의 로직을 구현하세요 (REPL 루프와 파싱은 제공됨)
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
            # TODO: 저장소 초기화
            # graph = CommitGraph() → graph.init(tokens[1])
            # index = InvertedIndex()
            # 출력: Initialized repository.
            #       Current branch: main
            #       Current user: <name>

        elif cmd == "COMMIT":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 커밋 생성 + 역색인 추가
            # commit = graph.commit(tokens[1])
            # index.add_commit(commit)
            # 출력: [<branch> <hash>] <message>

        elif cmd == "BRANCH":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 브랜치 생성
            # 출력: Created branch: <name>
            # 에러: (error) ERR branch '<name>' already exists

        elif cmd == "SWITCH":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 브랜치 전환
            # 출력: Switched to branch: <name>
            # 에러: (error) ERR branch '<name>' not found

        elif cmd == "LOG":
            # TODO: 커밋 로그 출력
            # --sort-by=date|author 옵션 처리
            #
            # 기본 (옵션 없음): 모든 브랜치의 모든 커밋, 시간 역순, 브랜치 라벨 포함
            #   commit <hash> (<author>, <timestamp>) [<branch>]
            #       <message>
            #
            # --sort-by=date: 시간순 (오래된 것부터), 브랜치 라벨 없음
            #   commit <hash> (<author>, <timestamp>)
            #       <message>
            #
            # --sort-by=author: 작성자 이름순, 브랜치 라벨 없음
            pass

        elif cmd == "PATH":
            if len(tokens) < 3:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 두 커밋 간 최단 경로 (무방향 BFS!)
            # path = find_path(graph, tokens[1], tokens[2])
            # 출력: Path: <h1> -> <h2> -> ...
            # 실패: No path found.

        elif cmd == "ANCESTORS":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 조상 커밋 목록
            # ancestors = find_ancestors(graph, tokens[1])
            # 출력: Ancestors of <hash>:
            #       - <ancestor_hash>
            # 없음: (none)

        elif cmd == "SEARCH":
            if len(tokens) < 2:
                print("(error) ERR wrong number of arguments")
                continue
            # TODO: 키워드 또는 작성자 검색
            # tokens[1]이 --author=Name 이면 작성자 검색
            # 아니면 키워드 검색
            # 출력: Found N commit(s):
            #       - <hash>: <message>

        else:
            print(f"(error) ERR unknown command '{tokens[0]}'")


if __name__ == "__main__":
    main()
