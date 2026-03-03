"""
프롬프트 관리 프로그램

AI 프롬프트를 관리하는 REPL 프로그램입니다.
아래 TODO를 구현하세요.
"""

# ── 카테고리 상수 ──────────────────────────────────
CATEGORIES = ["텍스트 생성", "이미지 생성", "페르소나", "코드 생성", "기타"]


# ── 초기 데이터 ────────────────────────────────────
def get_initial_data():
    """초기 프롬프트 데이터 3개를 리스트로 반환"""
    return [
        {
            "title": "블로그 글 작성 도우미",
            "content": "당신은 10년 경력의 전문 블로거입니다. 주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요.",
            "category": "텍스트 생성",
            "favorite": True,
        },
        {
            "title": "제품 썸네일 생성",
            "content": "다음 제품의 매력적인 썸네일 이미지를 생성해주세요. 배경은 깔끔하고 제품이 돋보이도록 해주세요.",
            "category": "이미지 생성",
            "favorite": False,
        },
        {
            "title": "IT 컨설턴트 페르소나",
            "content": "당신은 15년 경력의 IT 컨설턴트입니다. 기술적인 질문에 대해 비전문가도 이해할 수 있도록 쉽게 설명해주세요.",
            "category": "페르소나",
            "favorite": False,
        },
    ]


# ── 메뉴 출력 ──────────────────────────────────────
def show_menu():
    """메뉴를 출력합니다."""
    print("\n=== 프롬프트 관리 프로그램 ===")
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록 보기")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("0. 종료")


# ── 학생 구현 영역 (TODO) ──────────────────────────


def add_prompt(prompts):
    """
    새 프롬프트를 추가합니다.

    동작:
      1. 제목 입력 (input("제목: "))
      2. 빈 제목이면 안내 메시지 출력 후 return
      3. 내용 입력 (input("내용: "))
      4. 카테고리 목록 출력 후 선택 (input("선택: "))
      5. 프롬프트를 prompts 리스트에 추가
    """
    # TODO: 구현하세요
    pass


def list_prompts(prompts):
    """
    프롬프트 목록을 출력합니다.

    출력 형식: "번호. [카테고리] 제목 ⭐" (즐겨찾기인 경우 ⭐ 표시)
    예시: "1. [텍스트 생성] 블로그 글 작성 도우미 ⭐"
    """
    # TODO: 구현하세요
    pass


def filter_by_category(prompts):
    """
    카테고리별로 프롬프트를 필터링합니다.

    동작:
      1. CATEGORIES 목록 출력
      2. 번호 선택 (input("선택: "))
      3. 해당 카테고리의 프롬프트만 출력
    """
    # TODO: 구현하세요
    pass


def search_prompts(prompts):
    """
    키워드로 프롬프트를 검색합니다.

    동작:
      1. 검색어 입력 (input("검색어: "))
      2. 제목 또는 내용에 키워드가 포함된 프롬프트 출력
    """
    # TODO: 구현하세요
    pass


def show_detail(prompts):
    """
    프롬프트 상세 정보를 출력합니다.

    동작:
      1. 번호 입력 (input("번호 입력: "))
      2. 제목, 카테고리, 내용, 즐겨찾기 여부 출력
    """
    # TODO: 구현하세요
    pass


def manage_favorite(prompts):
    """
    즐겨찾기를 토글합니다 (추가 ↔ 해제).

    동작:
      1. 번호 입력 (input("번호 입력: "))
      2. 현재 즐겨찾기 상태를 반전 (True → False, False → True)
    """
    # TODO: 구현하세요
    pass


def show_favorites(prompts):
    """
    즐겨찾기 프롬프트만 출력합니다.

    동작: favorite가 True인 프롬프트만 필터링하여 출력
    """
    # TODO: 구현하세요
    pass


# ── 메인 루프 ──────────────────────────────────────
def main():
    prompts = get_initial_data()

    while True:
        show_menu()
        choice = input("선택: ").strip()

        if choice == "1":
            add_prompt(prompts)
        elif choice == "2":
            list_prompts(prompts)
        elif choice == "3":
            filter_by_category(prompts)
        elif choice == "4":
            search_prompts(prompts)
        elif choice == "5":
            show_detail(prompts)
        elif choice == "6":
            manage_favorite(prompts)
        elif choice == "7":
            show_favorites(prompts)
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")


if __name__ == "__main__":
    main()
