"""
프롬프트 관리 프로그램 상호작용 검증 플러그인 (30점)

subprocess.run + stdin pipe로 상세 보기, 즐겨찾기 토글/목록,
잘못된 입력 처리, 종료 메시지를 검증.

AI 트랩: favorite_toggle (즐겨찾기 해제 불가 — True→False 토글 미구현)
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem


class PMInteractionValidator(BaseValidator):
    """프롬프트 관리 상호작용 기능 검증"""

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
            id="detail_view",
            description="프롬프트 상세 보기 (제목+카테고리+내용)",
            points=8,
            validator=self._check_detail_view,
            hint="번호를 입력하면 제목, 카테고리, 내용을 모두 출력하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="favorite_toggle",
            description="즐겨찾기 토글 (True → False 해제)",
            points=7,
            validator=self._check_favorite_toggle,
            hint="이미 즐겨찾기인 프롬프트를 선택하면 즐겨찾기를 해제해야 합니다 (토글)",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="favorite_list",
            description="즐겨찾기 목록 출력",
            points=7,
            validator=self._check_favorite_list,
            hint="즐겨찾기로 등록된 프롬프트만 목록에 표시하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="invalid_input",
            description="잘못된 메뉴 입력 시 크래시 없이 안내",
            points=3,
            validator=self._check_invalid_input,
            hint="존재하지 않는 메뉴 번호 입력 시 안내 메시지를 출력하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="exit_message",
            description="종료 시 안내 메시지 출력",
            points=5,
            validator=self._check_exit_message,
            hint="'0'을 입력하여 종료할 때 종료 안내 메시지를 출력하세요",
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

    def _check_detail_view(self) -> bool:
        """상세 보기: 제목 + 카테고리 + 내용(SEO) 모두 출력"""
        stdin = "5\n1\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        required = ["블로그 글 작성 도우미", "텍스트 생성", "SEO"]
        return all(kw in output for kw in required)

    def _check_favorite_toggle(self) -> bool:
        """AI 트랩: #1 토글(True→False) 후 즐겨찾기 목록에서 사라져야 함

        stdin: 메뉴6(즐겨찾기 관리) → 1번 선택 → 메뉴7(즐겨찾기 목록) → 종료
        #1은 초기 favorite=True → 토글 후 False → 목록에 없어야 함

        검증 방식: show_favorites 출력은 "제목 ⭐" 형식을 사용.
        토글이 정상 동작하면 "블로그 글 작성 도우미"와 "⭐"가 같은 줄에 나타나지 않아야 함.
        (manage_favorite 확인 메시지는 ⭐를 포함하지 않으므로 오탐 방지)
        """
        stdin = "6\n1\n7\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        # show_favorites는 "제목 ⭐" 형식으로 출력
        # 토글이 제대로 동작했으면(True→False) 블로그 글이 즐겨찾기 목록에서 사라짐
        # → "블로그 글 작성 도우미"와 "⭐"가 같은 줄에 있으면 토글 실패
        for line in output.split("\n"):
            if "블로그 글 작성 도우미" in line and "⭐" in line:
                return False

        return True

    def _check_favorite_list(self) -> bool:
        """초기 상태에서 즐겨찾기 목록에 '블로그 글 작성 도우미' 존재"""
        stdin = "7\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "블로그 글 작성 도우미" in output

    def _check_invalid_input(self) -> bool:
        """잘못된 메뉴 입력 '99' → 크래시 없이 안내 메시지"""
        stdin = "99\n0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        # 크래시 없이 정상 종료 + 안내 키워드 존재
        keywords = ["잘못", "다시", "올바", "없는", "유효"]
        return any(kw in output for kw in keywords)

    def _check_exit_message(self) -> bool:
        """'0' 입력 → '종료' 키워드 존재"""
        stdin = "0\n"
        output = self._run_session(stdin)
        if not output:
            return False

        return "종료" in output
