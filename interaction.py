import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import io

from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def render_interaction():

  st.title("📊 交互折线")

    # ==================================================
    # Upload Excel
    # ==================================================

    uploaded_file = st.file_uploader("📁 上传 Excel 文件", type=["xlsx"])

    df = pd.read_excel(uploaded_file)

    st.subheader("Preview")

    st.dataframe(df.head())

    excel_cols = df.columns.tolist()

    # ==================================================
    # Factor Settings
    # ==================================================

    st.header("Factor Settings")

    num_factors = st.number_input(
        "Number of Factors",
        min_value=2,
        max_value=3,
        value=2,
        step=1
    )

    factor_names = []
    factor_levels = {}

    for i in range(num_factors):

        st.markdown(f"### Factor {i+1}")

        factor_name = st.text_input(
            f"Factor {i+1} Name",
            value=f"Factor{i+1}",
            key=f"factor_name_{i}"
        )

        factor_names.append(factor_name)

        n_levels = st.number_input(
            f"Number of Conditions for {factor_name}",
            min_value=2,
            max_value=10,
            value=2,
            key=f"n_levels_{i}"
        )

        levels = []

        for j in range(n_levels):

            level = st.text_input(
                f"{factor_name} Condition {j+1}",
                value=f"{factor_name}_{j+1}",
                key=f"level_{i}_{j}"
            )

            levels.append(level)

        factor_levels[factor_name] = levels

    # ==================================================
    # Generate Combinations
    # ==================================================

    st.header("Column Mapping")

    combinations = list(
        itertools.product(
            *[
                factor_levels[f]
                for f in factor_names
            ]
        )
    )

    mapping = {}

    for combo in combinations:

        combo_name = " × ".join(combo)

        mapping[combo] = st.selectbox(
            f"{combo_name}",
            excel_cols,
            key=f"map_{combo_name}"
        )

    # ==================================================
    # X Axis / Line Factor
    # ==================================================

    st.header("Plot Settings")

    x_factor = st.selectbox(
        "X Axis Factor",
        factor_names
    )

    line_factor = st.selectbox(
        "Line Factor",
        [
            f
            for f in factor_names
            if f != x_factor
        ]
    )

    # ==================================================
    # Images
    # ==================================================

    st.header("Condition Images")

    image_dict = {}

    for level in factor_levels[x_factor]:

        image_dict[level] = st.file_uploader(
            f"Image for {level}",
            type=["png", "jpg", "jpeg"],
            key=f"img_{level}"
        )

    # ==================================================
    # Generate Plot
    # ==================================================

    if st.button("Generate Plot"):

        summary_rows = []

        for combo, col in mapping.items():

            mean_val = df[col].mean()

            sd_val = df[col].std()

            row = {}

            for i, factor in enumerate(factor_names):

                row[factor] = combo[i]

            row["Mean"] = mean_val
            row["SD"] = sd_val

            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows)

        st.subheader("Summary")

        st.dataframe(summary_df)

        # ==============================================
        # Plot
        # ==============================================

        fig, ax = plt.subplots(
            figsize=(14, 8)
        )

        x_levels = factor_levels[x_factor]

        line_levels = factor_levels[line_factor]

        x_pos = np.arange(len(x_levels))

        for line_level in line_levels:

            plot_df = summary_df[
                summary_df[line_factor]
                == line_level
            ]

            plot_df = (
                plot_df
                .set_index(x_factor)
                .reindex(x_levels)
            )

            means = plot_df["Mean"]

            sds = plot_df["SD"]

            ax.errorbar(
                x_pos,
                means,
                yerr=sds,
                marker="o",
                capsize=5,
                linewidth=2,
                label=line_level
            )

            for x, y in zip(x_pos, means):

                ax.text(
                    x,
                    y + 0.1,
                    f"{y:.2f}",
                    ha="center",
                    fontsize=9
                )

        ax.set_xticks(x_pos)

        ax.set_xticklabels(
            x_levels,
            rotation=15
        )

        ax.set_ylabel("Mean Score")

        ax.set_title(
            f"{line_factor} × {x_factor} Interaction Plot"
        )

        ax.legend()

        ax.grid(
            axis="y",
            alpha=0.3
        )

        # ==============================================
        # Images
        # ==============================================

        ymin, ymax = ax.get_ylim()

        image_y = ymin - (ymax - ymin) * 0.30

        ax.set_ylim(
            image_y,
            ymax
        )

        for i, level in enumerate(x_levels):

            img_file = image_dict.get(level)

            if img_file is None:
                continue

            img = Image.open(img_file)

            imagebox = OffsetImage(
                np.array(img),
                zoom=0.15
            )

            ab = AnnotationBbox(
                imagebox,
                (i, image_y),
                frameon=False,
                box_alignment=(0.5, 1)
            )

            ax.add_artist(ab)

        plt.tight_layout()

        st.pyplot(fig)

        # ==============================================
        # Download
        # ==============================================

        buffer = io.BytesIO()

        fig.savefig(
            buffer,
            dpi=300,
            bbox_inches="tight"
        )

        st.download_button(
            label="📥 Download PNG",
            data=buffer.getvalue(),
            file_name="interaction_plot.png",
            mime="image/png"
        )
