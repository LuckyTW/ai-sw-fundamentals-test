"""
체크리스트 관리 클래스
"""
from typing import List, Dict, Any
from .check_item import CheckItem, CheckStatus


class Checklist:
    """
    체크리스트 (여러 CheckItem의 집합)
    """
    def __init__(self, name: str, description: str, passing_score: int = 70):
        """
        Args:
            name: 체크리스트 이름
            description: 설명
            passing_score: 합격 기준 점수 (기본 70점)
        """
        self.name = name
        self.description = description
        self.passing_score = passing_score
        self.items: List[CheckItem] = []

    def add_item(self, item: CheckItem) -> None:
        """체크 항목 추가"""
        self.items.append(item)

    def execute_all(self) -> Dict[str, Any]:
        """
        모든 체크 항목 실행

        Returns:
            실행 결과 딕셔너리
        """
        results = []
        passed_count = 0
        total_points = 0
        earned_points = 0

        for item in self.items:
            success = item.execute()
            results.append(item.to_dict())

            total_points += item.points
            if success:
                passed_count += 1
                earned_points += item.points

        score = (earned_points / total_points * 100) if total_points > 0 else 0
        is_passed = score >= self.passing_score

        return {
            "name": self.name,
            "description": self.description,
            "total_items": len(self.items),
            "passed_items": passed_count,
            "total_points": total_points,
            "earned_points": earned_points,
            "score": round(score, 2),
            "passing_score": self.passing_score,
            "is_passed": is_passed,
            "items": results
        }

    def get_total_points(self) -> int:
        """총 배점 계산"""
        return sum(item.points for item in self.items)
