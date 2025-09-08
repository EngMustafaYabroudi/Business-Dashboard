import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def show(df):
    st.subheader("Top 20 Agents for Selected Currency")
    currency_to_compare = st.selectbox("Select currency", df['Currency'].unique())
    df_currency = df[df['Currency'] == currency_to_compare]
    net_amount_by_agent = df_currency.groupby('Agent/GSA Name')['Net Amount'].sum().sort_values(ascending=False)
    top_agents = net_amount_by_agent.head(20)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=top_agents.values, y=top_agents.index, palette='viridis', ax=ax)
    ax.set_title(f'Net Amount by Agent/GSA Name for Currency: {currency_to_compare}')
    ax.set_xlabel('Net Amount')
    ax.set_ylabel('Agent/GSA Name')
    for i, v in enumerate(top_agents.values):
        ax.text(v + max(top_agents.values)*0.01, i, f"{v:,.2f}", color='black', va='center')
    st.pyplot(fig)
