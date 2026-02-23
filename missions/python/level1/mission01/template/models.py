"""
도서 관리 시스템 - 데이터 모델

TODO: 아래 요구사항에 맞게 Book 클래스를 구현하세요.

요구사항:
1. @dataclass 데코레이터를 사용하여 Book 클래스를 정의하세요.
2. 필수 필드: isbn(str), title(str), author(str), price(int)
3. 선택 필드: is_available(bool) - 기본값 True
4. 모든 필드에 타입 힌트를 적용하세요.
5. __post_init__에서 price < 0이면 ValueError를 발생시키세요.
6. to_dict() 메서드: Book 인스턴스를 딕셔너리로 변환
7. from_dict(data) 클래스 메서드: 딕셔너리에서 Book 인스턴스 생성
"""
from dataclasses import dataclass


# TODO: Book 데이터클래스를 구현하세요
