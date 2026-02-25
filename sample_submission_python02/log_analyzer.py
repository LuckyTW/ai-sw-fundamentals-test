"""서버 접근 로그 분석기 — 모범 답안"""
import argparse
import csv
from collections import defaultdict


def parse_log(filepath):
    """CSV 로그 파일을 파싱하여 레코드 리스트 반환"""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def analyze_ip_access(records):
    """IP별 접근 횟수 집계 (빈 IP 제외)"""
    ip_count = defaultdict(int)
    for r in records:
        ip = r["ip"].strip()
        if ip:
            ip_count[ip] += 1
    sorted_ips = sorted(ip_count.items(), key=lambda x: (x[1], x[0]), reverse=True)
    return sorted_ips[:5]


def analyze_status_codes(records):
    """HTTP 상태코드 그룹별 비율 계산 (1xx 포함)"""
    total = len(records)
    groups = defaultdict(int)
    for r in records:
        code = int(r["status_code"])
        if 100 <= code < 200:
            groups["1xx"] += 1
        elif 200 <= code < 300:
            groups["2xx"] += 1
        elif 300 <= code < 400:
            groups["3xx"] += 1
        elif 400 <= code < 500:
            groups["4xx"] += 1
        elif 500 <= code < 600:
            groups["5xx"] += 1
    result = {}
    for group in ["1xx", "2xx", "3xx", "4xx", "5xx"]:
        count = groups.get(group, 0)
        if count > 0:
            result[group] = round(count / total * 100, 1)
    return result


def analyze_slow_endpoints(records):
    """엔드포인트별 평균 응답시간 계산 (float 파싱)"""
    endpoint_times = defaultdict(list)
    for r in records:
        endpoint = r["endpoint"]
        response_time = float(r["response_time_ms"])
        endpoint_times[endpoint].append(response_time)
    averages = {}
    for endpoint, times in endpoint_times.items():
        averages[endpoint] = round(sum(times) / len(times), 1)
    sorted_endpoints = sorted(averages.items(), key=lambda x: x[1], reverse=True)
    return sorted_endpoints[:3]


def generate_report(top_ips, status_ratios, slow_endpoints):
    """리포트 텍스트 생성"""
    lines = []
    lines.append("=== IP Access Top 5 ===")
    for ip, count in top_ips:
        lines.append(f"{ip}: {count}")
    lines.append("")
    lines.append("=== Status Code Distribution ===")
    for group, ratio in sorted(status_ratios.items()):
        lines.append(f"{group}: {ratio:.1f}%")
    lines.append("")
    lines.append("=== Slowest Endpoints Top 3 ===")
    for endpoint, avg_time in slow_endpoints:
        lines.append(f"{endpoint}: {avg_time:.1f}ms")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="서버 접근 로그 분석기")
    parser.add_argument("--log", required=True, help="입력 CSV 로그 파일 경로")
    parser.add_argument("--output", required=True, help="출력 리포트 파일 경로")
    args = parser.parse_args()

    records = parse_log(args.log)
    top_ips = analyze_ip_access(records)
    status_ratios = analyze_status_codes(records)
    slow_endpoints = analyze_slow_endpoints(records)

    report = generate_report(top_ips, status_ratios, slow_endpoints)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
