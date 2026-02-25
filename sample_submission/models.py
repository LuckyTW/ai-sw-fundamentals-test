from dataclasses import dataclass, asdict


@dataclass
class Book:
    """도서 데이터 모델"""
    isbn: str
    title: str
    author: str
    price: int
    is_available: bool = True

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError(f"가격은 0 이상이어야 합니다: {self.price}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(**data)
