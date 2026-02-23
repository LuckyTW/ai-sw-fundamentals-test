"""
스크립트 검증 플러그인
"""
import os
from core.base_validator import BaseValidator
from core.check_item import CheckItem


class ScriptValidator(BaseValidator):
    """
    monitor.sh 스크립트 검증
    - 파일 존재
    - 실행 권한 (755)
    """

    def setup(self) -> None:
        """초기화"""
        self.script_path = "/opt/monitor.sh"

    def build_checklist(self) -> None:
        """스크립트 관련 체크 항목 구성"""

        # 체크 1: monitor.sh 파일 존재
        self.checklist.add_item(CheckItem(
            id="script_exists",
            description="/opt/monitor.sh 스크립트가 존재하는지 확인",
            points=15,
            validator=self._check_script_exists,
            hint="스크립트를 /opt 디렉토리에 생성하세요"
        ))

        # 체크 2: 실행 권한 확인 (755)
        self.checklist.add_item(CheckItem(
            id="script_executable",
            description="monitor.sh가 실행 권한(755)을 가지는지 확인",
            points=15,
            validator=self._check_script_executable,
            hint="sudo chmod 755 /opt/monitor.sh",
            ai_trap=True  # AI가 644로 설정하는 실수 방지
        ))

    def teardown(self) -> None:
        """정리 작업 (없음)"""
        pass

    def _check_script_exists(self) -> bool:
        """스크립트 파일 존재 확인"""
        try:
            return os.path.exists(self.script_path)
        except Exception:
            return False

    def _check_script_executable(self) -> bool:
        """스크립트 실행 권한 확인 (755)"""
        try:
            if not os.path.exists(self.script_path):
                return False

            # 파일 권한 확인
            stat_info = os.stat(self.script_path)
            mode = stat_info.st_mode

            # 755 권한 확인 (rwxr-xr-x)
            # Owner: read(4) + write(2) + execute(1) = 7
            # Group: read(4) + execute(1) = 5
            # Others: read(4) + execute(1) = 5
            permissions = oct(mode)[-3:]
            return permissions == "755"
        except Exception:
            return False
