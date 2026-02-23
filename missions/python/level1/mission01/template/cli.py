"""
도서 관리 시스템 - CLI 인터페이스

TODO: 아래 요구사항에 맞게 CLI를 구현하세요.

요구사항:
1. argparse를 사용하여 서브커맨드를 구현하세요
2. 서브커맨드:
   - add: 도서 추가 (--isbn, --title, --author, --price 옵션)
   - list: 전체 도서 목록 출력
   - search: 키워드로 도서 검색 (--keyword 옵션)
3. --help 옵션이 동작해야 합니다
4. 잘못된 입력에 Traceback이 출력되지 않도록 처리하세요
"""
import argparse
import sys


def main() -> None:
    """메인 CLI 진입점"""
    # TODO: argparse로 서브커맨드를 구성하세요
    # parser = argparse.ArgumentParser(description="도서 관리 시스템")
    # subparsers = parser.add_subparsers(dest="command")
    # ...
    pass


if __name__ == "__main__":
    main()
