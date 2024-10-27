import streamlit as st

st.set_page_config(page_title="About Skills Framework", page_icon="ℹ️")

st.title("Welcome to Skills Framework")

st.header("What This App Does")
st.write("""
This app is designed to help discover possible career based on a person's interest
""")

st.header("How to Use")
st.write("""
1. Just enter your interest in the chat
""")

st.header("Key Features")

st.subheader("Structured output")
st.write("Based on chat input, structure json output is produced. This will be used as part of hybrid search")

st.subheader("Hybrid search")
st.write("Fixed list of sector and tracks determined based on input, embedding of input is used to search against job description")

st.subheader("Summarization of possible job career")
st.write("After extraction of possible career from qdrant based on hybrid search, summary and a story of the jobs is generated.")


st.header("Data source")
st.write("Excel file from SSG(https://www.skillsfuture.gov.sg/docs/default-source/skills-framework/SkillsFramework_Dataset_2024_06.xlsx) is ingested into qdrant with job description been embedded.")