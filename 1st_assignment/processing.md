# Apriori 알고리즘 구현 과정 토의 기록

## 1. 초기 접근 방식에 대한 재고

### 토의 내용
- 처음에는 Apriori 의사코드(pseudocode)를 그대로 구현하는 방식으로 접근하려 했으나, 사용자가 **"그냥 의사코드만 구현하고 아무것도 안 하는 것 같다"**며 방식을 다시 고안하겠다고 제안함.

- 의사코드의 구현 문제. 길이가 1인 원소를 담는 배열부터 .... 특정 길이의 배열이 생성되지 않을 떄 까지 해당 로직을 반복할 것인가?

- 이후 `explain.py`라는 별도 파일에 먼저 각 단계를 설명하듯 코드를 작성하고, 사용자가 그것을 보며 `apriori.py`를 직접 채워나가는 **점진적 학습 방식**으로 전환함.

### 변경 사항
- `explain.py` 파일을 "설명용 레퍼런스"로 먼저 작성 → 사용자가 이해한 뒤 `apriori.py`에 직접 코드를 타이핑하는 흐름으로 진행.
- 최종적으로 `explain.py`는 역할을 다하여 삭제됨.

---

## 2. 트랜잭션 데이터의 자료구조 선택

### 토의 내용
- 입력 파일의 각 줄(트랜잭션)을 어떤 자료구조로 저장할지 논의함.
- **리스트(`list`)** vs **집합(`set`)** 중 어떤 것이 적합한지 비교함.

### 결론
- **`set`을 채택**.
- 이유: 이후 Apriori 알고리즘에서 후보 집합이 트랜잭션에 포함되는지를 `issubset()` 메서드로 빠르게 검사할 수 있기 때문.
- 코드: `transaction = set(int(item) for item in items_str_list)`

---

## 3. 빈발 1-아이템셋($L_1$) 저장 자료구조

### 토의 내용
- 처음에는 $L_1$을 리스트로 만들려고 했으나, 나중에 **신뢰도 계산 시 등장 횟수(count)가 필요**하므로 등장 횟수도 함께 저장해야 한다는 점을 논의함.

### 변경 사항
- **초기 구현**: `L1`을 리스트로 구현 시도
- **변경 후**: `L1`을 **딕셔너리** (`{frozenset: 등장횟수}`)로 변경
- 이유: 나중에 연관 규칙의 신뢰도를 계산할 때 `result[antecedent]`처럼 키로 바로 등장 횟수를 조회할 수 있어야 하기 때문.

### `frozenset` 도입 배경
- 파이썬의 일반 `set`은 mutable(변경 가능)이라 딕셔너리의 키로 사용할 수 없음.
- `frozenset`은 immutable이므로 딕셔너리 키로 사용 가능.
- `frozenset | frozenset`의 결과도 자동으로 `frozenset`이 되어, 이후 단계에서 별도의 형변환 없이 일관성 유지 가능.

---

## 4. 후보 집합 생성($C_k$)의 자료구조: 딕셔너리 vs 리스트

### 토의 내용
- 사용자가 `apriori_gen` 함수를 작성할 때, 처음에 `Ck = {}`(딕셔너리)로 초기화했으나 아래에서 `Ck.append()`를 사용하여 문법 오류가 발생하는 문제를 논의함.
- $L_k$(빈발 항목 집합)는 딕셔너리인데 $C_k$(후보 집합)는 왜 리스트여야 하는지 질문함.

### 결론
- **$L_k$는 딕셔너리**: "합격자 + 성적표" 역할. 키(frozenset)로 등장 횟수(int)를 바로 조회 가능해야 함.
- **$C_k$는 리스트**: "시험 볼 후보자 명단" 역할. 아직 등장 횟수를 세지 않았으므로, 순서대로 하나씩 꺼내보기 좋은 리스트가 적합.
- 전체 흐름: **L(dict) → C(list) → L(dict) → C(list)** 순환 구조.

### 변경 사항
- `Ck = {}` → `Ck = []` 로 수정

---

## 5. 후보 생성 최적화: 단순 합집합 → $k-2$ 슬라이싱

### 토의 내용
- 처음에는 모든 쌍의 합집합을 구한 뒤 `len(candidate) == k`로 필터링하는 단순 방식을 구현함.
- 사용자가 **"서로 다른 원소의 개수가 1개일 때만 고려하면 반복문 하나로 가능한가?"**라고 질문하며 최적화 아이디어를 제안함.

### 최적화 로직 설명
- Apriori 논문의 Join Step: 두 집합을 오름차순 정렬했을 때, **앞의 $k-2$개 원소가 동일하고 마지막 1개만 다를 때**만 합침.
- `k-2`인 이유: 입력 원소의 길이가 $k-1$이고, 마지막 1개를 제외하면 $(k-1)-1 = k-2$개.
- 이중 루프 자체는 여전히 필요하지만, 불필요한 합집합 연산을 원천 차단하여 **속도가 대폭 향상**됨.

### 변경 사항
```python
# 변경 전 (단순 방식)
candidate = L_prev[i] | L_prev[j]
if len(candidate) == k and candidate not in Ck:
    Ck.append(candidate)

# 변경 후 (최적화 방식)
list_i = list(L_prev[i])
list_j = list(L_prev[j])
list_i.sort()
list_j.sort()
if list_i[:k-2] == list_j[:k-2]:
    candidate = L_prev[i] | L_prev[j]
    if candidate not in Ck:
        Ck.append(candidate)
```

### 구체적 예시를 통한 검증
- $L_2 \to C_3$ ($k=3$): `[1,2]`와 `[1,3]`은 `[:1]`이 `[1]`로 같으므로 합격 → `{1,2,3}` 생성
- $L_3 \to C_4$ ($k=4$): `[1,2,3]`과 `[1,2,4]`는 `[:2]`가 `[1,2]`로 같으므로 합격 → `{1,2,3,4}` 생성

---

## 6. 빈 딕셔너리 검사 방식

### 토의 내용
- 사용자가 메인 루프에서 `if(process is {}):`로 빈 딕셔너리를 검사함.
- 파이썬에서 `is` 연산자는 객체의 **메모리 주소(identity)**를 비교하므로, 두 빈 딕셔너리는 생김새가 같아도 `is`로 비교하면 항상 `False`가 됨 → 무한루프 위험.

### 변경 사항
```python
# 변경 전 (잘못된 방식)
if(process is {}):
    break

# 변경 후 (올바른 방식)
if len(Lk) == 0:
    break
```
- 대안: `if not Lk:` (파이썬에서 빈 컨테이너는 `False`로 평가됨)

---

## 7. `result`에 결과를 쌓는 방식: `append` vs `update`

### 토의 내용
- 사용자가 `result = {}`(딕셔너리)로 선언한 뒤 `result.append(process)`를 사용하여 오류 발생.
- 딕셔너리에는 `append()` 메서드가 없으며, 딕셔너리를 합치려면 `update()`를 사용해야 함을 논의.

### 변경 사항
```python
# 변경 전
result.append(process)

# 변경 후
result.update(Lk)
```
- `update()`는 `Lk`의 모든 키-값 쌍을 `result`에 병합함.

---

## 8. `apriori_gen`에 전달하는 인자 타입 문제

### 토의 내용
- `previous`는 딕셔너리(`{frozenset: int}`)인데, `apriori_gen` 함수는 `frozenset`들의 **리스트**를 기대함.
- 딕셔너리를 그대로 넘기면 인덱스(`L_prev[i]`)로 접근할 수 없어 에러 발생.

### 변경 사항
```python
# 변경 전
apriori_gen(previous, k)

# 변경 후
apriori_gen(list(previous.keys()), k)
```
- `.keys()`로 키만 추출하고, `list()`로 인덱싱 가능한 리스트로 변환하여 전달.

---

## 9. 대입 연산자 오타 (`-` → `=`)

### 토의 내용
- 사용자가 `candidates - apriori_gen(...)` 으로 작성함.
- `-`는 뺄셈 연산자이므로 변수가 저장되지 않는 문제.

### 변경 사항
```python
# 변경 전
candidates - apriori_gen(list(previous.keys()), k)

# 변경 후
candidates = apriori_gen(list(previous.keys()), k)
```

---

## 10. 출력 포맷과 순서쌍(방향성) 논의

### 토의 내용
- 예시 출력 파일(`outputRsupport4.txt`)을 관찰한 결과, 같은 아이템 쌍(`{1}`과 `{8}`)에 대해 두 줄이 출력됨을 발견:
  - `{1} → {8}`: 지지도 15.40%, 신뢰도 51.68%
  - `{8} → {1}`: 지지도 15.40%, 신뢰도 34.07%
- **지지도는 순서에 무관**(둘 다 15.40%)하지만, **신뢰도는 조건부 확률이므로 순서에 따라 달라짐**.

### 결론
- 빈발 항목 집합을 찾는 과정(Apriori 메인 루프)에서는 **순서를 고려하지 않음** — 순수한 집합 연산.
- 연관 규칙을 생성하는 마지막 단계에서 **모든 가능한 방향의 규칙을 생성**하여 순서쌍을 처리.
- `itertools.combinations`를 사용해 부분집합을 생성하고, **조건절(antecedent)**과 **결과절(consequent = 전체 - 조건절)**로 분리.

---

## 11. f-string 포맷팅 문법 수정

### 토의 내용
- 사용자가 다음과 같이 작성:
  ```python
  f.write(f"{format_set(antecedent)}+'\t'+{format_set(consequent)}+'\t'+{str(support)}+'\t'+{str(confidence)}+'\n'")
  ```
- f-string 내부에서 `+'\t'+`는 문자열 연결이 아닌 **리터럴 텍스트**로 출력되는 문제.

### 변경 사항
```python
# 변경 전
f.write(f"{format_set(antecedent)}+'\t'+{format_set(consequent)}+'\t'+{str(support)}+'\t'+{str(confidence)}+'\n'")

# 변경 후
f.write(f"{format_set(antecedent)}\t{format_set(consequent)}\t{support:.2f}\t{confidence:.2f}\n")
```
- `:.2f` 포맷 지정자를 사용해 **소수점 둘째 자리 반올림** 요구사항도 동시에 해결.

---

## 12. 함수 이름 및 변수명 가독성 리팩토링

### 토의 내용
- `main_function(minimum_support, input, output)` 함수에서:
  - `input`은 파이썬 내장 함수와 이름이 겹침.
  - `output` 인자는 함수 내에서 사용되지 않음(파일 쓰기는 별도 함수가 담당).
  - `process`라는 변수명은 알고리즘적 의미가 불명확함.

### 변경 사항
| 변경 전 | 변경 후 | 이유 |
|---|---|---|
| `main_function` | `find_freq` | 함수의 실제 역할(빈발 집합 찾기)을 반영 |
| `input` | `input_file` | 내장 함수 충돌 방지 및 용도 명확화 |
| `output` 인자 | 삭제 | 사용되지 않는 인자 제거 |
| `process` | `Lk` | Apriori 논문 표기법과 일치시켜 의미 명확화 |

---

## 13. 기타 오타(Typo) 수정 내역

| 위치 | 변경 전 | 변경 후 |
|---|---|---|
| `explain_input_parsing` 인자 | `intput_file` | `input_file` |
| `get_frequent_k_itemsets` 내부 | `n_transcations` | `n_transactions` |
| 딕셔너리 컴프리헨션 | `{candidat: 0 for candidate in Ck}` | `{candidate: 0 for candidate in Ck}` |
| `apriori_gen` 함수명 | `aprior_gen` | `apriori_gen` |
| `except IOError` 내 변수 | `Output_file` (대문자 O) | `output_file` (소문자 o) |
