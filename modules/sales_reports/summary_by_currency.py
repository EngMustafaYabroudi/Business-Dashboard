import streamlit as st
import pandas as pd

def show(df):
    st.subheader("💰 Currency Totals")

    if df is None or df.empty:
        st.warning("⚠️ No data available.")
        return

    if "Currency" not in df.columns or "Net Amount" not in df.columns:
        st.error("🚨 Columns 'Currency' and 'Net Amount' not found in data.")
        return

    # -------- عرض فترة التقرير بشكل رسمي في بطاقة --------
    from_date = df['report_from_date'].iloc[0] if 'report_from_date' in df.columns else None
    to_date = df['report_to_date'].iloc[0] if 'report_to_date' in df.columns else None

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
                <div>📅 <strong>Report Period</strong></div>
                <div>From: {from_date.strftime('%d/%m/%Y')}</div>
                <div>To: {to_date.strftime('%d/%m/%Y')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # تنظيف وتحويل العمود الرقمي
    df["Net Amount"] = pd.to_numeric(df["Net Amount"], errors="coerce")

    # حساب المجموع لكل عملة
    summary = df.groupby("Currency")["Net Amount"].sum().reset_index()

    # ألوان مميزة
    colors = ["#1E88E5", "#43A047", "#FB8C00", "#8E24AA", "#E53935", "#00ACC1"]

    st.markdown("### 📊 Values by Currency")

    # عرض كل 3 بطاقات في صف
    for i in range(0, len(summary), 3):
        cols = st.columns(3)
        for j, row in enumerate(summary.iloc[i:i+3].itertuples()):
            currency = row.Currency
            amount = f"{row._2:,.0f}"
            color = colors[(i+j) % len(colors)]
            with cols[j]:
                st.markdown(
                    f"""
                    <div style="
                        background:{color};
                        padding:25px;
                        border-radius:12px;
                        text-align:center;
                        box-shadow:0px 4px 10px rgba(0,0,0,0.2);
                        margin-bottom:20px;
                    ">
                        <div style="font-size:24px; font-weight:bold; color:white;">{currency}</div>
                        <div style="font-size:22px; font-weight:bold; color:white; margin-top:10px;">{amount}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown("<br>", unsafe_allow_html=True)
