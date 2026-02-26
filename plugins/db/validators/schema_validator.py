"""
커밋 이력 DB 분석기 — 스키마 검증 플러그인 (20점)

DB 파일을 sqlite3로 열어 테이블 구조, FK, 인덱스, 데이터 적재를 검증.

AI 트랩: parent_hash NOT NULL 정의 → root commit INSERT 실패
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from typing import Dict, Any, Optional

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.db.validators._data import write_csv_files


class SchemaValidator(BaseValidator):
    """DB 스키마 구조 검증 (테이블, FK, 인덱스, 데이터 적재)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.db_path: Optional[str] = None
        self.report_path: Optional[str] = None
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None
        self._exec_success = False

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

        self.db_path = os.path.join(tmp, "analysis.db")
        self.report_path = os.path.join(tmp, "report.txt")

        try:
            subprocess.run(
                [sys.executable, script_path,
                 "--data-dir", data_dir,
                 "--output", self.report_path,
                 "--db", self.db_path],
                capture_output=True, text=True, timeout=15,
                cwd=self.submission_dir,
            )
            self._exec_success = True
        except (subprocess.TimeoutExpired, OSError):
            pass

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="db_created",
            description="analysis.db 생성 + 4개 테이블 존재",
            points=4,
            validator=self._check_db_created,
            hint="sqlite3.connect()로 DB 파일을 생성하고 authors, commits, branches, commit_files 테이블을 만드세요",
        ))
        self.checklist.add_item(CheckItem(
            id="foreign_keys",
            description="commits 테이블에 FK 제약조건 존재",
            points=4,
            validator=self._check_foreign_keys,
            hint="commits 테이블에서 author_id → authors, parent_hash → commits FK를 정의하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="root_commit_null",
            description="parent_hash NULL 허용 + root commit 존재",
            points=5,
            validator=self._check_root_commit_null,
            hint="root commit(최초 커밋)은 parent가 없으므로 parent_hash를 NULL로 저장해야 합니다",
            ai_trap=True,
        ))
        self.checklist.add_item(CheckItem(
            id="data_loaded",
            description="테이블별 행 수 정확성 (6, 12, 4, 25)",
            points=4,
            validator=self._check_data_loaded,
            hint="CSV 파일 4개를 빠짐없이 읽어 DB에 INSERT하세요",
        ))
        self.checklist.add_item(CheckItem(
            id="index_exists",
            description="최소 1개 사용자 정의 인덱스 존재",
            points=3,
            validator=self._check_index_exists,
            hint="자주 조회하는 컬럼(author_id, branch_name 등)에 인덱스를 생성하세요",
        ))

    def teardown(self) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()

    # -- 검증 함수 --

    def _open_db(self) -> Optional[sqlite3.Connection]:
        if self.db_path and os.path.isfile(self.db_path):
            return sqlite3.connect(self.db_path)
        return None

    def _check_db_created(self) -> bool:
        conn = self._open_db()
        if not conn:
            return False
        try:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}
            expected = {"authors", "commits", "branches", "commit_files"}
            return expected.issubset(tables)
        finally:
            conn.close()

    def _check_foreign_keys(self) -> bool:
        conn = self._open_db()
        if not conn:
            return False
        try:
            fk_list = conn.execute("PRAGMA foreign_key_list(commits)").fetchall()
            return len(fk_list) >= 1
        finally:
            conn.close()

    def _check_root_commit_null(self) -> bool:
        conn = self._open_db()
        if not conn:
            return False
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM commits WHERE parent_hash IS NULL"
            ).fetchone()[0]
            return count == 1
        finally:
            conn.close()

    def _check_data_loaded(self) -> bool:
        conn = self._open_db()
        if not conn:
            return False
        try:
            expected = {
                "authors": 6,
                "commits": 12,
                "branches": 4,
                "commit_files": 25,
            }
            for table, count in expected.items():
                actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                if actual != count:
                    return False
            return True
        finally:
            conn.close()

    def _check_index_exists(self) -> bool:
        conn = self._open_db()
        if not conn:
            return False
        try:
            indexes = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            return len(indexes) >= 1
        finally:
            conn.close()
