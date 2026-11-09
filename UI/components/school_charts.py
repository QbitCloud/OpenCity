import matplotlib.pyplot as plt
import streamlit as st

from components.charts import COLORS, TEXT_COLOR


# school facilities graph
def school_facility_chart(labels, available_values, functional_values):
    if not labels:
        st.info("No facility data reported.")
        return

    figure, axis = plt.subplots(figsize=(6, 5))
    figure.patch.set_alpha(0)
    axis.set_facecolor("none")

    axis.barh(labels, available_values, height=0.35, align="edge",
              color=COLORS[0], label="Available")
    axis.barh(labels, functional_values, height=-0.35, align="edge",
              color=COLORS[1], label="Functional")

    axis.set_xlabel("Schools (%)", color=TEXT_COLOR)
    axis.set_xlim(0, 100)
    axis.tick_params(colors=TEXT_COLOR, length=0)
    axis.legend(frameon=False, labelcolor=TEXT_COLOR,
                loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2)

    for border in axis.spines.values():
        border.set_visible(False)

    figure.tight_layout()
    st.pyplot(figure)
    plt.close(figure)
