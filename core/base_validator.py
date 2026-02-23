"""
BaseValidator 추상 클래스
모든 플러그인 검증기는 이 클래스를 상속받아야 함
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from .checklist import Checklist


class BaseValidator(ABC):
    """
    추상 검증기 클래스

    모든 미션 플러그인은 이 클래스를 상속받아 validate() 메서드를 구현해야 함
    """

    def __init__(self, mission_config: Dict[str, Any]):
        """
        Args:
            mission_config: 미션 설정 딕셔너리 (config.yaml에서 로드)
        """
        self.config = mission_config
        self.checklist = Checklist(
            name=mission_config.get("name", "Unknown Mission"),
            description=mission_config.get("description", ""),
            passing_score=mission_config.get("passing_score", 70)
        )

    @abstractmethod
    def setup(self) -> None:
        """
        검증 전 초기화 작업
        (예: 학습자 제출 스크립트 실행, 환경 변수 설정 등)
        """
        pass

    @abstractmethod
    def build_checklist(self) -> None:
        """
        체크리스트 구성
        CheckItem들을 생성하여 self.checklist에 추가
        """
        pass

    @abstractmethod
    def teardown(self) -> None:
        """
        검증 후 정리 작업
        (예: 임시 파일 삭제, 리소스 해제 등)
        """
        pass

    def validate(self) -> Dict[str, Any]:
        """
        전체 검증 프로세스 실행

        Returns:
            검증 결과 딕셔너리
        """
        try:
            self.setup()
            self.build_checklist()
            result = self.checklist.execute_all()
            return result
        except Exception as e:
            return {
                "error": str(e),
                "is_passed": False,
                "score": 0,
                "name": self.config.get("name", "Unknown"),
                "description": self.config.get("description", "")
            }
        finally:
            self.teardown()
