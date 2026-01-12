import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# ====== Animated background CSS ======
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

# ====== Load data ======
try:
    df = pd.read_csv("expenses.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# ====== Current Month ======
today = date.today()
current_month = today.month
current_year = today.year

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

df_month = df[
    (df["Date"].dt.month == current_month) &
    (df["Date"].dt.year == current_year)
]

# ====== Title ======
st.markdown(
    "<h1 style='text-align:center;color:white;'>💰 Monthly Expense Tracker</h1>",
    unsafe_allow_html=True
)

# ====== Manual Form ======
st.subheader("Add Expense")
with st.form("expense_form"):
    d = st.date_input("Date", today)
    cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Other"])
    amt = st.number_input("Amount", min_value=0.0, step=1.0)
    note = st.text_input("Note")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new = pd.DataFrame([[d, cat, amt, note]], columns=df.columns)
        df = pd.concat([df, new], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success(f"✅ Expense added: {cat} {amt} ({note})")

# ====== Monthly Summary ======
total_month = df_month["Amount"].sum()
st.markdown(
    f"""
    <div style="background-color:rgba(255,255,255,0.6);
                padding:15px;border-radius:10px;text-align:center;">
        <h2 style="color:#4B0082;">Total Spent This Month</h2>
        <h1 style="color:#FF4500;">${total_month:.2f}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ====== Table ======
st.subheader(f"Expenses for {today.strftime('%B %Y')}")
if not df_month.empty:
    st.dataframe(df_month.style.format({"Amount": "${:.2f}"}), height=250)
else:
    st.info("No expenses recorded this month yet.")

# ====== Interactive Graphs ======
if not df_month.empty:
    st.subheader("Spending by Category")
    fig_bar = px.bar(
        df_month,
        x="Category",
        y="Amount",
        color="Category",
        hover_data=["Note", "Date"],
        title="Spending by Category",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Spending Over Time")
    df_time = df_month.groupby("Date")["Amount"].sum().reset_index()
    fig_line = px.line(
        df_time,
        x="Date",
        y="Amount",
        markers=True,
        title="Daily Spending",
        color_discrete_sequence=["#FF4500"]
    )
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_line, use_container_width=True)
