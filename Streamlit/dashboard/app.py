import pandas as pd
import streamlit as st

df = pd.read_csv("data/mentions.csv")

ticker = st.selectbox("Select ticker", df["ticker"].unique())

data = df[df["ticker"] == ticker]

st.line_chart(data["news_mentions"])
