# apriori.py 함수별 세부 로직 설명

## 1. `explain_input_parsing(input_file)`

### 목적
입력 텍스트 파일(`input.txt`)을 읽어 트랜잭션 리스트로 변환한다.

### 입력 / 출력
- **입력**: `input_file` (str) — 텍스트 파일 경로
- **출력**: `transactions` (list of set) — 각 트랜잭션을 `set`으로 변환한 리스트. 파일이 없으면 `None` 반환

### 세부 로직
1. 빈 리스트 `transactions = []`를 준비한다.
2. 파일을 한 줄씩 읽으며 `line.strip().split()`으로 공백 기준 분리한다.
3. 빈 줄은 `continue`로 건너뛴다.
4. 각 줄의 아이템 문자열들을 `int`로 변환하고, **`set()`으로 묶어서** 하나의 트랜잭션으로 저장한다.
   - `set`을 사용하는 이유: 이후 `issubset()` 연산으로 후보 집합이 트랜잭션에 포함되는지 빠르게 검사하기 위함.
5. `FileNotFoundError` 발생 시 `None`을 반환한다.

### 자료구조
| 변수 | 타입 | 설명 |
|---|---|---|
| `transactions` | `list[set[int]]` | 전체 트랜잭션 목록 |
| `transaction` | `set[int]` | 개별 트랜잭션 (예: `{1, 3, 5}`) |

---

## 2. `get_frequent_1_itemsets(transactions, min_sup_percent)`

### 목적
길이가 1인 빈발 항목 집합($L_1$)을 생성한다.

### 입력 / 출력
- **입력**: `transactions` (list of set), `min_sup_percent` (float, 퍼센트 단위)
- **출력**: `L1` (dict) — `{frozenset: 등장횟수}` 형태의 딕셔너리

### 세부 로직
1. 전체 트랜잭션 수 `n_transactions`와 최소 등장 횟수 `min_count`를 계산한다.
   - `min_count = n_transactions * (min_sup_percent / 100.0)`
2. 모든 트랜잭션을 순회하며 각 아이템의 등장 횟수를 `item_counts` 딕셔너리에 기록한다.
3. `sorted(item_counts.items())`로 아이템을 오름차순 정렬한 뒤, `min_count` 이상인 아이템만 골라낸다.
4. 합격한 아이템은 **`frozenset({item})`으로 감싸서** `L1` 딕셔너리의 키로 저장하고, 값은 등장 횟수로 한다.

### `frozenset` 사용 이유
- 파이썬의 일반 `set`은 변경 가능(mutable)하여 딕셔너리의 **키(Key)로 사용할 수 없다.**
- `frozenset`은 변경 불가능(immutable)하므로 딕셔너리 키로 사용이 가능하다.
- 이후 `apriori_gen`에서 합집합 연산(`|`)을 할 때, `frozenset | frozenset`의 결과도 자동으로 `frozenset`이 되어 타입이 일관성 있게 유지된다.

### 자료구조
| 변수 | 타입 | 설명 |
|---|---|---|
| `item_counts` | `dict[int, int]` | 개별 아이템 → 등장 횟수 |
| `L1` | `dict[frozenset, int]` | 빈발 1-아이템셋 → 등장 횟수 |

---

## 3. `apriori_gen(L_prev, k)`

### 목적
이전 단계의 빈발 항목 집합 리스트($L_{k-1}$)로부터 길이가 $k$인 후보 집합($C_k$)을 생성한다.

### 입력 / 출력
- **입력**: `L_prev` (list of frozenset) — 이전 단계의 빈발 항목 집합 키 리스트, `k` (int) — 목표 길이
- **출력**: `Ck` (list of frozenset) — 후보 집합 리스트

### 세부 로직 (최적화된 Join Step)
1. `L_prev`의 모든 원소 쌍 `(i, j)`에 대해 이중 루프를 수행한다 (`j > i`).
2. 각 `frozenset`을 `list`로 변환하고 **오름차순 정렬**한다.
3. **앞쪽 `k-2`개 원소가 동일한 경우에만** 합집합 연산(`|`)을 수행한다.
   - 이 조건이 Apriori 알고리즘의 핵심 최적화 기법이다.
   - 길이 $k-1$인 두 집합을 합쳤을 때, 앞의 $k-2$개가 같고 마지막 1개만 다르면, 합집합의 길이가 정확히 $k$가 됨이 보장된다.
   - 예: $k=3$일 때, `[1,2]`와 `[1,3]`은 앞의 1개(`k-2=1`)가 같으므로 합쳐서 `{1,2,3}` 생성.
   - 반면 `[1,2]`와 `[3,4]`는 앞이 다르므로 건너뛴다 (합치면 길이 4가 되어 의미 없음).
4. 중복 후보가 없도록 `candidate not in Ck` 조건으로 필터링한 뒤 리스트에 추가한다.

### `k-2` 슬라이싱의 수학적 근거
- `L_prev` 원소의 길이 = $k-1$
- 마지막 1개만 달라야 하므로, 비교 대상 = 앞의 $(k-1) - 1 = k-2$개

### 자료구조
| 변수 | 타입 | 설명 |
|---|---|---|
| `L_prev` | `list[frozenset]` | 이전 단계 빈발 집합의 키 리스트 |
| `Ck` | `list[frozenset]` | 새로 생성된 후보 집합 리스트 |
| `list_i`, `list_j` | `list[int]` | 비교를 위해 정렬된 임시 리스트 |

---

## 4. `get_frequent_k_itemsets(transactions, min_sup_percent, Ck)`

### 목적
후보 집합($C_k$)의 각 원소가 전체 트랜잭션에서 몇 번 등장하는지 세고, 최소 지지도를 넘는 것만 골라서 $L_k$를 만든다.

### 입력 / 출력
- **입력**: `transactions` (list of set), `min_sup_percent` (float), `Ck` (list of frozenset)
- **출력**: `Lk` (dict) — `{frozenset: 등장횟수}` 형태의 딕셔너리

### 세부 로직
1. `min_count`를 계산한다 (전체 트랜잭션 수 × 최소지지도/100).
2. 딕셔너리 컴프리헨션으로 `{candidate: 0 for candidate in Ck}`를 만들어 카운터를 초기화한다.
3. 모든 트랜잭션을 순회하며, 각 후보에 대해 **`candidate.issubset(transaction)`**을 검사한다.
   - `frozenset`의 `issubset()` 메서드는 해당 후보의 모든 원소가 트랜잭션에 포함되어 있는지를 $O(k)$에 판별한다.
   - 포함되면 해당 후보의 카운트를 1 증가시킨다.
4. `min_count` 이상인 후보만 `Lk` 딕셔너리에 담아 반환한다.

### 자료구조
| 변수 | 타입 | 설명 |
|---|---|---|
| `candidate_counts` | `dict[frozenset, int]` | 후보 → 등장 횟수 카운터 |
| `Lk` | `dict[frozenset, int]` | 합격한 빈발 $k$-아이템셋 → 등장 횟수 |

---

## 5. `find_freq(minimum_support, input_file)`

### 목적
$L_1, L_2, \ldots, L_k$를 반복적으로 구해 모든 빈발 항목 집합을 하나의 딕셔너리에 모은다. (Apriori 메인 루프)

### 입력 / 출력
- **입력**: `minimum_support` (float, 퍼센트), `input_file` (str)
- **출력**: `result` (dict) — 모든 길이의 빈발 항목 집합과 등장 횟수를 담은 통합 딕셔너리

### 세부 로직
1. `explain_input_parsing()`으로 트랜잭션을 로드한다.
2. `k=1`부터 시작하는 `while True` 루프를 실행한다.
3. `k==1`이면 `get_frequent_1_itemsets()`를 호출한다.
4. `k>=2`이면:
   - `list(previous.keys())`로 이전 단계 빈발 집합의 키만 추출하여 리스트로 변환한다.
   - `apriori_gen()`으로 후보($C_k$)를 생성한다.
   - `get_frequent_k_itemsets()`로 후보를 채점하여 $L_k$를 구한다.
5. $L_k$가 비었으면(`len(Lk) == 0`) 루프를 종료한다.
6. 그렇지 않으면 `result.update(Lk)`로 전체 결과에 병합하고, `previous = Lk`, `k += 1`을 하여 다음 단계로 넘어간다.

### 자료 흐름
```
L1(dict) → keys → apriori_gen → C2(list) → get_frequent_k → L2(dict) → keys → apriori_gen → C3(list) → ...
```

### 자료구조
| 변수 | 타입 | 설명 |
|---|---|---|
| `result` | `dict[frozenset, int]` | 모든 $L_k$를 합친 최종 빈발 항목 집합 |
| `previous` | `dict[frozenset, int]` | 직전 단계의 $L_k$ (다음 후보 생성용) |

---

## 6. `format_set(itemset)`

### 목적
`frozenset`을 과제 출력 포맷인 `{1,2,3}` 형태의 문자열로 변환한다.

### 입력 / 출력
- **입력**: `itemset` (frozenset)
- **출력**: `str` — 예: `"{1,2,3}"`

### 세부 로직
1. `sorted(itemset)`으로 아이템을 오름차순 정렬한다.
2. 각 아이템을 `str()`로 문자열 변환한 뒤, `",".join()`으로 쉼표 구분 문자열을 만든다.
3. f-string의 이중 중괄호(`{{`, `}}`)를 활용하여 양쪽에 `{}`를 씌워 반환한다.
   - `f"{{{joined_items}}}"` → f-string에서 `{{`는 리터럴 `{`, `}}`는 리터럴 `}`로 출력된다.

---

## 7. `generate_rules_and_output(result, n_transactions, output_file)`

### 목적
빈발 항목 집합(`result`)으로부터 모든 연관 규칙(Association Rules)을 생성하고, 지지도/신뢰도를 계산하여 파일에 출력한다.

### 입력 / 출력
- **입력**: `result` (dict), `n_transactions` (int), `output_file` (str)
- **출력**: 파일 쓰기 (반환값 없음)

### 세부 로직
1. `output_file`을 쓰기 모드(`'w'`)로 연다. 파일이 없으면 자동 생성된다.
2. `result`의 모든 키(빈발 항목 집합)를 순회한다.
3. 길이가 2 미만인 집합은 규칙을 만들 수 없으므로 `continue`로 건너뛴다.
4. `itertools.combinations(itemset, r)`을 사용하여 길이 `r` (1부터 `length-1`까지)인 모든 부분집합을 생성한다.
   - 각 부분집합을 **`frozenset(subset)`으로 변환하여 조건절(antecedent)**로 삼는다.
   - **결과절(consequent)**은 차집합 연산 `itemset - antecedent`로 구한다.
     - `frozenset`끼리는 `-` 연산자로 차집합을 바로 계산할 수 있다.
5. 지지도와 신뢰도를 계산한다:
   - **지지도**: `(result[itemset] / n_transactions) * 100` — 전체 트랜잭션 대비 해당 집합의 등장 비율
   - **신뢰도**: `(result[itemset] / result[antecedent]) * 100` — 조건절 등장 횟수 대비 전체 집합 등장 횟수 (조건부 확률)
6. `f.write()`에서 `{support:.2f}` 포맷을 사용해 소수점 둘째 자리까지 반올림하여 출력한다.

### 규칙 생성 예시
빈발 집합 `{1, 2, 3}`으로부터 생성되는 6가지 규칙:

| 조건절 (antecedent) | 결과절 (consequent) | 지지도 | 신뢰도 |
|---|---|---|---|
| `{1}` | `{2,3}` | `result[{1,2,3}] / N` | `result[{1,2,3}] / result[{1}]` |
| `{2}` | `{1,3}` | 동일 | `result[{1,2,3}] / result[{2}]` |
| `{3}` | `{1,2}` | 동일 | `result[{1,2,3}] / result[{3}]` |
| `{1,2}` | `{3}` | 동일 | `result[{1,2,3}] / result[{1,2}]` |
| `{1,3}` | `{2}` | 동일 | `result[{1,2,3}] / result[{1,3}]` |
| `{2,3}` | `{1}` | 동일 | `result[{1,2,3}] / result[{2,3}]` |

---

## 8. `__main__` 블록 (프로그램 진입점)

### 목적
커맨드 라인 인자를 파싱하고, 위의 함수들을 순서대로 호출하여 프로그램을 실행한다.

### 실행 흐름
```
sys.argv 파싱 → find_freq() → explain_input_parsing() → generate_rules_and_output()
```

1. `sys.argv`에서 3개의 인자(최소지지도, 입력파일, 출력파일)를 읽는다. 인자 수가 틀리면 사용법을 출력하고 종료한다.
2. 최소지지도를 `float`로 변환한다. 실패 시 에러 메시지 출력 후 종료한다.
3. `find_freq()`를 호출하여 모든 빈발 항목 집합을 구한다.
4. 결과가 있으면 `explain_input_parsing()`으로 트랜잭션을 다시 로드하여 전체 개수(`n_transactions`)를 구한다.
5. `generate_rules_and_output()`을 호출하여 연관 규칙을 파일에 출력한다.
