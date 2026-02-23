# 리눅스 시스템 보안 설정 - 모범 답안

## 1. SSH 보안 설정 (30점)

```bash
# sshd_config 수정
sudo vim /etc/ssh/sshd_config

# 다음 내용 변경/추가
Port 20022
PermitRootLogin no

# SSH 서비스 재시작
sudo systemctl restart sshd
# 또는
sudo service sshd restart
```

**검증 방법**:
```bash
# 포트 확인
sudo netstat -tulnp | grep sshd
# 또는
sudo ss -tulnp | grep sshd

# 설정 파일 확인
grep "^Port" /etc/ssh/sshd_config
grep "^PermitRootLogin" /etc/ssh/sshd_config
```

---

## 2. 방화벽 설정 (20점)

```bash
# UFW 활성화
sudo ufw enable

# 포트 허용
sudo ufw allow 20022/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 상태 확인
sudo ufw status
```

**예상 출력**:
```
Status: active

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## 3. 계정 관리 (20점)

```bash
# 그룹 생성
sudo groupadd agent-common

# 계정 생성 (홈 디렉토리 자동 생성 + 기본 쉘 설정)
sudo useradd -m -G agent-common -s /bin/bash agent-admin
sudo useradd -m -G agent-common -s /bin/bash agent-dev

# 패스워드 설정 (선택)
sudo passwd agent-admin
sudo passwd agent-dev
```

**검증 방법**:
```bash
# 계정 존재 확인
id agent-admin
id agent-dev

# 그룹 소속 확인
groups agent-admin
groups agent-dev

# 또는
grep agent-common /etc/group
```

---

## 4. 관제 스크립트 (30점)

`/opt/monitor.sh` 파일 생성:

```bash
#!/bin/bash

# 프로세스 수
PROCESS_COUNT=$(ps aux | wc -l)
echo "[PROCESS] Total: $PROCESS_COUNT"

# SSH 포트 리스닝 확인
if ss -tuln | grep -q ":20022"; then
    echo "[PORT] SSH(20022): LISTENING"
else
    echo "[PORT] SSH(20022): NOT LISTENING"
fi

# 디스크 사용량
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
echo "[DISK] Usage: $DISK_USAGE"

# 메모리 사용량
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f%%", $3/$2 * 100}')
echo "[MEMORY] Usage: $MEMORY_USAGE"
```

**스크립트 생성 및 권한 설정**:
```bash
# 파일 생성
sudo vi /opt/monitor.sh
# (위 내용 복사)

# 실행 권한 부여 (755)
sudo chmod 755 /opt/monitor.sh

# 권한 확인
ls -l /opt/monitor.sh
# 출력: -rwxr-xr-x 1 root root ... /opt/monitor.sh
```

**테스트 실행**:
```bash
sudo /opt/monitor.sh
```

---

## 전체 검증 체크리스트

### SSH 설정
- [x] `grep "^Port 20022" /etc/ssh/sshd_config` → Port 20022
- [x] `grep "^PermitRootLogin no" /etc/ssh/sshd_config` → PermitRootLogin no

### 방화벽
- [x] `sudo ufw status` → Status: active
- [x] 20022/tcp ALLOW 확인
- [x] 80/tcp ALLOW 확인
- [x] 443/tcp ALLOW 확인

### 계정
- [x] `id agent-admin` → 계정 정보 출력
- [x] `id agent-dev` → 계정 정보 출력
- [x] `groups agent-admin | grep agent-common` → agent-common 포함
- [x] `groups agent-dev | grep agent-common` → agent-common 포함

### 스크립트
- [x] `ls -l /opt/monitor.sh` → 파일 존재
- [x] `ls -l /opt/monitor.sh | grep "rwxr-xr-x"` → 755 권한

---

## AI 함정 요소 주의

### 함정 1: PermitRootLogin prohibit-password
❌ **잘못된 설정**:
```
PermitRootLogin prohibit-password
```

✅ **올바른 설정**:
```
PermitRootLogin no
```

### 함정 2: 스크립트 권한 644
❌ **잘못된 권한** (실행 불가):
```bash
chmod 644 /opt/monitor.sh  # rw-r--r--
```

✅ **올바른 권한**:
```bash
chmod 755 /opt/monitor.sh  # rwxr-xr-x
```

### 함정 3: 포트 번호 오타
❌ **잘못된 포트**:
- 22022 (숫자 하나 더)
- 2022 (숫자 하나 덜)

✅ **올바른 포트**:
- 20022

---

## 전체 스크립트 (한 번에 실행)

```bash
#!/bin/bash

# SSH 설정
sudo sed -i 's/^#\?Port.*/Port 20022/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 방화벽 설정
sudo ufw --force enable
sudo ufw allow 20022/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 계정 관리
sudo groupadd agent-common 2>/dev/null
sudo useradd -m -G agent-common -s /bin/bash agent-admin 2>/dev/null
sudo useradd -m -G agent-common -s /bin/bash agent-dev 2>/dev/null

# 스크립트 생성
sudo cat > /opt/monitor.sh << 'EOF'
#!/bin/bash
PROCESS_COUNT=$(ps aux | wc -l)
echo "[PROCESS] Total: $PROCESS_COUNT"
if ss -tuln | grep -q ":20022"; then
    echo "[PORT] SSH(20022): LISTENING"
else
    echo "[PORT] SSH(20022): NOT LISTENING"
fi
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
echo "[DISK] Usage: $DISK_USAGE"
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f%%", $3/$2 * 100}')
echo "[MEMORY] Usage: $MEMORY_USAGE"
EOF

# 실행 권한 부여
sudo chmod 755 /opt/monitor.sh

echo "설정 완료!"
```

---

## 최종 점검

모든 설정이 완료되면 다음 명령으로 확인하세요:

```bash
# 종합 확인 스크립트
echo "=== SSH 설정 ==="
grep "^Port" /etc/ssh/sshd_config
grep "^PermitRootLogin" /etc/ssh/sshd_config

echo ""
echo "=== 방화벽 ==="
sudo ufw status

echo ""
echo "=== 계정 ==="
id agent-admin
id agent-dev
groups agent-admin
groups agent-dev

echo ""
echo "=== 스크립트 ==="
ls -l /opt/monitor.sh
```

**예상 점수**: 100점 (모든 항목 통과)
