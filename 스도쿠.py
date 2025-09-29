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
# CSS 스타일 (칸 크기 줄이기 + 선 굵기 + 중앙정렬 + 글자 크기)
# --------------------
st.markdown("""
    <style>
    .sudoku-cell {
        width: 40px !important;
        height: 40px !important;
        text-align: center !important;
        font-size: 20px !important;
        border: 1px solid #bbb;
    }
    .sudoku-cell input {
        text-align: center;
        font-size: 20px !important;
    }
    .sudoku-block-top {
        border-top: 3px solid black !important;
    }
    .sudoku-block-left {
        border-left: 3px solid black !important;
    }
    .sudoku-block-right {
        border-right: 3px solid black !important;
    }
    .sudoku-block-bottom {
        border-bottom: 3px solid black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# Streamlit 앱 초기화
# --------------------
if "board" not in st.session_state:
    # 초기 완성 스도쿠 (9x9)
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

    # 무작위 숫자 치환
    perm = list(range(1,10))
    random.shuffle(perm)
    mapped = np.vectorize(lambda x: perm[x-1])(base)

    # 일정 비율 비우기
    p = 0.5  # 빈칸 확률
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

# 타이머 표시
if not st.session_state.finished:
    elapsed = int(time.time() - st.session_state.start_time)
else:
    elapsed = st.session_state.end_time - st.session_state.start_time
st.write(f"⏱ 경과 시간: {elapsed//3600:02}:{(elapsed%3600)//60:02}:{elapsed%60:02}")

# 퍼즐 그리드 (CSS 적용)
new_board = []
for i in range(9):
    row = []
    cols = st.columns(9, gap="small")
    for j in range(9):
        val = st.session_state.board[i][j]

        # 블록 선 굵기 적용
        classes = ["sudoku-cell"]
        if i % 3 == 0: classes.append("sudoku-block-top")
        if j % 3 == 0: classes.append("sudoku-block-left")
        if i == 8: classes.append("sudoku-block-bottom")
        if j == 8: classes.append("sudoku-block-right")

        cell_class = " ".join(classes)

        if val == "":
            row.append(cols[j].text_input("", key=f"cell-{i}-{j}", max_chars=1, label_visibility="collapsed"))
        else:
            # 물음표(tooltip) 제거 → markdown 사용
            cols[j].markdown(f"<div class='{cell_class}'>{val}</div>", unsafe_allow_html=True)
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
            st.warning("⚠️ 모든 칸을 숫자로 채워주세요!")
            st.stop()

        is_correct = True
        for i in range(9):
            if len(np.unique(user_board[i,:])) != 9 or len(np.unique(user_board[:,i])) != 9:
                is_correct = False
                break
        for i in range(0,9,3):
            for j in range(0,9,3):
                box = user_board[i:i+3,j:j+3].flatten()
                if len(np.unique(box)) != 9:
                    is_correct = False
                    break

        if is_correct:
            st.success("🎉 정답입니다!")
            st.session_state.finished = True
            st.session_state.end_time = int(time.time())
            name = st.text_input("이름을 입력하세요:", key="rank_name")
            if st.button("랭킹 등록"):
                if name:
                    add_ranking(name, st.session_state.end_time - st.session_state.start_time)
                    st.success("랭킹에 등록되었습니다!")
        else:
            st.error("❌ 오답입니다. 다시 시도하세요!")

with col3:
    if st.button("🏆 랭킹 보기"):
        rankings = load_ranking()
        if not rankings:
            st.info("아직 랭킹이 없습니다.")
        else:
            st.subheader("Top 10 Rankings")
            for i, r in enumerate(rankings[:10]):
                t = r['time']
                st.write(f"{i+1}. {r['name']} - {t//3600:02}:{(t%3600)//60:02}:{t%60:02}")
