"""
Mini Git 커밋 그래프 시뮬레이터

커밋 DAG, BFS 경로 탐색, 역색인 검색, merge sort 직접 구현.
"""
import hashlib
from datetime import datetime


def generate_hash(message: str, seq: int) -> str:
    """커밋 해시 생성 (이 함수를 수정하지 마세요)"""
    return hashlib.sha256(f"{message}:{seq}".encode()).hexdigest()[:7]


class Commit:
    """커밋 노드"""

    def __init__(self, hash_val: str, message: str, author: str,
                 timestamp: str, parents: list | None = None,
                 branch: str = "main"):
        self.hash = hash_val
        self.message = message
        self.author = author
        self.timestamp = timestamp
        self.parents = parents or []
        self.branch = branch


class CommitGraph:
    """커밋 DAG + 저장소"""

    def __init__(self):
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, list[str]] = {}
        self.branches: dict[str, str | None] = {}
        self.head_branch: str = "main"
        self.author: str = ""
        self.commit_count: int = 0

    def init(self, author: str) -> None:
        """저장소 초기화"""
        self.commits = {}
        self.children = {}
        self.branches = {"main": None}
        self.head_branch = "main"
        self.author = author
        self.commit_count = 0

    def commit(self, message: str) -> Commit:
        """새 커밋 생성 — HEAD 브랜치의 최신 커밋을 부모로 설정"""
        self.commit_count += 1
        hash_val = generate_hash(message, self.commit_count)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        parent_hash = self.branches[self.head_branch]
        parents = [parent_hash] if parent_hash else []

        c = Commit(hash_val, message, self.author, timestamp,
                   parents, self.head_branch)
        self.commits[hash_val] = c

        for p in parents:
            if p not in self.children:
                self.children[p] = []
            self.children[p].append(hash_val)

        self.branches[self.head_branch] = hash_val
        return c

    def branch(self, name: str) -> None:
        """새 브랜치 생성 — 현재 HEAD 브랜치의 최신 커밋을 가리킴"""
        if name in self.branches:
            raise ValueError(f"branch '{name}' already exists")
        self.branches[name] = self.branches[self.head_branch]

    def switch(self, name: str) -> None:
        """브랜치 전환"""
        if name not in self.branches:
            raise ValueError(f"branch '{name}' not found")
        self.head_branch = name


class InvertedIndex:
    """역색인 — 단어/작성자 -> 커밋 해시 매핑"""

    def __init__(self):
        self.word_index: dict[str, set[str]] = {}
        self.author_index: dict[str, set[str]] = {}

    def add_commit(self, commit: Commit) -> None:
        """커밋의 메시지 단어와 작성자를 인덱싱"""
        words = commit.message.lower().split()
        for word in words:
            if word not in self.word_index:
                self.word_index[word] = set()
            self.word_index[word].add(commit.hash)

        author_key = commit.author.lower()
        if author_key not in self.author_index:
            self.author_index[author_key] = set()
        self.author_index[author_key].add(commit.hash)

    def search_by_keyword(self, keyword: str) -> set:
        """키워드로 커밋 검색"""
        return self.word_index.get(keyword.lower(), set())

    def search_by_author(self, author: str) -> set:
        """작성자로 커밋 검색"""
        return self.author_index.get(author.lower(), set())


# -- 직접 구현 정렬 --

def merge_sort(arr: list, key=None) -> list:
    """머지 소트 직접 구현"""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return _merge(left, right, key)


def _merge(left: list, right: list, key=None) -> list:
    """두 정렬된 리스트 병합"""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_val = key(left[i]) if key else left[i]
        right_val = key(right[j]) if key else right[j]
        if left_val <= right_val:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# -- 그래프 알고리즘 --

def find_path(graph: CommitGraph, hash1: str, hash2: str) -> list | None:
    """BFS로 두 커밋 간 최단 경로 (무방향 그래프 취급!)"""
    if hash1 not in graph.commits or hash2 not in graph.commits:
        return None
    if hash1 == hash2:
        return [hash1]

    # 무방향 인접 리스트 구축
    adj: dict[str, list[str]] = {}
    for h, commit in graph.commits.items():
        if h not in adj:
            adj[h] = []
        for p in commit.parents:
            if p not in adj:
                adj[p] = []
            adj[h].append(p)
            adj[p].append(h)

    # BFS
    visited = {hash1}
    queue = [(hash1, [hash1])]
    idx = 0
    while idx < len(queue):
        current, path = queue[idx]
        idx += 1
        for neighbor in adj.get(current, []):
            if neighbor == hash2:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def find_ancestors(graph: CommitGraph, commit_hash: str) -> list:
    """BFS로 모든 조상 탐색 (부모 방향만)"""
    if commit_hash not in graph.commits:
        return []

    ancestors = []
    visited = {commit_hash}
    queue = [commit_hash]
    idx = 0
    while idx < len(queue):
        current = queue[idx]
        idx += 1
        for parent in graph.commits[current].parents:
            if parent not in visited:
                visited.add(parent)
                ancestors.append(parent)
                queue.append(parent)
    return ancestors
