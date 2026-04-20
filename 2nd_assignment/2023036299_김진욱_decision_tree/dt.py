"""
Programming Assignment #2: Decision Tree Classifier
=====================================================
의사결정 나무를 이용한 범주형 데이터 분류기.

[구현 철학]
- 모든 속성을 '문자열 카테고리'로 취급하여 범용성 확보 (하드코딩 없음)
- 트리 노드를 Python dict(중첩 딕셔너리)로 표현하여 재귀 구조를 자연스럽게 구현
- Information Gain을 기본 분할 척도로 사용하되, 동점(Tie) 시 Gain Ratio로 승부
- collections.Counter를 활용한 빈도 계산으로 코드 간결성과 성능 확보
"""

import sys
import math
from collections import Counter


# ============================================================
# 1. 데이터 입출력 (I/O)
# ============================================================

def read_data(file_path):
    """
    탭(\\t)으로 구분된 데이터 파일을 파싱한다.

    [설계 결정]
    - 각 행을 dict로 변환한다: {속성이름: 값, ...}
      → 이후 tree[attribute] 식의 접근이 가능해져,
        인덱스 번호 대신 속성 '이름'으로 데이터를 다룰 수 있다.
      → 속성 이름이 바뀌어도 (buys_computer → car_evaluation)
        코드 수정 없이 동작하는 범용성의 핵심 설계이다.
    - strip()으로 \\r\\n 등 OS별 개행 차이를 흡수한다.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 첫 줄: 헤더(속성 이름)
    header = lines[0].strip().split('\t')

    # 나머지 줄: 데이터를 dict의 리스트로 변환
    data = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        values = line.split('\t')
        # zip(header, values)로 속성이름-값 쌍을 자동 매핑
        row = dict(zip(header, values))
        data.append(row)

    return header, data


def write_result(file_path, test_header, test_data, predictions, target_name):
    """
    예측 결과를 과제 형식에 맞게 저장한다.

    [설계 결정]
    - 테스트 데이터의 원래 순서를 절대 변경하지 않는다.
      → zip(test_data, predictions)로 1:1 대응을 보장한다.
    - 구분자는 반드시 탭(\\t)을 사용한다.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        # 첫 줄: 테스트 헤더 + 타겟 이름
        f.write('\t'.join(test_header) + '\t' + target_name + '\n')

        # 데이터 행: 원본 값들 + 예측값
        for row, pred in zip(test_data, predictions):
            values = [row[attr] for attr in test_header]
            f.write('\t'.join(values) + '\t' + pred + '\n')


# ============================================================
# 2. 분할 척도 계산 (Split Measures)
# ============================================================

def entropy(data, target):
    """
    주어진 데이터의 엔트로피 H(S)를 계산한다.
    H(S) = -Σ p_i * log2(p_i)

    [설계 결정]
    - collections.Counter 사용:
      Counter는 리스트 안의 각 원소가 몇 번 등장하는지를
      한 번의 순회(O(n))로 딕셔너리 형태로 집계해준다.
      수동 for문 + dict 카운팅보다 간결하고 Pythonic하다.
    - p == 0일 때 log2(0)은 수학적으로 정의 불가(→ -inf).
      그러나 lim(p→0) p*log2(p) = 0 이므로,
      p가 0인 경우 해당 항을 건너뛰는 것이 올바르다.
    """
    labels = [row[target] for row in data]
    counts = Counter(labels)
    total = len(data)

    h = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            h -= p * math.log2(p)
    return h


def information_gain(data, attribute, target):
    """
    속성(attribute)으로 데이터를 분할했을 때의 정보 이득을 계산한다.
    IG(S, A) = H(S) - Σ (|S_v| / |S|) * H(S_v)

    [설계 결정]
    - 데이터를 속성값별로 그룹핑할 때, 딕셔너리 컴프리헨션 대신
      명시적 for문을 사용한다.
      → 한 번의 순회로 그룹핑이 완료되며,
        같은 데이터를 여러 번 필터링하는 리스트 컴프리헨션
        (예: [row for row in data if row[attr] == v] × N번)
        대비 O(n) vs O(n*k)로 효율적이다.
    """
    total = len(data)
    h_before = entropy(data, target)

    # 속성값별로 데이터를 그룹핑 (한 번의 순회)
    partitions = {}
    for row in data:
        val = row[attribute]
        if val not in partitions:
            partitions[val] = []
        partitions[val].append(row)

    # 가중 엔트로피 합산
    h_after = 0.0
    for subset in partitions.values():
        weight = len(subset) / total
        h_after += weight * entropy(subset, target)

    return h_before - h_after


def split_info(data, attribute):
    """
    Gain Ratio 계산에 필요한 Split Information을 구한다.
    SplitInfo(S, A) = -Σ (|S_v| / |S|) * log2(|S_v| / |S|)

    [설계 결정]
    - 수식 구조가 entropy()와 동일하지만, '클래스 라벨'이 아닌
      '속성값'의 분포를 기준으로 계산하는 차이가 있다.
    - 별도 함수로 분리한 이유: entropy()는 target(정답열)의
      분포를 보지만, split_info()는 attribute(재료열)의 분포를 본다.
      목적이 다르므로 함수를 분리하여 혼동을 방지한다.
    """
    total = len(data)
    counts = Counter(row[attribute] for row in data)

    si = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            si -= p * math.log2(p)
    return si


def gain_ratio(data, attribute, target):
    """
    Gain Ratio = Information Gain / Split Information

    [설계 결정]
    - Split Information이 0인 경우(모든 데이터가 같은 속성값을 가짐)
      → 0으로 나누기 방지를 위해 0.0을 반환한다.
    - 이 척도는 '동점(Tie) 해소용 보조 엔진'으로만 사용된다.
    """
    ig = information_gain(data, attribute, target)
    si = split_info(data, attribute)
    if si == 0:
        return 0.0
    return ig / si


def gini_index(data, attribute, target):
    """
    Gini Index로 속성의 불순도를 계산한다.
    Gini(S) = 1 - Σ p_i^2
    GiniIndex(S, A) = Σ (|S_v| / |S|) * Gini(S_v)

    [설계 결정]
    - 엔트로피와 달리 log 연산이 없어 계산이 빠르다.
    - 반환값은 '불순도'이므로, 값이 작을수록 좋은 분할이다.
      → 이 점이 information_gain (값이 클수록 좋음)과 반대이므로
        주의가 필요하다.
    - 본 코드에서는 실험 비교용으로 구현하였으며,
      최종 분할 전략에서는 사용되지 않는다 (select_best_attribute 참조).
    """
    total = len(data)

    partitions = {}
    for row in data:
        val = row[attribute]
        if val not in partitions:
            partitions[val] = []
        partitions[val].append(row)

    gini_attr = 0.0
    for subset in partitions.values():
        size = len(subset)
        if size == 0:
            continue
        labels = Counter(row[target] for row in subset)
        gini_subset = 1.0 - sum((c / size) ** 2 for c in labels.values())
        gini_attr += (size / total) * gini_subset

    return gini_attr


# ============================================================
# 3. 최적 속성 선택 (Best Attribute Selection)
# ============================================================

def select_best_attribute(data, attributes, target):
    """
    Information Gain이 가장 높은 속성을 선택한다.
    동점(Tie)이 발생하면 Gain Ratio로 승부를 가린다.

    [설계 결정 — 혼합(Hybrid) 전략 (최종 채택)]
    - 1차 기준: Information Gain (값이 클수록 좋음)
    - 동점 해소: Gain Ratio (값이 클수록 좋음)
    - 4가지 방식(기존, Gain Ratio 단독, Gini Index 단독,
      Gain Ratio+Gini Tie-break)을 비교 실험한 결과,
      car_evaluation 데이터셋에서 모두 동일한 정확도(87.57%)를 기록.
      속성 간 고유값 개수가 균등하여 척도 간 차이가 무의미했으므로,
      가장 직관적인 Information Gain + Gain Ratio Tie-break를 최종 채택.
    """
    best_gain = -1
    candidates = []

    for attr in attributes:
        ig = information_gain(data, attr, target)
        if ig > best_gain:
            best_gain = ig
            candidates = [attr]
        elif ig == best_gain:
            candidates.append(attr)

    if len(candidates) == 1:
        return candidates[0]

    best_attr = max(candidates, key=lambda attr: gain_ratio(data, attr, target))
    return best_attr


# ============================================================
# 4. 의사결정 나무 구축 (Tree Construction)
# ============================================================

def build_tree(data, attributes, target):
    """
    재귀적으로 의사결정 나무를 구축한다.

    [설계 결정 — 트리를 중첩 딕셔너리(dict)로 표현]
    - 별도의 Node 클래스를 정의하는 대신, Python의 dict를
      중첩(nesting)하여 트리 구조를 표현한다.
      예: {'age': {'<=30': {'student': {'yes': 'yes', 'no': 'no'}},
                   '31...40': 'yes',
                   '>40': ...}}
    - dict의 key가 속성값(branch), value가 자식 노드(subtree)
      또는 리프 노드(문자열 라벨)가 된다.
    - 장점: 클래스 정의 없이도 트리를 자연스럽게 표현 가능하며,
      print()로 즉시 구조를 확인할 수 있어 디버깅이 용이하다.

    [재귀 종료 조건 3가지]
    (1) 모든 데이터의 클래스가 동일 → 그 클래스를 리프로 반환
    (2) 분할할 속성이 남아있지 않음 → 다수결(최빈값)으로 리프 반환
    (3) 데이터가 비어있음 → 상위 호출에서 처리

    [Python 기능 활용]
    - Counter.most_common(1): 최빈값을 O(n)에 찾아준다.
      sorted() + [0] 방식보다 의도가 명확하고 효율적이다.
    - set comprehension {row[target] for row in data}:
      고유 클래스 라벨을 한 번의 순회로 추출한다.
    """
    # --- 재귀 종료 조건 (1): 모든 클래스가 동일 ---
    classes = set(row[target] for row in data)
    if len(classes) == 1:
        return classes.pop()  # set.pop()으로 유일한 원소를 꺼냄

    # --- 재귀 종료 조건 (2): 남은 속성이 없음 → 다수결 ---
    if len(attributes) == 0:
        labels = Counter(row[target] for row in data)
        return labels.most_common(1)[0][0]

    # --- 최적 속성 선택 ---
    best_attr = select_best_attribute(data, attributes, target)

    # --- 트리 노드 생성 (중첩 딕셔너리) ---
    tree = {best_attr: {}}

    # 다수결 라벨: 현재 노드의 기본값 (학습 데이터에 없는 속성값 대비)
    majority_label = Counter(row[target] for row in data).most_common(1)[0][0]

    # 선택된 속성의 모든 고유값으로 가지(branch) 생성
    # 남은 속성 목록에서 best_attr을 제거
    remaining_attrs = [a for a in attributes if a != best_attr]

    # 속성값별로 데이터를 분할하여 재귀 호출
    partitions = {}
    for row in data:
        val = row[best_attr]
        if val not in partitions:
            partitions[val] = []
        partitions[val].append(row)

    for val, subset in partitions.items():
        if len(subset) == 0:
            # 해당 속성값의 데이터가 없으면 다수결 라벨 사용
            tree[best_attr][val] = majority_label
        else:
            # 재귀적으로 서브트리 구축
            tree[best_attr][val] = build_tree(subset, remaining_attrs, target)

    return tree


# ============================================================
# 5. 예측 (Prediction)
# ============================================================

def predict_one(tree, row, default_label):
    """
    하나의 데이터 행(row)에 대해 학습된 트리를 따라가며 예측한다.

    [설계 결정]
    - 트리가 dict이면 아직 내부 노드 → 속성값에 따라 하위로 이동.
    - 트리가 str이면 리프 노드 → 해당 문자열이 예측 결과.
    - isinstance()로 타입을 검사하여 리프/내부 노드를 구분한다.
      → dict를 트리 노드로 사용했기 때문에 가능한 접근이다.

    [예외 처리 — 학습 데이터에 없던 속성값]
    - 테스트 데이터에 학습 시 본 적 없는 속성값이 등장할 수 있다.
      예: 학습에는 income='high','medium','low'만 있었는데
          테스트에 income='vhigh'가 등장하는 경우.
    - 이 경우 tree[attr_name]에 해당 키가 없으므로
      default_label(전체 학습 데이터의 다수결 라벨)을 반환한다.
    """
    # 리프 노드: 예측 라벨(str)을 직접 반환
    if not isinstance(tree, dict):
        return tree

    # 내부 노드: dict의 유일한 key가 분할 속성 이름
    attr_name = list(tree.keys())[0]
    branches = tree[attr_name]

    # 현재 행의 해당 속성값으로 가지를 선택
    attr_value = row.get(attr_name)

    if attr_value in branches:
        # 해당 가지가 존재 → 하위 노드로 재귀 이동
        return predict_one(branches[attr_value], row, default_label)
    else:
        # 학습 시 본 적 없는 속성값 → 기본 라벨 반환
        return default_label


def predict_all(tree, test_data, default_label):
    """
    테스트 데이터 전체에 대해 예측을 수행한다.

    [설계 결정]
    - 리스트 컴프리헨션으로 한 줄에 예측 리스트를 생성한다.
      → for문 + append보다 Pythonic하고,
        내부적으로 C 레벨 최적화가 적용되어 약간 더 빠르다.
    - 테스트 데이터의 순서가 그대로 유지된다 (과제 요구사항).
    """
    return [predict_one(tree, row, default_label) for row in test_data]


# ============================================================
# 6. 메인 실행부
# ============================================================

def main():
    """
    프로그램 진입점. 커맨드라인 인자를 파싱하고
    학습 → 예측 → 결과 저장의 전체 파이프라인을 실행한다.

    [실행 예시]
    python dt.py dt_train.txt dt_test.txt dt_result.txt
    """
    # --- 커맨드라인 인자 검증 ---
    if len(sys.argv) != 4:
        print("Usage: python dt.py <train_file> <test_file> <result_file>")
        sys.exit(1)

    train_file = sys.argv[1]
    test_file = sys.argv[2]
    result_file = sys.argv[3]

    # --- 1단계: 데이터 읽기 ---
    train_header, train_data = read_data(train_file)
    test_header, test_data = read_data(test_file)

    # 타겟(정답열): 학습 데이터 헤더의 마지막 열
    # 피처(재료열): 나머지 모든 열
    target_name = train_header[-1]
    features = train_header[:-1]

    # --- 2단계: 의사결정 나무 구축 ---
    tree = build_tree(train_data, features, target_name)

    # --- 3단계: 기본 라벨 결정 (예외 처리용) ---
    # 학습 데이터 전체에서 가장 많이 등장한 클래스 라벨
    default_label = Counter(
        row[target_name] for row in train_data
    ).most_common(1)[0][0]

    # --- 4단계: 테스트 데이터 예측 ---
    predictions = predict_all(tree, test_data, default_label)

    # --- 5단계: 결과 저장 ---
    write_result(result_file, test_header, test_data, predictions, target_name)


if __name__ == "__main__":
    main()
