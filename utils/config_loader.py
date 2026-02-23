"""
YAML 설정 파일 로더
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_mission_config(mission_id: str) -> Optional[Dict[str, Any]]:
    """
    미션 설정 파일을 로드

    Args:
        mission_id: 미션 ID (예: "linux_level1_mission01")

    Returns:
        설정 딕셔너리 또는 None (파일 없을 경우)
    """
    # 미션 ID 파싱 (예: "linux_level1_mission01" → "linux/level1/mission_01")
    parts = mission_id.split("_")
    if len(parts) < 3:
        return None

    category = parts[0]  # linux
    level = parts[1]     # level1
    mission = "_".join(parts[2:])  # mission01

    # 프로젝트 루트 찾기
    project_root = Path(__file__).parent.parent
    config_path = project_root / "missions" / category / level / mission / "config.yaml"

    if not config_path.exists():
        return None

    # YAML 파일 로드
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"설정 파일 로드 실패: {e}")
        return None


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent
