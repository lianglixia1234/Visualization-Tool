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
# 统计函数
# =====================
def calc_stats(values):

    values = pd.to_numeric(values, errors="coerce").dropna()

    n = len(values)

    if n == 0:
        return {
            "n":0,
            "mean":np.nan,
            "sd":np.nan,
            "se":np.nan,
            "ci_lower":np.nan,
            "ci_upper":np.nan
        }

    mean = values.mean()

    if n > 1:
        sd = values.std(ddof=1)
        se = sd / np.sqrt(n)

        t_value = t.ppf(
            0.975,
            df=n-1
        )

        ci = t_value * se

    else:
        sd = 0
        se = 0
        ci = 0

    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "se": se,
        "ci_lower": mean - ci,
        "ci_upper": mean + ci
    }


# =====================
# 主函数
# =====================
def render_interaction():

    st.title("📈 交互折线")

    uploaded_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx"]
    )

    if uploaded_file is None:
        st.info("Please upload Excel file")
        return

    df = pd.read_excel(uploaded_file)

    st.success("Excel Loaded")

    # =====================
    # Analysis Settings
    # =====================

    st.header("Analysis Settings")

    col1, col2 = st.columns(2)

    with col1:
        scale_min = st.number_input(
            "Scale Minimum",
            value=1.0
        )

    with col2:
        scale_max = st.number_input(
            "Scale Maximum",
            value=7.0
        )

    error_type = st.selectbox(
        "Error Bar",
        [
            "95% CI",
            "SEM",
            "SD"
        ]
    )

    # =====================
    # Factor Settings
    # =====================

    st.header("Factor Settings")

    factor1_name = st.text_input(
        "Factor 1 Name",
        "Factor A"
    )

    factor1_levels = st.text_input(
        "Factor 1 Levels (comma separated)",
        "A1,A2"
    )

    factor2_name = st.text_input(
        "Factor 2 Name",
        "Factor B"
    )

    factor2_levels = st.text_input(
        "Factor 2 Levels (comma separated)",
        "B1,B2"
    )

    factor1_levels = [
        x.strip()
        for x in factor1_levels.split(",")
    ]

    factor2_levels = [
        x.strip()
        for x in factor2_levels.split(",")
    ]

    combinations = list(
        itertools.product(
            factor1_levels,
            factor2_levels
        )
    )

    # =====================
    # Mapping
    # =====================

    st.header("Column Mapping")

    mapping = {}

    cols = df.columns.tolist()

    for combo in combinations:

        key = f"{combo[0]} × {combo[1]}"

        mapping[key] = st.selectbox(
            key,
            cols,
            key=key
        )

    selected_cols = list(mapping.values())

    if len(selected_cols) != len(set(selected_cols)):
        st.error("存在重复映射，请检查")
        return

    # =====================
    # Plot Settings
    # =====================

    st.header("Plot Settings")

    factors = [
        factor1_name,
        factor2_name
    ]

    x_factor = st.selectbox(
        "X Axis Factor",
        factors
    )

    remaining = [
        f for f in factors
        if f != x_factor
    ]

    line_factor = remaining[0]

    plot_title = st.text_input(
        "Plot Title",
        "Interaction Plot"
    )

    y_label = st.text_input(
        "Y Axis Label",
        "Score"
    )

    # ====================
    # Images
    # =====================
    
    st.header("Condition Images")
    
    # X轴水平对应的条件
    if x_factor == factor1_name:
        x_levels = factor1_levels
    else:
        x_levels = factor2_levels
    
    use_images = st.radio(
        "Do you want to add images under X-axis conditions?",
        ["No", "Yes"],
        horizontal=True
    )
    
    image_dict = {}
    
    if use_images == "Yes":
    
        image_size = st.slider(
            "Image Size",
            min_value=60,
            max_value=180,
            value=120,
            step=10
        )
    
        st.info("Upload one image for each X-axis condition")
    
        for level in x_levels:
    
            image_dict[level] = st.file_uploader(
                f"{level}",
                type=["png", "jpg", "jpeg"],
                key=f"img_{level}"
            )
    

    # =====================
    # Generate
    # =====================

    if st.button("Generate Plot"):

        stat_rows = []

        if x_factor == factor1_name:

            line_levels = factor2_levels

            for line in line_levels:

                for x in factor1_levels:

                    col_name = mapping[f"{x} × {line}"]

                    stats = calc_stats(df[col_name])

                    stats["line_group"] = line
                    stats["x_group"] = x

                    stat_rows.append(stats)

        else:

            line_levels = factor1_levels

            for line in line_levels:

                for x in factor2_levels:

                    col_name = mapping[f"{line} × {x}"]

                    stats = calc_stats(df[col_name])

                    stats["line_group"] = line
                    stats["x_group"] = x

                    stat_rows.append(stats)

        stat_df = pd.DataFrame(stat_rows)

        # =====================
        # Plot
        # =====================

        fig, ax = plt.subplots(
            figsize=(12,6.75)
        )

        for line in line_levels:

            subset = stat_df[
                stat_df["line_group"] == line
            ]

            y = subset["mean"].values

            if error_type == "95% CI":

                err = (
                    subset["ci_upper"] -
                    subset["mean"]
                ).values

            elif error_type == "SEM":

                err = subset["se"].values

            else:

                err = subset["sd"].values

            x = np.arange(len(x_levels))

            ax.errorbar(
                x,
                y,
                yerr=err,
                marker="o",
                capsize=5,
                linewidth=2,
                label=line
            )

            for xi, yi in zip(x, y):

                ax.text(
                    xi,
                    yi,
                    f"{yi:.2f}",
                    ha="center",
                    va="bottom"
                )

        ax.set_xticks(
            np.arange(len(x_levels))
        )

        ax.set_xticklabels(x_levels)

        ax.set_ylim(
            scale_min,
            scale_max
        )

        ax.set_title(plot_title)

        ax.set_ylabel(y_label)

        ax.grid(
            axis="y",
            alpha=0.3
        )

        ax.legend(
            title=line_factor
        )



        # =====================
        # 图片
        # =====================
        
        if use_images == "Yes":
        
            plt.subplots_adjust(
                bottom=0.35,
                left=0.08,
                right=0.97,
                top=0.90
            )
        
            for i, level in enumerate(x_levels):
        
                uploaded_img = image_dict.get(level)
        
                if uploaded_img:
        
                    TARGET_SIZE = (
                        image_size,
                        image_size
                    )
        
                    img = Image.open(
                        uploaded_img
                    ).convert("RGBA")
        
                    img.thumbnail(TARGET_SIZE)
        
                    canvas = Image.new(
                        "RGBA",
                        TARGET_SIZE,
                        (255, 255, 255, 0)
                    )
        
                    x_offset = (
                        TARGET_SIZE[0] - img.width
                    ) // 2
        
                    y_offset = (
                        TARGET_SIZE[1] - img.height
                    ) // 2
        
                    canvas.paste(
                        img,
                        (x_offset, y_offset),
                        img
                    )
        
                    imagebox = OffsetImage(
                        canvas,
                        zoom=1
                    )
        
                    ab = AnnotationBbox(
                        imagebox,
                        (i, scale_min),
                        frameon=False,
                        xybox=(0, -120),
                        boxcoords="offset points"
                    )
        
                    ax.add_artist(ab)
        
        else:
        
            plt.tight_layout()



        st.pyplot(fig)

        # =====================
        # PNG下载
        # =====================

        png_buffer = io.BytesIO()

        fig.savefig(
            png_buffer,
            dpi=300,
            bbox_inches="tight"
        )

        st.download_button(
            "Download PNG",
            png_buffer.getvalue(),
            file_name="interaction_plot.png",
            mime="image/png"
        )

        # =====================
        # Statistics Table
        # =====================

        st.subheader("Statistics")

        show_cols = [
            "line_group",
            "x_group",
            "n",
            "mean",
            "sd",
            "se",
            "ci_lower",
            "ci_upper"
        ]

        st.dataframe(
            stat_df[show_cols]
        )

        csv = stat_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Download Statistics CSV",
            csv,
            file_name="statistics.csv",
            mime="text/csv"
        )
