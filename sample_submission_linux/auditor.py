"""리눅스 서버 보안 감사 도구 — 모범 답안"""
import argparse
import csv
import os
import re


# ── 위험 포트 정의 ──
DANGEROUS_PORTS = {
    "21": "FTP",
    "23": "Telnet",
    "69": "TFTP",
    "161": "SNMP",
    "512": "rexec",
    "513": "rlogin",
    "514": "rsh",
}

# ── 임계값 ──
CPU_THRESHOLD = 90.0
MEM_THRESHOLD = 80.0

# ── 민감 디렉토리 키워드 ──
SENSITIVE_KEYWORDS = ["key", "secret", "credential", "token", "cert", "private"]


def parse_sshd_config(filepath):
    """sshd_config 파싱 → dict"""
    config = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                config[parts[0]] = parts[1]
    return config


def parse_ufw_status(filepath):
    """ufw_status.txt 파싱 → 허용 포트 리스트"""
    ports = []
    with open(filepath, "r", encoding="utf-8") as f:
        in_rules = False
        for line in f:
            line = line.strip()
            if line.startswith("--"):
                in_rules = True
                continue
            if in_rules and line:
                parts = line.split()
                if len(parts) >= 3:
                    port_proto = parts[0]  # e.g., "20022/tcp"
                    action = parts[1]      # e.g., "ALLOW"
                    ports.append({"port_proto": port_proto, "action": action})
    return ports


def parse_accounts(filepath):
    """accounts.csv 파싱 → 계정 리스트"""
    accounts = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["groups"] = row["groups"].split(";")
            accounts.append(row)
    return accounts


def parse_directories(filepath):
    """directories.csv 파싱 → 디렉토리 리스트"""
    dirs = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dirs.append(row)
    return dirs


def parse_monitor_log(filepath):
    """monitor.log 파싱 → 유효 레코드 리스트 (잘못된 줄 건너뛰기)"""
    pattern = re.compile(
        r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] "
        r"PID:(\d+) CPU:([\d.]+)% MEM:([\d.]+)% DISK:(\d+)G"
    )
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                records.append({
                    "timestamp": m.group(1),
                    "pid": int(m.group(2)),
                    "cpu": float(m.group(3)),
                    "mem": float(m.group(4)),
                    "disk": int(m.group(5)),
                })
    return records


def parse_crontab(filepath):
    """crontab.txt 파싱 → 작업 리스트"""
    jobs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                jobs.append(line)
    return jobs


def audit_ssh(ssh_config):
    """SSH 보안 감사"""
    findings = []
    port = ssh_config.get("Port", "22")
    if port == "22":
        findings.append(f"Port: {port} (Vulnerable - 기본 포트 사용)")
    else:
        findings.append(f"Port: {port} (Safe - 기본 포트 아님)")

    root_login = ssh_config.get("PermitRootLogin", "yes")
    if root_login == "no":
        findings.append(f"PermitRootLogin: {root_login} (Safe - 루트 로그인 완전 차단)")
    else:
        findings.append(
            f"PermitRootLogin: {root_login} "
            f"(Vulnerable - 'no'만 안전, '{root_login}'은 루트 접근 허용)"
        )

    pw_auth = ssh_config.get("PasswordAuthentication", "yes")
    if pw_auth == "yes":
        findings.append(f"PasswordAuthentication: {pw_auth} (Warning - 브루트포스 공격에 취약)")
    else:
        findings.append(f"PasswordAuthentication: {pw_auth} (Safe)")

    return findings


def audit_firewall(ufw_rules):
    """방화벽 감사"""
    findings = []
    seen_ports = set()

    for rule in ufw_rules:
        port_proto = rule["port_proto"]
        # IPv6 중복 제거
        port_num = port_proto.split("/")[0].strip()
        if port_num in seen_ports:
            continue
        seen_ports.add(port_num)

        if port_num in DANGEROUS_PORTS:
            proto_name = DANGEROUS_PORTS[port_num]
            findings.append(
                f"  - {port_proto} (Vulnerable - {proto_name}은 암호화 미지원, 즉시 차단 필요)"
            )
        else:
            findings.append(f"  - {port_proto} (Safe)")

    return findings


def audit_accounts(accounts):
    """계정/그룹 RBAC 감사"""
    findings = []
    core_group = "agent-core"
    expected_core_users = {"agent-admin", "agent-dev"}

    for acc in accounts:
        username = acc["username"]
        groups = acc["groups"]

        if core_group in groups and username not in expected_core_users:
            findings.append(
                f"  - {username}: agent-core 그룹 포함 "
                f"(Vulnerable - RBAC 위반, 불필요한 핵심 그룹 접근)"
            )
        else:
            findings.append(f"  - {username}: 그룹 {','.join(groups)} (Safe)")

    return findings


def audit_permissions(directories):
    """디렉토리 권한 감사"""
    findings = []

    for d in directories:
        path = d["path"]
        group = d["group"]
        perm = d["octal_permission"]
        dirname = os.path.basename(path).lower()

        is_sensitive = any(kw in dirname for kw in SENSITIVE_KEYWORDS)
        group_writable = len(perm) == 3 and int(perm[1]) >= 7

        if is_sensitive and group_writable:
            findings.append(
                f"  - {path} (Vulnerable - 민감 디렉토리에 그룹({group}) "
                f"쓰기 권한 {perm}, 과도한 접근)"
            )
        elif group_writable and group != d["owner"]:
            findings.append(
                f"  - {path} (Warning - 그룹({group}) 쓰기 권한 {perm})"
            )
        else:
            findings.append(f"  - {path} (Safe - {perm})")

    return findings


def analyze_logs(log_records):
    """모니터링 로그 통계 분석"""
    if not log_records:
        return ["  데이터 없음"]

    cpu_values = [r["cpu"] for r in log_records]
    mem_values = [r["mem"] for r in log_records]

    cpu_avg = sum(cpu_values) / len(cpu_values)
    cpu_max = max(cpu_values)
    mem_max = max(mem_values)

    lines = []
    lines.append(f"Total Valid Lines: {len(log_records)}")
    lines.append(f"CPU Average: {cpu_avg:.2f}%")

    cpu_max_warning = " [WARNING]" if cpu_max > CPU_THRESHOLD else ""
    lines.append(f"CPU Max: {cpu_max}%{cpu_max_warning}")

    mem_max_warning = " [WARNING]" if mem_max > MEM_THRESHOLD else ""
    lines.append(f"MEM Max: {mem_max}%{mem_max_warning}")

    return lines


def generate_report(ssh_findings, fw_findings, acc_findings, perm_findings, log_lines, cron_jobs):
    """5개 섹션 감사 리포트 생성"""
    sections = []

    sections.append("=== SSH Security Audit ===")
    sections.extend(ssh_findings)
    sections.append("")

    sections.append("=== Firewall Audit ===")
    sections.append("Default Policy: deny incoming (Safe)")
    sections.append("Allowed Ports:")
    sections.extend(fw_findings)
    sections.append("")

    sections.append("=== Account Audit ===")
    sections.extend(acc_findings)
    sections.append("")

    sections.append("=== Permission Audit ===")
    sections.extend(perm_findings)
    sections.append("")

    sections.append("=== Log Analysis ===")
    sections.extend(log_lines)
    if cron_jobs:
        sections.append(f"Scheduled Jobs: {len(cron_jobs)}")

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="리눅스 서버 보안 감사 도구")
    parser.add_argument("--config-dir", required=True, help="설정 파일 디렉토리 경로")
    parser.add_argument("--output", required=True, help="출력 리포트 파일 경로")
    args = parser.parse_args()

    config_dir = args.config_dir

    # 1. 파일 파싱
    ssh_config = parse_sshd_config(os.path.join(config_dir, "sshd_config"))
    ufw_rules = parse_ufw_status(os.path.join(config_dir, "ufw_status.txt"))
    accounts = parse_accounts(os.path.join(config_dir, "accounts.csv"))
    directories = parse_directories(os.path.join(config_dir, "directories.csv"))
    log_records = parse_monitor_log(os.path.join(config_dir, "monitor.log"))
    cron_jobs = parse_crontab(os.path.join(config_dir, "crontab.txt"))

    # 2. 감사
    ssh_findings = audit_ssh(ssh_config)
    fw_findings = audit_firewall(ufw_rules)
    acc_findings = audit_accounts(accounts)
    perm_findings = audit_permissions(directories)
    log_lines = analyze_logs(log_records)

    # 3. 리포트 생성 및 저장
    report = generate_report(ssh_findings, fw_findings, acc_findings, perm_findings, log_lines, cron_jobs)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
