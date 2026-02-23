"""
데이터 모델 검증 플러그인 (25점)

학습자가 Book 데이터 모델을 @dataclass로 올바르게 정의했는지,
필수 필드·타입 힌트·유효성 검증(__post_init__)이 구현되어 있는지 확인.
"""
import ast
from typing import Dict, Any, List, Tuple

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.python.validators._helpers import (
    import_student_module,
    collect_py_files,
    parse_all_files,
)


class ModelValidator(BaseValidator):
    """Book 데이터 모델 검증 (dataclass, 필드, 타입 힌트, __post_init__)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.models_module = None
        self.parsed: List[Tuple[str, ast.Module]] = []

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        self.models_module = import_student_module(self.submission_dir, "models")
        py_files = collect_py_files(self.submission_dir)
        self.parsed = parse_all_files(py_files)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="model_dataclass",
            description="Book 클래스가 @dataclass로 정의되어 있는지 확인",
            points=7,
            validator=self._check_dataclass,
            hint="from dataclasses import dataclass 후 @dataclass로 Book을 정의하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="model_fields",
            description="Book에 필수 필드(isbn, title, author, price, is_available)가 있는지 확인",
            points=6,
            validator=self._check_fields,
            hint="Book(isbn=..., title=..., author=..., price=..., is_available=...)로 생성 가능해야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="model_type_hints",
            description="Book 필드에 타입 힌트가 적용되어 있는지 확인",
            points=5,
            validator=self._check_type_hints,
            hint="isbn: str, price: int 등 각 필드에 타입 힌트를 추가하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="model_post_init",
            description="price < 0일 때 ValueError가 발생하는지 확인",
            points=7,
            validator=self._check_post_init,
            hint="__post_init__에서 price < 0이면 ValueError를 raise하세요",
        ))

    def teardown(self) -> None:
        pass

    # -- 검증 함수 --

    def _check_dataclass(self) -> bool:
        """AST에서 @dataclass 데코레이터 확인 + 런타임 __dataclass_fields__ 확인"""
        # AST 확인: Book 클래스에 @dataclass 데코레이터가 있는지
        has_decorator = False
        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "Book":
                    for deco in node.decorator_list:
                        name = _extract_decorator_name(deco)
                        if name == "dataclass":
                            has_decorator = True
                            break
        if not has_decorator:
            return False

        # 런타임 확인
        if self.models_module is None:
            return False
        book_cls = getattr(self.models_module, "Book", None)
        if book_cls is None:
            return False
        return hasattr(book_cls, "__dataclass_fields__")

    def _check_fields(self) -> bool:
        """Book 인스턴스를 생성하여 필수 필드 존재 확인"""
        if self.models_module is None:
            return False
        book_cls = getattr(self.models_module, "Book", None)
        if book_cls is None:
            return False

        required_fields = {"isbn", "title", "author", "price", "is_available"}

        try:
            book = book_cls(
                isbn="978-89-1234-567-8",
                title="파이썬 프로그래밍",
                author="홍길동",
                price=25000,
            )
        except TypeError:
            # is_available에 기본값이 없어서 필수일 수도 있음
            try:
                book = book_cls(
                    isbn="978-89-1234-567-8",
                    title="파이썬 프로그래밍",
                    author="홍길동",
                    price=25000,
                    is_available=True,
                )
            except Exception:
                return False

        # 필수 필드가 모두 있는지 확인
        for field_name in required_fields:
            if not hasattr(book, field_name):
                return False
        return True

    def _check_type_hints(self) -> bool:
        """AST에서 Book 클래스 필드의 annotation 존재 확인"""
        required_fields = {"isbn", "title", "author", "price", "is_available"}

        for _, tree in self.parsed:
            for node in ast.walk(tree):
                if not (isinstance(node, ast.ClassDef) and node.name == "Book"):
                    continue
                annotated_fields = set()
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        annotated_fields.add(item.target.id)
                # 필수 필드가 모두 annotation을 가지고 있는지
                if required_fields.issubset(annotated_fields):
                    return True
        return False

    def _check_post_init(self) -> bool:
        """price < 0으로 Book 생성 시 ValueError 발생 확인"""
        if self.models_module is None:
            return False
        book_cls = getattr(self.models_module, "Book", None)
        if book_cls is None:
            return False

        try:
            book_cls(
                isbn="978-89-0000-000-0",
                title="테스트",
                author="테스터",
                price=-1000,
            )
            # ValueError 없이 생성되면 실패
            return False
        except ValueError:
            return True
        except Exception:
            return False


def _extract_decorator_name(deco: ast.expr) -> str:
    """데코레이터 노드에서 이름 추출"""
    if isinstance(deco, ast.Name):
        return deco.id
    if isinstance(deco, ast.Call):
        return _extract_decorator_name(deco.func)
    if isinstance(deco, ast.Attribute):
        return deco.attr
    return ""
