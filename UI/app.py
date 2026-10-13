import streamlit as st
from clients.client import check_backend


st.set_page_config(
    page_title="CS699 Project",
    page_icon="💻",
    layout="wide"
)

st.title("CS699 Project")
st.write("Welcome to the project dashboard!")

st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Page",
    ["Home", "About"]
)

if page == "Home":
    st.header("Home")
    st.write("Your project dashboard will appear here.")
    if st.button("Check Backend"):
        try:
            result = check_backend()
            st.success("Backend connected successfully!")
            st.json(result)
        except requests.RequestException:
            st.error("Backend connection failed.")

elif page == "About":
    st.header("About")
    st.write("This project uses FastAPI and Streamlit.")