"""
검색/정렬 검증 플러그인 (25점)

subprocess.run + stdin pipe로 SEARCH/LOG --sort-by 동작을 검증.
분기 없는 선형 시나리오로 독립적으로 테스트.
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.algo.validators._helpers import generate_hash, parse_responses


class SearchSortValidator(BaseValidator):
    """검색/정렬 검증 (SEARCH 키워드/작성자, LOG --sort-by)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.cli_path: Optional[str] = None
        self._responses: Optional[List[str]] = None

        # 사전 계산 해시값
        self._s1 = generate_hash("Initial commit", 1)
        self._s2 = generate_hash("Add user auth", 2)
        self._s3 = generate_hash("Add login page", 3)
        self._s4 = generate_hash("Fix login bug", 4)

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        cli_file = os.path.join(self.submission_dir, "cli.py")
        if os.path.isfile(cli_file):
            self.cli_path = cli_file

        # 검색/정렬 테스트 시나리오 (선형, 브랜치 없음)
        commands = (
            'INIT Alice\n'
            'COMMIT "Initial commit"\n'
            'COMMIT "Add user auth"\n'
            'COMMIT "Add login page"\n'
            'COMMIT "Fix login bug"\n'
            'SEARCH "login"\n'
            'SEARCH "nonexistent"\n'
            'SEARCH --author=Alice\n'
            'LOG --sort-by=date\n'
            'exit\n'
        )
        self._responses = self._run_repl(commands)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="search_keyword",
            description="SEARCH 키워드 검색 (정확한 매칭 + 결과 수)",
            points=7,
            validator=self._check_search_keyword,
            hint="역색인으로 메시지에 키워드가 포함된 커밋을 검색하세요",
        ))

        self.checklist.add_item(CheckItem(
            id="search_no_result",
            description="미존재 키워드 SEARCH → 'Found 0 commit(s):'",
            points=5,
            validator=self._check_search_no_result,
            hint="검색 결과가 없으면 'Found 0 commit(s):' 출력",
        ))

        self.checklist.add_item(CheckItem(
            id="search_author",
            description="SEARCH --author 작성자 검색",
            points=6,
            validator=self._check_search_author,
            hint="--author=Name 옵션으로 작성자별 커밋 검색",
        ))

        self.checklist.add_item(CheckItem(
            id="sort_by_date",
            description="LOG --sort-by=date 날짜순 정렬 확인",
            points=7,
            validator=self._check_sort_by_date,
            hint="LOG --sort-by=date는 모든 커밋을 시간순으로 출력 (merge sort 직접 구현)",
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

    def _check_search_keyword(self) -> bool:
        """SEARCH "login" → Found 2 commit(s): s3, s4

        "login"이 포함된 커밋: "Add login page"(s3), "Fix login bug"(s4)
        """
        if not self._responses or len(self._responses) < 6:
            return False

        # responses: [0]=INIT, [1]=c1, [2]=c2, [3]=c3, [4]=c4, [5]=SEARCH "login"
        search_resp = self._responses[5]

        return ("Found 2 commit(s):" in search_resp
                and self._s3 in search_resp
                and self._s4 in search_resp)

    def _check_search_no_result(self) -> bool:
        """SEARCH "nonexistent" → Found 0 commit(s):"""
        if not self._responses or len(self._responses) < 7:
            return False

        # responses[6] = SEARCH "nonexistent"
        search_resp = self._responses[6]

        return "Found 0 commit(s):" in search_resp

    def _check_search_author(self) -> bool:
        """SEARCH --author=Alice → Found 4 commit(s): (모든 커밋)"""
        if not self._responses or len(self._responses) < 8:
            return False

        # responses[7] = SEARCH --author=Alice
        search_resp = self._responses[7]

        return ("Found 4 commit(s):" in search_resp
                and self._s1 in search_resp
                and self._s2 in search_resp
                and self._s3 in search_resp
                and self._s4 in search_resp)

    def _check_sort_by_date(self) -> bool:
        """LOG --sort-by=date → 4개 커밋이 시간순 출력 (s1, s2, s3, s4)"""
        if not self._responses or len(self._responses) < 9:
            return False

        # responses[8] = LOG --sort-by=date
        log_resp = self._responses[8]

        # 4개 해시가 모두 존재
        if not (self._s1 in log_resp and self._s2 in log_resp
                and self._s3 in log_resp and self._s4 in log_resp):
            return False

        # 시간순 정렬: s1의 위치 < s2 < s3 < s4
        pos1 = log_resp.find(self._s1)
        pos2 = log_resp.find(self._s2)
        pos3 = log_resp.find(self._s3)
        pos4 = log_resp.find(self._s4)

        return pos1 < pos2 < pos3 < pos4
