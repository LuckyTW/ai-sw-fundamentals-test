"""
프롬프트 관리 프로그램 CLI 검증 플러그인 (45점)

subprocess.run + stdin pipe로 학습자의 prompt_manager.py REPL을 실행하여
메뉴 출력, 프롬프트 추가/목록/검색 등 기본 기능을 검증.

AI 트랩: search_content (내용 검색 미포함), add_validation (빈 제목 검증 미구현)
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem


class PMCLIValidator(BaseValidator):
    """프롬프트 관리 CLI 기본 기능 검증"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.script_path: Optional[str] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        script_file = os.path.join(self.submission_dir, "prompt_manager.py")
        if os.path.isfile(script_file):
            self.script_path = script_file

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="menu_display",
            description="메뉴 출력 + '0' 종료 동작",
            points=5,
            validator=self._check_menu_display,
            hint="프로그램 실행 시 메뉴를 출력하고, '0' 입력으로 종료되어야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="add_prompt",
            description="프롬프트 추가 후 목록 반영",
            points=8,
            validator=self._check_add_prompt,
            hint="프롬프트를 추가한 후 목록에서 확인 가능해야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="list_prompts",
            description="초기 3개 프롬프트 목록 출력",
            points=7,
            validator=self._check_list_prompts,
            hint="프로그램 시작 시 3개의 초기 프롬프트가 목록에 표시되어야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="category_filter",
            description="카테고리별 조회 동작",
            points=7,
            validator=self._check_category_filter,
            hint="카테고리를 선택하면 해당 카테고리의 프롬프트만 출력되어야 합니다",
        ))

        self.checklist.add_item(CheckItem(
            id="search_title",
            description="제목 키워드 검색",
            points=8,
            validator=self._check_search_title,
            hint="키워드로 검색하면 제목에 해당 키워드가 포함된 프롬프트를 출력하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="search_content",
            description="내용 필드도 검색 대상에 포함",
            points=5,
            validator=self._check_search_content,
            hint="검색 시 제목뿐 아니라 내용(content)에서도 키워드를 찾아야 합니다",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="add_validation",
            description="빈 제목 입력 시 추가 거부",
            points=5,
            validator=self._check_add_validation,
            hint="빈 제목을 입력하면 프롬프트를 추가하지 않고 안내 메시지를 출력하세요",
            ai_trap=True,
        ))

    def teardown(self) -> None:
        pass

    # -- subprocess 실행 헬퍼 --

    def _run_session(self, stdin_text: str, timeout: int = 5) -> Optional[str]:
        """prompt_manager.py를 subprocess로 실행하고 stdout 반환"""
        if not self.script_path:
            return None
        try:
            result = subprocess.run(
                [sys.executable, self.script_path],
                input=stdin_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.submission_dir,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, OSError):
            return None

    # -- 검증 함수 --

    def _check_menu_display(self) -> bool:
        """메뉴에 핵심 키워드가 있고 '0'으로 종료되는지"""
        output = self._run_session("0\n")
        if not output:
            return False

        keywords = ["추가", "목록", "검색", "즐겨찾기", "종료"]
        found = sum(1 for kw in keywords if kw in output)
        return found >= 4

    def _check_add_prompt(self) -> bool:
        """프롬프트 추가 후 목록에서 확인 가능한지"""
        # 메뉴1(추가): 제목=테스트 프롬프트, 내용=테스트 내용, 카테고리=1번
        # 메뉴2(목록): 추가된 항목 확인
        stdin = "1\n테스트 프롬프트\n테스트 내용입니다\n1\n2\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "테스트 프롬프트" in output

    def _check_list_prompts(self) -> bool:
        """초기 3개 프롬프트가 모두 목록에 표시되는지"""
        stdin = "2\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        initial_titles = [
            "블로그 글 작성 도우미",
            "제품 썸네일 생성",
            "IT 컨설턴트 페르소나",
        ]
        return all(title in output for title in initial_titles)

    def _check_category_filter(self) -> bool:
        """카테고리 '텍스트 생성'(1번) 선택 → '블로그 글 작성 도우미' 존재"""
        stdin = "3\n1\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "블로그 글 작성 도우미" in output

    def _check_search_title(self) -> bool:
        """'블로그' 검색 → '블로그 글 작성 도우미' 존재"""
        stdin = "4\n블로그\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "블로그 글 작성 도우미" in output

    def _check_search_content(self) -> bool:
        """AI 트랩: 'SEO' 검색 → '블로그 글 작성 도우미' 존재 (content에만 SEO 포함)"""
        stdin = "4\nSEO\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "블로그 글 작성 도우미" in output

    def _check_add_validation(self) -> bool:
        """AI 트랩: 빈 제목 → 추가 거부 (목록에 4번째 항목이 없어야 함)

        정상 구현: 메뉴1→빈 제목(return)→메뉴2(목록: 3개)→종료. extra 입력 미소비.
        트랩 구현: 메뉴1→빈 제목→내용("2")→카테고리("0")→메뉴2(목록: 4개!)→종료.
        """
        stdin = "1\n\n2\n0\n2\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        # 4번째 프롬프트가 없어야 함 (초기 3개만 유지)
        # "4." 뒤에 "[" 패턴이 있으면 4번째 항목이 존재
        lines = output.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("4.") and "[" in stripped:
                return False

        return True
