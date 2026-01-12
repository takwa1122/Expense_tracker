import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import os

# =========================
# CONFIG
# =========================
FILE = "expenses.csv"

st.set_page_config(page_title="Expense Tracker", layout="wide")

# =========================
# BACKGROUND
# =========================
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

# =========================
# LOAD DATA
# =========================
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    df.to_csv(FILE, index=False)

# FIX DATE
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

# =========================
# CURRENT MONTH
# =========================
today = date.today()
df_month = df[
    (df["Date"].dt.month == today.month) &
    (df["Date"].dt.year == today.year)
]

# =========================
# TITLE
# =========================
st.markdown(
    "<h1 style='text-align:center;color:white;'>💰 Monthly Expense Tracker</h1>",
    unsafe_allow_html=True
)

# =========================
# ADD EXPENSE
# =========================
st.subheader("➕ Add Expense")

with st.form("expense_form"):
    d = st.date_input("Date", today)
    cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Utility", "Other"])
    amt = st.number_input("Amount", min_value=0.0, step=1.0)
    note = st.text_input("Note")

    submit = st.form_submit_button("Add")

    if submit:
        new = pd.DataFrame(
            [[d.strftime("%Y-%m-%d"), cat, amt, note]],
            columns=df.columns
        )
        df = pd.concat([df, new], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("✅ Expense added")
        st.rerun()

# =========================
# TOTAL
# =========================
total = df_month["Amount"].sum()

st.markdown(
    f"""
    <div style="background-color:rgba(255,255,255,0.6);
                padding:20px;border-radius:15px;text-align:center;">
        <h2>Total this month</h2>
        <h1 style="color:#FF4500;">${total:.2f}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# TABLE + DELETE
# =========================
st.subheader("📋 Expenses")

if df_month.empty:
    st.info("No expenses yet.")
else:
    df_display = df_month.reset_index(drop=True)

    selected = st.selectbox(
        "🗑️ Select an expense to delete",
        df_display.index,
        format_func=lambda i: f"{df_display.loc[i,'Date'].date()} | "
                               f"{df_display.loc[i,'Category']} | "
                               f"${df_display.loc[i,'Amount']} | "
                               f"{df_display.loc[i,'Note']}"
    )

    if st.button("Delete selected expense"):
        idx_to_delete = df_display.loc[selected].name
        df = df.drop(df_month.iloc[selected].name)
        df.to_csv(FILE, index=False)
        st.warning("❌ Expense deleted")
        st.rerun()

    st.dataframe(
        df_display.style.format({"Amount": "${:.2f}"}),
        height=250
    )

# =========================
# GRAPHS
# =========================
if not df_month.empty:
    st.subheader("📊 Spending by Category")

    fig_bar = px.bar(
        df_month,
        x="Category",
        y="Amount",
        color="Category",
        title="Spending by Category",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📈 Daily Spending")

    df_time = df_month.groupby("Date")["Amount"].sum().reset_index()
    fig_line = px.line(
        df_time,
        x="Date",
        y="Amount",
        markers=True,
        color_discrete_sequence=["#FF4500"]
    )
    fig_line.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_line, use_container_width=True)
