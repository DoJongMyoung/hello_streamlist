import streamlit as st 
import duckdb
import pandas as pd
import time

# DuckDB 연결 (경로만 수정해서 사용)
conn = duckdb.connect("madangdb")

# pymysql 구조 흉내 내기 위한 query 함수
def query(sql):
    return conn.execute(sql).fetchdf()   # DataFrame 반환

# ---------------------------------------------
# 책 목록 불러오기 (Book → Book_madang 로 변경)
# ---------------------------------------------
books = [None]
result = query("SELECT bookid || ',' || bookname AS book_info FROM Book_madang")

for res in result['book_info']:
    books.append(res)

# ---------------------------------------------
# Streamlit 화면 구성
# ---------------------------------------------
tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

name = ""
custid = 999
result = pd.DataFrame()
name = tab1.text_input("고객명")
select_book = ""

# ---------------------------------------------
# 고객 조회
# ---------------------------------------------
if len(name) > 0:

    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer_madang c, Book_madang b, Orders_madang o
        WHERE c.custid = o.custid
        AND o.bookid = b.bookid
        AND c.name = '{name}';
    """

    result = query(sql)

    if not result.empty:
        tab1.write(result)
        custid = int(result['custid'][0])

        tab2.write("고객번호: " + str(custid))
        tab2.write("고객명: " + name)

        select_book = tab2.selectbox("구매 서적:", books)

        # ---------------------------------------------
        # 거래 입력
        # ---------------------------------------------
        if select_book is not None:

            bookid = select_book.split(",")[0]
            dt = time.strftime('%Y-%m-%d', time.localtime())

            # 최대 orderid 가져오기
            max_order = query("SELECT MAX(orderid) AS max_order FROM Orders_madang")
            maxid = max_order['max_order'][0]
            orderid = 1 if pd.isna(maxid) else int(maxid) + 1

            price = tab2.text_input("금액")

            if tab2.button('거래 입력') and price:

                sql = f"""
                    INSERT INTO Orders_madang(orderid, custid, bookid, saleprice, orderdate)
                    VALUES ({orderid}, {custid}, {bookid}, {price}, '{dt}');
                """
                conn.execute(sql)

                tab2.success('거래가 입력되었습니다.')

    else:
        tab1.warning("해당 고객의 구매 기록이 없습니다.")
