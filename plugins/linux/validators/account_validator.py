"""
계정 관리 검증 플러그인
"""
import subprocess
from core.base_validator import BaseValidator
from core.check_item import CheckItem


class AccountValidator(BaseValidator):
    """
    사용자 계정 및 그룹 검증
    - agent-admin 계정 존재
    - agent-dev 계정 존재
    - agent-common 그룹 소속
    """

    def setup(self) -> None:
        """초기화"""
        pass

    def build_checklist(self) -> None:
        """계정 관련 체크 항목 구성"""

        # 체크 1: agent-admin 계정 존재
        self.checklist.add_item(CheckItem(
            id="user_agent_admin_exists",
            description="agent-admin 계정이 존재하는지 확인",
            points=7,
            validator=lambda: self._check_user_exists("agent-admin"),
            hint="sudo useradd -m -s /bin/bash agent-admin"
        ))

        # 체크 2: agent-dev 계정 존재
        self.checklist.add_item(CheckItem(
            id="user_agent_dev_exists",
            description="agent-dev 계정이 존재하는지 확인",
            points=7,
            validator=lambda: self._check_user_exists("agent-dev"),
            hint="sudo useradd -m -s /bin/bash agent-dev"
        ))

        # 체크 3: agent-admin이 agent-common 그룹에 속함
        self.checklist.add_item(CheckItem(
            id="user_admin_in_common_group",
            description="agent-admin이 agent-common 그룹에 속해 있는지 확인",
            points=3,
            validator=lambda: self._check_user_in_group("agent-admin", "agent-common"),
            hint="sudo usermod -aG agent-common agent-admin"
        ))

        # 체크 4: agent-dev가 agent-common 그룹에 속함
        self.checklist.add_item(CheckItem(
            id="user_dev_in_common_group",
            description="agent-dev가 agent-common 그룹에 속해 있는지 확인",
            points=3,
            validator=lambda: self._check_user_in_group("agent-dev", "agent-common"),
            hint="sudo usermod -aG agent-common agent-dev"
        ))

    def teardown(self) -> None:
        """정리 작업 (없음)"""
        pass

    def _check_user_exists(self, username: str) -> bool:
        """사용자 계정 존재 확인"""
        try:
            result = subprocess.run(
                ["id", username],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and username in result.stdout
        except Exception:
            return False

    def _check_user_in_group(self, username: str, groupname: str) -> bool:
        """사용자가 특정 그룹에 속하는지 확인"""
        try:
            result = subprocess.run(
                ["groups", username],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and groupname in result.stdout
        except Exception:
            return False
