import streamlit as st
import pandas as pd
from openpyxl import load_workbook

st.set_page_config(page_title="🎯 Goals", layout="wide")
st.title("🎯 Income Goals Editor")

excel_path = "Raw Data.xlsx"
sheet = "Goals"

# Load data
try:
    df = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl")
except:
    df = pd.DataFrame(columns=["Year", "Month", "Income Goal"])

# Add row selector
df["Delete"] = False
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="goals_editor"
)

# Save + Delete buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("💾 Save Changes"):
        try:
            save_df = edited_df.drop(columns=["Delete"])  # remove checkbox
            with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                save_df.to_excel(writer, sheet_name=sheet, index=False)
            st.success("✅ Saved successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error saving: {e}")

with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

with col3:
    if st.button("🗑️ Delete Selected Rows"):
        try:
            df_filtered = edited_df[~edited_df["Delete"]]  # keep unchecked rows
            df_filtered = df_filtered.drop(columns=["Delete"])
            with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df_filtered.to_excel(writer, sheet_name=sheet, index=False)
            st.success("🗑️ Selected rows deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error deleting: {e}")
