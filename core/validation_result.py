"""
검증 결과 클래스
"""
from typing import Dict, Any, List
from datetime import datetime
import json


class ValidationResult:
    """
    최종 검증 결과 집합
    """

    def __init__(self, student_id: str, mission_id: str):
        self.student_id = student_id
        self.mission_id = mission_id
        self.timestamp = datetime.now().isoformat()
        self.results: List[Dict[str, Any]] = []
        self.overall_passed = False
        self.overall_score = 0.0

    def add_result(self, validator_name: str, result: Dict[str, Any],
                   weight: float = 0) -> None:
        """검증기 결과 추가"""
        self.results.append({
            "validator": validator_name,
            "result": result,
            "weight": weight,
        })

    def finalize(self) -> None:
        """최종 점수 및 합격 여부 계산"""
        if not self.results:
            self.overall_passed = False
            self.overall_score = 0.0
            return

        # 모든 검증기가 통과해야 최종 합격
        self.overall_passed = all(r["result"].get("is_passed", False) for r in self.results)

        # 가중 평균 점수 계산 (weight가 설정되어 있으면 사용, 없으면 단순 평균)
        total_weight = sum(r.get("weight", 0) for r in self.results)
        if total_weight > 0:
            self.overall_score = sum(
                r["result"].get("score", 0) * r.get("weight", 0)
                for r in self.results
            ) / total_weight
        else:
            total_score = sum(r["result"].get("score", 0) for r in self.results)
            self.overall_score = total_score / len(self.results)

    def to_json(self) -> str:
        """JSON 형식으로 변환"""
        return json.dumps({
            "student_id": self.student_id,
            "mission_id": self.mission_id,
            "timestamp": self.timestamp,
            "overall_passed": self.overall_passed,
            "overall_score": round(self.overall_score, 2),
            "results": self.results
        }, indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Markdown 리포트 생성"""
        md = f"# 채점 결과 리포트\n\n"
        md += f"- **학습자 ID**: {self.student_id}\n"
        md += f"- **미션 ID**: {self.mission_id}\n"
        md += f"- **채점 시각**: {self.timestamp}\n"
        md += f"- **최종 결과**: {'✅ PASS' if self.overall_passed else '❌ FAIL'}\n"
        md += f"- **종합 점수**: {round(self.overall_score, 2)}점\n\n"

        md += "---\n\n"

        for idx, result_item in enumerate(self.results, 1):
            validator = result_item["validator"]
            result = result_item["result"]

            md += f"## {idx}. {validator}\n\n"
            md += f"- **결과**: {'✅ 통과' if result.get('is_passed') else '❌ 실패'}\n"
            md += f"- **점수**: {result.get('earned_points', 0)} / {result.get('total_points', 0)}\n"
            md += f"- **통과율**: {result.get('passed_items', 0)} / {result.get('total_items', 0)}\n\n"

            md += "### 세부 체크리스트\n\n"
            for item in result.get("items", []):
                status_emoji = "✅" if item["status"] == "passed" else "❌"
                md += f"{status_emoji} **[{item['points']}점]** {item['description']}\n"

                if item.get("error_message"):
                    md += f"   - 오류: `{item['error_message']}`\n"
                if item.get("hint") and item["status"] != "passed":
                    md += f"   - 힌트: {item['hint']}\n"

            md += "\n---\n\n"

        return md
