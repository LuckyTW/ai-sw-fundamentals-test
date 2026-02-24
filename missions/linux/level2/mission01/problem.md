# 리눅스 서버 보안 감사 도구 코딩 시험

## 시험 개요

- **시간**: 25분
- **합격 기준**: 100점 만점 중 70점 이상
- **제출물**: 1개의 Python 파일 (`auditor.py`)

리눅스 서버 설정 파일 스냅샷 6개를 분석하여 보안 취약점을 탐지하고,
감사 리포트를 생성하는 프로그램을 작성합니다.

SSH 보안, 방화벽 규칙, 계정/그룹 RBAC, 파일 권한, 시스템 모니터링 로그 분석 능력을 측정합니다.

---

## CLI 인터페이스

`argparse`를 사용하여 다음 인자를 받으세요:

```bash
python auditor.py --config-dir <설정파일디렉토리> --output <리포트출력경로>
```

| 인자 | 설명 |
|------|------|
| `--config-dir` | 6개 설정 파일이 있는 디렉토리 경로 |
| `--output` | 출력 리포트 파일 경로 |

---

## 입력 파일 (6개)

`--config-dir` 디렉토리에 다음 6개 파일이 존재합니다:

### 1. `sshd_config` — SSH 서버 설정

```
Port 20022
PermitRootLogin prohibit-password
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers agent-admin agent-dev
```

> **주의**: `PermitRootLogin`의 각 설정값(`yes`, `no`, `prohibit-password`, `without-password`, `forced-commands-only`)이 의미하는 보안 수준을 정확히 이해하세요. 단순히 "password 아닌 것은 안전"이라고 판단하지 마세요.

### 2. `ufw_status.txt` — 방화벽 규칙

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW IN    Anywhere
15034/tcp                  ALLOW IN    Anywhere
23/tcp                     ALLOW IN    Anywhere
20022/tcp (v6)             ALLOW IN    Anywhere (v6)
15034/tcp (v6)             ALLOW IN    Anywhere (v6)
23/tcp (v6)                ALLOW IN    Anywhere (v6)
```

> **주의**: IANA well-known 위험 포트가 허용되어 있지 않은지 확인하세요. 암호화되지 않은 원격 접속 프로토콜은 보안 위험입니다.

### 3. `accounts.csv` — 사용자 계정 정보

| 컬럼 | 설명 | 예시 |
|------|------|------|
| `username` | 사용자명 | `agent-admin` |
| `uid` | 사용자 ID | `1001` |
| `groups` | 소속 그룹 (`;`로 구분) | `agent-common;agent-core` |
| `home` | 홈 디렉토리 | `/home/agent-admin` |
| `shell` | 로그인 셸 | `/bin/bash` |

> **주의**: 최소 권한 원칙(Principle of Least Privilege)에 따라, 각 계정의 그룹 소속이 적절한지 판단하세요. 테스트/개발 계정이 핵심 운영 그룹에 포함되어 있으면 RBAC 위반입니다.

### 4. `directories.csv` — 디렉토리 권한 정보

| 컬럼 | 설명 | 예시 |
|------|------|------|
| `path` | 디렉토리 경로 | `/home/agent-admin/agent-app` |
| `owner` | 소유자 | `agent-admin` |
| `group` | 소속 그룹 | `agent-admin` |
| `octal_permission` | 8진수 권한 | `755` |

> **주의**: 민감 데이터가 저장되는 디렉토리에 광범위 그룹 쓰기 권한이 부여되어 있지 않은지 확인하세요. 디렉토리 이름과 그룹 범위를 함께 고려하여 판단해야 합니다.

### 5. `monitor.log` — 시스템 모니터링 로그

```
[2025-12-24 09:56:01] PID:48291 CPU:24.8% MEM:5.1% DISK:45G
```

- 각 줄은 `[timestamp] PID:xxx CPU:xx.x% MEM:xx.x% DISK:xxG` 형식입니다
- **잘못된 형식의 줄이 포함될 수 있습니다** — 올바른 형식이 아닌 줄은 건너뛰세요
- CPU/MEM 임계값: CPU 90% 초과 또는 MEM 80% 초과 시 WARNING 표시

### 6. `crontab.txt` — 예약 작업 목록

표준 crontab 형식입니다. 등록된 작업의 개수와 내용을 리포트에 포함하세요.

---

## 보안 판단 기준

### SSH 보안
- Port: 기본 포트(22)가 아닌 다른 포트 → Safe
- `PermitRootLogin`: **`no`만 안전**. 그 외의 값은 보안 위험
- `PasswordAuthentication yes`: 브루트포스 공격에 취약

### 방화벽
- 기본 정책: deny (incoming) → Safe
- 허용된 포트 중 well-known 위험 포트 확인 (Telnet, FTP 등)

### 계정/그룹 (RBAC)
- 최소 권한 원칙: 각 계정은 필요한 그룹에만 소속
- 테스트/임시 계정이 핵심 운영 그룹에 포함되면 위반

### 파일 권한
- 민감 디렉토리 (키, 인증 관련): 소유자만 접근 (700 또는 750)
- 일반 공유 디렉토리: 775 허용 가능

### 모니터링 로그
- 잘못된 형식의 줄은 제외하고 통계 계산
- CPU 평균, 최대값, MEM 최대값 등 기본 통계
- 임계값 초과 시 WARNING

---

## 출력 형식 (report.txt)

5개 섹션으로 구성된 리포트를 생성하세요:

```
=== SSH Security Audit ===
Port: 20022 (Safe - 기본 포트 아님)
PermitRootLogin: prohibit-password (Vulnerable - ...)
...

=== Firewall Audit ===
Default Policy: deny incoming (Safe)
Allowed Ports:
  - 20022/tcp (Safe)
  - 15034/tcp (Info)
  - 23/tcp (Vulnerable - ...)
...

=== Account Audit ===
...

=== Permission Audit ===
...

=== Log Analysis ===
Total Valid Lines: 6
CPU Average: 36.32%
CPU Max: 92.5% [WARNING]
MEM Max: 85.3% [WARNING]
...
```

> 위 수치는 예시입니다. 실제 채점 시 동일 데이터로 검증됩니다.

---

## 채점 기준

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | 설정 파일 파싱 | 10점 | 6개 파일 정상 파싱 + report.txt 생성 |
| 2 | SSH 감사 | 15점 | PermitRootLogin 취약점 정확 탐지 |
| 3 | 방화벽 감사 | 15점 | 위험 포트(23/tcp) 탐지 |
| 4 | 계정 감사 | 15점 | RBAC 위반 탐지 |
| 5 | 권한 감사 | 15점 | 민감 디렉토리 권한 위반 탐지 |
| 6 | 로그 통계 | 15점 | CPU 평균값 정확 계산 |
| 7 | 리포트 섹션 | 15점 | 5개 섹션 중 4개 이상 포함 |
| | **합계** | **100점** | |

---

## 제출 및 채점

```bash
# 채점 실행
python3 scripts/run_grading.py \
  --student-id <학생ID> \
  --mission-id linux_level2_mission01 \
  --submission-dir /path/to/your/submission
```

---

**제출 기한**: 25분
**참고**: AI 어시스턴트를 활용할 수 있지만, 각 설정값의 보안 의미와 최소 권한 원칙을 반드시 직접 검증하세요.
