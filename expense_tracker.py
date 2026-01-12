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
    /* Mobile formatting */
    h1, h2, h3 { text-align: center; color: #333 !important; }
    .stForm {
        background-color: rgba(255, 255, 255, 0.5);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.7);
    }
    /* Make buttons larger for thumbs */
    .stButton button {
        height: 3em;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# DATA HANDLING
# =========================
def load_data():
    columns = ["Date", "Category", "Amount", "Note"]
    if os.path.exists(FILE):
        try:
            temp_df = pd.read_csv(FILE)
            if temp_df.empty:
                return pd.DataFrame(columns=columns)
            temp_df["Date"] = pd.to_datetime(temp_df["Date"])
            return temp_df
        except Exception:
            # If file is corrupted or unreadable, return empty structure
            return pd.DataFrame(columns=columns)
    else:
        # Create the file if it doesn't exist
        empty_df = pd.DataFrame(columns=columns)
        empty_df.to_csv(FILE, index=False)
        return empty_df

df = load_data()

# Filter for current month
today = date.today()
if not df.empty:
    # Convert series to datetime just in case of format mismatches
    df["Date"] = pd.to_datetime(df["Date"])
    df_month = df[
        (df["Date"].dt.month == today.month) & 
        (df["Date"].dt.year == today.year)
    ].copy()
else:
    df_month = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# =========================
# HEADER & TOTAL
# =========================
st.markdown("<h1>💰 My Expenses</h1>", unsafe_allow_html=True)

total = df_month["Amount"].sum() if not df_month.empty else 0.0
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
col1, col2, col3 = st.columns([1, 8, 1])

with col2:
    st.markdown("### ➕ Add New")
    with st.form("expense_form", clear_on_submit=True):
        d = st.date_input("Date", today)
        cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Shopping", "Utility", "Other"])
        amt = st.number_input("Amount", min_value=0.0, step=1.0)
        note = st.text_input("Note")
        submit = st.form_submit_button("Save Expense", use_container_width=True)

    if submit:
        # Create new entry with correct format
        new_row = pd.DataFrame({
            "Date": [pd.to_datetime(d)],
            "Category": [cat],
            "Amount": [amt],
            "Note": [note]
        })
        # Concatenate and save
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("Expense Saved!")
        st.rerun()

# =========================
# ANALYTICS & RECENT LIST
# =========================
st.markdown("---")
if not df_month.empty:
    # 1. VISUALIZATION
    st.subheader("📊 Category View")
    fig_pie = px.pie(df_month, values='Amount', names='Category', hole=0.4)
    fig_pie.update_layout(
        margin=dict(l=20, r=20, t=20, b=20), 
        height=300,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # 2. DATA TABLE
    st.subheader("📋 Recent Items")
    df_recent = df_month.sort_values(by="Date", ascending=False)
    # Clean up date for display
    df_recent["Date"] = df_recent["Date"].dt.strftime('%Y-%m-%d')
    st.dataframe(
        df_recent[["Date", "Category", "Amount", "Note"]], 
        use_container_width=True, 
        hide_index=True
    )

    # 3. DELETE OPTION
    with st.expander("🗑️ Delete an entry"):
        to_delete = st.selectbox(
            "Choose item to remove:",
            options=df_month.index,
            format_func=lambda x: f"{df_month.loc[x, 'Date'].date()} | {df_month.loc[x, 'Category']} | ${df_month.loc[x, 'Amount']}"
        )
        if st.button("Confirm Delete", use_container_width=True):
            # Drop from main df and save
            df = df.drop(to_delete)
            df.to_csv(FILE, index=False)
            st.rerun()
else:
    st.info("Your list is currently empty. Use the form above to add your first expense!")
