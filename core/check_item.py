"""
개별 체크 항목 클래스
"""
from typing import Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class CheckStatus(Enum):
    """체크 상태 열거형"""
    PENDING = "pending"      # 검증 전
    PASSED = "passed"        # 통과
    FAILED = "failed"        # 실패
    ERROR = "error"          # 에러 발생


@dataclass
class CheckItem:
    """
    개별 체크 항목

    Attributes:
        id: 체크 항목 고유 ID (예: "ssh_port_check")
        description: 체크 항목 설명 (예: "SSH 포트가 20022로 설정되어 있는지 확인")
        points: 배점 (기본 10점)
        validator: 검증 함수 (Callable, 반환값: bool)
        hint: 실패 시 힌트 메시지
        ai_trap: AI가 놓치기 쉬운 함정 요소 여부
    """
    id: str
    description: str
    points: int
    validator: Callable[[], bool]
    hint: Optional[str] = None
    ai_trap: bool = False

    # 실행 결과 (dataclass field로 기본값 설정)
    status: CheckStatus = field(default=CheckStatus.PENDING)
    error_message: Optional[str] = field(default=None)
    execution_time: float = field(default=0.0)

    def execute(self) -> bool:
        """
        검증 함수 실행

        Returns:
            검증 성공 여부
        """
        import time
        start_time = time.time()

        try:
            result = self.validator()
            self.status = CheckStatus.PASSED if result else CheckStatus.FAILED
            return result
        except Exception as e:
            self.status = CheckStatus.ERROR
            self.error_message = str(e)
            return False
        finally:
            self.execution_time = time.time() - start_time

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (결과 저장용)"""
        return {
            "id": self.id,
            "description": self.description,
            "points": self.points,
            "status": self.status.value,
            "error_message": self.error_message,
            "execution_time": round(self.execution_time, 3),
            "ai_trap": self.ai_trap,
            "hint": self.hint if self.status != CheckStatus.PASSED else None
        }
