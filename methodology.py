
import streamlit as st

st.set_page_config(page_title="Methodology", page_icon="ℹ️")

st.title("Methodology")

st.image("ingestion.png", caption="Ingestion flow")

st.image("chat.png", caption="Chat flow")

st.header("Listen in")
st.write("By using the job description based on sector, this is passed to google LM notebook to generate a podcast")