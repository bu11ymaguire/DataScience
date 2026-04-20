# explain.py
import sys

def explain_input_parsing(input_file):
    """
    transaction을 읽어오는 함수입니다.
    """
    transactions = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                items_str_list = line.strip().split()
                if not items_str_list:
                    continue
                transaction = set(int(item) for item in items_str_list)
                transactions.append(transaction)
    except FileNotFoundError:
        print(f"에러: '{input_file}' 파일을 찾을 수 없습니다.")
        return None
    return transactions

def get_frequent_1_itemsets(transactions, min_sup_percent):
    """
    질문자님의 아이디어 "length [1]의 리스트를 만든다"의 첫 단추!
    우선 트랜잭션을 훑으면서 길이가 1인 아이템들의 등장 횟수를 세고,
    min_sup을 넘는 진짜배기(L1)들만 오름차순으로 정리해 반환합니다.
    """
    print(f"\n--- [단계 1] 길이가 1인 빈발 항목 집합(L1) 찾기 ---")
    
    # 1. 전체 트랜잭션 수(N)와 최소 등장 횟수(min_count) 계산
    n_transactions = len(transactions)
    min_count = n_transactions * (min_sup_percent / 100.0)
    
    print(f"전체 트랜잭션 개수: {n_transactions}")
    print(f"최소 지지도: {min_sup_percent}%")
    print(f"-> 통과 커트라인(min_count): {min_count}번 이상 등장해야 함\n")
    
    # 2. 아이템별 등장 횟수 세기 (C1: Candidate 1-itemsets)
    # 딕셔너리를 사용하여 각 아이템(정수)이 몇 번 나오는지 셉니다.
    item_counts = {}
    for transaction in transactions:
        for item in transaction:
            if item in item_counts:
                item_counts[item] += 1
            else:
                item_counts[item] = 1
                
    # 3. 커트라인을 넘는 항목만 추려내기 (L1: Frequent 1-itemsets)
    # 질문자님의 아이디어 1: 나중에 조인(Join)과 딕셔너리 키로 쓰기 위해 frozenset으로 감싸줍니다.
    # 질문자님의 아이디어 2: "오름차순"으로 다루기 쉽게 추출할 때 정렬을 해줍니다.
    L1 = []
    
    # item_counts.items()는 (아이템, 등장횟수) 형태입니다.
    # 먼저 아이템 번호를 기준으로 오름차순 정렬을 해줍니다.
    sorted_items = sorted(item_counts.items())
    
    for item, count in sorted_items:
        if count >= min_count:
            # 부분집합 연산 및 불변성(Key로 사용)을 위해 frozenset({아이템}) 형태로 저장
            itemset = frozenset({item})
            L1.append(itemset)
            
    print(f"찾아낸 L1의 원소 개수: {len(L1)}개")
    print(f"L1의 앞부분 5개 모습: {L1[:5]}\n")
    
    # 참고: Python 리스트나 딕셔너리에 담아둘 때,
    # 각 빈발 항목 집합들의 실제 지지도(support count)도 어딘가에 저장해두어야 나중에 규칙 신뢰도를 계산할 수 있습니다.
    # 이 부분은 나중에 Apriori 메인 로직을 짤 때 통합할 예정입니다.
    
    return L1

# 실행 테스트 코드
if __name__ == "__main__":
    test_file = "input.txt" 
    
    # 1. 파싱
    transactions = explain_input_parsing(test_file)
    
    if transactions:
        # 2. 비율 5%로 L1 구하기 테스트
        min_support_percent = 5.0
        L1 = get_frequent_1_itemsets(transactions, min_support_percent)
