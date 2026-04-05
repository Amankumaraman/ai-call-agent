#!/usr/bin/env python
# file: dashboard.py

import streamlit as st
import requests
import pandas as pd

st.title("AI Call Agent")

ngrok_url = st.text_input(
    "Enter ngrok url",
    placeholder="https://xxxx.ngrok-free.app"
)

phone = st.text_input(
    "Customer phone",
    placeholder="+91xxxxxxxxxx"
)

if st.button("Start Call"):

    requests.post(

        "http://localhost:8000/call",

        json={
            "phone": phone,
            "ngrok_url": ngrok_url
        }
    )

    st.success("Calling...")


st.divider()

st.subheader("Leads")

try:

    df = pd.read_csv("leads.csv")

    st.dataframe(df)

except:

    st.write("No leads yet")