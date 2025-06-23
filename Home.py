# 📦 Import Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

# 📥 Load and Preprocess Data
# Load Excel Data
df = pd.read_excel("Raw Data.xlsx", sheet_name="Raw Data")
goals_df = pd.read_excel("Raw Data.xlsx", sheet_name="Goals")
goals_df.columns = goals_df.columns.str.strip()
goals_df.rename(columns={"Income Goal": "Income_Goal"}, inplace=True)

# Format & Feature Engineering
df["Date"] = pd.to_datetime(df["Date"])
df["Final Amount"] = df["Amount"] - df["Fee"]
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year
df["Paid %"] = pd.to_numeric(df["Paid %"].astype(str).str.replace("%", ""), errors="coerce").fillna(0) / 100
df["Payment Status"] = df["Payment Status"].astype(str).str.strip().str.lower()
years = sorted(df["Year"].unique())
months = sorted(df["Month"].unique())

# Outstanding Calculation
df["Outstanding"] = df.apply(
    lambda row: (1 - row["Paid %"]) * row["Final Amount"]
    if row["Payment Status"] in ["unpaid", "partial"]
    else 0,
    axis=1
)

# Days Due Calculation
df["Payment Due Date"] = pd.to_datetime(df["Payment Due Date"], errors="coerce")
today = pd.to_datetime(date.today())
df["Days Due"] = df.apply(
    lambda row: (today - row["Payment Due Date"]).days
    if row["Payment Status"] in ["unpaid", "partial"] and pd.notnull(row["Payment Due Date"])
    else None,
    axis=1
)

# Outstanding Payments Table
outstanding_df = df[df["Outstanding"] > 0][
    ["Client Name", "Project Details", "Paid %", "Outstanding", "Payment Status", "Days Due"]
]
outstanding_df["Paid %"] = (outstanding_df["Paid %"] * 100).round(0).astype(int)

# 🎯 Dashboard Header & Filters
st.title("💼 Freelancer Earnings Dashboard")
st.markdown("Track your income, projects, and productivity — all in one place.")

# Sidebar Filters
current_year = datetime.now().year
current_month = datetime.now().month

if "selected_year" not in st.session_state:
    st.session_state.selected_year = current_year
if "selected_month" not in st.session_state:
    st.session_state.selected_month = current_month

st.sidebar.title("📊 Filter Data")
year = st.sidebar.selectbox(
    "Select Year",
    options=["All"] + years,
    key="selected_year"
)

month = st.sidebar.selectbox(
    "Select Month",
    options=["All"] + months,
    key="selected_month"
)

# Refresh Button
with st.sidebar:
    if st.button("🔄 Refresh Dashboard"):
        st.cache_data.clear()
        st.rerun()

# Filter Data Based on Selection
if year != "All":
    df = df[df["Year"] == year]
if month != "All":
    df = df[df["Month"] == month]

# 🎯 Income Goal Progress (Gauge)
selected_year = year if year != "All" else datetime.now().year
selected_month = month if month != "All" else datetime.now().month

# Monthly Progress
df_filtered = df[df["Year"] == selected_year]
df_monthly = df_filtered[df_filtered["Month"] == selected_month]
actual_month = df_monthly["Final Amount"].sum()
goal_month_row = goals_df[(goals_df["Year"] == selected_year) & (goals_df["Month"] == selected_month)]
goal_month = goal_month_row["Income_Goal"].values[0] if not goal_month_row.empty else 0

# Yearly Progress
actual_year = df_filtered["Final Amount"].sum()
goal_year = goals_df[goals_df["Year"] == selected_year]["Income_Goal"].sum()

# Compute % Progress
month_progress = min(actual_month / goal_month * 100, 100) if goal_month > 0 else 0
year_progress = min(actual_year / goal_year * 100, 100) if goal_year > 0 else 0

# Display Gauges
st.subheader(f"📅 Goal Progress for {selected_year} — {datetime(1900, selected_month, 1).strftime('%B')}")
year_label = f"{year}" if year != "All" else "All Years"
col1, col2 = st.columns(2)

if not (year == "All" and month == "All"):
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=month_progress,
            number={'suffix': "%"},
            title={'text': f"Monthly ({actual_month:,.0f} / {goal_month:,.0f})"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc96"}}
        ))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📆 Select a specific month or year to view monthly goal progress.")

with col1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=year_progress,
        number={'suffix': "%"},
        title={'text': f"Yearly {year_label} ({actual_year:,.0f} / {goal_year:,.0f})"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc96"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# 📌 Summary Metrics
st.subheader("📌 Summary Metrics")

total_income = df["Final Amount"].sum()
total_hours = df["Actual Working Hours"].sum()
total_projects = df.shape[0]
unique_clients = df["Client Name"].nunique()
average_rate = df["Rate/Hour"].mean()

card_style = """
<style>
.metric-card-container {
    display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6; padding: 1.2rem; border-radius: 0.5rem;
    flex: 1; min-width: 180px; max-width: 250px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
.metric-label { font-size: 0.95rem; color: #6c757d; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.5rem; font-weight: bold; color: #212529; }
</style>
"""

cards_html = f"""
<div class="metric-card-container">
    <div class="metric-card"><div class="metric-label">💰 Total Income</div><div class="metric-value">${total_income:,.2f}</div></div>
    <div class="metric-card"><div class="metric-label">⏱️ Total Hours</div><div class="metric-value">{total_hours:.1f} hrs</div></div>
    <div class="metric-card"><div class="metric-label">📁 Projects</div><div class="metric-value">{total_projects}</div></div>
    <div class="metric-card"><div class="metric-label">👤 Clients</div><div class="metric-value">{unique_clients}</div></div>
    <div class="metric-card"><div class="metric-label">💵 Avg Rate/hr</div><div class="metric-value">${average_rate:.2f}</div></div>
</div>
"""
st.markdown(card_style, unsafe_allow_html=True)
st.write(cards_html, unsafe_allow_html=True)

# 1️⃣ Income Trend Over Time
st.subheader("1️⃣ Overall Income Performance")
income_over_time = df.groupby(df["Date"].dt.to_period("M"))["Final Amount"].sum().reset_index()
income_over_time["Date"] = income_over_time["Date"].dt.to_timestamp()
fig1 = px.line(income_over_time, x="Date", y="Final Amount", title="Total Income by Month")
st.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Client & Source Analytics
st.subheader("2️⃣ Client & Source Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    fig2 = px.bar(df.groupby("Client Name")["Final Amount"].sum().reset_index().sort_values(by="Final Amount", ascending=False),
                  x="Client Name", y="Final Amount", title="Income by Client")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    fig4 = px.bar(df.groupby("Source")["Client Name"].nunique().reset_index(name="Unique Clients").sort_values("Unique Clients", ascending=False),
                  x="Source", y="Unique Clients", title="Unique Clients per Source")
    st.plotly_chart(fig4, use_container_width=True)

with col3:
    fig5 = px.bar(df.groupby("Project Categories")["Client Name"].nunique().reset_index(name="Unique Clients").sort_values("Unique Clients", ascending=False),
                  x="Project Categories", y="Unique Clients", title="Unique Clients per Category")
    st.plotly_chart(fig5, use_container_width=True)

col4, col5, _ = st.columns(3)

with col4:
    fig3 = px.bar(df.groupby("Source")["Final Amount"].sum().reset_index().sort_values(by="Final Amount", ascending=False),
                  x="Source", y="Final Amount", title="Income by Source")
    st.plotly_chart(fig3, use_container_width=True)

with col5:
    fig_fee = px.bar(df.groupby("Source")["Fee"].sum().reset_index().sort_values(by="Fee", ascending=False),
                     x="Source", y="Fee", title="Total Fees by Source")
    st.plotly_chart(fig_fee, use_container_width=True)

# 3️⃣ Project & Category Insights
st.subheader("3️⃣ Project & Category Insights")

col7, col8, col9 = st.columns(3)

with col7:
    fig6 = px.bar(df.groupby("Project Categories")["Final Amount"].sum().reset_index().sort_values(by="Final Amount", ascending=False),
                  x="Project Categories", y="Final Amount", title="Income by Project Categories")
    st.plotly_chart(fig6, use_container_width=True)

with col8:
    fig9 = px.bar(df.groupby("Project Categories")["Rate/Hour"].mean().reset_index().sort_values(by="Rate/Hour", ascending=False),
                  x="Project Categories", y="Rate/Hour", title="Ave Hourly Rate by Category")
    st.plotly_chart(fig9, use_container_width=True)

with col9:
    fig7 = px.bar(df.groupby("Project Categories")["Actual Working Hours"].sum().reset_index().sort_values("Actual Working Hours", ascending=False),
                  x="Project Categories", y="Actual Working Hours", title="Top Time-Consuming Categories")
    st.plotly_chart(fig7, use_container_width=True)

# 4️⃣ Payment & Collection
st.subheader("4️⃣ Payment & Collection")

col10, col11 = st.columns([1, 2])

with col10:
    fig8 = px.pie(df, names="Payment Status", values="Final Amount", title="Payment Status Breakdown")
    st.plotly_chart(fig8, use_container_width=True)

with col11:
    st.markdown("#### 🔎 Outstanding Payments")
    st.dataframe(outstanding_df.sort_values(by="Outstanding", ascending=False), use_container_width=True)

# 📌 Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: left; font-size: 0.95rem;">
        📊 Love this dashboard and want to personalize it for your own? <br>
        📬 Reach out to me via <a href="mailto:msminyi@gmail.com">email</a> or connect via 
        <a href="https://www.linkedin.com/in/minyiyeo/" target="_blank">LinkedIn</a>.<br>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("© 2025 Built by Codinci Lab")
