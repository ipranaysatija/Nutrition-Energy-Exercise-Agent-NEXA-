import streamlit as st
import os
import json
from agents.LookOutAgent import extracter
st.title("Upload Files")

context = st.selectbox(
    "Select the context of this PDF",
    ["food_items","workouts","fat_reduction","others"]
)
if context:
    uploaded_file = st.file_uploader("Upload a file")

    if uploaded_file:
        
        if not os.path.exists("data/inputs"):
            os.makedirs("data/inputs")
        if not os.path.exists("data/inputs/" + uploaded_file.name):
            with open("data/inputs/" + uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            extracter("data/inputs/" + uploaded_file.name,context)
            st.success("File uploaded ✅")
        else:
            st.info("File already exists.")

    

    