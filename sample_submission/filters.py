import functools
from typing import List, Generator, Callable


def validate_args(func: Callable) -> Callable:
    """인자 타입 검증 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg is None:
                raise TypeError("None은 허용되지 않습니다")
        return func(*args, **kwargs)
    return wrapper


@validate_args
def search_books(books: List, keyword: str) -> Generator:
    """도서 목록에서 keyword가 제목에 포함된 도서를 yield합니다."""
    for book in books:
        if keyword.lower() in book.title.lower():
            yield book


def filter_by_price(books: List, max_price: int) -> Generator:
    """가격 기준 필터링"""
    for book in books:
        if book.price <= max_price:
            yield book
