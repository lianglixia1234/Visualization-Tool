import streamlit as st
from data_cleaning import render_data_cleaning

st.set_page_config(layout="wide")

def main():
    st.sidebar.title("导航")

    page = st.sidebar.radio(
        "选择模块",
        ["平均分+标准差"],
        ["夹持力客观主观"]
    )

    if page == "数据清洗":
        render_data_cleaning()

if __name__ == "__main__":
    main()
