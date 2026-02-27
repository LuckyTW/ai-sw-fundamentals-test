"""
커밋 이력 DB 분석기 — 분석 섹션 검증 플러그인 (45점)

리포트 파일의 분석 결과를 라인 기반 매칭으로 검증.

AI 트랩: LEFT JOIN 누락(황서진/hotfix), COUNT(DISTINCT) 미사용, root commit 누락
"""
import os
import subprocess
import sys
import tempfile
from typing import Dict, Any, Optional, List

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.db.validators._data import write_csv_files, EXPECTED_MAIN_HISTORY


class AnalysisValidator(BaseValidator):
    """리포트 분석 섹션 검증 (라인 기반 매칭)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.report_lines: List[str] = []
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        script_path = os.path.join(self.submission_dir, "commit_analyzer.py")
        if not os.path.isfile(script_path):
            return

        self._tmpdir = tempfile.TemporaryDirectory()
        tmp = self._tmpdir.name
        data_dir = os.path.join(tmp, "data")
        os.makedirs(data_dir)
        write_csv_files(data_dir)

        db_path = os.path.join(tmp, "analysis.db")
        report_path = os.path.join(tmp, "report.txt")

        try:
            subprocess.run(
                [sys.executable, script_path,
                 "--data-dir", data_dir,
                 "--output", report_path,
                 "--db", db_path],
                capture_output=True, text=True, timeout=15,
                cwd=self.submission_dir,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

        if os.path.isfile(report_path):
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    self.report_lines = f.read().splitlines()
            except (OSError, UnicodeDecodeError):
                pass

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="author_commit_count",
            description="김민수 4 commits 확인",
            points=5,
            validator=self._check_author_commit_count,
            hint="작성자별 커밋 수를 정확히 집계하세요 (GROUP BY + COUNT)",
        ))
        self.checklist.add_item(CheckItem(
            id="author_left_join",
            description="황서진(0 commits) 포함 확인",
            points=8,
            validator=self._check_author_left_join,
            hint="커밋이 없는 작성자도 리포트에 포함되어야 합니다 (LEFT JOIN 사용)",
            ai_trap=True,
        ))
        self.checklist.add_item(CheckItem(
            id="branch_commit_count",
            description="main 7 commits 확인",
            points=5,
            validator=self._check_branch_commit_count,
            hint="브랜치별 커밋 수를 정확히 집계하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="branch_no_commits",
            description="hotfix/urgent 0 commits 포함",
            points=6,
            validator=self._check_branch_no_commits,
            hint="자체 커밋이 없는 브랜치도 리포트에 포함되어야 합니다 (LEFT JOIN 사용)",
            ai_trap=True,
        ))
        self.checklist.add_item(CheckItem(
            id="distinct_file_count",
            description="김민수 5 files changed 확인",
            points=6,
            validator=self._check_distinct_file_count,
            hint="같은 파일이 여러 커밋에서 변경되었을 때 고유 파일 수를 세세요 (COUNT DISTINCT)",
            ai_trap=True,
        ))
        self.checklist.add_item(CheckItem(
            id="most_changed_files",
            description="requirements.txt 최다 변경 (5 commits)",
            points=6,
            validator=self._check_most_changed_files,
            hint="파일별 변경 횟수를 커밋 수 기준으로 집계하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="self_join_parent",
            description="커밋 히스토리에 root(a1b2c3d) 포함",
            points=8,
            validator=self._check_self_join_parent,
            hint="커밋 히스토리를 parent_hash로 추적할 때 root commit(parent=NULL)도 포함해야 합니다",
            ai_trap=True,
        ))
        self.checklist.add_item(CheckItem(
            id="history_count",
            description="main 히스토리 7개 커밋 전부 포함",
            points=1,
            validator=self._check_history_count,
            hint="main 브랜치의 head에서 root까지 모든 커밋이 포함되어야 합니다",
        ))

    def teardown(self) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()

    # -- 헬퍼 --

    def _find_section_lines(self, section_header: str) -> List[str]:
        """특정 섹션 헤더 이후의 라인들을 반환 (다음 === 까지)"""
        lines = []
        in_section = False
        for line in self.report_lines:
            if section_header in line:
                in_section = True
                continue
            if in_section:
                if line.startswith("===") and section_header not in line:
                    break
                lines.append(line)
        return lines

    # -- 검증 함수 --

    def _check_author_commit_count(self) -> bool:
        for line in self.report_lines:
            if "김민수" in line and "4 commits" in line:
                return True
        return False

    def _check_author_left_join(self) -> bool:
        for line in self.report_lines:
            if "황서진" in line and "0 commits" in line:
                return True
        return False

    def _check_branch_commit_count(self) -> bool:
        for line in self.report_lines:
            if "main" in line and "7 commits" in line:
                return True
        return False

    def _check_branch_no_commits(self) -> bool:
        for line in self.report_lines:
            if "hotfix/urgent" in line and "0 commits" in line:
                return True
        return False

    def _check_distinct_file_count(self) -> bool:
        for line in self.report_lines:
            if "김민수" in line and "5 files" in line:
                return True
        return False

    def _check_most_changed_files(self) -> bool:
        for line in self.report_lines:
            if "requirements.txt" in line and "5 commits" in line:
                return True
        return False

    def _check_self_join_parent(self) -> bool:
        """History 섹션에 root commit(a1b2c3d) 존재 확인"""
        history_lines = self._find_section_lines("Commit History")
        for line in history_lines:
            if "a1b2c3d" in line:
                return True
        return False

    def _check_history_count(self) -> bool:
        """History 섹션에 7개 해시 전부 존재 확인"""
        history_lines = self._find_section_lines("Commit History")
        history_text = "\n".join(history_lines)
        for h in EXPECTED_MAIN_HISTORY:
            if h not in history_text:
                return False
        return True
