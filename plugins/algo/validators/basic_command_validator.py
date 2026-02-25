"""
기본 명령어 검증 플러그인 (20점)

subprocess.run + stdin pipe로 학습자의 cli.py REPL을 실행하여
INIT/COMMIT/BRANCH/SWITCH 기본 동작을 검증.
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.algo.validators._helpers import generate_hash, parse_responses


class BasicCommandValidator(BaseValidator):
    """기본 명령어 동작 검증 (INIT/COMMIT/BRANCH/SWITCH)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.cli_path: Optional[str] = None
        self._responses: Optional[List[str]] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        cli_file = os.path.join(self.submission_dir, "cli.py")
        if os.path.isfile(cli_file):
            self.cli_path = cli_file

        # 테스트 시나리오 실행
        commands = (
            'INIT Alice\n'
            'COMMIT "Initial commit"\n'
            'COMMIT "Add feature"\n'
            'BRANCH dev\n'
            'SWITCH dev\n'
            'COMMIT "Dev work"\n'
            'SWITCH main\n'
            'exit\n'
        )
        self._responses = self._run_repl(commands)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="cli_runnable",
            description="cli.py 실행 + mini-git> 프롬프트 출력 확인",
            points=3,
            validator=self._check_runnable,
            hint="cli.py에서 'mini-git> ' 프롬프트를 출력하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="init_command",
            description="INIT 명령어 정상 동작 (저장소 초기화 + 사용자 설정)",
            points=5,
            validator=self._check_init,
            hint="INIT Alice → 'Initialized repository.' + 'Current user: Alice'",
        ))

        self.checklist.add_item(CheckItem(
            id="commit_basic",
            description="COMMIT 후 [branch hash] message 형식 출력 확인",
            points=6,
            validator=self._check_commit,
            hint="COMMIT 출력은 '[<branch> <hash>] <message>' 형식",
        ))

        self.checklist.add_item(CheckItem(
            id="branch_switch",
            description="BRANCH/SWITCH 정상 동작 확인",
            points=6,
            validator=self._check_branch_switch,
            hint="BRANCH → 'Created branch: <name>', SWITCH → 'Switched to branch: <name>'",
        ))

    def teardown(self) -> None:
        pass

    # -- REPL 실행 헬퍼 --

    def _run_repl(self, commands: str, timeout: int = 10) -> Optional[List[str]]:
        """cli.py REPL을 실행하고 응답 리스트를 반환"""
        if not self.cli_path:
            return None
        try:
            result = subprocess.run(
                [sys.executable, self.cli_path],
                input=commands,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.submission_dir,
            )
            return parse_responses(result.stdout)
        except (subprocess.TimeoutExpired, OSError):
            return None

    # -- 검증 함수 --

    def _check_runnable(self) -> bool:
        """cli.py 실행 가능 + 프롬프트 출력 확인"""
        if not self.cli_path:
            return False
        try:
            result = subprocess.run(
                [sys.executable, self.cli_path],
                input="exit\n",
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.submission_dir,
            )
            return "mini-git>" in result.stdout
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _check_init(self) -> bool:
        """INIT Alice → 저장소 초기화 메시지 확인"""
        if not self._responses or len(self._responses) < 1:
            return False

        # responses[0] = INIT Alice
        init_resp = self._responses[0]
        return ("Initialized" in init_resp
                and "Alice" in init_resp)

    def _check_commit(self) -> bool:
        """COMMIT 후 [branch hash] message 형식 확인"""
        if not self._responses or len(self._responses) < 3:
            return False

        c1_hash = generate_hash("Initial commit", 1)
        c2_hash = generate_hash("Add feature", 2)

        # responses[1] = COMMIT "Initial commit" → "[main <hash>] Initial commit"
        # responses[2] = COMMIT "Add feature" → "[main <hash>] Add feature"
        resp1 = self._responses[1]
        resp2 = self._responses[2]

        return (c1_hash in resp1 and "[main" in resp1 and "Initial commit" in resp1
                and c2_hash in resp2 and "[main" in resp2 and "Add feature" in resp2)

    def _check_branch_switch(self) -> bool:
        """BRANCH dev → Created branch: dev, SWITCH dev → Switched to branch: dev"""
        if not self._responses or len(self._responses) < 7:
            return False

        c3_hash = generate_hash("Dev work", 3)

        # responses[3] = BRANCH dev → "Created branch: dev"
        # responses[4] = SWITCH dev → "Switched to branch: dev"
        # responses[5] = COMMIT "Dev work" → "[dev <hash>] Dev work"
        # responses[6] = SWITCH main → "Switched to branch: main"
        branch_resp = self._responses[3]
        switch_resp = self._responses[4]
        commit_resp = self._responses[5]
        switch_back = self._responses[6]

        return ("Created branch: dev" in branch_resp
                and "Switched to branch: dev" in switch_resp
                and "[dev" in commit_resp and c3_hash in commit_resp
                and "Switched to branch: main" in switch_back)
