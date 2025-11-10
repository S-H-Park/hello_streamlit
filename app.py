import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Madang DB Viewer", layout="wide")

st.title("📚 Madang 데이터베이스 ")

DB_PATH = "madang.db"

@st.cache_resource
def get_connection():
    # read_only=True로 안전하게
    return duckdb.connect(DB_PATH, read_only=True)

con = get_connection()

# 테이블 목록 
tables_df = con.execute("SHOW TABLES").df()
table_names = tables_df["name"].tolist()

st.sidebar.header("테이블 & 모드 선택")

mode = st.sidebar.radio(
    "기능 선택",
    ["테이블 조회", "간단 리포트 (JOIN 예제)", "직접 SQL 쿼리"]
)

if mode == "테이블 조회":
    selected_table = st.sidebar.selectbox("테이블 선택", table_names)
    limit = st.sidebar.number_input("LIMIT", min_value=5, max_value=5000, value=100, step=5)

    st.subheader(f"테이블: `{selected_table}` (상위 {limit}행)")

    query = f"SELECT * FROM {selected_table} LIMIT {limit};"
    st.code(query, language="sql")

    df = con.execute(query).df()
    st.dataframe(df, use_container_width=True)

elif mode == "간단 리포트 (JOIN 예제)":
    st.subheader("💡 고객별 주문 요약 (예시)")

    query = """
        SELECT 
            c.CustomerID,
            c.Name,
            COUNT(DISTINCT o.OrderID) AS num_orders,
            SUM(o.qty) AS total_qty
        FROM Orders o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        GROUP BY c.CustomerID, c.Name
        ORDER BY num_orders DESC
        LIMIT 20;
    """
    st.code(query, language="sql")

    try:
        df = con.execute(query).df()
        st.dataframe(df, use_container_width=True)

        st.bar_chart(df.set_index("Name")["num_orders"])
    except Exception as e:
        st.error(f"JOIN 예제 실행 중 오류: {e}")
        st.info("Customer, Orders 테이블의 실제 컬럼명을 쿼리에 맞게 수정해줘야 할 수 있어요.")

else:  # 직접 SQL 쿼리
    st.subheader("🧪 직접 SQL 입력해서 실행")

    default_query = "SELECT * FROM Book LIMIT 10;"
    query = st.text_area("SQL 쿼리", value=default_query, height=180)

    if st.button("쿼리 실행"):
        try:
            df = con.execute(query).df()
            st.write(f"결과: {len(df)} rows")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"쿼리 실행 오류: {e}")
