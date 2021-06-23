import streamlit as st
from app.pages.experimentation import experimentation
from app.pages.jd_generator import jd_generator
from app.pages.results import results

PAGES = ["JD Generator","Exp Page", "Results dashboard"]
page_select = st.sidebar.radio("Pages", options=PAGES)

if page_select == "Exp Page":
    st.title("GPT3 Experimentation")
    experimentation()
elif page_select == "JD Generator":
    st.title("JD Generator")
    jd_generator()
elif page_select == "Results dashboard":
    st.title("Results")
    results()
