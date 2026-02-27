"""
그래프 알고리즘 검증 플러그인 (35점)

subprocess.run + stdin pipe로 PATH/ANCESTORS/LOG 알고리즘을 검증.

조정 1 적용: path_same_branch는 독립 세션(선형 체인)으로 테스트하여
commit_parent 트랩에 의한 연쇄 실패를 방지.

AI 트랩:
- commit_parent_after_switch: SWITCH 후 COMMIT 부모 설정 오류
- log_all_branches: LOG가 현재 브랜치만 출력
- path_cross_branch: 다른 브랜치 간 PATH 검색 실패
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List

from core.base_validator import BaseValidator
from core.check_item import CheckItem
from plugins.algo.validators._helpers import generate_hash, parse_responses


class GraphAlgorithmValidator(BaseValidator):
    """그래프 알고리즘 검증 (PATH/ANCESTORS/LOG)"""

    def __init__(self, mission_config: Dict[str, Any]):
        super().__init__(mission_config)
        self.submission_dir = ""
        self.cli_path: Optional[str] = None

        # 독립 세션 결과
        self._linear_responses: Optional[List[str]] = None    # 세션 A: 선형 체인
        self._branch_responses: Optional[List[str]] = None    # 세션 B: 브랜치 분기

        # 사전 계산 해시값
        # 세션 A: 선형 체인
        self._p1 = generate_hash("Init", 1)
        self._p2 = generate_hash("Second", 2)
        self._p3 = generate_hash("Third", 3)

        # 세션 B: 브랜치 분기
        self._c1 = generate_hash("Initial commit", 1)
        self._c2 = generate_hash("Add user auth", 2)
        self._c3 = generate_hash("Add login page", 3)
        self._c4 = generate_hash("Add dashboard", 4)
        self._c5 = generate_hash("Add payment", 5)

    def setup(self) -> None:
        self.submission_dir = self.config.get("submission_dir", "")
        cli_file = os.path.join(self.submission_dir, "cli.py")
        if os.path.isfile(cli_file):
            self.cli_path = cli_file

        # 세션 A: 선형 체인 (path_same_branch 독립 테스트)
        # PATH p3 p1: 부모 방향 BFS로 p3→p2→p1 탐색 가능 (트랩4 연쇄 방지)
        linear_commands = (
            'INIT Alice\n'
            'COMMIT "Init"\n'
            'COMMIT "Second"\n'
            'COMMIT "Third"\n'
            f'PATH {self._p3} {self._p1}\n'
            'exit\n'
        )
        self._linear_responses = self._run_repl(linear_commands)

        # 세션 B: 브랜치 분기 (나머지 테스트)
        # LOG를 COMMIT c5 전에 배치하여 트랩2(선형 체인화)가 트랩3(LOG)을 상쇄하지 않도록 함
        # LOG 시점: c1,c2(main) + c3,c4(feature) = 4커밋. main HEAD=c2에서 부모 탐색 시 c3,c4 미도달
        branch_commands = (
            'INIT Alice\n'
            'COMMIT "Initial commit"\n'
            'COMMIT "Add user auth"\n'
            'BRANCH feature\n'
            'SWITCH feature\n'
            'COMMIT "Add login page"\n'
            'COMMIT "Add dashboard"\n'
            'SWITCH main\n'
            'LOG\n'
            'COMMIT "Add payment"\n'
            f'ANCESTORS {self._c5}\n'
            f'PATH {self._c4} {self._c5}\n'
            f'ANCESTORS {self._c4}\n'
            'exit\n'
        )
        self._branch_responses = self._run_repl(branch_commands)

    def build_checklist(self) -> None:
        self.checklist.add_item(CheckItem(
            id="commit_parent_after_switch",
            description="SWITCH 후 COMMIT이 올바른 부모 설정 (ANCESTORS 개수 검증)",
            points=7,
            validator=self._check_commit_parent,
            hint="SWITCH 후 COMMIT의 부모는 해당 브랜치의 최신 커밋이어야 합니다",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="log_all_branches",
            description="LOG가 모든 브랜치의 커밋을 출력하는지 확인",
            points=8,
            validator=self._check_log_all,
            hint="LOG는 저장소의 모든 커밋을 출력해야 합니다 (현재 브랜치만이 아님)",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="path_same_branch",
            description="같은 브랜치 내 두 커밋 간 최단 경로 확인",
            points=5,
            validator=self._check_path_same_branch,
            hint="선형 체인에서 PATH는 중간 노드를 포함한 경로를 반환",
        ))

        self.checklist.add_item(CheckItem(
            id="path_cross_branch",
            description="다른 브랜치 간 두 커밋 최단 경로 확인",
            points=10,
            validator=self._check_path_cross_branch,
            hint="부모-자식 양방향으로 BFS해야 다른 브랜치 커밋 간 경로를 찾을 수 있습니다",
            ai_trap=True,
        ))

        self.checklist.add_item(CheckItem(
            id="ancestors_complete",
            description="ANCESTORS가 모든 조상을 출력하는지 확인",
            points=5,
            validator=self._check_ancestors,
            hint="BFS로 부모 방향을 따라 모든 조상을 탐색하세요",
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

    def _check_commit_parent(self) -> bool:
        """세션 B: ANCESTORS c5 → 조상이 c2, c1 (2개)

        AI 실수: c5의 부모를 c4로 설정하면 조상이 c4, c3, c2, c1 (4개)
        """
        if not self._branch_responses or len(self._branch_responses) < 11:
            return False

        # responses[10] = ANCESTORS c5 (LOG가 [8]로 이동하여 인덱스 +1)
        ancestors_resp = self._branch_responses[10]

        # c2, c1이 조상에 포함되어야 함
        has_c2 = self._c2 in ancestors_resp
        has_c1 = self._c1 in ancestors_resp

        # c3, c4는 조상에 포함되면 안 됨 (다른 브랜치)
        has_c3 = self._c3 in ancestors_resp
        has_c4 = self._c4 in ancestors_resp

        return has_c2 and has_c1 and not has_c3 and not has_c4

    def _check_log_all(self) -> bool:
        """세션 B: LOG → 4개 커밋 모두 출력 (feature 브랜치 포함)

        LOG는 COMMIT c5 전에 실행되므로 c1,c2(main) + c3,c4(feature) = 4개.
        AI 실수: HEAD(main) 도달 가능 커밋만 출력 → c3, c4 누락
        독립 타이밍: commit_parent 트랩(선형 체인화)이 LOG 결과를 상쇄하지 않음
        """
        if not self._branch_responses or len(self._branch_responses) < 9:
            return False

        # responses[8] = LOG (COMMIT c5 전, 4개 커밋만 존재)
        log_resp = self._branch_responses[8]

        # 4개 커밋 해시가 모두 존재해야 함 (c5는 아직 미생성)
        return (self._c1 in log_resp
                and self._c2 in log_resp
                and self._c3 in log_resp
                and self._c4 in log_resp)

    def _check_path_same_branch(self) -> bool:
        """세션 A (독립): PATH p3 p1 → 경로에 p1, p2, p3 모두 포함

        선형 체인 p1→p2→p3에서 부모 방향 BFS로 p3→p2→p1 탐색 가능
        """
        if not self._linear_responses or len(self._linear_responses) < 4:
            return False

        # 세션 A: responses[0]=INIT, [1]=c1, [2]=c2, [3]=c3, [4]=PATH
        # INIT 응답은 3줄이지만 하나로 합쳐짐 → index 0
        # COMMIT 3개 → index 1, 2, 3
        # PATH → index 4
        if len(self._linear_responses) < 5:
            return False

        path_resp = self._linear_responses[4]

        return ("Path:" in path_resp
                and self._p1 in path_resp
                and self._p2 in path_resp
                and self._p3 in path_resp
                and "No path" not in path_resp)

    def _check_path_cross_branch(self) -> bool:
        """세션 B: PATH c4 c5 → 경로 존재 (c4→c3→c2→c5)

        AI 실수: 부모 방향만 BFS → "No path found."
        """
        if not self._branch_responses or len(self._branch_responses) < 12:
            return False

        # responses[11] = PATH c4 c5
        path_resp = self._branch_responses[11]

        return ("Path:" in path_resp
                and self._c4 in path_resp
                and self._c5 in path_resp
                and "No path" not in path_resp)

    def _check_ancestors(self) -> bool:
        """세션 B: ANCESTORS c4 → c3, c2, c1 (3개 조상)"""
        if not self._branch_responses or len(self._branch_responses) < 13:
            return False

        # responses[12] = ANCESTORS c4
        ancestors_resp = self._branch_responses[12]

        return (self._c3 in ancestors_resp
                and self._c2 in ancestors_resp
                and self._c1 in ancestors_resp)
