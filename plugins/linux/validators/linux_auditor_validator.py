"""
리눅스 서버 보안 감사 도구 검증 플러그인 (100점)

학습자가 6개의 리눅스 설정 파일 스냅샷을 분석하여
보안 취약점을 탐지하는 감사 리포트를 생성하는지 검증.

AI 트랩: PermitRootLogin prohibit-password 오판, Telnet 포트 미탐지,
         RBAC 위반 미탐지, api_keys 권한 위반 미탐지
"""
import os
import re
import subprocess
import sys
import tempfile
from typing import Dict, Any, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem

# ── 트랩 입력 파일 6개 (모듈 레벨 상수) ──

TRAP_SSHD_CONFIG = """\
Port 20022
PermitRootLogin prohibit-password
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers agent-admin agent-dev
"""

TRAP_UFW_STATUS = """\
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW IN    Anywhere
15034/tcp                  ALLOW IN    Anywhere
23/tcp                     ALLOW IN    Anywhere
20022/tcp (v6)             ALLOW IN    Anywhere (v6)
15034/tcp (v6)             ALLOW IN    Anywhere (v6)
23/tcp (v6)                ALLOW IN    Anywhere (v6)
"""

TRAP_ACCOUNTS_CSV = """\
username,uid,groups,home,shell
agent-admin,1001,agent-common;agent-core,/home/agent-admin,/bin/bash
agent-dev,1002,agent-common;agent-core,/home/agent-dev,/bin/bash
agent-test,1003,agent-common;agent-core,/home/agent-test,/bin/bash
"""

TRAP_DIRECTORIES_CSV = """\
path,owner,group,octal_permission
/home/agent-admin/agent-app,agent-admin,agent-admin,755
/home/agent-admin/agent-app/upload_files,agent-admin,agent-common,775
/home/agent-admin/agent-app/api_keys,agent-admin,agent-common,775
/var/log/agent-app,agent-admin,agent-core,770
/home/agent-admin/agent-app/bin,agent-admin,agent-admin,755
"""

TRAP_MONITOR_LOG = """\
[2025-12-24 09:56:01] PID:48291 CPU:24.8% MEM:5.1% DISK:45G
[2025-12-24 09:57:01] PID:48291 CPU:25.0% MEM:5.1% DISK:45G
[INVALID] This line has bad format
[2025-12-24 09:58:01] PID:48291 CPU:25.2% MEM:5.2% DISK:45G
[2025-12-24 09:59:01] PID:48291 CPU:25.1% MEM:5.2% DISK:45G
[2025-12-24 10:00:01] PID:48291 CPU:25.3% MEM:5.2% DISK:45G
[2025-12-24 10:01:01] PID:48291 CPU:92.5% MEM:85.3% DISK:12G
"""

TRAP_CRONTAB = """\
* * * * * /home/agent-admin/agent-app/bin/monitor.sh >> /var/log/agent-app/monitor.log 2>&1
0 2 * * 0 /home/agent-admin/agent-app/bin/backup.sh
0 0 * * * find /var/log/agent-app/archive -name "*.gz" -mtime +30 -delete
"""

# ── 기대 정답값 ──
# CPU: (24.8 + 25.0 + 25.2 + 25.1 + 25.3 + 92.5) / 6 = 217.9 / 6 ≈ 36.32
EXPECTED_CPU_AVG = 36.32
CPU_TOLERANCE = 0.5  # ±0.5 허용


class LinuxAuditorValidator(BaseValidator):
    """리눅스 서버 보안 감사 도구 검증 (설정 파일 파싱 + 취약점 탐지)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.report_content: Optional[str] = None
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")

        # 학생 제출 파일 확인
        script_path = os.path.join(self.submission_dir, "auditor.py")
        if not os.path.isfile(script_path):
            return

        # 임시 디렉토리 생성 및 트랩 파일 쓰기
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = self._tmpdir.name

        self._write_trap_files(tmp_path)

        report_path = os.path.join(tmp_path, "report.txt")

        # subprocess로 학생 코드 실행
        try:
            subprocess.run(
                [sys.executable, script_path,
                 "--config-dir", tmp_path,
                 "--output", report_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.submission_dir,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

        # report.txt 읽기
        if os.path.isfile(report_path):
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    self.report_content = f.read()
            except (OSError, UnicodeDecodeError):
                pass

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="config_parse",
            description="설정 파일 파싱 + report.txt 생성 확인",
            points=10,
            validator=self._check_config_parse,
            hint="argparse로 --config-dir, --output 인자를 받아 6개 파일을 파싱하고 report.txt를 생성하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="ssh_audit",
            description="SSH 보안 감사: PermitRootLogin 취약점 탐지",
            points=15,
            validator=self._check_ssh_audit,
            hint="PermitRootLogin의 각 설정값(no, prohibit-password, yes)의 보안 의미를 정확히 이해하세요",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="firewall_audit",
            description="방화벽 감사: 위험 포트(23/tcp Telnet) 탐지",
            points=15,
            validator=self._check_firewall_audit,
            hint="well-known 위험 포트(Telnet 등)가 허용되어 있는지 확인하세요",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="account_audit",
            description="계정 감사: agent-test의 agent-core 그룹 RBAC 위반 탐지",
            points=15,
            validator=self._check_account_audit,
            hint="테스트 계정이 핵심 운영 그룹에 포함되어 있으면 최소 권한 원칙 위반입니다",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="permission_audit",
            description="권한 감사: api_keys 디렉토리 775+agent-common 탐지",
            points=15,
            validator=self._check_permission_audit,
            hint="민감 데이터 디렉토리에 광범위 그룹 쓰기 권한이 있으면 보안 위험입니다",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="log_stats",
            description="모니터링 로그 통계: CPU 평균값 정확성",
            points=15,
            validator=self._check_log_stats,
            hint="잘못된 형식의 로그 줄은 건너뛰고 유효한 줄만으로 통계를 계산하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="report_sections",
            description="리포트 5개 섹션(SSH, 방화벽, 계정, 권한, 로그) 포함 확인",
            points=15,
            validator=self._check_report_sections,
            hint="리포트에 SSH, 방화벽, 계정, 권한, 로그 관련 섹션을 모두 포함하세요",
        ))

    def teardown(self) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()

    # -- 헬퍼 --

    @staticmethod
    def _write_trap_files(tmp_path: str) -> None:
        """트랩 포함 설정 파일 6개 쓰기"""
        files = {
            "sshd_config": TRAP_SSHD_CONFIG,
            "ufw_status.txt": TRAP_UFW_STATUS,
            "accounts.csv": TRAP_ACCOUNTS_CSV,
            "directories.csv": TRAP_DIRECTORIES_CSV,
            "monitor.log": TRAP_MONITOR_LOG,
            "crontab.txt": TRAP_CRONTAB,
        }
        for filename, content in files.items():
            filepath = os.path.join(tmp_path, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

    # -- 검증 함수 --

    def _check_config_parse(self) -> bool:
        """report.txt가 생성되었고 내용이 있는지 확인"""
        return self.report_content is not None and len(self.report_content.strip()) > 0

    def _check_ssh_audit(self) -> bool:
        """SSH 감사: PermitRootLogin 관련 라인에서 취약점 판정 확인 (라인 기반)

        AI 트랩: AI가 prohibit-password를 'Safe'로 판정.
        라인 기반 매칭으로 PermitRootLogin 라인에 취약 키워드가 있는지 확인.
        """
        if not self.report_content:
            return False

        topic_keywords = ["permitrootlogin", "prohibit-password", "root login", "루트 로그인"]
        vuln_keywords = ["취약", "위험", "vulnerable", "unsafe", "warning", "주의", "경고"]

        for line in self.report_content.split("\n"):
            line_lower = line.lower()
            if any(kw in line_lower for kw in topic_keywords):
                if any(kw in line_lower for kw in vuln_keywords):
                    return True
        return False

    def _check_firewall_audit(self) -> bool:
        """방화벽 감사: 23/tcp 라인에서 위험 판정 확인 (라인 기반)

        AI 트랩: AI가 23/tcp(Telnet)를 일반 포트로 취급.
        라인 기반 매칭으로 23번 포트 라인에 취약 키워드가 있는지 확인.
        """
        if not self.report_content:
            return False

        vuln_keywords = ["취약", "위험", "차단", "block", "deny", "vulnerable",
                         "unsafe", "warning", "주의", "경고", "close"]

        for line in self.report_content.split("\n"):
            line_lower = line.lower()
            if "23" in line_lower and ("tcp" in line_lower or "telnet" in line_lower):
                if any(kw in line_lower for kw in vuln_keywords):
                    return True
        return False

    def _check_account_audit(self) -> bool:
        """계정 감사: agent-test 라인에서 RBAC 위반 판정 확인 (라인 기반)

        AI 트랩: AI가 agent-test의 agent-core 그룹 포함을 정상으로 판정.
        라인 기반 매칭으로 agent-test 라인에 위반 키워드가 있는지 확인.
        """
        if not self.report_content:
            return False

        vuln_keywords = ["위반", "취약", "violation", "vulnerable", "unauthorized",
                         "unnecessary", "불필요", "위험", "warning", "주의", "경고",
                         "제거", "remove"]

        for line in self.report_content.split("\n"):
            line_lower = line.lower()
            if "agent-test" in line_lower:
                if any(kw in line_lower for kw in vuln_keywords):
                    return True
        return False

    def _check_permission_audit(self) -> bool:
        """권한 감사: api_keys 라인에서 권한 위반 판정 확인 (라인 기반)

        AI 트랩: AI가 api_keys 775 권한을 일반적으로 판정.
        라인 기반 매칭으로 api_keys 라인에 취약 키워드가 있는지 확인.
        """
        if not self.report_content:
            return False

        vuln_keywords = ["취약", "위험", "vulnerable", "unsafe", "warning",
                         "주의", "경고", "과도", "excessive"]

        for line in self.report_content.split("\n"):
            line_lower = line.lower()
            if "api_keys" in line_lower or "api-keys" in line_lower:
                if any(kw in line_lower for kw in vuln_keywords):
                    return True
        return False

    def _check_log_stats(self) -> bool:
        """로그 통계: CPU 평균값이 36.32% (±0.5) 범위 내인지 확인"""
        if not self.report_content:
            return False

        report = self.report_content

        # CPU 평균 관련 섹션에서 숫자 추출
        # "cpu" 또는 "CPU" 근처의 숫자를 찾음
        cpu_section = ""
        lines = report.split("\n")
        for i, line in enumerate(lines):
            if "cpu" in line.lower() and ("평균" in line.lower() or "avg" in line.lower()
                                          or "average" in line.lower() or "mean" in line.lower()):
                cpu_section = line
                break

        if not cpu_section:
            # CPU 평균 줄을 찾지 못하면 전체에서 탐색
            cpu_section = report

        # 숫자 추출하여 기대값 범위 확인
        numbers = re.findall(r"\d+\.\d+", cpu_section)
        for num_str in numbers:
            num = float(num_str)
            if abs(num - EXPECTED_CPU_AVG) <= CPU_TOLERANCE:
                return True

        return False

    def _check_report_sections(self) -> bool:
        """리포트 5개 섹션 존재 확인 (4개 이상이면 통과)"""
        if not self.report_content:
            return False

        report = self.report_content.lower()

        section_checks = [
            "ssh" in report,
            any(kw in report for kw in ["방화벽", "firewall", "ufw"]),
            any(kw in report for kw in ["계정", "account", "user"]),
            any(kw in report for kw in ["권한", "permission", "directory"]),
            any(kw in report for kw in ["로그", "log", "monitor"]),
        ]

        return sum(section_checks) >= 4
