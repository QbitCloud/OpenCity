import matplotlib.pyplot as plt
import streamlit as st

from components.charts import COLORS, FIGURE_SIZE, TEXT_COLOR, show_figure


# Two bars for each label, side by side
def paired_bar_chart(labels, first_values, second_values, first_name, second_name, value_unit):
    if not labels:
        st.info("No data reported for this chart.")
        return

    figure, axis = plt.subplots(figsize=FIGURE_SIZE)
    figure.patch.set_alpha(0)
    axis.set_facecolor("none")

    axis.barh(labels, first_values, height=0.35, align="edge",
              color=COLORS[0], label=first_name)
    axis.barh(labels, second_values, height=-0.35, align="edge",
              color=COLORS[1], label=second_name)

    axis.set_xlabel(value_unit, color=TEXT_COLOR)
    axis.tick_params(colors=TEXT_COLOR, length=0)
    axis.legend(frameon=False, labelcolor=TEXT_COLOR,
                loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2)

    for border in axis.spines.values():
        border.set_visible(False)

    figure.tight_layout()
    show_figure(figure)
