"""알고리즘 미션 검증 공통 유틸리티"""
import hashlib
from typing import List


def generate_hash(message: str, seq: int) -> str:
    """검증용 해시 생성 (학생 코드와 동일한 함수)"""
    return hashlib.sha256(f"{message}:{seq}".encode()).hexdigest()[:7]


def parse_responses(stdout: str) -> List[str]:
    """REPL stdout에서 프롬프트를 제거하고 응답만 추출

    "mini-git> [main abc1234] msg" → "[main abc1234] msg"
    여러 줄 응답(LOG, ANCESTORS 등)은 하나로 합침
    """
    responses = []
    lines = stdout.split("\n")
    current_response_lines = []

    for line in lines:
        if "mini-git>" in line:
            if current_response_lines:
                responses.append("\n".join(current_response_lines))
                current_response_lines = []

            after_prompt = line.split("mini-git>", 1)[1].strip()
            if after_prompt:
                current_response_lines.append(after_prompt)
        elif line.strip():
            current_response_lines.append(line.strip())

    if current_response_lines:
        responses.append("\n".join(current_response_lines))

    return responses
