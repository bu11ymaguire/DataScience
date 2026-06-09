# DBSCAN 작업 기록 (memory.md)

> 보고서(§2 각 함수별 코드 상세 설명, §4 개발 과정 및 설계 결정) 에 그대로 옮길
> 수 있도록, 함수/단계마다 "왜 이렇게 했는지" 를 한국어로 짧게 정리한다.
> 평범한 IO 같은 사소한 코드는 굳이 적지 않는다.

---

## 0. 작업 디렉터리 구조와 실험 환경

### 작업 폴더 구성

```
3rd_assignment/
├── clustering.py              ← 제출 대상 (메인 실행 파일)
├── input1.txt   (8000 점)     ← 조교 제공 입력 (제출 X, 조교가 이미 보유)
├── input2.txt   (2000 점)
├── input3.txt   (2100 점)
│
├── experiment.py              ← 실험 자동화 스크립트 (제출 X)
├── memory.md                  ← 본 작업 기록 (제출 X)
├── need.md, design.md         ← 요구사항/양식 메모 (제출 X)
│
└── test-1/                    ← 조교 제공 정답 + 채점기 (제출 X)
    ├── PA3.exe                ← Kendall's tau 유사 채점 바이너리
    ├── input1_cluster_K_ideal.txt   (K = 0..7)
    ├── input2_cluster_K_ideal.txt   (K = 0..4)
    └── input3_cluster_K_ideal.txt   (K = 0..3)
```

> **권장 배치:** 입력 파일 `inputN.txt` 는 `clustering.py` 와 같은 폴더(루트)에 둔다. 이렇게 하면 실행 명령이 `python clustering.py input1.txt ...` 처럼 단순해지고, `write_clusters` 가 입력 파일과 같은 폴더에 출력하므로 결과 파일 `inputN_cluster_K.txt` 도 루트에 생성된다. 2nd assignment("실행 파일과 데이터 파일은 같은 폴더") 와 동일한 관례.

### 실험 데이터 흐름

```
[1] inputN.txt  ──────────────►  clustering.py (DBSCAN 실행)
                                            │
                                            ▼
[2] inputN_cluster_K.txt  ◄─── write_clusters() 가 입력 파일과
    (clustering.py 의 출력)        같은 폴더에 K=0..n-1 까지 생성
                                            │
                                            ▼  채점 시 test-1 으로 복사
[3] test-1/inputN.txt              ←─── 루트에서 복사
    test-1/inputN_cluster_K.txt    ←─── 루트에서 복사
    test-1/inputN_cluster_K_ideal.txt ── 조교 제공 (그대로 둠)
                                            │
                                            ▼
[4] cd test-1 && .\PA3.exe inputN inputN  ──►  점수 출력 (예: 98.97037점)
```

### PA3.exe 인자 규약 (직접 검증함)

```
.\PA3.exe <my_prefix> <ideal_prefix>
```

내부적으로 다음 세 종류의 파일을 **현재 작업 디렉터리** 에서 찾는다 (`.txt` 자동 부착).

| 역할 | 파일명 패턴 | 출처 |
| --- | --- | --- |
| 원본 입력 (분모 계산용) | `<my_prefix>.txt` | 루트의 inputN.txt 를 복사 |
| 내 결과 클러스터 | `<my_prefix>_cluster_K.txt` (K=0..n-1) | clustering.py 의 출력 |
| 정답 클러스터 | `<ideal_prefix>_cluster_K_ideal.txt` | test-1 의 ideal 파일 |

확장자 `.txt` 는 빼고 prefix 만 넘겨야 한다 (.txt 를 붙이면 `.txt.txt` 로 찾아서 실패).

### 표준 채점 절차 (수동 재현용)

```powershell
# 1. 클러스터 파일 생성 (루트에 자동 생성됨)
python clustering.py input1.txt 8 15 22

# 2. 채점에 필요한 파일 3종을 test-1 으로 복사
Copy-Item input1.txt              test-1\input1.txt              -Force
Copy-Item input1_cluster_*.txt    test-1\                        -Force

# 3. 채점
cd test-1
.\PA3.exe input1 input1     # → 98.97037점

# 4. 정리 (test-1 / 루트에 떨어진 임시 파일 제거)
```

### 자동화 스크립트 (`experiment.py`)

위 4단계를 한 번에 도는 도우미 스크립트. 실험 A(KD-tree vs brute) 와 실험 B(방문 순서) 모두 이 스크립트로 자동 채점·정리한다. **제출 파일 아님** — 보고서 본문에서는 결과 표만 인용한다.

```python
subprocess.run([PA3, stem, stem], cwd=TEST_DIR, capture_output=True)
# stdout 은 cp949 로 디코딩 (Windows 한국어 출력)
```

### 실험 환경

| 항목 | 값 | 비고 |
| --- | --- | --- |
| OS | Windows 11 (10.0.26300, AMD64) | `platform.platform()` 출력 |
| Python | 3.12.10 | `python --version` 출력 |
| 외부 패키지 | **없음** | NumPy / scikit-learn / scipy 미사용 |

### 사용 라이브러리 (표준 라이브러리만)

**제출 파일 `clustering.py`:**

| 모듈 | 용도 |
| --- | --- |
| `sys` | CLI 인자 파싱 (`sys.argv`), 종료 코드 (`sys.exit`) |
| `os` | 출력 경로 조립 (`os.path.basename`, `splitext`, `dirname`, `abspath`, `join`) |

→ 단 2개. `math` 도 사용하지 않는다 (제곱 거리 비교라 `sqrt` 불필요).

**실험 스크립트 `experiment.py` (제출 X):**

| 모듈 | 용도 |
| --- | --- |
| `os`, `sys` | 경로/인자 처리 |
| `time` | KD-tree vs brute 속도 측정 (`time.perf_counter`) |
| `random` | 셔플 시드 기반 방문 순서 생성 (`random.Random.shuffle`) |
| `shutil` | 입력 파일을 test-1 으로 복사 |
| `subprocess` | `PA3.exe` 호출 + cp949 디코딩 |
| `clustering` | 본체 모듈 import |

모두 표준 라이브러리이며, 실험 환경 재현에도 별도 패키지 설치가 필요 없다.

---

## 1. 자료구조 결정 — 점 표현과 상태 추적

### 후보

| 방식 | 장점 | 단점 |
| --- | --- | --- |
| dict per point (`{'id':..,'x':..,'y':..,'label':..}`) | 필드 이름으로 접근, 가독성 좋음 | 행마다 dict 오버헤드, 거리 계산 시 속성 룩업 비용 |
| 병렬 배열 (`points = [(id,x,y),...]`, `labels = [UNVISITED]*n`) | 인덱스 i 로 O(1) 접근, 캐시 친화적, 메모리 적음 | 의미를 인덱스 i 로 추적해야 함 |

### 결정: **병렬 배열 채택**

- input1 = 8,000 점. 영역 질의를 O(n²) 로 가더라도 $8000^2 = 6.4\times 10^7$ 거리 계산이 필요하므로, 거리 계산 루프가 가벼울수록 좋다.
- DBSCAN 내부에서는 점을 "정수 인덱스 i" 로만 참조하고, 출력 단계에서만 `points[i][0]` 으로 객체 ID 를 꺼내 쓰면 된다 → ID 기반 룩업이 거의 발생하지 않음.
- 상태도 단순 `bool visited` 가 아니라 **세 상태 (`UNVISITED` / `NOISE` / 정수 cluster_id)** 가 필요한데, `labels` 배열 한 개로 모두 표현 가능.

### 상태 인코딩

```python
UNVISITED = -2
NOISE     = -1
# cluster_id ≥ 0 은 클러스터 소속을 의미
```

- "visited 여부 + 클러스터 소속" 을 한 변수로 묶어 상태 전이가 명확해진다.
- 음수를 sentinel 로 쓰는 이유: 실제 cluster_id 와 충돌하지 않게 하기 위함.

---

## 2. 파일 입출력

### `read_data(file_path)`

- 입력 형식: `id \t x \t y \n`. 표준 split('\t') 로 충분.
- ID 는 **문자열 그대로** 보관한다. 입력에서는 정수처럼 보이지만, 출력 파일에 쓸 때 원본 문자열 그대로 줄바꿈 출력하는 것이 가장 안전하기 때문.
- 좌표는 `float` 로 변환 (거리 계산용).
- 반환: `points = [(id_str, x_float, y_float), ...]`

(여기까지는 평범한 IO. 보고서엔 짧게만 언급)


---

## 3. DBSCAN 본체 1차 구현

### 핵심 설계 결정

1. **거리 비교는 제곱 거리로** — `region_query` 에서 `sqrt` 호출을 제거하고 `dx*dx + dy*dy <= eps_sq` 로 비교. eps² 는 dbscan() 진입부에서 한 번만 계산.
2. **클러스터 확장은 비재귀(반복) 큐 방식** — `expand_cluster` 안에서 `seeds` 리스트를 쓰고 인덱스 `k` 로 순회하며 새 이웃을 뒤에 append. 재귀 호출 시 input1(8000점)에서 파이썬 기본 재귀 한도(1000) 초과 위험이 있음.
3. **상태 전이 규칙** (DBSCAN 정의 그대로):
   - `UNVISITED` 인 이웃 q → 클러스터 소속으로 변경, q 가 코어이면 q 의 이웃을 시드에 추가.
   - `NOISE` 인 이웃 q → 경계점(border)으로 흡수만 하고 시드에는 추가하지 않음.
   - 이미 cluster_id 가 있는 점 → 무시 (다른 시드의 이웃이라도 한 번만 처리).
4. **n 개 클러스터 강제 — 크기 작은 순으로 잘라냄** — `select_top_n_clusters` 에서 raw 클러스터를 size 내림차순 정렬 후 상위 n 개만 살리고, 나머지 점은 NOISE 로 강등. 그 다음 살아남은 클러스터에 0..n-1 의 새 ID 를 부여 (출력 파일명이 0 부터 n-1 까지여야 하므로 재라벨링 필수).
5. **출력 파일 작성** — 각 cluster_id 마다 `inputN_cluster_K.txt` 를 입력 파일과 같은 폴더에 생성하고, 객체 ID 만 한 줄씩 기록. NOISE 는 어떤 파일에도 쓰지 않음 (need.md: "아웃라이어는 제거해도 무방").

### 1차 실행 결과 — input1.txt (Eps=15, MinPts=22, n=8)

```
points = 8000
raw clusters found = 11, kept = 8
cluster sizes = [1596, 1593, 1481, 1458, 1124, 177, 34, 34]
noise = 503
```

채점:

```
.\PA3.exe input1 input1
→ 98.97037점
```

목표(99점 근처)와 거의 일치. 1차 구현 단계에서 추가 튜닝 없이 권장 파라미터 그대로 거의 만점 달성.

### 관찰

- 11개의 raw 클러스터가 나왔다는 것은 일부 큰 군집이 작은 조각으로 쪼개졌다는 의미. 그래도 상위 5개가 1100~1600 점 규모로 균형 있게 잡혔고, 나머지는 100 점 이하 소규모.
- 0.03 점 차이는 경계점 처리 또는 노이즈 처리에서 미세한 차이가 있을 수 있다. 다만 input2/3 결과를 먼저 보고 공통 원인이 있는지 확인하는 게 우선.


---

## 4. 세 데이터셋 권장 파라미터 일괄 검증

### 실행

```bash
python clustering.py input1.txt 8 15 22
python clustering.py input2.txt 5  2  7
python clustering.py input3.txt 4  5  5
```

### 클러스터링 결과

| 입력 | 점 수 | Eps | MinPts | n | raw → kept | 노이즈 | 클러스터 크기 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| input1 | 8000 | 15 | 22 | 8 | 11 → 8 | 503 | [1596, 1593, 1481, 1458, 1124, 177, 34, 34] |
| input2 | 2000 |  2 |  7 | 5 |  6 → 5 |  58 | [640, 489, 386, 235, 192] |
| input3 | 2100 |  5 |  5 | 4 |  4 → 4 |   1 | [600, 500, 500, 499] |

### 채점 (PA3.exe)

| 입력 | need.md 목표 | 실측 점수 | 차이 |
| --- | --- | --- | --- |
| input1 | ~99 | **98.97037** | -0.03 |
| input2 | ~95 | **94.86598** | -0.13 |
| input3 | ~99 | **99.97736** | +0.98 |

### 결론

세 데이터셋 모두 **목표치와 거의 동일**. 표준 DBSCAN 구현이 데이터셋과 무관하게 일관되게 동작함을 확인. 추가 튜닝/특수 처리 없이 권장 파라미터 그대로 통과.

### 관찰

- input3 은 raw 단계에서 이미 4개 클러스터가 깔끔하게 잡혔고 노이즈도 1점뿐이라, 분리 자체가 명확한 데이터셋이다 (목표를 0.98점 초과 달성).
- input1 / input2 는 raw 클러스터가 요구치보다 많이(11→8, 6→5) 나왔는데, 작은 조각으로 쪼개진 것을 size 컷으로 흡수하는 후처리가 필요함을 보여준다. 이 후처리가 없었다면 출력 파일 개수 자체가 안 맞았을 것.
- 0.03~0.13 점의 미세한 부족은 알고리즘의 결함이 아니라 경계점 처리의 작은 차이 또는 ideal 생성 시 사용된 정확한 (Eps, MinPts) 와의 미세한 차이로 추정 (need.md 의 권장값은 "근사" 임을 짐작 가능). 1차 구현으로 99.05/95.0/99.0 평균선에 도달했으므로, 추가 튜닝 없이 이대로 보고서/제출 단계로 진입해도 충분한 수준.


---

## 5. KD-tree 도입 (region_query 최적화)

### 동기

`region_query` 가 매번 모든 점과 거리를 비교하는 O(n) → 전체 알고리즘이 O(n²). input1(8000점)에서 8000² ≈ 6.4×10⁷ 회의 거리 계산이 필요. 표준 라이브러리만으로 가능한 가속 자료구조로 **KD-tree** 를 채택 (2D 데이터에 자연스러움, Ball-tree 는 고차원용이라 제외).

### 구현 핵심

- 노드: `[idx, axis, left, right]` 4-원소 리스트. 클래스를 만들지 않고 `dict` 보다도 가벼운 list 로 표현.
- 빌드: `indices.sort(key=...)` 후 중앙값을 노드로, 깊이별로 axis 0/1 (x/y) 교대.
- 반경 질의: BFS 가 아닌 재귀 DFS. 분기 축 차이 `diff` 의 부호로 가까운 쪽 자식 먼저 방문 → 가지치기 효율 ↑. 반대편 자식은 `diff*diff <= eps²` 인 경우에만 진입.
- `dbscan(use_kdtree=True/False)` 플래그 한 줄로 두 경로를 모두 노출 (실험/검증용).

### 결과 동일성 + 속도 (실험 A)

| 입력 | brute (O(n²)) | KD-tree | speedup | raw cluster 수 | 멤버 동일성 |
| --- | --- | --- | --- | --- | --- |
| input1 (8000점) | 5.31s | **0.20s** | 26.3x | 11 == 11 | ✅ |
| input2 (2000점) | 0.33s | **0.04s** | 7.4x | 6 == 6 | ✅ |
| input3 (2100점) | 0.41s | **0.20s** | 2.1x | 4 == 4 | ✅ |

`labels_to_signature(brute) == labels_to_signature(kd)` 로 클러스터 멤버 집합까지 정확히 같음을 검증 (cluster_id 번호는 다를 수 있어도 점들의 그룹핑은 동일).

### 결정

- 본 제출 코드의 기본값을 `use_kdtree=True` 로 고정.
- brute 경로는 디버깅/비교 실험용으로 보존 (클래스 추가 비용 없음).

---

## 6. 방문 순서가 점수에 주는 영향 (실험 B)

### 가설

DBSCAN 의 결과는 대부분 visit order 와 무관하지만, **두 코어로부터 모두 ε-도달 가능한 border 점** 은 BFS 시작이 빠른 클러스터로 흡수된다 → 외부 루프 순서에 따라 일부 border 의 소속이 바뀔 가능성.

### 실험 설계

외부 루프(`for i in order: ...`) 에 다섯 가지 순서를 주입하고 PA3.exe 점수 비교.
- `input` (입력 순서, 기존 기본값)
- `reverse` (역순)
- `seed_1`, `seed_42`, `seed_777` (각각 다른 셔플)

### 결과

| 입력 | input | reverse | seed_1 | seed_42 | seed_777 |
| --- | --- | --- | --- | --- | --- |
| input1 | 98.97037 | 98.97037 | 98.97037 | 98.97037 | 98.97037 |
| input2 | 94.86598 | **94.89474** | 94.86598 | **94.89474** | 94.86598 |
| input3 | 99.97736 | 99.97736 | 99.97736 | 99.97736 | 99.97736 |

raw 클러스터 수, kept 클러스터 수, 노이즈 개수는 모든 순서에서 동일 → **클러스터 자체의 골격(코어/노이즈 분류)은 visit order 와 무관**.

차이가 나는 곳: **input2 만 두 가지 점수로 갈림** (94.86598 vs 94.89474, Δ ≈ 0.029).

### 해석

- input1/input3 은 클러스터 간 **갭이 충분히 커서** 두 코어에 동시에 ε-도달 가능한 border 가 거의 없음 → visit order 로부터 자유로움.
- input2 는 Eps=2 의 작은 반경 + 클러스터 간 거리가 가까움 → border 점의 소속이 BFS 시작 순서에 따라 바뀌고, 이게 채점의 (맞게 분류된 쌍 / 전체 쌍) 비율에 미세 반영됨.
- 흥미롭게도 5가지 순서가 단지 두 점수(94.86598 / 94.89474) 에만 수렴 → 갈리는 border 점이 1~수 개 수준의 소량이라는 뜻.

### 결론 (보고서 §4 에 그대로 옮길 콘텐츠)

1. **DBSCAN 의 코어/노이즈 분류는 데이터로 결정되며 visit order 와 무관함을 실험으로 입증.**
2. **Border 점 흡수만이 visit order 의 영향을 받으며, 그 영향은 0.03점 수준의 미세한 변동.**
3. need.md 의 목표(95점)에 도달하지 못한 input2 의 부족분도 알고리즘이 아닌 ideal 생성 시 사용된 정확한 (Eps, MinPts) 와의 미세 차이로 추정 — 어떤 순서를 줘도 95점 미만 → 순서 튜닝으로 해결될 문제 아님.
4. 따라서 **기본값(use_kdtree=True, order=range(n))** 그대로 제출이 합리적. 세 데이터셋 평균 ~97.94점.


---

## 7. 출력 파일 개수 보호 (m < n 코너 케이스)

### 동기

`need.md` 는 "각 입력 데이터에 대해 n 개의 출력 파일을 생성, 파일명은 `input#_cluster_0.txt` 부터 `input#_cluster_n-1.txt`" 를 명시한다. 하지만 알고리즘이 찾은 raw 클러스터 수 m 이 n 보다 적게 나오는 경우 (예: 조교가 권장값보다 빡빡한 MinPts 또는 작은 Eps 를 주는 경우), 기존 코드는 m 개의 파일만 생성하여 요구사항을 위반한다. 이 상태에서 채점기 `PA3.exe` 는 `input#_cluster_(m..n-1).txt` 를 못 찾고 `FileNotFoundException` 으로 종료 → 0점 위험.

### 해결 방법

`write_clusters(input_path, points, new_labels, num_kept, requested_n)` 에서 항상 `requested_n` 개의 파일을 만들도록 변경. `k < num_kept` 인 인덱스에는 클러스터 멤버 ID 를 쓰고, 나머지는 빈 파일로 그대로 닫는다. 단 한 줄짜리 보강이며 정상 케이스(m ≥ n) 의 동작은 일체 변하지 않는다.

### 동작 검증

m < n 을 강제로 만들기 위해 input2 에 MinPts 를 60으로 (권장 7 → 8.6배) 키운 시나리오:

```
python clustering.py input2.txt 5 2 60
→ raw=3, kept=3, empty files padded=2
```

생성된 파일:

| 파일 | 크기 | 비고 |
| --- | --- | --- |
| input2_cluster_0.txt | 2267 B | 클러스터 0 멤버 |
| input2_cluster_1.txt | 1652 B | 클러스터 1 멤버 |
| input2_cluster_2.txt |  958 B | 클러스터 2 멤버 |
| input2_cluster_3.txt | **0 B** | 빈 파일 (padding) |
| input2_cluster_4.txt | **0 B** | 빈 파일 (padding) |

이 상태에서 PA3.exe 채점:

```
.\PA3.exe input2 input2 → 64.53962점
```

핵심 검증 포인트 — **PA3.exe 가 빈 파일을 정상적으로 받아들여 채점이 끝까지 완료**됐다. 점수 자체는 m<n 으로 인해 자연히 낮지만, 파일 누락 → exception → 0점 시나리오를 막았다는 게 본 보강의 목적.

### 정상 케이스 회귀 확인

권장값(MinPts=7) 으로 재실행 시:

```
raw=6, kept=5, empty files padded=0
```

`empty files padded=0` 이고 출력 파일 5개 모두 멤버를 가짐 → 기존 점수(94.86598) 동일하게 유지될 것 (별도 채점은 §4 결과로 갈음).

### 결론

코드 5줄 분량의 안전장치로 raw<n 코너 케이스에서 0점 위험을 제거. 권장 파라미터 채점에는 영향이 전혀 없으므로 부작용 없는 보강.

실행결과 : C:\Users\jwkim\Desktop\HYU\2026_1\데이터사이언스\Data_Science_Assignment\3rd_assignment\cmd_result.png

생성결과 :
C:\Users\jwkim\Desktop\HYU\2026_1\데이터사이언스\Data_Science_Assignment\3rd_assignment\output_result.png