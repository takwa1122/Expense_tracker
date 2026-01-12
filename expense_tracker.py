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
# BACKGROUND & MOBILE STYLING
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
    /* Mobile-friendly spacing and readability */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    h1, h2, h3 { text-align: center; color: #333 !important; }
    
    /* Card style for the form and metrics */
    .css-1r6slb0, .stForm {
        background-color: rgba(255, 255, 255, 0.4);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# DATA HANDLING
# =========================
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    return df

df = load_data()

# Filter for current month
today = date.today()
df_month = df[
    (df["Date"].dt.month == today.month) & 
    (df["Date"].dt.year == today.year)
].copy()

# =========================
# HEADER & TOTAL
# =========================
st.markdown("<h1>💰 My Expenses</h1>", unsafe_allow_html=True)

total = df_month["Amount"].sum()
st.markdown(
    f"""
    <div style="background-color:rgba(255,255,255,0.7); padding:15px; border-radius:15px; text-align:center; margin-bottom: 20px;">
        <p style="margin:0; font-size: 1.2rem; color: #555;">Spent this month</p>
        <h1 style="color:#D32F2F; margin:0; font-size: 2.5rem;">${total:,.2f}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# ADD EXPENSE (CENTERED)
# =========================
# Using columns to center the form on larger screens; it will stack on mobile.
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.markdown("### ➕ Add New")
    with st.form("expense_form", clear_on_submit=True):
        d = st.date_input("Date", today)
        cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Utility", "Other"])
        amt = st.number_input("Amount", min_value=0.0, step=1.0)
        note = st.text_input("Note")
        submit = st.form_submit_button("Save Expense", use_container_width=True)

    if submit:
        new_row = pd.DataFrame([[pd.to_datetime(d), cat, amt, note]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("Saved!")
        st.rerun()

# =========================
# ANALYTICS
# =========================
st.markdown("---")
if not df_month.empty:
    st.subheader("📊 Category View")
    fig_pie = px.pie(df_month, values='Amount', names='Category', hole=0.4)
    fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Recent Items")
    # Show the last 5 items added first for quick mobile check
    df_recent = df_month.sort_values(by="Date", ascending=False).head(10)
    st.dataframe(df_recent[["Date", "Category", "Amount"]], use_container_width=True)

    # DELETE SECTION
    with st.expander("🗑️ Delete an entry"):
        to_delete = st.selectbox(
            "Select to remove:",
            options=df_month.index,
            format_func=lambda x: f"{df_month.loc[x, 'Date'].date()} | {df_month.loc[x, 'Category']} | ${df_month.loc[x, 'Amount']}"
        )
        if st.button("Confirm Delete", use_container_width=True):
            df = df.drop(to_delete)
            df.to_csv(FILE, index=False)
            st.rerun()
else:
    st.info("No expenses found for this month.")
