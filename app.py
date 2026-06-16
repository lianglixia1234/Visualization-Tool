import streamlit as st
from mean_and_SD import render_mean_and_SD
from interaction import render_interaction

st.set_page_config(layout="wide")


def main():
    st.sidebar.title("导航")

    page = st.sidebar.radio(
        "选择模块",
        ["平均分+标准差","交互折线（被试内）","交互折线（混合）"]
    )

    if page == "平均分+标准差":
        render_mean_and_SD()
    elif  page == "交互折线（被试内）":
        render_interaction()
        
if __name__ == "__main__":
    main()
