import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from telegram import Bot
import plotly.express as px
# ====== Telegram setup ======
TELEGRAM_TOKEN = ""
CHAT_ID = ""
bot = Bot(TELEGRAM_TOKEN)
#bot.send_message(chat_id=CHAT_ID, text="Bonjour Takwa 👋 Ton bot fonctionne !")

# ====== Animated background CSS ======
st.markdown(
    """
    <style>
    /* Animated gradient background */
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
df["Date"] = pd.to_datetime(df["Date"])
df_month = df[
    (df["Date"].dt.month == current_month) &
    (df["Date"].dt.year == current_year)
]

# ====== Reset for new month ======
if df_month.empty and not df.empty and df["Date"].dt.month.max() < current_month:
    df = pd.DataFrame(columns=df.columns)
    df.to_csv("expenses.csv", index=False)

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

# ====== Monthly Summary Card ======
total_month = df_month["Amount"].sum()
st.markdown(
    f"""
    <div style="background-color:rgba(255,255,255,0.6);padding:15px;border-radius:10px;text-align:center;">
        <h2 style="color:#4B0082;">Total Spent This Month</h2>
        <h1 style="color:#FF4500;">${total_month:.2f}</h1>
    </div>
    """, unsafe_allow_html=True
)

# ====== Show Monthly Table ======
st.subheader(f"Expenses for {today.strftime('%B %Y')}")
if not df_month.empty:
    st.dataframe(df_month.style.format({"Amount": "${:.2f}"}), height=250)
else:
    st.info("No expenses recorded this month yet.")

# ====== Interactive Graphs with Plotly ======
if not df_month.empty:
    # ----- Bar Chart: Spending by Category -----
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
        title_font=dict(size=22, color='white'),
        xaxis_title_font=dict(size=16, color='white'),
        yaxis_title_font=dict(size=16, color='white'),
        legend_title_font=dict(size=14, color='white'),
        font=dict(color='white')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ----- Line Chart: Spending Over Time -----
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
    fig_line.update_traces(marker=dict(size=10))
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=22, color='white'),
        xaxis_title_font=dict(size=16, color='white'),
        yaxis_title_font=dict(size=16, color='white'),
        font=dict(color='white')
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ====== Telegram Monthly Summary ======
if today.day == pd.Timestamp(today).days_in_month:
    message = f"💰 Your expenses for {today.strftime('%B %Y')}:\nTotal: {total_month}\n\n"
    for _, row in df_month.iterrows():
        message += f"{row['Date'].strftime('%d-%m')} - {row['Category']}: {row['Amount']} ({row['Note']})\n"
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        st.success("Telegram summary sent!")
    except Exception as e:
        st.error(f"Failed to send Telegram message: {e}")
