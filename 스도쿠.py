import streamlit as st
import numpy as np
import random
import json
import os
import time

# --------------------
# 랭킹 관련 함수
# --------------------
RANK_FILE = "ranking.json"

def load_ranking():
    if os.path.exists(RANK_FILE):
        try:
            with open(RANK_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_ranking(rankings):
    with open(RANK_FILE, "w") as f:
        json.dump(rankings, f, indent=4)

def add_ranking(name, seconds):
    rankings = load_ranking()
    rankings.append({"name": name, "time": seconds})
    rankings.sort(key=lambda x: x["time"])
    save_ranking(rankings)

# --------------------
# CSS 스타일
# --------------------
st.markdown("""
    <style>
    .sudoku-cell {
        width: 40px !important;
        height: 40px !important;
        text-align: center !important;
        font-size: 22px !important;
        border: 1px solid #ccc;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #ffffff;
    }
    .sudoku-cell input {
        text-align: center;
        font-size: 22px !important;
        color: blue !important;
    }
    /* 블록 굵은 선 */
    .sudoku-block-top    { border-top: 2px solid black !important; }
    .sudoku-block-left   { border-left: 2px solid black !important; }
    .sudoku-block-right  { border-right: 2px solid black !important; }
    .sudoku-block-bottom { border-bottom: 2px solid black !important; }

    /* 3x3 블록 배경 번갈아 적용 */
    .block-alt {
        background-color: #f7f7f7;
    }
    /* 채워진 숫자 */
    .prefilled {
        color: black;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# 초기화
# --------------------
if "board" not in st.session_state:
    base = np.array([
        [1,2,3,4,5,6,7,8,9],
        [4,5,6,7,8,9,1,2,3],
        [7,8,9,1,2,3,4,5,6],
        [2,3,4,5,6,7,8,9,1],
        [5,6,7,8,9,1,2,3,4],
        [8,9,1,2,3,4,5,6,7],
        [3,4,5,6,7,8,9,1,2],
        [6,7,8,9,1,2,3,4,5],
        [9,1,2,3,4,5,6,7,8]
    ])

    # 무작위 치환
    perm = list(range(1,10))
    random.shuffle(perm)
    mapped = np.vectorize(lambda x: perm[x-1])(base)

    # 빈칸 만들기
    p = 0.5
    puzzle = mapped.copy().astype("object")
    mask = np.random.rand(9,9) < p
    puzzle[mask] = ""

    st.session_state.board = puzzle
    st.session_state.solution = mapped
    st.session_state.start_time = time.time()
    st.session_state.finished = False

# --------------------
# UI
# --------------------
st.title("🧩 Sudoku (Streamlit 버전)")
st.write("빈칸에 숫자를 채워 스도쿠를 완성해보세요!")

# 타이머
if not st.session_state.finished:
    elapsed = int(time.time() - st.session_state.start_time)
else:
    elapsed = st.session_state.end_time - st.session_state.start_time
st.write(f"⏱ 경과 시간: {elapsed//3600:02}:{(elapsed%3600)//60:02}:{elapsed%60:02}")

# 보드 표시
new_board = []
for i in range(9):
    row = []
    cols = st.columns(9, gap="small")
    for j in range(9):
        val = st.session_state.board[i][j]

        # 블록 선 스타일
        classes = ["sudoku-cell"]
        if i % 3 == 0: classes.append("sudoku-block-top")
        if j % 3 == 0: classes.append("sudoku-block-left")
        if i == 8: classes.append("sudoku-block-bottom")
        if j == 8: classes.append("sudoku-block-right")

        # 블록 배경 교차
        if (i//3 + j//3) % 2 == 0:
            classes.append("block-alt")

        cell_class = " ".join(classes)

        if val == "":
            row.append(cols[j].text_input("", key=f"cell-{i}-{j}", max_chars=1, label_visibility="collapsed"))
        else:
            cols[j].markdown(f"<div class='{cell_class} prefilled'>{val}</div>", unsafe_allow_html=True)
            row.append(val)
    new_board.append(row)

# 버튼 영역
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 새 게임"):
        st.session_state.clear()
        st.experimental_rerun()

with col2:
    if st.button("✅ 정답 확인"):
        try:
            user_board = np.array([
                [int(x) if x != "" else 0 for x in row]
                for row in new_board
            ])
        except ValueError:
            st.wa
