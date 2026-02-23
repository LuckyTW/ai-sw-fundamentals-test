"""
Python 검증 공통 유틸리티

학생 모듈 안전 import, Python 소스 파일 수집, AST 파싱 헬퍼.
모든 Python Validator가 공유한다.
"""
import ast
import glob
import importlib
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# 모듈 타입 힌트 (importlib에서 반환)
from types import ModuleType


def import_student_module(submission_dir: str, module_name: str) -> Optional[ModuleType]:
    """
    학생 제출 코드를 안전하게 import

    1. submission_dir을 sys.path 선두에 추가
    2. 이미 캐시된 모듈 제거 (재채점 대비)
    3. importlib.import_module 실행
    4. 실패 시 None 반환

    Args:
        submission_dir: 제출물 디렉토리 절대 경로
        module_name: import할 모듈 이름 (예: "models", "storage")

    Returns:
        import된 모듈 객체 또는 None
    """
    resolved = str(Path(submission_dir).resolve())

    # sys.path 선두에 추가 (중복 방지)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)

    # 캐시된 모듈 제거 → 재채점 시 최신 코드 반영
    if module_name in sys.modules:
        del sys.modules[module_name]

    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def collect_py_files(submission_dir: str) -> List[str]:
    """
    제출물 디렉토리에서 모든 .py 파일 경로를 수집 (재귀)

    Args:
        submission_dir: 제출물 루트 디렉토리 경로

    Returns:
        .py 파일 절대 경로 리스트
    """
    return glob.glob(f"{submission_dir}/**/*.py", recursive=True)


def parse_all_files(py_files: List[str]) -> List[Tuple[str, ast.Module]]:
    """
    여러 .py 파일을 AST로 파싱

    SyntaxError/UnicodeDecodeError가 발생하는 파일은 건너뜀.

    Args:
        py_files: .py 파일 경로 리스트

    Returns:
        (파일 경로, AST 모듈) 튜플 리스트
    """
    results = []
    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=filepath)
            results.append((filepath, tree))
        except (SyntaxError, UnicodeDecodeError):
            continue
    return results
