import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import io

from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def render_mean_and_SD():
    # =========================
    # 页面设置
    # =========================
    st.title("📊 平均值+标准差")
    st.write("Only support English: make sure all input are in English")
    
    # =========================
    # 上传 Excel
    # =========================
    uploaded_file = st.file_uploader("📁 上传 Excel 文件", type=["xlsx"])
    
    # =========================
    # 侧边栏参数
    # =========================
    st.sidebar.header("📌 图表参数设置")
    
    # Y轴范围
    Y_MIN = st.sidebar.number_input("Y轴最小值", value=1, step=1)
    Y_MAX = st.sidebar.number_input("Y轴最大值", value=7, step=1)
    
    # =========================
    # 标题设置（多行）
    # =========================
    st.sidebar.subheader("📝 标题设置")
    
    title_lines_num = st.sidebar.number_input(
        "标题行数",
        min_value=1,
        max_value=5,
        value=2,
        step=1
    )
    
    title_lines = []
    for i in range(int(title_lines_num)):
        line = st.sidebar.text_input(f"标题第 {i+1} 行", value="")
        title_lines.append(line)
    
    TITLE = "\n".join(title_lines)
    
    # Y轴标题
    Y_LABEL = st.sidebar.text_input(
        "Y轴标题",
        value=""
    )
    
    # ========================
    # 评分说明（逐条输入）
    # =========================
    st.sidebar.subheader("⭐ 评分说明（逐条填写）")
    
    score_labels = {}
    
    for i in range(int(Y_MIN), int(Y_MAX) + 1):
        score_labels[i] = st.sidebar.text_input(f"{i}分说明", value="")
    
    # 生成右侧文本
    score_text = "Score Meaning\n\n"
    for i in range(int(Y_MIN), int(Y_MAX) + 1):
        label = score_labels[i] if score_labels[i] else "(not defined)"
        score_text += f"{i} = {label}\n"
    
    st.sidebar.subheader(" 👈 调整图的长宽")
    
    FIG_WIDTH = st.sidebar.slider(
        "图宽度",
        min_value=4,
        max_value=20,
        value=8
    )
    
    FIG_HEIGHT = st.sidebar.slider(
        "图高度",
        min_value=4,
        max_value=15,
        value=6
    )
    
    
    # =========================
    # 主逻辑
    # =========================
    if uploaded_file is not None:
    
        df = pd.read_excel(uploaded_file)
    
        st.write("### 📄 数据预览")
        st.dataframe(df)
    
        # 只取数值列（避免报错）
        df_numeric = df.select_dtypes(include=np.number)
    
        conditions = df_numeric.columns.tolist()
    
        means = df_numeric.mean()
        sds = df_numeric.std()
        maxs = df_numeric.max()
        mins = df_numeric.min()
    
        # 蓝色渐变色
        colors = plt.cm.Blues(np.linspace(0.45, 0.85, len(conditions)))
        
        # 改变图的大小
        fig, ax = plt.subplots(
            figsize=(FIG_WIDTH, FIG_HEIGHT)
        )
        x = np.arange(len(conditions))
    
        # 关键：给右侧说明留空间
        plt.subplots_adjust(right=0.70)
    
        # =========================
        # 柱状图 + error bar
        # =========================
        ax.bar(
            x,
            means,
            yerr=sds,
            width=0.3,
            capsize=8,
            color=colors,
            edgecolor="black",
            linewidth=1.2
        )
    
        # mean点
        ax.scatter(x, means, color="black", s=70, zorder=5)
    
        # 最大最小值
        for j, mean in enumerate(means):
            ax.text(
            j + 0.08,      # 向右偏移
            mean,          # 与均值点同高
            f"Mean={mean:.2f}",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
            bbox=dict(
                facecolor="white",
                alpha=0.8,
                edgecolor="none"
            )
        )
        
        # 最大最小值
        for i in range(len(conditions)):
            
            
            ax.hlines(
                y=maxs.iloc[i],
                xmin=i-0.25,
                xmax=i+0.25,
                colors="#1B4F72",
                linestyles="--",
                linewidth=2,
                zorder=4
            )
        
            ax.text(
                i,
                maxs.iloc[i] + 0.08,
                f"Max={maxs.iloc[i]:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#1B4F72",
                fontweight="bold",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none")
            )
        
            ax.hlines(
                y=mins.iloc[i],
                xmin=i-0.25,
                xmax=i+0.25,
                colors="#AED6F1",
                linestyles="--",
                linewidth=2,
                zorder=4
            )
        
            ax.text(
                i,
                mins.iloc[i] - 0.08,
                f"Min={mins.iloc[i]:.1f}",
                ha="center",
                va="top",
                fontsize=9,
                color="#2980B9",
                fontweight="bold",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none")
            )
    
        # =========================
        # 坐标轴设置
        y_min_data = mins.min()
        y_max_data = maxs.max()
        
        ax.set_ylim(
            min(Y_MIN, y_min_data) ,   # 👈 下方留白
            max(Y_MAX, y_max_data)
        )
        
        ax.set_ylabel(
            Y_LABEL,
            fontsize=13,
            fontweight="bold"
        )
    
        # X轴标签
        ax.set_xticks(x)
        ax.tick_params(axis='x', pad=15)
        ax.set_xticklabels(
            conditions,
            fontsize=12
        )
        
        # ==================================================
        # 网格
        # ==================================================
        
        ax.grid(
            axis="y",
            linestyle=":",
            alpha=0.4
        )
        
        ax.set_axisbelow(True)
    
        # =========================
        # 右侧评分说明框
        # =========================
        ax.text(
            1.2, 0.5,   # ← 关键：往右移
            score_text,
            transform=ax.transAxes,
            va="center",
            ha="left",
            fontsize=10,
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="white",
                edgecolor="black",
                alpha=0.9
            )
        )
    
        
        # 控制的是标题与绘图区之间的距离
        ax.set_title(
            TITLE,
            fontsize=14,
            fontweight="bold",
            pad=35
        )
    
        # 美化边框
        # ==================================================
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        # ==================================================
        # 自动布局
        # ==================================================
        
        plt.tight_layout()
        
        # =========================
        # 显示图
        # =========================
        st.pyplot(fig)
    
        # =========================
        # 下载 PNG
        # =========================
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    
        st.download_button(
            label="📥 下载 PNG 图片",
            data=buf.getvalue(),
            file_name="flicker_plot.png",
            mime="image/png"
        )
    
    else:
        st.info("请先上传 Excel 文件")
