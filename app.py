import streamlit as st
from mean_and_SD import render_mean_and_SD

st.set_page_config(layout="wide")


def main():
    st.sidebar.title("导航")

    page = st.sidebar.radio(
        "选择模块",
        ["平均分+标准差"],
        ["夹持力客观主观"]
    )

    if page == "平均分+标准差":
        render_mean_and_SD()

if __name__ == "__main__":
    main()
