import json
from typing import List
from models import Book


def save_books(books: List[Book], filepath: str) -> None:
    """도서 목록을 JSONL 형식으로 저장"""
    with open(filepath, "w", encoding="utf-8") as f:
        for book in books:
            f.write(json.dumps(book.to_dict(), ensure_ascii=False) + "\n")


def load_books(filepath: str) -> List[Book]:
    """JSONL 파일에서 도서 목록을 로드"""
    books = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                books.append(Book.from_dict(data))
    return books
