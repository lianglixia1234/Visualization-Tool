
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import io

from scipy.stats import t
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image



# =====================
# 中文字体
# =====================
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS"
]
plt.rcParams["axes.unicode_minus"] = False

# =====================



# =====================
# 主函数
# =====================
def render_interaction_mix():

    st.title("📈 交互折线（混合）")

    uploaded_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx"]
    )

    if uploaded_file is None:
        st.info("Please upload Excel file")
        return

    df = pd.read_excel(uploaded_file)

    st.success("Excel Loaded")


    # 被试间
    group_col = st.selectbox(
        "Between-subject Factor Column",
        df.columns
    )

    between_name = st.text_input(
        "Between-subject Factor Name",
        "Version"
    )

    group_labels = {}
    
    for level in group_levels:

    group_labels[level] = st.text_input(
        f"Meaning of {level}",
        str(level)
    )

    # 被试内
    within_name = st.text_input(
        "Within-subject Factor Name",
        "Scenario"
    )

    n_levels = st.number_input(
        "Number of Within Levels",
        min_value=2,
        value=3
    )



    within_levels = []
    condition_cols = []




    for i in range(n_levels):
    
        level = st.text_input(
            f"Level {i+1} Name",
            f"Condition{i+1}"
        )
    
        col = st.selectbox(
            f"Column for {level}",
            df.columns,
            key=f"col_{i}"
        )
    
        within_levels.append(level)
        condition_cols.append(col)


    records = []
    
    for g in group_levels:
    
        subset = df[
            df[group_col] == g
        ]
    
        for level, col in zip(
            within_levels,
            condition_cols
        ):
    
            values = subset[col].dropna()
    
            n = len(values)
    
            mean = values.mean()
    
            sd = values.std(ddof=1)
    
            se = sd / np.sqrt(n)
    
            ci = (
                t.ppf(0.975, n - 1)
                * se
            )
    
            records.append({
                "group": g,
                "condition": level,
                "mean": mean,
                "sd": sd,
                "se": se,
                "ci": ci
            })

          error_type = st.selectbox(
              "Error Bar",
              [
                  "SEM",
                  "95% CI",
                  "SD"
              ]
          )

        fig, ax = plt.subplots(
            figsize=(8,6)
        )
        
        x = np.arange(
            len(within_levels)
        )
        
        width = 0.35
        
        for i, g in enumerate(group_levels):
        
            subset = stats_df[
                stats_df["group"] == g
            ]
    
        if error_type == "95% CI":
            err = subset["ci"]
    
        elif error_type == "SEM":
            err = subset["se"]
    
        else:
            err = subset["sd"]
    
        ax.bar(
            x + i*width,
            subset["mean"],
            width,
            yerr=err,
            capsize=5,
            label=group_labels[g]
        )
    
    ax.set_xticks(
        x + width/2
    )
    
    ax.set_xticklabels(
        within_levels
    )
