"""
데이터 저장 방식 검증 플러그인 (20점)

학습자가 도서 데이터를 save_books/load_books로 왕복 저장하는지,
JSONL/JSON/CSV 형식을 사용하는지, pickle을 사용하지 않는지,
저장 데이터에 필수 필드가 포함되어 있는지 검증.

AI 트랩: pickle 사용
"""
import ast
import csv
import glob
import io
import json
import os
import tempfile
from typing import Dict, Any, List, Tuple, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.python.validators._helpers import (
    import_student_module,
    collect_py_files,
    parse_all_files,
)


class PersistenceValidator(BaseValidator):
    """데이터 저장 검증 (왕복 무결성, 형식, pickle 미사용, 필수 필드)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.storage_module = None
        self.models_module = None
        self.parsed_trees: List[Tuple[str, ast.Module]] = []
        # save 후 생성된 파일 경로
        self.saved_file: Optional[str] = None
        # 임시 디렉토리 (save 테스트용)
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        self.models_module = import_student_module(self.submission_dir, "models")
        self.storage_module = import_student_module(self.submission_dir, "storage")

        py_files = collect_py_files(self.submission_dir)
        self.parsed_trees = parse_all_files(py_files)

        # 미리 save를 실행하여 format/integrity가 roundtrip과 독립 동작하도록 함
        books = self._make_test_books()
        if books is not None:
            self.saved_file = self._do_save(books)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="persist_roundtrip",
            description="save_books → load_books 왕복 무결성 확인",
            points=7,
            validator=self._check_roundtrip,
            hint="save_books로 저장한 데이터를 load_books로 정확히 복원할 수 있어야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="persist_format",
            description="저장 파일이 JSONL/JSON/CSV 형식인지 확인",
            points=3,
            validator=self._check_format,
            hint="데이터를 JSONL, JSON, 또는 CSV 형식으로 저장하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="persist_no_pickle",
            description="pickle 모듈을 사용하지 않는지 확인",
            points=5,
            validator=self._check_no_pickle,
            hint="pickle 대신 json/csv 등 텍스트 기반 직렬화를 사용하세요",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="persist_integrity",
            description="저장된 데이터에 isbn, title, author, price 필드가 포함되어 있는지 확인",
            points=5,
            validator=self._check_integrity,
            hint="각 도서 레코드에 isbn, title, author, price 필드를 포함하세요",
        ))

    def teardown(self) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()

    # -- save/load 테스트 헬퍼 --

    def _make_test_books(self) -> Optional[list]:
        """테스트용 Book 인스턴스 리스트 생성"""
        if self.models_module is None:
            return None
        book_cls = getattr(self.models_module, "Book", None)
        if book_cls is None:
            return None

        try:
            return [
                book_cls(isbn="978-89-1111-111-1", title="파이썬 입문", author="홍길동", price=20000),
                book_cls(isbn="978-89-2222-222-2", title="자바 입문", author="김철수", price=25000),
            ]
        except Exception:
            return None

    def _do_save(self, books: list) -> Optional[str]:
        """storage.save_books 호출, 생성된 파일 경로 반환"""
        if self.storage_module is None:
            return None
        save_fn = getattr(self.storage_module, "save_books", None)
        if save_fn is None:
            return None

        # 임시 디렉토리에서 save 테스트
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = self._tmpdir.name

        try:
            # save_books(books, filepath) 형태 시도
            filepath = os.path.join(tmp_path, "books_test.jsonl")
            save_fn(books, filepath)
            if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
                return filepath
        except TypeError:
            pass
        except Exception:
            pass

        # save_books(books) 형태 → submission_dir에 파일 생성될 수 있음
        try:
            save_fn(books)
            # submission_dir에서 데이터 파일 탐색
            for pattern in ["*.jsonl", "*.json", "*.csv"]:
                found = glob.glob(os.path.join(self.submission_dir, pattern))
                if found:
                    return found[0]
            # 임시 디렉토리에서도 탐색
            for pattern in ["*.jsonl", "*.json", "*.csv"]:
                found = glob.glob(os.path.join(tmp_path, pattern))
                if found:
                    return found[0]
        except Exception:
            pass

        return None

    def _do_load(self, filepath: str) -> Optional[list]:
        """storage.load_books 호출"""
        if self.storage_module is None:
            return None
        load_fn = getattr(self.storage_module, "load_books", None)
        if load_fn is None:
            return None

        try:
            return load_fn(filepath)
        except Exception:
            return None

    # -- 검증 함수 --

    def _check_roundtrip(self) -> bool:
        """save → load 왕복 무결성 확인 (save는 setup에서 실행 완료)"""
        if self.saved_file is None:
            return False

        books = self._make_test_books()
        if books is None:
            return False

        loaded = self._do_load(self.saved_file)
        if loaded is None or len(loaded) != len(books):
            return False

        # isbn으로 매칭하여 필드 비교
        original_isbns = {getattr(b, "isbn", None) for b in books}
        loaded_isbns = set()
        for item in loaded:
            if hasattr(item, "isbn"):
                loaded_isbns.add(item.isbn)
            elif isinstance(item, dict):
                loaded_isbns.add(item.get("isbn"))

        return original_isbns == loaded_isbns

    def _check_format(self) -> bool:
        """저장된 파일이 유효한 JSONL/JSON/CSV인지 파싱"""
        filepath = self.saved_file
        if not filepath or not os.path.isfile(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except (OSError, UnicodeDecodeError):
            return False

        if not content:
            return False

        # JSONL
        if filepath.endswith(".jsonl"):
            return _parse_jsonl(content) is not None
        # JSON
        if filepath.endswith(".json"):
            return _parse_json(content) is not None
        # CSV
        if filepath.endswith(".csv"):
            return _parse_csv(content) is not None

        # 확장자가 없으면 순서대로 시도
        return (_parse_jsonl(content) is not None
                or _parse_json(content) is not None
                or _parse_csv(content) is not None)

    def _check_no_pickle(self) -> bool:
        """
        AI 트랩: AI가 편의상 pickle로 직렬화할 수 있음.
        AST에서 pickle import 탐색 + .pkl/.pickle 파일 존재 확인
        """
        # 1. AST에서 pickle import 탐색
        for _, tree in self.parsed_trees:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "pickle" or alias.name.startswith("pickle."):
                            return False
                if isinstance(node, ast.ImportFrom):
                    if node.module and (node.module == "pickle"
                                        or node.module.startswith("pickle.")):
                        return False

        # 2. .pkl / .pickle 파일 존재 확인
        for pattern in ["*.pkl", "*.pickle"]:
            if glob.glob(os.path.join(self.submission_dir, "**", pattern), recursive=True):
                return False

        return True

    def _check_integrity(self) -> bool:
        """저장된 파일의 레코드에 isbn, title, author, price 키 포함"""
        filepath = self.saved_file
        if not filepath or not os.path.isfile(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except (OSError, UnicodeDecodeError):
            return False

        records = (_parse_jsonl(content)
                   or _parse_json(content)
                   or _parse_csv(content))

        if not records:
            return False

        required_keys = {"isbn", "title", "author", "price"}
        for record in records:
            keys_lower = {k.lower() for k in record.keys()}
            if required_keys.issubset(keys_lower):
                return True
        return False


# -- 파싱 헬퍼 (모듈 레벨) --

def _parse_jsonl(content: str) -> Optional[List[Dict[str, Any]]]:
    records = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except json.JSONDecodeError:
            return None
    return records if records else None


def _parse_json(content: str) -> Optional[List[Dict[str, Any]]]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)] or None
    if isinstance(data, dict):
        return [data]
    return None


def _parse_csv(content: str) -> Optional[List[Dict[str, Any]]]:
    try:
        reader = csv.DictReader(io.StringIO(content))
        records = [dict(row) for row in reader]
        return records if records else None
    except csv.Error:
        return None
