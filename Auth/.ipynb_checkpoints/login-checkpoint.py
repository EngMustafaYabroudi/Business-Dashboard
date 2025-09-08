import streamlit as st

users = {
    "admin": {"name": "Admin User", "password": "123"},
    "sales": {"name": "Sales Staff", "password": "456"},
    "agent": {"name": "Agent Manager", "password": "789"}
}

def login_page(cookies):
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>✈️ Syrian Airlines Login</h2>", unsafe_allow_html=True)

    with st.form(key="login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if username_input in users and users[username_input]["password"] == password_input:
                # تحديث session_state
                st.session_state.authenticated = True
                st.session_state.username = username_input
                st.session_state.name = users[username_input]["name"]
                st.session_state.role = username_input

                # حفظ الجلسة في الكوكيز
                cookies["authenticated"] = "true"
                cookies["username"] = username_input
                cookies["name"] = users[username_input]["name"]
                cookies["role"] = username_input
                cookies.save()

                # لن نستخدم st.experimental_rerun بعد الآن
                st.success(f"✅ Welcome {st.session_state.name}. Refresh the page if needed.")
            else:
                st.error("❌ Incorrect username or password")

    st.markdown("</div>", unsafe_allow_html=True)
