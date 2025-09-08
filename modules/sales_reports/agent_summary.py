import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.pyplot as plt

def show(df):
    st.title("📊 Agent Summary by Currency")

    # ---------- فلتر الوكلاء ----------
    all_agents = sorted(df['Agent/GSA Name'].unique())
    selected_agent = st.selectbox(
        "Select Agent (or leave to see all)",
        options=["All"] + all_agents,
        index=0
    )

    # ---------- فلتر العملات ----------
    all_currencies = sorted(df['Currency'].unique())
    selected_currency = st.selectbox(
        "Select Currency (or leave to see all)",
        options=["All"] + all_currencies,
        index=0
    )

    # ---------- تطبيق الفلاتر ----------
    df_filtered = df.copy()
    if selected_agent != "All":
        df_filtered = df_filtered[df_filtered['Agent/GSA Name'] == selected_agent]
    if selected_currency != "All":
        df_filtered = df_filtered[df_filtered['Currency'] == selected_currency]

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    # ---------- إعداد الجدول النهائي ----------
    display_df = df_filtered[['Agent/GSA Name', 'Currency', 'Net Amount']].copy()

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        wrapText=True,
        minWidth=150,
        cellStyle={'font-size': '16px'}
    )
    gb.configure_column("Agent/GSA Name", minWidth=300)
    gb.configure_column("Currency", minWidth=200)
    gb.configure_column("Net Amount", minWidth=200)
    gb.configure_grid_options(headerHeight=40)
    grid_options = gb.build()

    st.subheader("📂 Agent Summary Table")
    AgGrid(
        display_df,
        gridOptions=grid_options,
        height=600,
        width='100%',
        fit_columns_on_grid_load=True
    )

    st.markdown("---")

    # ---------- مخطط Bar: عدد الوكلاء لكل عملة (غير مرتبط بالفلتر) ----------
    st.subheader("📈 Number of Agents per Currency (All Data)")

    # نستخدم df الأصلي هنا
    agent_counts_all = df.groupby('Currency')['Agent/GSA Name'].nunique().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10,5))
    bars = ax.bar(
        agent_counts_all.index,
        agent_counts_all.values,
        color=plt.cm.viridis(agent_counts_all.values / agent_counts_all.values.max())
    )
    ax.set_xlabel("Currency", fontsize=14)
    ax.set_ylabel("Number of Agents", fontsize=14)
    ax.set_title("Number of Agents per Currency", fontsize=16)

    # عرض العدد أعلى كل عمود
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f'{int(height)}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0,5),
            textcoords="offset points",
            ha='center', va='bottom',
            fontsize=12
        )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
