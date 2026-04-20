'''
2023036299 김진욱
2026.03.11

'''

import sys
from itertools import combinations

def explain_input_parsing(input_file):

    transactions = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:

            for line_number, line in enumerate(f, start = 1):

                items_str_list = line.strip().split()

                if not items_str_list:
                    continue

                transaction = set(int(item) for item in items_str_list)

                transactions.append(transaction)

    except FileNotFoundError:
        return None
    return transactions

def get_frequent_1_itemsets(transactions, min_sup_percent):
    n_transactions = len(transactions)
    min_count = n_transactions * (min_sup_percent / 100.0)

    item_counts = {}
    for transaction in transactions:
        for item in transaction:      
            if item in item_counts:  
                item_counts[item] += 1
            else:
                item_counts[item] = 1

    L1 = {}                          
    sorted_items = sorted(item_counts.items())

    for item, count in sorted_items:
        if count >= min_count:
            itemset = frozenset({item})  
            L1[itemset] = count      
    return L1        

def apriori_gen(L_prev, k):

    Ck = []
    len_L = len(L_prev)

    for i in range(len_L):
        for j in range(i+1, len_L):

            list_i = list(L_prev[i])
            list_j = list(L_prev[j])

            list_i.sort()
            list_j.sort()

            if list_i[:k-2] == list_j[:k-2]:

                candidate = L_prev[i] | L_prev[j]

                if candidate not in Ck:
                    Ck.append(candidate)

    return Ck


def get_frequent_k_itemsets(transactions, min_sup_percent, Ck):
    n_transactions = len(transactions)
    min_count = n_transactions * (min_sup_percent / 100.0)

    candidate_counts = {candidate: 0 for candidate in Ck}

    for transaction in transactions:
        for candidate in Ck:
            if candidate.issubset(transaction):
                candidate_counts[candidate] += 1

    Lk = {}
    for candidate, count in candidate_counts.items():
        if count >= min_count:
            Lk[candidate] = count            

    return Lk

def find_freq(minimum_support, input_file):
    result = {}
    transactions = explain_input_parsing(input_file)
    k = 1
    previous = {}

    while True:
        Lk = {}  # 이번 단계에서 찾아낼 빈발 항목 집합 (전 코드의 'process')
        if k == 1:
            Lk = get_frequent_1_itemsets(transactions, minimum_support)
        else:
            # 이전 단계의 Lk(previous)를 바탕으로 Ck를 만들고 채점
            candidates = apriori_gen(list(previous.keys()), k)
            Lk = get_frequent_k_itemsets(transactions, minimum_support, candidates)

        # 합격한 후보가 하나도 없으면 반복문 종료!
        if len(Lk) == 0:
            break
        else:
            # 전체 명부에 이번 합격자들을 추가하고, 다음 단계를 위해 저장
            result.update(Lk)
            previous = Lk
            k += 1

    return result


def format_set(itemset):

    str_itmes = [str(item) for item in sorted(itemset)]

    joined_items =",".join(str_itmes)

    return f"{{{joined_items}}}"


def generate_rules_and_output(result, n_transactions, output_file):

    try: 
        with open(output_file, 'w', encoding='utf-8') as f:

            for itemset in result.keys():

                length = len(itemset)
                if length < 2:
                    continue

                for r in range(1, length):

                    for subset in combinations(itemset, r):

                        antecedent = frozenset(subset)
                        consequent = itemset - antecedent

                        support = (result[itemset] / n_transactions) * 100
                        confidence = (result[itemset] / result[antecedent]) * 100

                        f.write(f"{format_set(antecedent)}\t{format_set(consequent)}\t{support:.2f}\t{confidence:.2f}\n") 

                        pass

    except IOError:
        print(f"Error: Could not write to file '{output_file}'")                

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python apriori.py [minimum_support] [input_file] [output_file]")
        sys.exit(1)

    try:
        min_sup = float(sys.argv[1])
    except ValueError:
        print("Error: minimum_support must be a number.")
        sys.exit(1)

    input_file = sys.argv[2]
    output_file = sys.argv[3]

    print(f"Running Apriori with min_sup={min_sup}% on {input_file}...")
    
    # 1. 메인 함수 실행해서 빈발 항목 집합 모두 찾기
    result = find_freq(min_sup, input_file)
    
    if result:
        # 트랜잭션 개수 가져오기 (파일을 한번 더 읽거나, main_function에서 반환해야 하지만 
        # 간단히 다시 파싱해서 개수만 구합니다)
        transactions = explain_input_parsing(input_file)
        n_transactions = len(transactions)
        
        # 2. 규칙 생성 및 파일에 적기
        generate_rules_and_output(result, n_transactions, output_file)
        print(f"Done! Results saved to {output_file}")
    else:
        print("No frequent itemsets found.")