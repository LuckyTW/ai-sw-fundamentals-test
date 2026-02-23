"""
SSH 설정 검증 플러그인
"""
import re
from core.base_validator import BaseValidator
from core.check_item import CheckItem


class SSHValidator(BaseValidator):
    """
    SSH 보안 설정 검증
    - 포트 변경 (20022)
    - Root 로그인 차단
    """

    def setup(self) -> None:
        """초기화 (필요 시 sshd_config 파일 경로 확인)"""
        self.sshd_config_path = "/etc/ssh/sshd_config"

    def build_checklist(self) -> None:
        """SSH 관련 체크 항목 구성"""

        # 체크 1: SSH 포트가 20022로 설정되어 있는지
        self.checklist.add_item(CheckItem(
            id="ssh_port_20022",
            description="SSH 포트가 20022로 설정되어 있는지 확인",
            points=15,
            validator=self._check_ssh_port,
            hint="sshd_config에서 'Port 20022' 설정을 확인하세요",
            ai_trap=False
        ))

        # 체크 2: Root 로그인이 차단되어 있는지
        self.checklist.add_item(CheckItem(
            id="ssh_root_login_no",
            description="PermitRootLogin이 no로 설정되어 있는지 확인",
            points=15,
            validator=self._check_root_login_disabled,
            hint="PermitRootLogin no 설정을 확인하세요 (prohibit-password는 불합격)",
            ai_trap=True  # AI가 'prohibit-password'로 설정할 수 있음
        ))

    def teardown(self) -> None:
        """정리 작업 (없음)"""
        pass

    def _check_ssh_port(self) -> bool:
        """SSH 포트 20022 설정 확인"""
        try:
            with open(self.sshd_config_path, 'r') as f:
                content = f.read()

            # 주석 제거 후 Port 설정 찾기
            match = re.search(r'^\s*Port\s+(\d+)', content, re.MULTILINE)
            if match:
                return match.group(1) == "20022"
            return False
        except Exception:
            return False

    def _check_root_login_disabled(self) -> bool:
        """Root 로그인 차단 확인"""
        try:
            with open(self.sshd_config_path, 'r') as f:
                content = f.read()

            # AI 함정: 'prohibit-password'가 아닌 'no'여야 함
            match = re.search(r'^\s*PermitRootLogin\s+(\S+)', content, re.MULTILINE)
            if match:
                return match.group(1).lower() == "no"
            return False
        except Exception:
            return False
