"""
도서 관리 시스템 - 필터링 및 검색

TODO: 아래 요구사항에 맞게 함수들을 구현하세요.

요구사항:
1. search_books: yield 제너레이터로 구현 (리스트 반환 금지!)
2. validate_args: 사용자 정의 데코레이터로 구현
   - functools.wraps를 사용하세요
   - 잘못된 타입 입력 시 TypeError를 발생시키세요
3. 모든 함수에 타입 힌트를 적용하세요 (Any 사용 금지!)
"""
from typing import List, Generator


# TODO: validate_args 데코레이터를 구현하세요
# 힌트: functools.wraps를 사용하여 원래 함수의 메타데이터를 유지하세요


# TODO: search_books 제너레이터 함수를 구현하세요
# 힌트: yield를 사용하여 검색 결과를 하나씩 반환하세요
# def search_books(books: List, keyword: str) -> Generator:
#     """도서 목록에서 keyword가 제목에 포함된 도서를 yield합니다."""
#     pass
