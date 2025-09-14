import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def show(df):
    st.title("📊 Agent Summary Dashboard")

    # ---------- تحويل الأعمدة المالية إلى أرقام ----------
    df["Net Amount"] = pd.to_numeric(df["Net Amount"], errors="coerce").fillna(0)
    df["Refund Amount"] = pd.to_numeric(df["Refund Amount"], errors="coerce").fillna(0)

    # ---------- دمج العملات لكل وكيل لتجنب التكرار ----------
    df_grouped = df.groupby("Agent/GSA Name", as_index=False).agg({
        "Net Amount": "sum",
        "Refund Amount": "sum"
    })

    # ---------- جدول الوكلاء باستخدام st.dataframe ----------
    st.subheader("📂 Agent Summary Table")
    st.dataframe(df_grouped[['Agent/GSA Name', 'Net Amount']].sort_values(by='Net Amount', ascending=False))

    st.markdown("---")

    # ---------- Bar: عدد الوكلاء لكل عملة ----------
    st.subheader("📈 Number of Agents per Currency (All Data)")
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
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0,5), textcoords="offset points", ha='center', va='bottom', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)

    st.markdown("---")

    # ---------- Top N Agents by Refund ----------
    st.subheader("⚖️ Top N Agents by Refund Amount")
    top_n = st.slider("Select Top N Agents", min_value=1, max_value=20, value=5)
    refund_summary = df_grouped.nlargest(top_n, "Refund Amount")
    fig_refund = px.bar(
        refund_summary,
        x="Refund Amount",
        y="Agent/GSA Name",
        orientation="h",
        text="Refund Amount",
        color="Refund Amount",
        color_continuous_scale="Reds",
        labels={"Agent/GSA Name":"Agent","Refund Amount":"Refund Amount (Total)"}
    )
    fig_refund.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_refund.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
    st.plotly_chart(fig_refund, use_container_width=True)
