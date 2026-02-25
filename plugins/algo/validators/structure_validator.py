"""
Mini Git 구조 검증 플러그인 (20점)

AST 분석으로 학습자가 Commit 클래스를 올바르게 정의했는지,
내장 정렬 함수를 사용하지 않았는지, dict 기반 저장소를 사용하는지 검증.

AI 트랩: sorted()/list.sort()/heapq 사용
"""
import ast
from typing import Dict, Any, List, Tuple

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.python.validators._helpers import (
    collect_py_files,
    parse_all_files,
)


class StructureValidator(BaseValidator):
    """Mini Git 코드 구조 검증 (Commit 클래스, 금지 정렬, dict 저장소)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.parsed: List[Tuple[str, ast.Module]] = []

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        py_files = collect_py_files(self.submission_dir)
        self.parsed = parse_all_files(py_files)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="commit_class",
            description="Commit 클래스에 hash/message/author/timestamp/parents 속성이 존재하는지 확인",
            points=8,
            validator=self._check_commit_class,
            hint="Commit 클래스에 hash, message, author, timestamp, parents 속성을 정의하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="no_builtin_sort",
            description="sorted()/list.sort()/heapq를 사용하지 않는지 확인",
            points=7,
            validator=self._check_no_builtin_sort,
            hint="sorted(), list.sort(), heapq 대신 merge sort를 직접 구현하세요",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="graph_structure",
            description="커밋 저장소가 dict(해시맵) 기반인지 확인",
            points=5,
            validator=self._check_graph_structure,
            hint="커밋 저장소를 dict 또는 {} 로 초기화하세요 (예: self.commits = {})",
        ))

    def teardown(self) -> None:
        pass

    # -- 검증 함수 --

    def _check_commit_class(self) -> bool:
        """AST에서 Commit 클래스의 __init__에 hash/message/author/timestamp/parents 할당 확인"""
        required_attrs = {"hash", "message", "author", "timestamp", "parents"}

        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if not (isinstance(node, ast.ClassDef) and node.name == "Commit"):
                    continue

                found_attrs = set()
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if (isinstance(target, ast.Attribute)
                                            and isinstance(target.value, ast.Name)
                                            and target.value.id == "self"):
                                        found_attrs.add(target.attr)
                            if isinstance(stmt, ast.AnnAssign):
                                if (isinstance(stmt.target, ast.Attribute)
                                        and isinstance(stmt.target.value, ast.Name)
                                        and stmt.target.value.id == "self"):
                                    found_attrs.add(stmt.target.attr)

                if required_attrs.issubset(found_attrs):
                    return True

        return False

    def _check_no_builtin_sort(self) -> bool:
        """AST에서 sorted()/list.sort()/heapq 사용 탐지"""
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                # sorted() 호출
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                        return False
                    # .sort() 메서드 호출
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                        return False

                # import heapq
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "heapq":
                            return False

                # from heapq import ...
                if isinstance(node, ast.ImportFrom):
                    if node.module == "heapq":
                        return False

        return True

    def _check_graph_structure(self) -> bool:
        """클래스 __init__에서 dict 기반 커밋 저장소 사용 확인

        self.commits = {} 또는 self.commits = dict() 또는
        self.store = {} 등의 패턴을 탐지
        """
        dict_attr_names = {"commits", "store", "commit_store", "graph", "nodes"}

        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                for item in node.body:
                    if not (isinstance(item, ast.FunctionDef)
                            and item.name == "__init__"):
                        continue

                    for stmt in ast.walk(item):
                        # self.attr = {} 패턴
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if (isinstance(target, ast.Attribute)
                                        and isinstance(target.value, ast.Name)
                                        and target.value.id == "self"
                                        and target.attr in dict_attr_names):
                                    # 값이 {} 또는 dict()인지 확인
                                    if isinstance(stmt.value, ast.Dict):
                                        return True
                                    if (isinstance(stmt.value, ast.Call)
                                            and isinstance(stmt.value.func, ast.Name)
                                            and stmt.value.func.id == "dict"):
                                        return True

                        # self.attr: dict = {} 패턴 (AnnAssign)
                        if isinstance(stmt, ast.AnnAssign):
                            if (isinstance(stmt.target, ast.Attribute)
                                    and isinstance(stmt.target.value, ast.Name)
                                    and stmt.target.value.id == "self"
                                    and stmt.target.attr in dict_attr_names):
                                if stmt.value is not None:
                                    if isinstance(stmt.value, ast.Dict):
                                        return True
                                    if (isinstance(stmt.value, ast.Call)
                                            and isinstance(stmt.value.func, ast.Name)
                                            and stmt.value.func.id == "dict"):
                                        return True

        return False
