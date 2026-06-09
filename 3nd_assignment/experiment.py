"""
실험 스크립트 (제출 대상 아님).

목적:
  1) KD-tree 와 brute-force 의 결과 동일성 검증 + 속도 비교
  2) 외부 루프의 방문 순서가 결과에 어떤 영향을 주는지 측정

각 실험에서 'input1' 채점은 별도 PA3.exe 호출이 필요하므로,
이 스크립트는 클러스터 파일을 만들고 점수 집계를 위해 외부 호출하는 부분까지 자동화한다.
"""

import os
import sys
import time
import random
import shutil
import subprocess

import clustering as cl

# KD-tree 빌드/질의 재귀 깊이 보호 (input1=8000 점이라도 log2(8000)≈13 이지만,
# 정렬 후 mid 분할이라 일반적으로 안전. 안전 마진으로 늘려둔다.)
sys.setrecursionlimit(50000)


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = HERE                                     # 입력 파일은 루트에 위치
TEST_DIR = os.path.join(HERE, "test-1")
PA3 = os.path.join(TEST_DIR, "PA3.exe")


CASES = [
    # (input file stem, n, eps, min_pts)
    ("input1", 8, 15.0, 22),
    ("input2", 5,  2.0,  7),
    ("input3", 4,  5.0,  5),
]


def run_pa3(stem, n_clusters, new_labels, points):
    """
    new_labels 로부터 cluster 파일을 test-1 에 직접 생성하고 (입력 파일도 복사),
    PA3.exe 를 호출해서 점수 문자열을 반환.
    """
    # 입력 파일 복사
    shutil.copy(os.path.join(DATA_DIR, f"{stem}.txt"),
                os.path.join(TEST_DIR, f"{stem}.txt"))

    # 클러스터 파일 직접 작성 (write_clusters 와 동일 로직, 출력 폴더만 test-1)
    buckets = [[] for _ in range(n_clusters)]
    for idx, lab in enumerate(new_labels):
        if lab >= 0:
            buckets[lab].append(points[idx][0])
    for k in range(n_clusters):
        out_path = os.path.join(TEST_DIR, f"{stem}_cluster_{k}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for pid in buckets[k]:
                f.write(pid + "\n")

    # PA3 호출 (Windows 한국어 출력 → cp949 디코딩)
    res = subprocess.run([PA3, stem, stem],
                         cwd=TEST_DIR, capture_output=True)
    raw = res.stdout or b""
    try:
        score_text = raw.decode("cp949").strip()
    except UnicodeDecodeError:
        score_text = raw.decode("utf-8", errors="replace").strip()

    # 정리
    os.remove(os.path.join(TEST_DIR, f"{stem}.txt"))
    for k in range(n_clusters):
        p = os.path.join(TEST_DIR, f"{stem}_cluster_{k}.txt")
        if os.path.exists(p):
            os.remove(p)

    return score_text


def labels_to_signature(labels):
    """
    클러스터 ID 가 BFS 시작 순서에 따라 다를 수 있으므로,
    '같은 클러스터에 들어간 점들의 집합' 으로 정규화하여 비교한다.
    """
    groups = {}
    for i, lab in enumerate(labels):
        groups.setdefault(lab, set()).add(i)
    # NOISE/UNVISITED 는 그대로 둔다 (key 가 다른 정수라도 set 내용으로 비교)
    return frozenset(frozenset(s) for s in groups.values())


def experiment_kdtree_vs_brute():
    print("=" * 70)
    print("실험 A: KD-tree vs brute-force — 결과 동일성 + 속도")
    print("=" * 70)
    for stem, n, eps, min_pts in CASES:
        points = cl.read_data(os.path.join(DATA_DIR, f"{stem}.txt"))

        t0 = time.perf_counter()
        labels_brute, m_brute = cl.dbscan(
            points, eps, min_pts, use_kdtree=False)
        t_brute = time.perf_counter() - t0

        t0 = time.perf_counter()
        labels_kd, m_kd = cl.dbscan(
            points, eps, min_pts, use_kdtree=True)
        t_kd = time.perf_counter() - t0

        same = labels_to_signature(labels_brute) == labels_to_signature(labels_kd)
        speedup = t_brute / t_kd if t_kd > 0 else float("inf")

        print(f"{stem}: brute={t_brute:.3f}s  kd={t_kd:.3f}s  "
              f"speedup={speedup:.2f}x  m_brute={m_brute}  m_kd={m_kd}  "
              f"identical_clusters={same}")
    print()


def experiment_visit_order():
    print("=" * 70)
    print("실험 B: 외부 루프 방문 순서가 점수에 주는 영향")
    print("=" * 70)
    print(f"{'case':<8} {'order':<14} {'raw':>4} {'kept':>4} "
          f"{'noise':>6} {'score':>14}")
    print("-" * 70)

    for stem, n, eps, min_pts in CASES:
        points = cl.read_data(os.path.join(DATA_DIR, f"{stem}.txt"))
        L = len(points)

        orders = [
            ("input",   list(range(L))),
            ("reverse", list(range(L - 1, -1, -1))),
            ("seed_1",  None),     # 채워서 셔플
            ("seed_42", None),
            ("seed_777", None),
        ]
        for i, (name, _) in enumerate(orders):
            if name.startswith("seed_"):
                seed = int(name.split("_")[1])
                rng = random.Random(seed)
                arr = list(range(L))
                rng.shuffle(arr)
                orders[i] = (name, arr)

        for name, order in orders:
            labels, m = cl.dbscan(points, eps, min_pts,
                                  use_kdtree=True, order=order)
            new_labels, kept = cl.select_top_n_clusters(labels, m, n)
            noise = sum(1 for lab in new_labels if lab == cl.NOISE)
            score = run_pa3(stem, kept, new_labels, points)
            print(f"{stem:<8} {name:<14} {m:>4} {kept:>4} "
                  f"{noise:>6} {score:>14}")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "B":
        experiment_visit_order()
    elif len(sys.argv) > 1 and sys.argv[1] == "A":
        experiment_kdtree_vs_brute()
    else:
        experiment_kdtree_vs_brute()
        experiment_visit_order()
