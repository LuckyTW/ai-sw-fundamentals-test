"""
CLI 동작 검증 플러그인 (30점)

학습자의 도서 관리 cli.py가 올바르게 동작하는지 subprocess로 검증.
cli.py 존재 → --help → add → list → 크래시 안전성 순서로 체크.

AI 트랩: --help 옵션 누락
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem


class CLIValidator(BaseValidator):
    """CLI 서브커맨드 동작 검증 (cli.py, --help, add, list, 크래시 방지)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.cli_path: Optional[str] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        cli_file = os.path.join(self.submission_dir, "cli.py")
        if os.path.isfile(cli_file):
            self.cli_path = cli_file

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="cli_runnable",
            description="cli.py 파일이 존재하고 실행 가능한지 확인",
            points=5,
            validator=self._check_runnable,
            hint="cli.py 파일을 제출 디렉토리에 포함하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="cli_help",
            description="--help 옵션이 정상 동작하는지 확인",
            points=5,
            validator=self._check_help,
            hint="argparse를 사용하여 --help 옵션을 지원하세요",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="cli_add",
            description="add 서브커맨드로 도서 추가가 동작하는지 확인",
            points=8,
            validator=self._check_add,
            hint="add 서브커맨드에 --isbn, --title, --author, --price 옵션을 구현하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="cli_list",
            description="list 서브커맨드로 도서 목록 조회가 동작하는지 확인",
            points=7,
            validator=self._check_list,
            hint="list 서브커맨드를 구현하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="cli_no_crash",
            description="잘못된 입력에 Traceback이 출력되지 않는지 확인",
            points=5,
            validator=self._check_no_crash,
            hint="예외 처리로 잘못된 입력에도 Traceback 없이 안내 메시지를 출력하세요",
        ))

    def teardown(self) -> None:
        pass

    # -- subprocess 실행 헬퍼 --

    def _run(self, args: list, timeout: int = 10) -> Optional[subprocess.CompletedProcess]:
        """학생 cli.py를 subprocess로 실행"""
        if not self.cli_path:
            return None
        try:
            return subprocess.run(
                [sys.executable, self.cli_path] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.submission_dir,
            )
        except (subprocess.TimeoutExpired, OSError):
            return None

    # -- 검증 함수 --

    def _check_runnable(self) -> bool:
        """cli.py 파일 존재 확인"""
        return self.cli_path is not None

    def _check_help(self) -> bool:
        """
        AI 트랩: AI가 --help를 구현하지 않거나 argparse 없이 구현할 수 있음.
        --help → returncode 0 + stdout 길이 > 10
        """
        result = self._run(["--help"])
        if result and result.returncode == 0 and len(result.stdout.strip()) > 10:
            return True
        # -h 도 시도
        result = self._run(["-h"])
        if result and result.returncode == 0 and len(result.stdout.strip()) > 10:
            return True
        return False

    def _check_add(self) -> bool:
        """
        add 서브커맨드 동작 확인.
        returncode 0 + (stdout에 출력이 있거나 데이터 파일이 생성됨)
        """
        # add 전 데이터 파일 목록 스냅샷
        before_files = set(self._find_data_files())

        result = self._run([
            "add",
            "--isbn", "978-89-0000-000-0",
            "--title", "테스트 도서",
            "--author", "테스터",
            "--price", "10000",
        ])
        if result is None or result.returncode != 0:
            return False

        # 출력이 있거나 데이터 파일이 새로 생겼으면 동작한 것으로 판단
        after_files = set(self._find_data_files())
        has_output = len(result.stdout.strip()) > 0
        has_new_file = len(after_files - before_files) > 0
        has_file_changed = self._any_file_changed(before_files, after_files)

        return has_output or has_new_file or has_file_changed

    def _check_list(self) -> bool:
        """
        list 서브커맨드 동작 확인.
        먼저 add로 데이터를 넣고, list로 조회하여 stdout에 출력이 있는지 확인.
        """
        # 먼저 add로 데이터 넣기
        self._run([
            "add",
            "--isbn", "978-89-9999-999-9",
            "--title", "목록확인용",
            "--author", "테스터",
            "--price", "5000",
        ])

        result = self._run(["list"])
        if result is None or result.returncode != 0:
            return False

        # list 결과에 내용이 있어야 함
        return len(result.stdout.strip()) > 0

    def _find_data_files(self) -> list:
        """submission_dir 내 데이터 파일 목록"""
        import glob
        patterns = ["*.jsonl", "*.json", "*.csv"]
        found = []
        for pattern in patterns:
            found.extend(glob.glob(os.path.join(self.submission_dir, pattern)))
        return found

    @staticmethod
    def _any_file_changed(before: set, after: set) -> bool:
        """기존 파일 중 크기가 변한 것이 있는지"""
        for f in before & after:
            try:
                if os.path.getsize(f) > 0:
                    return True
            except OSError:
                continue
        return False

    def _check_no_crash(self) -> bool:
        """잘못된 입력에 Traceback이 출력되지 않는지 확인"""
        result = self._run(["invalid_command_xyz"])
        if result is None:
            # cli.py 자체가 없으면 별도 감점 (cli_runnable에서 처리)
            return self.cli_path is None
        return "Traceback" not in result.stderr
