import streamlit as st
import pandas as pd
from openpyxl import load_workbook

st.set_page_config(page_title="📄 Raw Data Editor", layout="wide")
st.title("📄 Raw Data Editor")

excel_path = "Raw Data.xlsx"
sheet = "Raw Data"

# Load raw data
try:
    df = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl")
except:
    df = pd.DataFrame(columns=[
        "Invoice Number","Date", "Source", "Client Name", "Project Categories", "Project Details",
        "Amount", "Fee","Paid %" ,"Payment Method", "Payment Status", "Payment Due Date",
        "Expected Working Hours", "Actual Working Hours"
    ])

# Convert date column and sort
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values(by="Date", ascending=False)

# Calculate derived fields
df["Final Amount"] = df["Amount"] - df["Fee"]
df["Rate/Hour"] = df["Final Amount"] / df["Actual Working Hours"]
df["Delete"] = False  # for deletion checkbox

# Streamlit editable grid
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="raw_data_editor",
    column_config={
        "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Bank Transfer", "PayPal", "Cash", "Others"]),
        "Payment Status": st.column_config.SelectboxColumn("Payment Status", options=["Paid", "Unpaid", "Partial"]),
        "Final Amount": st.column_config.NumberColumn("Final Amount (calculated)", disabled=True),
        "Rate/Hour": st.column_config.NumberColumn("Rate/Hour (calculated)", disabled=True),
        "Delete": st.column_config.CheckboxColumn("Delete")
    }
)

# Recalculate formulas after edit
edited_df["Final Amount"] = edited_df["Amount"] - edited_df["Fee"]
edited_df["Rate/Hour"] = edited_df["Final Amount"] / edited_df["Actual Working Hours"]

# Buttons
col1, col2, col3 = st.columns([1, 1,1])
with col1:
    if st.button("💾 Save Changes"):
        try:
            save_df = edited_df.drop(columns=["Delete"])
            with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                save_df.to_excel(writer, sheet_name=sheet, index=False)
            st.success("✅ Raw data saved successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error saving: {e}")

with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

with col3:
    if st.button("🗑️ Delete Selected Rows"):
        try:
            filtered_df = edited_df[~edited_df["Delete"]].drop(columns=["Delete"])
            with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                filtered_df.to_excel(writer, sheet_name=sheet, index=False)
            st.success("🗑️ Selected rows deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error deleting: {e}")
