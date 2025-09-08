import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

def show(df: pd.DataFrame):
    st.title("📊 Reservation Breakdown Report")

    # ----- عرض From Date و To Date أعلى الجدول -----
    from_date = df['from_date'].iloc[0] if 'from_date' in df.columns else None
    to_date = df['to_date'].iloc[0] if 'to_date' in df.columns else None
    if from_date and to_date:
        st.subheader("Report Period")
        st.write(f"**From Date:** {from_date.strftime('%d/%m/%Y')}  |  **To Date:** {to_date.strftime('%d/%m/%Y')}")

    # ----- فلترة البيانات قبل عرض الجدول -----
    filter_agent = st.multiselect(
        "Filter by Travel Agent Name",
        options=df['Travel Agent Name'].unique(),
        default=None
    )
    filter_agent_code = st.multiselect(
        "Filter by Travel Agent",
        options=df['Travel Agent'].unique(),
        default=None
    )

    df_filtered = df.copy()
    if filter_agent:
        df_filtered = df_filtered[df_filtered['Travel Agent Name'].isin(filter_agent)]
    if filter_agent_code:
        df_filtered = df_filtered[df_filtered['Travel Agent'].isin(filter_agent_code)]

    # ----- إزالة الأعمدة الفارغة تمامًا وحذف عمود To Detail -----
    df_filtered = df_filtered.dropna(axis=1, how='all')
    if "To Detail" in df_filtered.columns:
        df_filtered = df_filtered.drop(columns=["To Detail"])
    
    # ----- إزالة أعمدة from_date و to_date من الجدول -----
    df_display = df_filtered.drop(columns=["from_date", "to_date"], errors='ignore')

    # ----- عرض الجدول باستخدام AgGrid -----
    st.subheader("Reservation Data")
    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        wrapText=True,
        minWidth=150,
        cellStyle={'font-size': '14px'}
    )
    gb.configure_grid_options(headerHeight=40)
    grid_options = gb.build()

    AgGrid(
        df_display,
        gridOptions=grid_options,
        height=600,
        width='100%',
        fit_columns_on_grid_load=True
    )

    st.markdown("---")

    # ----- ملخص تحت الجدول -----
    numeric_cols = ["Fare(USD)", "Taxes(USD)", "Surcharges(USD)", "Total(USD)", "Refund(USD)"]
    st.subheader("Summary Statistics")
    summary_html = '<div style="font-size: 14px; line-height: 1.6;">'
    for col in numeric_cols:
        if col in df_display.columns:
            total = df_display[col].sum()
            summary_html += f"<b>{col} Total:</b> ${total:,.2f}<br>"
    summary_html += "</div>"

    st.markdown(summary_html, unsafe_allow_html=True)
