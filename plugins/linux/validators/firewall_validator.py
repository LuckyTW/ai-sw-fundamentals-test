"""
방화벽 설정 검증 플러그인
"""
import subprocess
from core.base_validator import BaseValidator
from core.check_item import CheckItem


class FirewallValidator(BaseValidator):
    """
    UFW 방화벽 설정 검증
    - UFW 활성화
    - 필수 포트 허용 (20022, 80, 443)
    """

    def setup(self) -> None:
        """초기화"""
        pass

    def build_checklist(self) -> None:
        """방화벽 관련 체크 항목 구성"""

        # 체크 1: UFW 활성화
        self.checklist.add_item(CheckItem(
            id="ufw_enabled",
            description="UFW 방화벽이 활성화되어 있는지 확인",
            points=5,
            validator=self._check_ufw_enabled,
            hint="sudo ufw enable 명령으로 활성화하세요"
        ))

        # 체크 2-4: 필수 포트 허용
        ports = [
            (20022, "SSH 포트(20022)가 허용되어 있는지 확인", "sudo ufw allow 20022/tcp"),
            (80, "HTTP 포트(80)가 허용되어 있는지 확인", "sudo ufw allow 80/tcp"),
            (443, "HTTPS 포트(443)가 허용되어 있는지 확인", "sudo ufw allow 443/tcp")
        ]

        for port, description, hint in ports:
            self.checklist.add_item(CheckItem(
                id=f"ufw_port_{port}",
                description=description,
                points=5,
                validator=lambda p=port: self._check_port_allowed(p),
                hint=hint
            ))

    def teardown(self) -> None:
        """정리 작업 (없음)"""
        pass

    def _check_ufw_enabled(self) -> bool:
        """UFW 활성화 확인"""
        try:
            result = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "Status: active" in result.stdout
        except Exception:
            return False

    def _check_port_allowed(self, port: int) -> bool:
        """특정 포트가 UFW에서 허용되는지 확인"""
        try:
            result = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # 포트 번호가 출력에 포함되어 있는지 확인
            return str(port) in result.stdout
        except Exception:
            return False
