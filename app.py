import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from Auth.login import login_page
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

cookies = EncryptedCookieManager(
    prefix="airline_",
    password="any_secure_random_password_123!"
)
if not cookies.ready():
    st.stop()  # الانتظار حتى تكون الكوكيز جاهزة

st.set_page_config(page_title="Airline Business Analytics", layout="wide")
st.sidebar.title("🗂 Menu") 



# ---------- استرجاع حالة الجلسة من الكوكيز ----------
if "authenticated" in cookies and cookies["authenticated"] == "true":
    st.session_state.authenticated = True
    st.session_state.username = cookies.get("username", "")
    st.session_state.name = cookies.get("name", "")
    st.session_state.role = cookies.get("role", "")
else:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.name = ""
    st.session_state.role = ""

# ---------- فرض تسجيل الدخول ----------
if not st.session_state.authenticated:
    login_page(cookies)
    st.stop()  # يمنع باقي التطبيق من التنفيذ حتى تسجيل الدخول

# ---------- Main App ----------
st.sidebar.success(f"✅ Welcome {st.session_state.name}")

# ---------- Navigation based on role ----------
role_pages = {
    "admin": [
        "🏠 Overview",
        "💺 Seat Inventory",
        "🛫 Passenger Enplanement",
        "💵 Sales & Collections",
        "👨‍💼 Staff Performance",
        "🤝 Agent Productivity",
        "📑 Invoice Summary",
        "🔐 User Privileges"
    ],
    "sales": [
        "💵 Sales & Collections",
        "👨‍💼 Staff Performance"
    ],
    "agent": [
        "🤝 Agent Productivity",
        "📑 Invoice Summary"
    ]
}

allowed_pages = role_pages.get(st.session_state.role, ["🏠 Overview"])
page = st.sidebar.radio("Go to", allowed_pages)

# ---------- Load Data ----------
df = None
if page == "💺 Seat Inventory":
    df = load_seat_inventory("SeatInventoryAndCollectionsReport2023.csv")
elif page == "👨‍💼 Staff Performance":
    df = load_employee_performance("PerformanaceOfSalesStaffDetail.csv")
elif page == "💵 Sales & Collections":
    df = load_payment_report("CompanyPaymentReport (7).csv")
elif page == "🛫 Passenger Enplanement":
    df = load_enplanement_report("EnplanementReport.csv")
elif page == "🤝 Agent Productivity":
    df = load_agent_productivity("AgentProductivityReport.csv")
elif page == "📑 Invoice Summary":
    df = load_invoice_summary_report("InvoiceSummaryReport.csv")
elif page == "🔐 User Privileges":
    df = load_agent_user_privileges("AgentUserPrivileges.csv")

# ---------- Page Rendering ----------
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


# التأكد من وجود المتغير في session_state
if "logout_confirm" not in st.session_state:
    st.session_state.logout_confirm = False

# زر تسجيل الخروج في sidebar
if st.sidebar.button("🔓 Logout", key="logout_sidebar"):
    st.session_state.logout_confirm = True

# مربع التأكيد في sidebar
if st.session_state.logout_confirm:
    st.sidebar.warning(" Are you sure you want to log out?", icon="⚠️")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("✅ Yes", key="logout_yes"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.name = ""
            st.session_state.role = ""

            # مسح الكوكيز
            cookies["authenticated"] = "false"
            cookies["username"] = ""
            cookies["name"] = ""
            cookies["role"] = ""
            cookies.save()

            st.session_state.logout_confirm = False
            st.success("🔓 You have been logged out. Redirecting...")
            st.markdown(
                """<meta http-equiv="refresh" content="1;url=/" />""",
                unsafe_allow_html=True
            )
            st.stop()
            
    with col2:
        if st.button("❌ Cancel", key="logout_no"):
            st.session_state.logout_confirm = False 
