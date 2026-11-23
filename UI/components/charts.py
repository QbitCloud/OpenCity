import io

import matplotlib.pyplot as plt
import streamlit as st


COLORS = ["#36a99a", "#e5b45e", "#629de3", "#a797df"]
TEXT_COLOR = "#ffffff"
# Every chart is drawn at the same size, so charts side by side line up
FIGURE_SIZE = (6, 5)


# Show a chart at its full figure size. st.pyplot crops each chart to its content,
# which gives charts of the same size different shapes.
def show_figure(figure):
    image = io.BytesIO()
    figure.savefig(image, format="png", dpi=200)
    st.image(image, width="stretch")
    plt.close(figure)

# Draw a pie chart from labelled values
def pie_chart(labels, values):
    if not values or sum(values) == 0:
        st.info("No data reported for this chart.")
        return

    figure, axis = plt.subplots(figsize=FIGURE_SIZE)
    figure.patch.set_alpha(0)
    axis.set_facecolor("none")
    axis.pie(
        values,
        colors=COLORS,
        # hocus pocus 
        autopct=lambda percent: f"{percent:.1f}%" if percent >= 5 else "",
        startangle=90,
        textprops={"color": "black"},
    )
    axis.legend(
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0),
        ncol=2,
        frameon=False,
        labelcolor=TEXT_COLOR,
    )
    figure.tight_layout()
    show_figure(figure)


# Draw a simple bar chart
def bar_chart(labels, values, value_unit=""):
    if not labels or not values:
        st.info("No data reported for this chart.")
        return

    figure, axis = plt.subplots(figsize=FIGURE_SIZE)
    figure.patch.set_alpha(0)
    axis.set_facecolor("none")

    axis.barh(labels, values, color=COLORS[0])
    axis.set_xlabel(value_unit, color=TEXT_COLOR)
    axis.set_ylabel("")
    axis.tick_params(colors=TEXT_COLOR, length=0)

    for border in axis.spines.values():
        border.set_visible(False)

    figure.tight_layout()
    show_figure(figure)
