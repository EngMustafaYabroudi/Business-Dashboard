import streamlit as st
from modules.sales_reports import summary_by_currency, top_agents_by_currency, agent_summary

def show(df):
    st.title("💰 Sales Dashboard")

    # إنشاء Tabs علوية
    tab_names = [
        "📊 Currency Totals",
        "🏅 Top Agents by Currency",
        "🗂️ Agent Summary"
    ]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        summary_by_currency.show(df)
    with tabs[1]:
        top_agents_by_currency.show(df)
    with tabs[2]:
        agent_summary.show(df)
