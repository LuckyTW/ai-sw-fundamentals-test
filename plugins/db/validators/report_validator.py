"""
커밋 이력 DB 분석기 — 리포트 형식/요약 검증 플러그인 (35점)

리포트 파일의 존재, 섹션 구조, 요약 통계를 검증.
"""
import os
import subprocess
import sys
import tempfile
from typing import Dict, Any, Optional, List

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.db.validators._data import write_csv_files


class ReportValidator(BaseValidator):
    """리포트 형식 및 요약 섹션 검증"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.report_content: Optional[str] = None
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
                    self.report_content = f.read()
                    self.report_lines = self.report_content.splitlines()
            except (OSError, UnicodeDecodeError):
                pass

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="report_created",
            description="리포트 파일 생성 확인",
            points=3,
            validator=self._check_report_created,
            hint="--output 경로에 리포트 텍스트 파일을 생성하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="report_sections",
            description="5개 섹션 헤더 존재",
            points=4,
            validator=self._check_report_sections,
            hint="리포트에 Commit Statistics, Branch Analysis, Commit History, File Change Analysis, Summary 섹션을 포함하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="top_author",
            description="Most Active Author = 김민수 (4 commits)",
            points=7,
            validator=self._check_top_author,
            hint="Summary 섹션에 가장 많은 커밋을 작성한 저자를 표시하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="commit_total",
            description="Total Commits: 12 확인",
            points=6,
            validator=self._check_commit_total,
            hint="전체 커밋 수를 정확히 집계하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="summary_stats",
            description="요약 3항목 (Author/Branch/File) 존재",
            points=8,
            validator=self._check_summary_stats,
            hint="Summary 섹션에 Most Active Author, Largest Branch, Most Changed File을 포함하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="file_ranking_order",
            description="requirements.txt가 파일 변경 순위 1위",
            points=7,
            validator=self._check_file_ranking_order,
            hint="파일 변경 횟수를 내림차순 정렬하여 첫 번째 항목이 requirements.txt여야 합니다",
        ))

    def teardown(self) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()

    # -- 검증 함수 --

    def _check_report_created(self) -> bool:
        return self.report_content is not None and len(self.report_content.strip()) > 0

    def _check_report_sections(self) -> bool:
        if not self.report_content:
            return False
        content = self.report_content.lower()
        sections = [
            "commit statistics",
            "branch analysis",
            "commit history",
            "file change analysis",
            "summary",
        ]
        found = sum(1 for s in sections if s in content)
        return found >= 5

    def _check_top_author(self) -> bool:
        if not self.report_content:
            return False
        for line in self.report_lines:
            lower = line.lower()
            if "most active author" in lower and "김민수" in line:
                if "4" in line:
                    return True
        return False

    def _check_commit_total(self) -> bool:
        if not self.report_content:
            return False
        for line in self.report_lines:
            lower = line.lower()
            if "total commits" in lower and "12" in line:
                return True
        return False

    def _check_summary_stats(self) -> bool:
        if not self.report_content:
            return False
        content = self.report_content.lower()
        checks = [
            "most active author" in content,
            "largest branch" in content,
            "most changed file" in content,
        ]
        return all(checks)

    def _check_file_ranking_order(self) -> bool:
        """파일 변경 분석 섹션에서 첫 번째 순위가 requirements.txt인지 확인"""
        if not self.report_content:
            return False
        in_section = False
        for line in self.report_lines:
            if "file change analysis" in line.lower() or "most changed files" in line.lower():
                in_section = True
                continue
            if in_section:
                if line.startswith("==="):
                    break
                stripped = line.strip()
                if stripped and ("1." in stripped or "1 " in stripped):
                    if "requirements.txt" in stripped:
                        return True
                    return False
        return False
