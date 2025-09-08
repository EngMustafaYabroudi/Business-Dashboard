import streamlit as st
import pandas as pd

def show(df: pd.DataFrame):
    st.title("📑 Invoice Summary Report")

    # ----- معلومات أساسية -----
    st.subheader("Report Info")
    st.write(f"**Year:** {df['report_year'].iloc[0]}  |  **Month:** {df['report_month'].iloc[0]}")

    # ----- وضع الفلاتر جنب بعض (بدون Territory) -----
    col1, col2 = st.columns(2)

    with col1:
        filter_country = st.multiselect(
            "Filter by Country",
            options=df['Country'].unique(),
            default=None
        )

    with col2:
        filter_agent = st.multiselect(
            "Filter by Agent Name",
            options=df['Agent Name'].unique(),
            default=None
        )

    # ----- تطبيق الفلاتر -----
    df_filtered = df.copy()
    if filter_country:
        df_filtered = df_filtered[df_filtered['Country'].isin(filter_country)]
    if filter_agent:
        df_filtered = df_filtered[df_filtered['Agent Name'].isin(filter_agent)]

    # ----- الأعمدة التي نريد عرضها فقط -----
    columns_to_show = [
        col for col in df_filtered.columns
        if col not in ["report_year", "report_month", "Invoice Number", "Emails Sent", "Detail",
                       "Agent Code", "Station Name", "Station Code"]
    ]
    df_display = df_filtered[columns_to_show]

    # ----- عرض الجدول العادي -----
    st.subheader("Invoice Data")
    st.dataframe(df_display, use_container_width=True)

    st.markdown("---")

    # ----- التأكد من الأعمدة الرقمية -----
    if "Invoice Total" in df_filtered.columns:
        df_filtered["Invoice Total"] = pd.to_numeric(df_filtered["Invoice Total"], errors="coerce").fillna(0)
    if "Modify" in df_filtered.columns:
        df_filtered["Modify"] = pd.to_numeric(df_filtered["Modify"], errors="coerce").fillna(0)

    # ----- حساب الملخص -----
    total_invoices = df_filtered["Invoice Total"].sum() if "Invoice Total" in df_filtered.columns else 0
    avg_invoice = df_filtered["Invoice Total"].mean() if "Invoice Total" in df_filtered.columns else 0
    max_invoice = df_filtered["Invoice Total"].max() if "Invoice Total" in df_filtered.columns else 0
    min_invoice = df_filtered["Invoice Total"].min() if "Invoice Total" in df_filtered.columns else 0
    total_modify = df_filtered["Modify"].sum() if "Modify" in df_filtered.columns else 0

    # ----- عرض الملخص -----
    st.subheader("Summary Statistics")
    st.markdown(f"""
    <div style="font-size: 14px; line-height: 1.6;">
        <b>Total Invoices:</b> ${total_invoices:,.2f}<br>
        <b>Average Invoice:</b> ${avg_invoice:,.2f}<br>
        <b>Max Invoice:</b> ${max_invoice:,.2f}<br>
        <b>Min Invoice:</b> ${min_invoice:,.2f}<br>
        <b>Total Modifications:</b> {total_modify:,.0f}
    </div>
    """, unsafe_allow_html=True)
