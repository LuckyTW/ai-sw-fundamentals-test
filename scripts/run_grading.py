#!/usr/bin/env python3
"""
메인 채점 실행 스크립트
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.grader import Grader
from utils.config_loader import load_mission_config


def main():
    parser = argparse.ArgumentParser(description="코디세이 시험 자동 채점 시스템")
    parser.add_argument("--student-id", required=True, help="학습자 ID")
    parser.add_argument("--mission-id", required=True, help="미션 ID (예: linux_level1_mission01)")
    parser.add_argument("--output-dir", default="results", help="결과 저장 디렉토리")
    parser.add_argument("--submission-dir", default=None,
                        help="학습자 제출물 디렉토리 경로 (Python 미션 등)")

    args = parser.parse_args()

    # 1. 미션 설정 로드
    print(f"📝 미션 설정 로드 중: {args.mission_id}")
    config = load_mission_config(args.mission_id)
    if not config:
        print(f"❌ Error: 미션 설정을 찾을 수 없습니다 - {args.mission_id}")
        sys.exit(1)

    # submission-dir이 지정된 경우 config에 주입
    if args.submission_dir:
        config["submission_dir"] = str(Path(args.submission_dir).resolve())

    print(f"✅ 미션: {config.get('name', 'Unknown')}")
    print(f"   난이도: {config.get('level', '?')}")
    print(f"   합격 기준: {config.get('passing_score', 70)}점 이상")
    print()

    # 2. Grader 인스턴스 생성
    grader = Grader(args.student_id, args.mission_id, config)

    # 3. 채점 실행
    print(f"🔍 채점 시작: {args.student_id}")
    print("="*60)
    result = grader.execute()

    # 4. 결과 저장
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = result.timestamp.replace(":", "").replace("-", "").split(".")[0]

    # JSON 저장
    json_path = output_dir / f"{args.student_id}_{args.mission_id}_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(result.to_json())

    # Markdown 저장
    md_path = output_dir / f"{args.student_id}_{args.mission_id}_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(result.to_markdown())

    # 5. 결과 출력
    print()
    print(f"{'='*60}")
    print(f"채점 완료!")
    print(f"{'='*60}")
    print(f"학습자: {args.student_id}")
    print(f"미션: {args.mission_id}")
    print(f"결과: {'✅ PASS' if result.overall_passed else '❌ FAIL'}")
    print(f"점수: {result.overall_score:.2f}점")
    print(f"\n결과 파일:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    print(f"{'='*60}\n")

    # 6. 종료 코드 반환 (CI/CD 통합용)
    sys.exit(0 if result.overall_passed else 1)


if __name__ == "__main__":
    main()
