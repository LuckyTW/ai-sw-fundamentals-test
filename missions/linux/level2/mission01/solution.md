## 문항 3 정답지

### 정답 코드

모범 답안은 `sample_submission_linux/` 디렉토리에 위치합니다:
- `sample_submission_linux/auditor.py` — 설정 파일 파싱 + 보안 감사 + 리포트 생성

### 핵심 구현 포인트

1. **PermitRootLogin 판정**: `no`만 안전, `prohibit-password`/`yes` 등은 모두 취약
2. **위험 포트 탐지**: 23/tcp(Telnet), 21/tcp(FTP) 등 well-known 위험 포트 분류
3. **RBAC 검증**: 테스트 계정(`agent-test`)이 핵심 그룹(`agent-core`)에 포함 → 위반
4. **민감 디렉토리 권한**: `api_keys` + 775 + 광범위 그룹 → 취약

### 정답 체크리스트

| 번호 | 체크 항목 | 배점 | 검증 방법 | AI 트랩 |
|------|----------|------|----------|---------|
| 1 | 설정 파일 파싱 + report.txt 생성 | 10 | subprocess | - |
| 2 | SSH PermitRootLogin 취약점 탐지 | 15 | 라인 매칭 | **Yes** |
| 3 | 23/tcp Telnet 위험 포트 탐지 | 15 | 라인 매칭 | **Yes** |
| 4 | agent-test RBAC 위반 탐지 | 15 | 라인 매칭 | **Yes** |
| 5 | api_keys 775 권한 위반 탐지 | 15 | 라인 매칭 | **Yes** |
| 6 | CPU 평균값 정확 계산 | 15 | 수치 매칭 | - |
| 7 | 리포트 5개 섹션 포함 (4개 이상) | 15 | 키워드 검색 | - |

- Pass 기준: 총 100점 중 70점 이상

### AI 트랩 해설 (4개)

#### 트랩 1: PermitRootLogin prohibit-password (ssh_audit, 15점)

`PermitRootLogin prohibit-password`는 패스워드 인증만 차단하고 **SSH 키 인증으로 루트 로그인을 허용**합니다.

**❌ AI가 흔히 하는 실수 (안전으로 판정)**:
```python
if root_login != "yes":
    return "Safe"  # prohibit-password도 Safe로 판정
```

**✅ 올바른 구현 (no만 안전)**:
```python
if root_login == "no":
    return "Safe"
else:
    return "Vulnerable"  # prohibit-password, yes 등 모두 취약
```

#### 트랩 2: 23/tcp Telnet 포트 (firewall_audit, 15점)

방화벽에 23번 포트(Telnet)가 ALLOW로 설정되어 있습니다. Telnet은 암호화 없이 데이터를 전송하므로 보안 위험입니다.

**❌ AI가 흔히 하는 실수 (위험 포트 미분류)**:
```python
for rule in rules:
    findings.append(f"{rule['port']} - ALLOW")  # 모든 포트를 동일하게 처리
```

**✅ 올바른 구현 (well-known 위험 포트 분류)**:
```python
DANGEROUS_PORTS = {"21": "FTP", "23": "Telnet", "69": "TFTP"}
if port_num in DANGEROUS_PORTS:
    findings.append(f"{port} (Vulnerable - {DANGEROUS_PORTS[port_num]})")
```

#### 트랩 3: agent-test의 agent-core 그룹 (account_audit, 15점)

`agent-test`(테스트 계정)가 `agent-core`(핵심 운영 그룹)에 포함되어 있습니다. 최소 권한 원칙에 따라 테스트 계정은 핵심 그룹에 포함되어서는 안 됩니다.

**❌ AI가 흔히 하는 실수 (그룹 소속 일괄 통과)**:
```python
for acc in accounts:
    findings.append(f"{acc['username']}: Safe")  # 그룹 검증 없이 통과
```

**✅ 올바른 구현 (RBAC 검증)**:
```python
expected_core_users = {"agent-admin", "agent-dev"}
if "agent-core" in groups and username not in expected_core_users:
    findings.append(f"{username}: Vulnerable - RBAC 위반")
```

#### 트랩 4: api_keys 775+agent-common (permission_audit, 15점)

`api_keys` 디렉토리에 `agent-common` 그룹 + 775 권한이 설정되어 있습니다. 민감 데이터(API 키)가 저장되는 디렉토리에 광범위 그룹의 쓰기 권한을 부여하면 데이터 유출 위험이 있습니다.

**❌ AI가 흔히 하는 실수 (디렉토리 민감도 미고려)**:
```python
if perm == "777":
    findings.append("Vulnerable")
else:
    findings.append("Safe")  # 775는 무조건 Safe
```

**✅ 올바른 구현 (디렉토리명 + 권한 조합 검사)**:
```python
SENSITIVE_KEYWORDS = ["key", "secret", "credential", "token"]
is_sensitive = any(kw in dirname for kw in SENSITIVE_KEYWORDS)
if is_sensitive and group_writable:
    findings.append("Vulnerable - 민감 디렉토리에 그룹 쓰기 권한")
```

### AI 트랩 점수 시뮬레이션

| 시나리오 | 감점 | 총점 | 결과 |
|---------|------|------|------|
| 트랩 4개 모두 걸림 | -60 | 40점 | **Fail** |
| 트랩 3개 걸림 | -45 | 55점 | Fail |
| 트랩 2개 걸림 | -30 | 70점 | **Pass** |
| 트랩 1개 걸림 | -15 | 85점 | Pass |
| 트랩 0개 | 0 | 100점 | Pass |

### 기대 정답값 (트랩 데이터 기준)

#### SSH 감사
| 항목 | 값 | 판정 | 근거 |
|------|-----|------|------|
| Port | 20022 | Safe | 기본 포트(22) 아님 |
| PermitRootLogin | prohibit-password | **Vulnerable** | `no`만 안전, 키 인증 루트 접근 허용 |
| PasswordAuthentication | yes | Warning | 브루트포스 공격 취약 |

#### 방화벽 감사
| 포트 | 판정 | 근거 |
|------|------|------|
| 20022/tcp | Safe | SSH 포트 |
| 15034/tcp | Info | 커스텀 포트 |
| 23/tcp | **Vulnerable** | Telnet — 암호화 없는 원격 접속 |

#### 계정 감사
| 계정 | 판정 | 근거 |
|------|------|------|
| agent-admin | Safe | 핵심 운영 계정 |
| agent-dev | Safe | 개발 계정, core 그룹 적절 |
| agent-test | **Vulnerable** | 테스트 계정이 agent-core에 포함 (RBAC 위반) |

#### 권한 감사
| 디렉토리 | 권한 | 그룹 | 판정 | 근거 |
|----------|------|------|------|------|
| agent-app | 755 | agent-admin | Safe | 소유자 그룹, 적절 |
| upload_files | 775 | agent-common | Warning | 공유 디렉토리, 그룹 쓰기 권한 |
| api_keys | 775 | agent-common | **Vulnerable** | 민감 디렉토리에 광범위 그룹 쓰기 |
| /var/log/agent-app | 770 | agent-core | Warning | 그룹(agent-core) 쓰기 권한 |
| bin | 755 | agent-admin | Safe | 실행 디렉토리, 적절 |

#### 로그 통계
| 항목 | 값 | 근거 |
|------|-----|------|
| 유효 줄 수 | 6 | 잘못된 형식 줄(`[INVALID]...`) 제외 |
| CPU 평균 | 36.32% | (24.8+25.0+25.2+25.1+25.3+92.5)/6 = 217.9/6 |
| CPU 최대 | 92.5% | 임계값(90%) 초과 → WARNING |
| MEM 최대 | 85.3% | 임계값(80%) 초과 → WARNING |
