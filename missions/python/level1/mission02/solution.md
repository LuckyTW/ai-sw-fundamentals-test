## 문항 2 정답지

### 정답 코드

모범 답안은 `sample_submission_python02/` 디렉토리에 위치합니다:
- `sample_submission_python02/log_analyzer.py` — CSV 파싱 + 분석 + 리포트 생성

### 핵심 구현 포인트

1. **빈 IP 제외**: `ip.strip()` 후 빈 문자열은 IP 집계에서 제외, 다른 분석에는 포함
2. **동점 IP 내림차순**: `sorted(items, key=lambda x: (x[1], x[0]), reverse=True)`
3. **1xx 상태코드 포함**: 1xx~5xx 모든 그룹을 분류하고 출력
4. **소수점 응답시간**: `float(r["response_time_ms"])`로 파싱 (int가 아닌 float)

### 정답 체크리스트

| 번호 | 체크 항목 | 배점 | 검증 방법 | AI 트랩 |
|------|----------|------|----------|---------|
| 1 | CSV 파싱 + report.txt 생성 | 15 | subprocess | - |
| 2 | IP TOP 5 값 정확 | 15 | 문자열 매칭 | - |
| 3 | 동점 IP 내림차순 정렬 | 8 | 위치 비교 | **Yes** |
| 4 | 상태코드 그룹별 비율 (1xx 포함) | 10 | 라인 매칭 | **Yes** |
| 5 | 느린 엔드포인트 TOP 3 순서 | 20 | 위치 비교 | - |
| 6 | 리포트 3개 섹션 포함 | 25 | 키워드 검색 | - |
| 7 | 엔드포인트 평균시간 수치 정확 | 7 | 문자열 매칭 | **Yes** |

- Pass 기준: 총 100점 중 70점 이상

### AI 트랩 해설 (3개)

#### 트랩 1: 동점 IP 내림차순 정렬 (ip_order, 8점)

접근 횟수가 같은 IP가 여러 개 있을 때, IP 주소도 내림차순으로 정렬해야 합니다.

**❌ AI가 흔히 하는 실수 (횟수만 정렬)**:
```python
sorted_ips = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)
# 동점 IP 순서가 불확실 (오름차순 기본값)
```

**✅ 올바른 구현 (복합 정렬)**:
```python
sorted_ips = sorted(ip_count.items(), key=lambda x: (x[1], x[0]), reverse=True)
# 횟수 내림차순 + IP 내림차순
```

#### 트랩 2: 1xx 상태코드 미출력 (status_ratio, 10점)

채점용 CSV에 `100` 상태코드가 포함되어 있습니다. 샘플 CSV에는 1xx가 없으므로 AI가 1xx 분류를 생략할 수 있습니다.

**❌ AI가 흔히 하는 실수 (2xx~5xx만 처리)**:
```python
if 200 <= code < 300: groups["2xx"] += 1
elif 300 <= code < 400: groups["3xx"] += 1
# 1xx가 누락되어 리포트에 1xx 비율이 출력되지 않음
```

**✅ 올바른 구현 (1xx 포함)**:
```python
if 100 <= code < 200: groups["1xx"] += 1
elif 200 <= code < 300: groups["2xx"] += 1
# 1xx를 포함하여 모든 그룹 출력
```

#### 트랩 3: 소수점 response_time (slow_values, 7점)

채점용 CSV에 `33.7`처럼 소수점 응답시간이 포함되어 있습니다.

**❌ AI가 흔히 하는 실수 (int 변환)**:
```python
response_time = int(r["response_time_ms"])  # 33.7 → ValueError 또는 33
```

**✅ 올바른 구현 (float 변환)**:
```python
response_time = float(r["response_time_ms"])  # 33.7 → 33.7 정확 처리
```

### AI 트랩 점수 시뮬레이션

| 시나리오 | 감점 | 총점 | 결과 |
|---------|------|------|------|
| 트랩 3개 모두 걸림 | -25 | 75점 | **Pass** |
| 트랩 2개 걸림 | -13~18 | 82~87점 | Pass |
| 트랩 1개 걸림 | -7~10 | 90~93점 | Pass |
| 트랩 0개 | 0 | 100점 | Pass |

### 기대 정답값 (채점용 CSV 24행 기준)

#### IP 접근 횟수 TOP 5
| 순위 | IP | 횟수 |
|------|-----|------|
| 1 | 192.168.1.1 | 6 |
| 2 | 10.0.0.5 | 6 |
| 3 | 172.16.0.10 | 5 |
| 4 | 192.168.2.20 | 3 |
| 5 | 10.0.0.99 | 3 |

#### 상태코드 비율
| 그룹 | 비율 |
|------|------|
| 1xx | 4.2% |
| 2xx | 70.8% |
| 3xx | 4.2% |
| 4xx | 8.3% |
| 5xx | 12.5% |

#### 느린 엔드포인트 TOP 3
| 순위 | 엔드포인트 | 평균 응답시간 |
|------|-----------|-------------|
| 1 | /api/orders | 2488.8ms |
| 2 | /api/products | 502.4ms |
| 3 | /api/users | 31.5ms |
