"""
프롬프트 관리 프로그램 구조 검증 플러그인 (25점)

AST 분석으로 학습자의 prompt_manager.py 소스코드를 검증.
함수 분리, list+dict 데이터 구조, 초기 데이터, 외부 라이브러리 미사용을 확인.
"""
import ast
from typing import Dict, Any, List, Tuple

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.python.validators._helpers import collect_py_files, parse_all_files


# 허용 import 목록 (표준 라이브러리)
_ALLOWED_MODULES = frozenset({
    "os", "sys", "json", "csv", "re", "math", "random",
    "datetime", "time", "pathlib", "collections", "itertools",
    "functools", "typing", "dataclasses", "abc", "io",
    "string", "textwrap", "copy", "enum", "operator",
})


class PMStructureValidator(BaseValidator):
    """프롬프트 관리 프로그램 소스코드 구조 검증"""

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
            id="func_separation",
            description="기능별 함수 분리 (def 5개 이상)",
            points=8,
            validator=self._check_func_separation,
            hint="add_prompt, list_prompts, search_prompts 등 기능별로 함수를 분리하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="data_structure",
            description="list + dict 데이터 구조 사용",
            points=7,
            validator=self._check_data_structure,
            hint="프롬프트를 딕셔너리의 리스트로 관리하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="initial_data",
            description="초기 데이터 3개 이상 포함",
            points=5,
            validator=self._check_initial_data,
            hint="프로그램 시작 시 3개 이상의 프롬프트가 있어야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="no_external_lib",
            description="외부 라이브러리 미사용",
            points=5,
            validator=self._check_no_external_lib,
            hint="표준 라이브러리만 사용하세요 (pip install 없이 실행 가능해야 함)",
        ))

    def teardown(self) -> None:
        pass

    # -- 검증 함수 --

    def _check_func_separation(self) -> bool:
        """소스코드에 def 5개 이상 존재하는지 확인"""
        total_funcs = 0
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_funcs += 1
        return total_funcs >= 5

    def _check_data_structure(self) -> bool:
        """AST에서 List + Dict 리터럴 사용 확인"""
        has_list = False
        has_dict = False

        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.List):
                    has_list = True
                if isinstance(node, ast.Dict):
                    has_dict = True
                if has_list and has_dict:
                    return True

        return has_list and has_dict

    def _check_initial_data(self) -> bool:
        """dict 3개 이상을 포함하는 list 리터럴이 있는지 확인"""
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.List):
                    dict_count = sum(
                        1 for elt in node.elts
                        if isinstance(elt, ast.Dict)
                    )
                    if dict_count >= 3:
                        return True
        return False

    def _check_no_external_lib(self) -> bool:
        """import 문에서 외부 라이브러리를 사용하지 않는지 확인"""
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_module = alias.name.split(".")[0]
                        if top_module not in _ALLOWED_MODULES:
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top_module = node.module.split(".")[0]
                        if top_module not in _ALLOWED_MODULES:
                            return False
        return True
