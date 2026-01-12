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
# BACKGROUND (CSS)
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
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    /* Make text more readable on colors */
    h1, h2, h3, p, label { color: white !important; }
    .stDataFrame { background-color: rgba(255,255,255,0.1); border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# LOAD DATA
# =========================
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)
        df["Date"] = pd.to_datetime(df["Date"]) # Ensure datetime type
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    return df

df = load_data()

# =========================
# CURRENT MONTH FILTER
# =========================
today = date.today()
# Filter for current month using a copy to avoid SettingWithCopy warnings
df_month = df[
    (df["Date"].dt.month == today.month) & 
    (df["Date"].dt.year == today.year)
].copy()

# =========================
# TITLE
# =========================
st.markdown("<h1 style='text-align:center;'>💰 Monthly Expense Tracker</h1>", unsafe_allow_html=True)

# =========================
# ADD EXPENSE
# =========================
with st.sidebar:
    st.header("➕ Add Expense")
    with st.form("expense_form", clear_on_submit=True):
        d = st.date_input("Date", today)
        cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Utility", "Other"])
        amt = st.number_input("Amount", min_value=0.0, step=1.0)
        note = st.text_input("Note")
        submit = st.form_submit_button("Add Expense")

    if submit:
        new_row = pd.DataFrame([[pd.to_datetime(d), cat, amt, note]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("Expense added!")
        st.rerun()

# =========================
# METRICS
# =========================
total = df_month["Amount"].sum()
st.markdown(
    f"""
    <div style="background-color:rgba(255,255,255,0.2); padding:20px; border-radius:15px; text-align:center; border: 1px solid white;">
        <h2 style="margin:0;">Total this month</h2>
        <h1 style="color:#FFFFFF; font-size: 50px;">${total:,.2f}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# DISPLAY & DELETE
# =========================
st.subheader("📋 Monthly Breakdown")

if not df_month.empty:
    # We display df_month but use the original index to delete from 'df'
    df_display = df_month.copy()
    df_display["Display_Date"] = df_display["Date"].dt.date
    
    # Select box to choose which row to delete
    to_delete = st.selectbox(
        "Select an expense to delete",
        options=df_month.index,
        format_func=lambda x: f"{df_month.loc[x, 'Date'].date()} - {df_month.loc[x, 'Category']}: ${df_month.loc[x, 'Amount']}"
    )
    
    if st.button("🗑️ Delete Selected"):
        df = df.drop(to_delete)
        df.to_csv(FILE, index=False)
        st.rerun()

    st.dataframe(df_month, use_container_width=True)
else:
    st.info("No expenses recorded for this month yet.")

# =========================
# GRAPHS
# =========================
if not df_month.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.pie(df_month, values='Amount', names='Category', title="Expenses by Category")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        df_daily = df_month.groupby("Date")["Amount"].sum().reset_index()
        fig_line = px.line(df_daily, x="Date", y="Amount", title="Daily Spending Trend")
        fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_line, use_container_width=True)
