import streamlit as st
from modules import (
    dashboard,
    SeatInventoryCollections,
    employee_performance_analysis,
    sales_dashboard,
    enplanement_analysis  # استدعاء الصفحة الجديدة
)
from modules.data_loader import (
    load_seat_inventory,
    load_employee_performance,
    load_payment_report,
    load_enplanement_report  # تابع التحميل للـ Enplanement
)
import pandas as pd

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="Airline Business Analytics", layout="wide")
st.sidebar.title("📂 Main Navigation")

# ---------- اختيار الصفحة ----------
page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Seat Inventory & Collections",
    "Employee Performance",
    "Sales",
    "Enplanement Analysis"
])

# ---------- تحميل البيانات ----------
df = None

if page == "Seat Inventory & Collections":
    SEAT_FILE = "SeatInventoryAndCollectionsReport.csv"
    df = load_seat_inventory(SEAT_FILE)

elif page == "Employee Performance":
    EMP_FILE = "PerformanaceOfSalesStaffDetail.csv"
    df = load_employee_performance(EMP_FILE)

elif page == "Sales":
    SALES_FILE = "CompanyPaymentReport (6).csv"
    df = load_payment_report(SALES_FILE)

elif page == "Enplanement Analysis":
    ENP_FILE = "EnplanementReport.csv"
    df = load_enplanement_report(ENP_FILE)  # استخدام التابع الجديد

# ---------- استدعاء الصفحات ----------
if page == "Dashboard":
    dashboard.show()

elif page == "Seat Inventory & Collections":
    SeatInventoryCollections.show(df)

elif page == "Employee Performance":
    employee_performance_analysis.show(df)

elif page == "Sales":
    sales_dashboard.show(df)

elif page == "Enplanement Analysis":
    enplanement_analysis.show(df)
