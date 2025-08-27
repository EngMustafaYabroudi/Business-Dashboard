# modules/dashboard.py

import streamlit as st
import pandas as pd
from modules.data_loader import load_payment_report, load_employee_performance

def show():
    st.title("📊 General Business Dashboard")

    # ---------- Load Data ----------
    SALES_FILE = "CompanyPaymentReport (6).csv"
    EMP_FILE = "PerformanaceOfSalesStaffDetail.csv"

    try:
        sales_df = load_payment_report(SALES_FILE)
        emp_df = load_employee_performance(EMP_FILE)
        st.success("✅ Data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return

    # ---------- Report Date Range ----------
    from_date = sales_df['report_from_date'].iloc[0] if 'report_from_date' in sales_df.columns else None
    to_date = sales_df['report_to_date'].iloc[0] if 'report_to_date' in sales_df.columns else None

    if from_date and to_date:
        st.markdown(
            f"""
            <div style="
                background:#f0f2f6;
                padding:15px 20px;
                border-left:5px solid #1E88E5;
                border-radius:8px;
                font-size:18px;
                font-weight:bold;
                color:#333;
                margin-bottom:20px;
            ">
                📅 <strong>Report Period</strong><br>
                From: {pd.to_datetime(from_date).strftime('%d/%m/%Y')}<br>
                To: {pd.to_datetime(to_date).strftime('%d/%m/%Y')}
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- Sales by Currency ----------
    st.subheader("💰 Total Sales by Currency")

    if not sales_df.empty and "Currency" in sales_df.columns and "Net Amount" in sales_df.columns:
        sales_by_currency = (
            sales_df.groupby("Currency")["Net Amount"]
            .sum()
            .reset_index()
            .sort_values("Net Amount", ascending=False)
        )
        st.dataframe(sales_by_currency, use_container_width=True)
    else:
        st.warning("⚠️ Columns 'Currency' and 'Net Amount' not found in sales data.")

    st.markdown("---")

    # ---------- Employee Performance Summary ----------
    st.subheader("👨‍💼 Employee Performance Summary")

    if not emp_df.empty:
        total_reservations = emp_df["reservations"].sum() if "reservations" in emp_df.columns else 0
        total_pax = emp_df["pax"].sum() if "pax" in emp_df.columns else 0
        total_revenue = emp_df["total_charges"].sum() if "total_charges" in emp_df.columns else 0
        total_discount = emp_df["total_discount"].sum() if "total_discount" in emp_df.columns else 0
        total_employees = emp_df["user_name"].nunique() if "user_name" in emp_df.columns else 0

        st.write(f"📝 Total Reservations: {total_reservations:,}")
        st.write(f"👥 Total PAX: {total_pax:,}")
        st.write(f"💵 Total Revenue ($): {total_revenue:,.2f}")
        st.write(f"🔖 Total Discounts ($): {total_discount:,.2f}")
        st.write(f"👤 Employees Contributed: {total_employees:,}")
    else:
        st.warning("⚠️ Employee performance data not found.")
