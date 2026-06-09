# 3rd Assignment 보고서 양식 (Design Template)

> 본 문서는 `2nd_assignment/processing/assignment2_report.tex` 의 양식을 그대로 계승하여
> 3rd assignment 보고서에 적용하기 위한 **LaTeX 템플릿 설계서**이다.
> 보고서의 일관성 유지를 위해 패키지 구성, 헤더 스타일, 섹션 구조,
> 코드/표/순서도 표현 방식을 동일하게 가져간다.

---

## 1. 컴파일 환경

| 항목 | 값 |
| --- | --- |
| 문서 클래스 | `article`, 12pt, A4 |
| 컴파일러 | **XeLaTeX** (한글 + minted shell-escape 필요) |
| 빌드 옵션 | `-shell-escape` 필수 (minted 사용) |
| 여백 | `geometry` 패키지로 `margin=2.5cm` |

빌드 예시:

```bash
xelatex -shell-escape assignment3_report.tex
```

---

## 2. 프리앰블 (패키지 구성)

```latex
\documentclass[12pt, a4paper]{article}

% ===== 패키지 =====
\usepackage{fontspec}         % XeLaTeX/LuaLaTeX 폰트 설정
\usepackage{kotex}            % 한글 지원
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{minted}           % 코드 삽입 (XeLaTeX + shell-escape 필요)
\usepackage{xcolor}           % 색상
\usepackage{booktabs}         % 깔끔한 표
\usepackage{amsmath, amssymb} % 수식
\usepackage{hyperref}         % 하이퍼링크
\usepackage{graphicx}         % 이미지
\usepackage{enumitem}         % 리스트 커스텀
\usepackage{caption}
\usepackage{adjustbox}        % 큰 표 너비 조절용
\usepackage{pifont}           % 체크마크 기호용
\newcommand{\cmark}{\ding{51}}
\usepackage{tikz}             % 순서도 도형
\usetikzlibrary{shapes.geometric, arrows.meta, positioning}

% ===== 코드 스타일 =====
\setminted[python]{
    bgcolor=black!5,
    linenos=true,
    breaklines=true,
    fontsize=\small,
    frame=lines,
    framesep=2mm
}
\setminted[bash]{
    bgcolor=black!5,
    linenos=false,
    breaklines=true,
    fontsize=\small,
    frame=lines,
    framesep=2mm
}
```

---

## 3. 표지 헤더 (제목 페이지 없이 바로 시작)

본 양식은 별도의 `\maketitle` 표지 페이지를 두지 않고,
문서 상단에 가운데 정렬된 커스텀 헤더 블록을 배치한다.

```latex
\begin{document}

\begin{center}
    {\Large\bfseries Programming Assignment \#3}\\[0.4em]
    {\large\bfseries <과제 부제목 — 예: 클러스터링(Clustering)을 이용한 ...>}\\[1em]
    {\normalsize
        \textbf{과목:} Data Science (ITE4005) \quad
        \textbf{학번:} 2023036299 \quad
        \textbf{이름:} 김진욱 \quad
        \textbf{<제출일: YYYY.MM.DD>}\\[0.3em]
        \textbf{OS:} Windows 10/11 \quad
        \textbf{Python:} 3.12.10 \quad
        \textbf{라이브러리:} <표준 라이브러리 명세>
    }
\end{center}
\vspace{0.5em}
\hrule
\vspace{1em}
```

채워야 할 placeholder:
- `Programming Assignment #N` 의 N
- 과제 부제목 (한 줄)
- 제출일
- 사용 라이브러리 명세

---

## 4. 보고서 섹션 구조 (5개 대단원 고정)

2nd assignment 와 동일하게 다음 5개 `\section` 으로 구성한다.

### Section 1 — 알고리즘 요약

- `\subsection{알고리즘 개요}` — 알고리즘 동작 원리 1문단 + 핵심 설계 결정 요약
- `\subsection{전체 순서도}` — TikZ 로 그린 파이프라인 다이어그램 (아래 §6 참고)
- `\subsection{핵심 자료 흐름}` — `verbatim` 으로 데이터가 변환되는 흐름 표기

### Section 2 — 각 함수별 코드 상세 설명

- `\subsection{\texttt{함수명()} --- 한 줄 설명}` 으로 함수 단위 분할
- 각 함수마다:
  1. 한 문단의 한국어 개요
  2. `\begin{minted}{python} ... \end{minted}` 로 핵심 코드 발췌
  3. `\textbf{핵심 설계 결정:}` + `itemize` 로 설계 의도 정리
- 수식이 필요한 함수는 `$ ... $` 또는 `\[ ... \]` 로 inline 표기

### Section 3 — 소스 코드 컴파일 및 실행 방법

- `\subsection{실행 환경}` — OS / Python / 라이브러리
- `\subsection{실행 명령어}` — `minted{bash}` 코드 블록
- `\subsection{실행 예시}` — 실제 입력 예시 + 동작 설명 `enumerate`
- `\subsection{파일 구조}` — `verbatim` 트리
- `\subsection{실행 화면}` — `\includegraphics{screenshot.png}`

### Section 4 — 개발 과정 및 설계 결정 상세 기록

- 개발 중 마주친 의사결정을 `\subsection` 단위로 기록
- 비교 실험이 있다면 `\subsection{... 비교 실험}` 안에서 표 + 결과 + 원인 분석
- before/after 코드 비교는 minted 로 두 블록 연달아 배치

### Section 5 — 테스트 결과

- `\subsection{소규모 데이터셋 (...)}`
- `\subsection{대규모 데이터셋 (...)}`
- `\subsection{범용성 검증}` (해당되는 경우)
- 결과는 booktabs + adjustbox 표로 정리, 통과 항목에 `\cmark` 사용

---

## 5. 표 / 코드 / 순서도 공통 양식

### 5.1 코드 블록

```latex
\begin{minted}{python}
def example():
    return 42
\end{minted}
```

- 행번호 포함, 자동 줄바꿈, 회색 배경, 좌우 라인 프레임.
- 짧은 인라인 코드/식별자: `\texttt{...}` 사용.

### 5.2 표 (booktabs + adjustbox)

```latex
\begin{table}[h]
\centering
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{ll}
\toprule
\textbf{항목} & \textbf{값} \\
\midrule
... & ... \\
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{표 설명}
\end{table}
```

- 가로줄은 `\toprule / \midrule / \bottomrule` 만 사용 (세로줄 금지).
- 폭이 넓은 표는 반드시 `adjustbox` 로 감싸 본문 너비에 맞춘다.

### 5.3 순서도 (TikZ)

```latex
\begin{figure}[h]
\centering
\begin{tikzpicture}[
    node distance=0.75cm and 2cm,
    box/.style={rectangle, rounded corners=5pt, draw=black!70, fill=blue!8,
                minimum width=9cm, minimum height=0.8cm,
                align=center, font=\small},
    loopbox/.style={rectangle, rounded corners=5pt, draw=black!60, fill=orange!10,
                    minimum width=9cm, minimum height=1.6cm,
                    align=center, font=\small},
    arr/.style={->, thick, draw=black!60}
]
\node[box] (start) {시작};
% ... 노드들 ...
\node[box] (end) {종료};
\draw[arr] (start) -- (...);
\end{tikzpicture}
\caption{알고리즘 전체 파이프라인}
\end{figure}
```

- 일반 단계는 `box` 스타일 (연한 파랑).
- 반복/재귀가 일어나는 핵심 단계는 `loopbox` 스타일 (연한 주황) 로 강조.

### 5.4 체크마크

검증 통과를 표기할 때는 `\cmark` 명령(프리앰블에 정의됨)을 사용한다.

---

## 6. 작성 규칙 (스타일 가이드)

- 본문 언어: 한국어. 알고리즘/함수/식별자 명은 영어 그대로 `\texttt{...}` 처리.
- 수식은 항상 LaTeX 수학 모드(`$...$`, `\[...\]`)로 표기.
- 코드 인용은 본문 흐름 안에서는 `\texttt{}`, 블록 단위는 `minted`.
- 표/그림에는 반드시 `\caption{}` 을 단다.
- 강조는 `\textbf{...}`, 중복 강조(이탤릭+볼드) 사용 금지.
- 각주(`\footnote`)는 가급적 사용하지 않고 본문 또는 itemize 로 흡수.
- 한 절(subsection) 내 itemize 는 핵심 설계 결정/근거 정리 용도로만 사용.
- 파일/명령어/경로는 모두 `\texttt{}` 로 감싼다 (`\_` 는 `\textbackslash` 가 아닌 `\_` 로 이스케이프).

---

## 7. 디렉터리 구조 (예시)

```
3rd_assignment/
├── <code>.py                 <- 실행 파일
├── <input1>.txt              <- 입력 데이터
├── <input2>.txt
├── <output>.txt              <- 결과 (실행 후 생성)
└── processing/
    ├── assignment3_report.tex   <- 본 양식을 적용한 보고서 소스
    ├── screenshot.png            <- 실행 화면 캡처
    └── _minted/                  <- minted 캐시 (자동 생성)
```

> 보고서 소스 파일명은 `assignment3_report.tex` 로 통일하여
> 2nd assignment(`assignment2_report.tex`) 와 명명 규칙을 맞춘다.

---

## 8. 새 보고서 시작용 스켈레톤

아래 블록을 그대로 복사해 `assignment3_report.tex` 의 시작점으로 사용한다.

```latex
\documentclass[12pt, a4paper]{article}

% ===== 패키지 ===== (위 §2 와 동일하게 복사)
\usepackage{fontspec}
\usepackage{kotex}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{minted}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{amsmath, amssymb}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{adjustbox}
\usepackage{pifont}
\newcommand{\cmark}{\ding{51}}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning}

\setminted[python]{bgcolor=black!5, linenos=true, breaklines=true,
    fontsize=\small, frame=lines, framesep=2mm}
\setminted[bash]{bgcolor=black!5, linenos=false, breaklines=true,
    fontsize=\small, frame=lines, framesep=2mm}

\begin{document}

\begin{center}
    {\Large\bfseries Programming Assignment \#3}\\[0.4em]
    {\large\bfseries <부제목>}\\[1em]
    {\normalsize
        \textbf{과목:} Data Science (ITE4005) \quad
        \textbf{학번:} 2023036299 \quad
        \textbf{이름:} 김진욱 \quad
        \textbf{<YYYY.MM.DD>}\\[0.3em]
        \textbf{OS:} Windows 10/11 \quad
        \textbf{Python:} 3.12.10 \quad
        \textbf{라이브러리:} <명세>
    }
\end{center}
\vspace{0.5em}
\hrule
\vspace{1em}

\section{알고리즘 요약}
\subsection{알고리즘 개요}
% ...
\subsection{전체 순서도}
% TikZ 다이어그램
\subsection{핵심 자료 흐름}
% verbatim 흐름도

\section{각 함수별 코드 상세 설명}
% \subsection{\texttt{func()} --- 한 줄 설명}

\section{소스 코드 컴파일 및 실행 방법}
\subsection{실행 환경}
\subsection{실행 명령어}
\subsection{실행 예시}
\subsection{파일 구조}
\subsection{실행 화면}

\section{개발 과정 및 설계 결정 상세 기록}
% \subsection{...}

\section{테스트 결과}
\subsection{소규모 데이터셋}
\subsection{대규모 데이터셋}
\subsection{범용성 검증}

\end{document}
```

---

## 9. 체크리스트 (제출 전 검수)

- [ ] XeLaTeX + `-shell-escape` 로 경고 없이 빌드되는가
- [ ] 헤더의 학번/이름/제출일/라이브러리 명세가 정확한가
- [ ] 5개 대섹션 구조가 유지되는가
- [ ] 모든 표가 booktapule (toprule/midrule/bottomrule) 사용 + caption 보유
- [ ] 모든 코드 블록이 `minted` 사용 + 언어 지정
- [ ] 함수 설명마다 "핵심 설계 결정" itemize 가 존재하는가
- [ ] 실행 화면 스크린샷이 `screenshot.png` 로 포함되었는가
- [ ] 한국어 본문 + 영어 식별자 `\texttt{}` 규칙이 일관되는가
