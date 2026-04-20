# DataScience 과제 저장소

데이터사이언스 과목 과제(연관 규칙 마이닝, 의사결정나무 분류기) 작업물을 모아둔 저장소입니다.

## 저장소 개요

- 1차 과제: Apriori 알고리즘 기반 연관 규칙 마이닝
- 2차 과제: Decision Tree(의사결정나무) 기반 범주형 데이터 분류
- 보고서/실험 결과/중간 정리 문서 포함

## 디렉터리 구조

```text
DataScience/
├─ READEME.md
├─ 1st_assignment/
│  ├─ apriori.py
│  ├─ input.txt
│  ├─ output.txt
│  ├─ report.md
│  ├─ process.md
│  ├─ processing.md
│  └─ processing/
│     ├─ explain.py
│     ├─ homework.md
│     └─ outputRsupport4.txt
└─ 2nd_assignment/
   ├─ 2023036299_김진욱_decision_tree/
   │  ├─ dt.py
   │  ├─ dt_train.txt / dt_test.txt
   │  ├─ dt_train1.txt / dt_test1.txt
   │  ├─ dt_result.txt / dt_result1.txt
   │  ├─ dt_answer.txt / dt_answer1.txt
   │  └─ Decision_tree_report.pdf 등
   ├─ dt_result_expA.txt / dt_result_expB.txt / dt_result_expC.txt
   ├─ dt_result1_expA.txt / dt_result1_expB.txt / dt_result1_expC.txt
   └─ processing/
      ├─ assignment2_report.tex
      ├─ ltx.tex
      ├─ homework.md
      ├─ r2cord.md
      └─ _minted/
```

## 1차 과제: Apriori

### 구현 파일

- `1st_assignment/apriori.py`

### 기능

- 트랜잭션 파일 파싱
- 최소 지지도(minimum support) 기준 빈발 항목집합 탐색
- 연관 규칙 생성
- 지지도/신뢰도 계산 후 파일 출력

### 실행 방법

루트(DataScience) 기준:

```bash
python 1st_assignment/apriori.py [최소지지도(%)] [입력파일] [출력파일]
```

예시:

```bash
python 1st_assignment/apriori.py 5 1st_assignment/input.txt 1st_assignment/output.txt
```

### 입력 형식

- 한 줄 = 한 트랜잭션
- 아이템은 공백으로 구분된 정수

예시:

```text
1 3 4
2 3 5
1 2 3 5
```

### 출력 형식

- 규칙별 1줄
- 형식: `조건절\t결과절\t지지도(%)\t신뢰도(%)`

예시:

```text
{1}\t{8}\t15.40\t51.68
```

## 2차 과제: Decision Tree

### 구현 파일

- `2nd_assignment/2023036299_김진욱_decision_tree/dt.py`

### 기능

- 학습 데이터(`train`)로 의사결정나무 생성
- 테스트 데이터(`test`) 분류 예측
- 결과 파일(`result`) 저장

### 실행 방법

루트(DataScience) 기준:

```bash
python 2nd_assignment/2023036299_김진욱_decision_tree/dt.py [학습파일] [테스트파일] [출력파일]
```

예시:

```bash
python 2nd_assignment/2023036299_김진욱_decision_tree/dt.py \
  2nd_assignment/2023036299_김진욱_decision_tree/dt_train.txt \
  2nd_assignment/2023036299_김진욱_decision_tree/dt_test.txt \
  2nd_assignment/2023036299_김진욱_decision_tree/dt_result.txt
```

### 데이터 형식

- 탭(`\t`)으로 구분된 텍스트
- 첫 줄은 헤더(속성명)
- 학습 데이터의 마지막 컬럼은 클래스 라벨

## 포함된 문서/결과물

- 1차 과제 문서: `report.md`, `process.md`, `processing.md`
- 2차 과제 문서: `Decision_tree_report.pdf`, `assignment2_report.tex`, `ltx.tex` 등
- 실험 결과 파일: `dt_result_expA/B/C.txt`, `dt_result1_expA/B/C.txt`

## 실행 환경

- Python 3.x
- 표준 라이브러리 기반 구현(별도 외부 패키지 의존도 낮음)

## 참고

- 파일명은 현재 저장소 상태를 따라 `READEME.md`로 유지했습니다.
- 필요 시 파일명을 `README.md`로 바꿔 사용해도 됩니다.
