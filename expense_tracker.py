import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

# =========================
# FILE PATH (Cloud Safe)
# =========================
FILE = "/tmp/expenses.csv"

# =========================
# LOAD / CREATE CSV
# =========================
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    df.to_csv(FILE, index=False)

# =========================
# DATE CONVERSION
# =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

today = date.today()
current_month = today.month
current_year = today.year

df_month = df[
    (df["Date"].dt.month == current_month) &
    (df["Date"].dt.year == current_year)
]

# =========================
# UI STYLE
# =========================
st.markdown("""
<style>
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.stApp {
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #a1c4fd, #c2e9fb);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown("<h1 style='text-align:center;color:white;'>💰 Expense Tracker</h1>", unsafe_allow_html=True)

# =========================
# FORM
# =========================
st.subheader("➕ Add Expense")

with st.form("expense_form"):
    d = st.date_input("Date", today)
    cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Other"])
    amt = st.number_input("Amount", min_value=0.0, step=1.0)
    note = st.text_input("Note")

    submitted = st.form_submit_button("Save Expense")

    if submitted:
        new = pd.DataFrame([[d, cat, amt, note]], columns=df.columns)
        df = pd.concat([df, new], ignore_index=True)
        df.to_csv(FILE, index=False)

        st.success("✅ Expense saved successfully!")
        st.rerun()

# =========================
# SUMMARY
# =========================
total = df_month["Amount"].sum()

st.markdown(f"""
<div style="background:rgba(255,255,255,0.6);
            padding:15px;
            border-radius:12px;
            text-align:center;">
    <h2>Total This Month</h2>
    <h1 style="color:#FF4500;">${total:.2f}</h1>
</div>
""", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.subheader("📋 Expenses List")
st.dataframe(df, use_container_width=True)

# =========================
# GRAPH
# =========================
if not df_month.empty:
    st.subheader("📊 Spending by Category")

    fig = px.bar(
        df_month,
        x="Category",
        y="Amount",
        color="Category",
        hover_data=["Note", "Date"]
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)
