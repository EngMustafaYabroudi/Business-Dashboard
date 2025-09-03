import streamlit as st
from modules import (
    dashboard,
    SeatInventoryCollections,
    employee_performance_analysis,
    sales_dashboard,
    enplanement_analysis,
    agent_productivity,
    invoice_summary,
    agent_user_privileges
)
from modules.data_loader import (
    load_seat_inventory,
    load_employee_performance,
    load_payment_report,
    load_enplanement_report,
    load_agent_productivity,
    load_invoice_summary_report,
    load_agent_user_privileges
)

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="Airline Business Analytics", layout="wide")
st.sidebar.title("📂 Navigation")

# ---------- اختيار الصفحة ----------
page = st.sidebar.radio("Go to", [
    "🏠 Overview",
    "💺 Seat Inventory",
    "🛫 Passenger Enplanement",
    "💵 Sales & Collections",
    "👨‍💼 Staff Performance",
    "🤝 Agent Productivity",
    "📑 Invoice Summary",
    "🔐 User Privileges"
])

# ---------- تحميل البيانات ----------
df = None

if page == "💺 Seat Inventory":
    df = load_seat_inventory("SeatInventoryAndCollectionsReport.csv")

elif page == "👨‍💼 Staff Performance":
    df = load_employee_performance("PerformanaceOfSalesStaffDetail.csv")

elif page == "💵 Sales & Collections":
    df = load_payment_report("CompanyPaymentReport (6).csv")

elif page == "🛫 Passenger Enplanement":
    df = load_enplanement_report("EnplanementReport.csv")

elif page == "🤝 Agent Productivity":
    df = load_agent_productivity("AgentProductivityReport.csv")

elif page == "📑 Invoice Summary":
    df = load_invoice_summary_report("InvoiceSummaryReport.csv")

elif page == "🔐 User Privileges":
    df = load_agent_user_privileges("AgentUserPrivileges.csv")

# ---------- استدعاء الصفحات ----------
if page == "🏠 Overview":
    dashboard.show()

elif page == "💺 Seat Inventory":
    SeatInventoryCollections.show(df)

elif page == "👨‍💼 Staff Performance":
    employee_performance_analysis.show(df)

elif page == "💵 Sales & Collections":
    sales_dashboard.show(df)

elif page == "🛫 Passenger Enplanement":
    enplanement_analysis.show(df)

elif page == "🤝 Agent Productivity":
    agent_productivity.show(df)

elif page == "📑 Invoice Summary":
    invoice_summary.show(df)

elif page == "🔐 User Privileges":
    agent_user_privileges.show(df)
