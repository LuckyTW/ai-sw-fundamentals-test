## 문항 3 정답지

### 정답 코드

```python
"""
프롬프트 관리 프로그램 — 모범 답안
"""

CATEGORIES = ["텍스트 생성", "이미지 생성", "페르소나", "코드 생성", "기타"]


def get_initial_data():
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


def show_menu():
    print("\n=== 프롬프트 관리 프로그램 ===")
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록 보기")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("0. 종료")


def add_prompt(prompts):
    title = input("제목: ").strip()
    if not title:
        print("제목은 비어있을 수 없습니다.")
        return

    content = input("내용: ").strip()

    print("\n카테고리 선택:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")

    try:
        cat_choice = int(input("선택: ").strip())
        if 1 <= cat_choice <= len(CATEGORIES):
            category = CATEGORIES[cat_choice - 1]
        else:
            category = "기타"
    except ValueError:
        category = "기타"

    prompts.append({
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
    })
    print(f"'{title}' 프롬프트가 추가되었습니다.")


def list_prompts(prompts):
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    for i, p in enumerate(prompts, 1):
        star = " ⭐" if p["favorite"] else ""
        print(f"{i}. [{p['category']}] {p['title']}{star}")


def filter_by_category(prompts):
    print("\n카테고리 선택:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")

    try:
        cat_choice = int(input("선택: ").strip())
        if 1 <= cat_choice <= len(CATEGORIES):
            selected = CATEGORIES[cat_choice - 1]
        else:
            print("잘못된 선택입니다.")
            return
    except ValueError:
        print("잘못된 입력입니다.")
        return

    filtered = [p for p in prompts if p["category"] == selected]
    if not filtered:
        print(f"'{selected}' 카테고리에 프롬프트가 없습니다.")
        return

    print(f"\n[{selected}] 카테고리 프롬프트:")
    for i, p in enumerate(filtered, 1):
        star = " ⭐" if p["favorite"] else ""
        print(f"  {i}. {p['title']}{star}")


def search_prompts(prompts):
    keyword = input("검색어: ").strip()
    if not keyword:
        print("검색어를 입력해주세요.")
        return

    results = []
    for p in prompts:
        if keyword.lower() in p["title"].lower() or keyword.lower() in p["content"].lower():
            results.append(p)

    if not results:
        print(f"'{keyword}'에 대한 검색 결과가 없습니다.")
        return

    print(f"\n'{keyword}' 검색 결과:")
    for i, p in enumerate(results, 1):
        star = " ⭐" if p["favorite"] else ""
        print(f"  {i}. [{p['category']}] {p['title']}{star}")


def show_detail(prompts):
    try:
        num = int(input("번호 입력: ").strip())
    except ValueError:
        print("잘못된 입력입니다.")
        return

    if num < 1 or num > len(prompts):
        print("잘못된 번호입니다.")
        return

    p = prompts[num - 1]
    star = "예" if p["favorite"] else "아니오"
    print(f"\n제목: {p['title']}")
    print(f"카테고리: {p['category']}")
    print(f"내용: {p['content']}")
    print(f"즐겨찾기: {star}")


def manage_favorite(prompts):
    try:
        num = int(input("번호 입력: ").strip())
    except ValueError:
        print("잘못된 입력입니다.")
        return

    if num < 1 or num > len(prompts):
        print("잘못된 번호입니다.")
        return

    p = prompts[num - 1]
    p["favorite"] = not p["favorite"]
    if p["favorite"]:
        print(f"'{p['title']}'을(를) 즐겨찾기에 추가했습니다.")
    else:
        print(f"'{p['title']}'을(를) 즐겨찾기에서 해제했습니다.")


def show_favorites(prompts):
    favorites = [p for p in prompts if p["favorite"]]
    if not favorites:
        print("즐겨찾기한 프롬프트가 없습니다.")
        return

    print("\n즐겨찾기 목록:")
    for i, p in enumerate(favorites, 1):
        print(f"  {i}. [{p['category']}] {p['title']} ⭐")


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
```

### 정답 체크리스트

| 번호 | 체크 항목 | 배점 | AI 트랩 | 검증 방법 |
|------|----------|------|---------|----------|
| 1 | func_separation: 기능별 함수 분리 (def 5개 이상) | 8 | - | AST 자동 |
| 2 | data_structure: list + dict 데이터 구조 사용 | 7 | - | AST 자동 |
| 3 | initial_data: 초기 데이터 3개 이상 | 5 | - | AST 자동 |
| 4 | no_external_lib: 외부 라이브러리 미사용 | 5 | - | AST 자동 |
| 5 | menu_display: 메뉴 출력 + 종료 | 5 | - | subprocess 자동 |
| 6 | add_prompt: 프롬프트 추가 | 8 | - | subprocess 자동 |
| 7 | list_prompts: 초기 목록 출력 | 7 | - | subprocess 자동 |
| 8 | category_filter: 카테고리 필터링 | 7 | - | subprocess 자동 |
| 9 | search_title: 제목 키워드 검색 | 8 | - | subprocess 자동 |
| 10 | search_content: 내용 필드도 검색 | 5 | Yes | subprocess 자동 |
| 11 | add_validation: 빈 제목 추가 거부 | 5 | Yes | subprocess 자동 |
| 12 | detail_view: 상세 보기 | 8 | - | subprocess 자동 |
| 13 | favorite_toggle: 즐겨찾기 토글 | 7 | Yes | subprocess 자동 |
| 14 | favorite_list: 즐겨찾기 목록 | 7 | - | subprocess 자동 |
| 15 | invalid_input: 잘못된 입력 처리 | 3 | - | subprocess 자동 |
| 16 | exit_message: 종료 메시지 | 5 | - | subprocess 자동 |

- Pass 기준: 총 100점 중 70점 이상
- AI 트랩 합계: 17점 (모두 실패해도 83점으로 PASS 가능)

### AI 트랩 상세

1. **search_content** (5점): AI가 `keyword in prompt["title"]`만 체크하여 content 검색을 누락. 올바른 구현은 `title` **또는** `content`에서 모두 검색.

2. **add_validation** (5점): AI가 입력 검증 없이 빈 제목도 프롬프트로 등록. 올바른 구현은 빈 제목 → 안내 메시지 출력 + 추가 거부.

3. **favorite_toggle** (7점): AI가 `favorite = True`만 설정하여 즐겨찾기 해제 불가. 올바른 구현은 `not p["favorite"]`로 토글.
