"""
채점 엔진 (Grader)
"""
from typing import List, Dict, Any
import importlib
from pathlib import Path

from .base_validator import BaseValidator
from .validation_result import ValidationResult


class Grader:
    """
    채점 엔진
    플러그인을 로드하고 실행하여 최종 결과를 생성
    """

    def __init__(self, student_id: str, mission_id: str, mission_config: Dict[str, Any]):
        """
        Args:
            student_id: 학습자 ID
            mission_id: 미션 ID (예: "linux_level1_mission01")
            mission_config: 미션 설정 (config.yaml에서 로드)
        """
        self.student_id = student_id
        self.mission_id = mission_id
        self.config = mission_config
        self.result = ValidationResult(student_id, mission_id)

    def load_validators(self) -> List[BaseValidator]:
        """
        설정에 정의된 검증기 클래스들을 동적으로 로드

        Returns:
            BaseValidator 인스턴스 리스트
        """
        validators = []

        for validator_config in self.config.get("validators", []):
            module_path = validator_config["module"]
            class_name = validator_config["class"]

            # 동적 import
            module = importlib.import_module(module_path)
            validator_class = getattr(module, class_name)

            # 인스턴스 생성
            validator = validator_class(self.config)
            validators.append(validator)

        return validators

    def execute(self) -> ValidationResult:
        """
        모든 검증기 실행 및 결과 수집

        Returns:
            ValidationResult 객체
        """
        validators = self.load_validators()

        # validator별 weight 매핑 (config에서 로드)
        weight_map = {}
        for vc in self.config.get("validators", []):
            weight_map[vc["class"]] = vc.get("weight", 0)

        for validator in validators:
            validator_name = validator.__class__.__name__
            weight = weight_map.get(validator_name, 0)

            try:
                result = validator.validate()
                self.result.add_result(validator_name, result, weight=weight)
            except Exception as e:
                # 검증기 실행 중 오류 발생 시 기록
                self.result.add_result(validator_name, {
                    "error": f"검증기 실행 실패: {str(e)}",
                    "is_passed": False,
                    "score": 0
                }, weight=weight)

        self.result.finalize()
        return self.result
