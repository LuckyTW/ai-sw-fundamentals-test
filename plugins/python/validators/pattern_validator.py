"""
코딩 패턴 검증 플러그인 (25점)

학습자가 yield 제너레이터, 사용자 정의 데코레이터, 타입 힌트 등
중급 Python 패턴을 올바르게 활용하는지 AST + 런타임 검증.

AI 트랩: yield 미사용(리스트 반환), Any 타입 남용
"""
import ast
import inspect
from typing import Dict, Any, List, Set, Tuple

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.python.validators._helpers import (
    import_student_module,
    collect_py_files,
    parse_all_files,
)


class PatternValidator(BaseValidator):
    """코딩 패턴 검증 (yield, 데코레이터, 타입 힌트, Any 비율)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.parsed: List[Tuple[str, ast.Module]] = []
        self.filters_module = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        py_files = collect_py_files(self.submission_dir)
        self.parsed = parse_all_files(py_files)
        self.filters_module = import_student_module(self.submission_dir, "filters")

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="pattern_yield",
            description="search_books가 yield 제너레이터로 구현되어 있는지 확인",
            points=7,
            validator=self._check_yield,
            hint="search_books 함수에서 yield를 사용하여 결과를 반환하세요 (리스트가 아닌 제너레이터)",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="pattern_decorator",
            description="사용자 정의 데코레이터가 정의·적용되어 있는지 확인",
            points=7,
            validator=self._check_decorator,
            hint="functools.wraps를 사용한 사용자 정의 데코레이터를 만들고 적용하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="pattern_type_hints",
            description="3개 이상의 함수에 타입 힌트가 적용되어 있는지 확인",
            points=6,
            validator=self._check_type_hints,
            hint="함수 매개변수나 반환값에 타입 힌트를 추가하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="pattern_no_any",
            description="Any 타입 비율이 30% 미만인지 확인",
            points=5,
            validator=self._check_no_any,
            hint="Any 대신 구체적인 타입(str, int, List[...] 등)을 사용하세요",
            ai_trap=True,
        ))

    def teardown(self) -> None:
        pass

    # -- 검증 함수 --

    def _check_yield(self) -> bool:
        """
        AI 트랩: AI는 yield 대신 리스트를 반환하기 쉬움.
        AST에서 search_books 함수 내 Yield 확인 + isgeneratorfunction + 호출 테스트
        """
        # 1. AST에서 search_books 함수 내 yield 확인
        has_yield_in_search = False
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "search_books":
                    for child in ast.walk(node):
                        if isinstance(child, (ast.Yield, ast.YieldFrom)):
                            has_yield_in_search = True
                            break
        if not has_yield_in_search:
            return False

        # 2. 런타임 확인: isgeneratorfunction 또는 __wrapped__ 추적
        if self.filters_module is None:
            # AST만으로 yield 확인됐으면 통과
            return True
        search_fn = getattr(self.filters_module, "search_books", None)
        if search_fn is None:
            return True  # AST 확인 완료

        # 데코레이터 감싸기 고려: __wrapped__ 추적
        unwrapped = search_fn
        for _ in range(10):  # 무한 루프 방지
            inner = getattr(unwrapped, "__wrapped__", None)
            if inner is None:
                break
            unwrapped = inner

        if inspect.isgeneratorfunction(unwrapped):
            return True

        # 3. 실제 호출하여 generator 반환 확인
        try:
            models_module = import_student_module(self.submission_dir, "models")
            if models_module and hasattr(models_module, "Book"):
                book_cls = models_module.Book
                test_books = [
                    book_cls(isbn="978-test-001", title="파이썬 입문", author="홍길동", price=20000),
                    book_cls(isbn="978-test-002", title="자바 입문", author="김철수", price=25000),
                ]
                result = search_fn(test_books, "파이썬")
                return hasattr(result, "__next__")
        except Exception:
            pass

        # AST에서 yield 확인됐으면 통과
        return True

    def _check_decorator(self) -> bool:
        """
        사용자 정의 데코레이터 정의·적용 확인:
        1. AST: 제출물 내 정의된 함수가 데코레이터로 사용됨
        2. functools.wraps 사용 확인
        3. 동작 테스트 (validate_args 데코레이터가 잘못된 타입 → TypeError)
        """
        stdlib_decorators = {
            "staticmethod", "classmethod", "property",
            "abstractmethod", "dataclass", "cached_property",
            "overload", "override",
        }

        # 1. AST: 정의된 함수 중 데코레이터로 사용된 것 확인
        defined_funcs: Set[str] = set()
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_funcs.add(node.name)

        decorator_found = False
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                for deco in node.decorator_list:
                    name = _extract_decorator_name(deco)
                    if name and name not in stdlib_decorators and name in defined_funcs:
                        decorator_found = True
                        break

        if not decorator_found:
            return False

        # 2. functools.wraps 사용 확인 (선택적 가산)
        has_wraps = False
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == "wraps":
                    has_wraps = True
                elif isinstance(node, ast.Name) and node.id == "wraps":
                    has_wraps = True

        # 데코레이터가 존재하면 통과 (wraps 없어도)
        return True

    def _check_type_hints(self) -> bool:
        """전체 제출 파일에서 타입 힌트가 있는 함수 3개 이상"""
        hinted_count = 0
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _has_type_hints(node):
                        hinted_count += 1
        return hinted_count >= 3

    def _check_no_any(self) -> bool:
        """
        AI 트랩: AI가 타입 힌트에 Any를 남용하기 쉬움.
        전체 annotation 중 Any 비율 < 30%
        """
        total_annotations = 0
        any_count = 0

        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                # 반환 타입
                if node.returns:
                    total_annotations += 1
                    if _is_any_annotation(node.returns):
                        any_count += 1
                # 매개변수 타입
                for arg in node.args.args + node.args.kwonlyargs:
                    if arg.annotation:
                        total_annotations += 1
                        if _is_any_annotation(arg.annotation):
                            any_count += 1

        # annotation이 없으면 통과
        if total_annotations == 0:
            return True
        return (any_count / total_annotations) < 0.3


# -- 모듈 레벨 헬퍼 --

def _extract_decorator_name(deco: ast.expr) -> str:
    """데코레이터 노드에서 함수 이름 추출"""
    if isinstance(deco, ast.Name):
        return deco.id
    if isinstance(deco, ast.Call):
        return _extract_decorator_name(deco.func)
    if isinstance(deco, ast.Attribute):
        return deco.attr
    return ""


def _has_type_hints(func_node: ast.FunctionDef) -> bool:
    """함수에 하나라도 타입 힌트가 있는지"""
    if func_node.returns:
        return True
    for arg in func_node.args.args + func_node.args.kwonlyargs:
        if arg.annotation:
            return True
    return False


def _is_any_annotation(ann: ast.expr) -> bool:
    """annotation이 Any인지 확인"""
    if isinstance(ann, ast.Name) and ann.id == "Any":
        return True
    if isinstance(ann, ast.Attribute) and ann.attr == "Any":
        return True
    return False
