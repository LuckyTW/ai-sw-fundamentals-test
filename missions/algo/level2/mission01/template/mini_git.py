"""
Mini Git 커밋 그래프 시뮬레이터

## 요구사항
- Commit 클래스: hash, message, author, timestamp, parents 속성
- CommitGraph 클래스: dict 기반 커밋 저장소, 브랜치 관리
- InvertedIndex 클래스: 단어/작성자 역색인
- merge sort 직접 구현 (내장 sorted/list.sort/heapq 사용 금지!)
- BFS 기반 경로 탐색 (무방향) 및 조상 탐색
"""
import hashlib
from datetime import datetime


def generate_hash(message: str, seq: int) -> str:
    """커밋 해시 생성 (이 함수를 수정하지 마세요)"""
    return hashlib.sha256(f"{message}:{seq}".encode()).hexdigest()[:7]


class Commit:
    """커밋 노드

    TODO: hash, message, author, timestamp, parents, branch 속성을 구현하세요
    """

    def __init__(self, hash_val: str, message: str, author: str,
                 timestamp: str, parents: list | None = None,
                 branch: str = "main"):
        pass  # TODO: 구현하세요


class CommitGraph:
    """커밋 DAG + 저장소

    TODO: commits(dict), branches(dict), head_branch 등을 구현하세요
    """

    def __init__(self):
        pass  # TODO: 초기화

    def init(self, author: str) -> None:
        """저장소 초기화"""
        pass  # TODO: 구현하세요

    def commit(self, message: str):
        """새 커밋 생성

        주의: HEAD 브랜치의 최신 커밋을 부모로 설정해야 합니다!
        (전역 '마지막 커밋'이 아닌, 현재 브랜치의 최신 커밋)
        """
        pass  # TODO: 구현하세요

    def branch(self, name: str) -> None:
        """새 브랜치 생성"""
        pass  # TODO: 구현하세요

    def switch(self, name: str) -> None:
        """브랜치 전환"""
        pass  # TODO: 구현하세요


class InvertedIndex:
    """역색인 — 단어/작성자 -> 커밋 해시 매핑

    TODO: word_index(dict), author_index(dict)를 구현하세요
    """

    def __init__(self):
        pass  # TODO: 초기화

    def add_commit(self, commit) -> None:
        """커밋의 메시지 단어와 작성자를 인덱싱"""
        pass  # TODO: 구현하세요

    def search_by_keyword(self, keyword: str) -> set:
        """키워드로 커밋 검색"""
        pass  # TODO: 구현하세요

    def search_by_author(self, author: str) -> set:
        """작성자로 커밋 검색"""
        pass  # TODO: 구현하세요


# -- 직접 구현 정렬 (내장 sorted/list.sort/heapq 사용 금지!) --

def merge_sort(arr: list, key=None) -> list:
    """머지 소트 직접 구현"""
    pass  # TODO: 구현하세요


def _merge(left: list, right: list, key=None) -> list:
    """두 정렬된 리스트 병합"""
    pass  # TODO: 구현하세요


# -- 그래프 알고리즘 --

def find_path(graph, hash1: str, hash2: str):
    """BFS로 두 커밋 간 최단 경로

    주의: 부모-자식 양방향으로 탐색해야 합니다! (무방향 그래프 취급)
    부모 방향으로만 탐색하면, 다른 브랜치에 있는 커밋 간 경로를 찾을 수 없습니다.
    """
    pass  # TODO: 구현하세요


def find_ancestors(graph, commit_hash: str) -> list:
    """BFS로 모든 조상 탐색 (부모 방향만)"""
    pass  # TODO: 구현하세요
