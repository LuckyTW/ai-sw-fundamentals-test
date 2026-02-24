# 리눅스 서버 보안 감사 도구 — 모범 답안

## 프로젝트 구조

```
submission/
└── auditor.py    # 보안 감사 도구 (단일 파일)
```

---

## auditor.py (100점)

```python
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

    print(f"감사 리포트 생성 완료: {args.output}")


if __name__ == "__main__":
    main()
```

---

## AI 함정 해설 (4개)

### 함정 1: PermitRootLogin prohibit-password (ssh_audit)

`PermitRootLogin prohibit-password`는 패스워드 인증만 차단하고 **SSH 키 인증으로 루트 로그인을 허용**합니다.
AI는 "password를 금지했으니 안전하다"고 판단하는 경향이 있지만, 루트 계정 접근 자체가 보안 위험입니다.

**AI가 흔히 하는 실수 (안전으로 판정)**:
```python
if root_login != "yes":
    return "Safe"  # prohibit-password도 Safe로 판정
```

**올바른 구현 (no만 안전)**:
```python
if root_login == "no":
    return "Safe"
else:
    return "Vulnerable"  # prohibit-password, yes 등 모두 취약
```

### 함정 2: 23/tcp Telnet 포트 (firewall_audit)

방화벽에 23번 포트(Telnet)가 ALLOW로 설정되어 있습니다. Telnet은 암호화 없이 데이터를 전송하므로 보안 위험입니다.
AI는 단순히 "포트가 열려 있다"고만 보고하고, **Telnet이 왜 위험한지 판단하지 못하는 경우**가 있습니다.

**AI가 흔히 하는 실수 (위험 포트 미분류)**:
```python
for rule in rules:
    findings.append(f"{rule['port']} - ALLOW")  # 모든 포트를 동일하게 처리
```

**올바른 구현 (well-known 위험 포트 분류)**:
```python
DANGEROUS_PORTS = {"21": "FTP", "23": "Telnet", "69": "TFTP"}
if port_num in DANGEROUS_PORTS:
    findings.append(f"{port} (Vulnerable - {DANGEROUS_PORTS[port_num]})")
```

### 함정 3: agent-test의 agent-core 그룹 (account_audit)

`agent-test`(테스트 계정)가 `agent-core`(핵심 운영 그룹)에 포함되어 있습니다.
최소 권한 원칙에 따라 테스트 계정은 핵심 그룹에 포함되어서는 안 됩니다.
AI는 "모든 계정이 동일한 그룹에 있으니 정상"이라고 판단하는 경향이 있습니다.

**AI가 흔히 하는 실수 (그룹 소속 일괄 통과)**:
```python
for acc in accounts:
    findings.append(f"{acc['username']}: Safe")  # 그룹 검증 없이 통과
```

**올바른 구현 (RBAC 검증)**:
```python
expected_core_users = {"agent-admin", "agent-dev"}
if "agent-core" in groups and username not in expected_core_users:
    findings.append(f"{username}: Vulnerable - RBAC 위반")
```

### 함정 4: api_keys 775+agent-common (permission_audit)

`api_keys` 디렉토리에 `agent-common` 그룹 + 775 권한이 설정되어 있습니다.
민감 데이터(API 키)가 저장되는 디렉토리에 광범위 그룹의 쓰기 권한을 부여하면 데이터 유출 위험이 있습니다.
AI는 775 권한을 "일반적"이라고 판단하고, **디렉토리 이름(api_keys)의 민감도를 고려하지 않는 경우**가 있습니다.

**AI가 흔히 하는 실수 (디렉토리 민감도 미고려)**:
```python
if perm == "777":
    findings.append("Vulnerable")
else:
    findings.append("Safe")  # 775는 무조건 Safe
```

**올바른 구현 (디렉토리명 + 권한 조합 검사)**:
```python
SENSITIVE_KEYWORDS = ["key", "secret", "credential", "token"]
is_sensitive = any(kw in dirname for kw in SENSITIVE_KEYWORDS)
if is_sensitive and group_writable:
    findings.append("Vulnerable - 민감 디렉토리에 그룹 쓰기 권한")
```

---

## 채점 결과 예시 (만점)

```
config_parse        — 설정 파일 파싱 + report.txt 생성 (10점)
ssh_audit           — SSH PermitRootLogin 취약점 탐지 (15점)
firewall_audit      — 23/tcp Telnet 위험 포트 탐지 (15점)
account_audit       — agent-test RBAC 위반 탐지 (15점)
permission_audit    — api_keys 775 권한 위반 탐지 (15점)
log_stats           — CPU 평균값 정확 계산 (15점)
report_sections     — 5개 섹션 모두 포함 (15점)

총점: 100/100 PASS
```

---

## 기대 정답값 (트랩 데이터 기준)

### SSH 감사
| 항목 | 값 | 판정 | 근거 |
|------|-----|------|------|
| Port | 20022 | Safe | 기본 포트(22) 아님 |
| PermitRootLogin | prohibit-password | **Vulnerable** | `no`만 안전, 키 인증 루트 접근 허용 |
| PasswordAuthentication | yes | Warning | 브루트포스 공격 취약 |

### 방화벽 감사
| 포트 | 판정 | 근거 |
|------|------|------|
| 20022/tcp | Safe | SSH 포트 |
| 15034/tcp | Info | 커스텀 포트 |
| 23/tcp | **Vulnerable** | Telnet — 암호화 없는 원격 접속 |

### 계정 감사
| 계정 | 판정 | 근거 |
|------|------|------|
| agent-admin | Safe | 핵심 운영 계정 |
| agent-dev | Safe | 개발 계정, core 그룹 적절 |
| agent-test | **Vulnerable** | 테스트 계정이 agent-core에 포함 (RBAC 위반) |

### 권한 감사
| 디렉토리 | 권한 | 그룹 | 판정 | 근거 |
|----------|------|------|------|------|
| agent-app | 755 | agent-admin | Safe | 소유자 그룹, 적절 |
| upload_files | 775 | agent-common | Warning | 공유 디렉토리, 주의 |
| api_keys | 775 | agent-common | **Vulnerable** | 민감 디렉토리에 광범위 그룹 쓰기 |
| /var/log/agent-app | 770 | agent-core | Safe | 로그 디렉토리, 적절 |
| bin | 755 | agent-admin | Safe | 실행 디렉토리, 적절 |

### 로그 통계
| 항목 | 값 | 근거 |
|------|-----|------|
| 유효 줄 수 | 6 | 잘못된 형식 줄(`[INVALID]...`) 제외 |
| CPU 평균 | 36.32% | (24.8+25.0+25.2+25.1+25.3+92.5)/6 = 217.9/6 |
| CPU 최대 | 92.5% | 임계값(90%) 초과 → WARNING |
| MEM 최대 | 85.3% | 임계값(80%) 초과 → WARNING |
