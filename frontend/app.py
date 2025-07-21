# frontend/app.py

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from io import BytesIO
from sqlalchemy import create_engine

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🧾 Smart Receipt Analyzer", layout="wide")

# ---------- Sidebar ----------
st.sidebar.title("📁 Upload Receipt")
uploaded_file = st.sidebar.file_uploader("Upload receipt (.jpg/.png/.pdf/.txt)", type=["jpg", "png", "pdf", "txt"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    response = requests.post(f"{API_URL}/upload/", files=files)

    if response.status_code == 200:
        receipt_data = response.json()
        st.sidebar.success("✅ Receipt processed successfully.")

         # Store in session state
        st.session_state["selected_receipt"] = receipt_data["data"]


        result = response.json()["data"]
        st.sidebar.markdown("### ✏️ Edit Receipt Fields")

        with st.sidebar.form("edit_form"):
            vendor = st.text_input("Vendor", value=result.get("vendor", ""))
            date = st.date_input("Date", value=pd.to_datetime(result.get("date")) if result.get("date") else pd.to_datetime("today"))
            amount = st.number_input("Amount", value=float(result.get("amount", 0.0)), step=0.01)
            category = st.selectbox("Category", ["Groceries", "Electricity", "Internet", "Others"], index=3 if result.get("category") not in ["Groceries", "Electricity", "Internet"] else ["Groceries", "Electricity", "Internet"].index(result["category"]))
            currency = st.text_input("Currency", value=result.get("currency", "INR"))

            submitted = st.form_submit_button("💾 Save Edited Receipt")
        

        

        if submitted:
            corrected_data = {
                "id": st.session_state["selected_receipt"]["id"],
                "vendor": vendor,
                "date": str(date),
                "amount": amount,
                "category": category,
                "currency": currency
            }

            res = requests.post(f"{API_URL}/save-corrected/", json=corrected_data)

            if res.status_code == 200:
                st.sidebar.success("✅ Corrected receipt saved!")
                st.rerun()
            else:
                st.sidebar.error("❌ Failed to save. Check backend.")





# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📋 All Receipts", "📊 Insights", "🔎 Search & Sort"])

# ---------- Fetch DB Records ----------

def fetch_all_receipts():
    try:
        engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/smartDB")
        df = pd.read_sql("SELECT vendor, date, amount, category, currency FROM receipts", con=engine)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching data from DB: {e}")
        return pd.DataFrame()


df = fetch_all_receipts()

# ---------- Tab 1: All Records ----------
with tab1:
    st.header("📋 Uploaded Receipts")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.markdown("📥 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download CSV", df.to_csv(index=False), "receipts.csv", "text/csv")
        with col2:
            st.download_button("⬇️ Download JSON", df.to_json(orient="records"), "receipts.json", "application/json")
    else:
        st.info("No receipts found.")

# ---------- Tab 2: Visual Insights ----------
with tab2:
    st.header("📊 Insights")
    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            vendor_counts = df["vendor"].value_counts().reset_index()
            vendor_counts.columns = ["vendor", "count"]
            st.subheader("Top Vendors")
            fig = px.bar(vendor_counts, x="vendor", y="count", color="vendor", text="count")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            category_pie = df["category"].value_counts().reset_index()
            category_pie.columns = ["category", "count"]
            st.subheader("Category Distribution")
            fig2 = px.pie(category_pie, names="category", values="count", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

        df["date"] = pd.to_datetime(df["date"], errors='coerce')
        df["month"] = df["date"].dt.to_period("M").astype(str)
        monthly_trend = df.groupby("month")["amount"].sum().reset_index()

        st.subheader("📈 Monthly Spend Trend")
        fig3 = px.line(monthly_trend, x="month", y="amount", markers=True)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Upload some receipts to view insights.")

# ---------- Tab 3: Search & Sort ----------
with tab3:
    st.header("🔎 Search & Sort Receipts")

    if not df.empty:
        st.markdown("### 🔍 Filters")

        col1, col2 = st.columns(2)

        with col1:
            search_vendor = st.text_input("Search by Vendor Name")
            start_date = st.date_input("Start Date", value=df["date"].min().date())
            end_date = st.date_input("End Date", value=df["date"].max().date())

        with col2:
            min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0, step=1.0)
            max_amount = st.number_input("Maximum Amount", min_value=0.0, value=float(df["amount"].max()), step=1.0)

            sort_by = st.selectbox("Sort By", ["amount", "date", "vendor"])
            sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

        # Apply filters
        filtered = df.copy()

        if search_vendor:
            filtered = filtered[filtered["vendor"].str.contains(search_vendor, case=False, na=False)]

        filtered = filtered[
            (filtered["date"] >= pd.to_datetime(start_date)) &
            (filtered["date"] <= pd.to_datetime(end_date)) &
            (filtered["amount"] >= min_amount) &
            (filtered["amount"] <= max_amount)
        ]

        filtered = filtered.sort_values(
            by=sort_by,
            ascending=True if sort_order == "Ascending" else False
        )

        st.markdown("### 📋 Filtered Results")
        st.dataframe(filtered, use_container_width=True)

        st.download_button("⬇️ Download Filtered CSV", filtered.to_csv(index=False), "filtered_receipts.csv", "text/csv")
    else:
        st.info("No data available.")




