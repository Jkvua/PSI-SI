import streamlit as st
#from view import 

st.set_page_config(
    page_title="PSI-SI", 
    page_icon=":bar_chart:", 
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)