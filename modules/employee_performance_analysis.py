import streamlit as st
import pandas as pd
import plotly.express as px

def show(df: pd.DataFrame):
    st.title("👨‍💼 Employee Performance Dashboard")

    # ------------------ Agent Selection ------------------
    agent_names = df['agent_name'].dropna().unique().tolist()
    agent_options = ["All Agents"] + sorted(agent_names)
    selected_agent = st.selectbox("Select Agent", agent_options)

    # ------------------ Filter by Agent ------------------
    if selected_agent == "All Agents":
        agent_filtered_df = df.copy()
    else:
        agent_filtered_df = df[df['agent_name'] == selected_agent]

    # ------------------ Employee Selection ------------------
    user_names = agent_filtered_df['user_name'].dropna().unique().tolist()
    user_options = ["All Employees"] + sorted(user_names)
    selected_user = st.selectbox("Select Employee", user_options)

    # ------------------ Filter by Employee ------------------
    if selected_user == "All Employees":
        filtered_df = agent_filtered_df.copy()
    else:
        filtered_df = agent_filtered_df[agent_filtered_df['user_name'] == selected_user]

    # ------------------ Display Table ------------------
    st.subheader("📋 Employee Data")
    st.dataframe(
        filtered_df[['agent_name', 'user_name', 'reservations', 'pax', 'total_charges', 'total_discount']],
        use_container_width=True
    )

    # ------------------ Totals ------------------
    total_reservations = int(filtered_df['reservations'].sum())
    total_pax = int(filtered_df['pax'].sum())
    total_charges = round(filtered_df['total_charges'].sum(), 2)
    total_discount = round(filtered_df['total_discount'].sum(), 2)
    total_employees = filtered_df['user_name'].nunique()  # عدد الموظفين الفريدين

    st.subheader("📊 Totals")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Reservations", f"{total_reservations:,}")
    col2.metric("Total PAX", f"{total_pax:,}")
    col3.metric("Total Revenue ($)", f"{total_charges:,.2f}")
    col4.metric("Total Discounts ($)", f"{total_discount:,.2f}")
    col5.metric("Employees Contributed", f"{total_employees:,}")

    # ------------------ Top N Sliders ------------------
    top_n_reservations = st.slider("Top N Employees by Reservations", min_value=1, max_value=20, value=5)
    top_n_revenue = st.slider("Top N Employees by Revenue", min_value=1, max_value=20, value=5)
    top_n_multi = st.slider("Top N Employees for Combined Metrics Chart", min_value=1, max_value=20, value=5)

    # ------------------ Top N by Reservations ------------------
    ranking_df = filtered_df.groupby("user_name", as_index=False).agg({
        'reservations': 'sum',
        'pax': 'sum'
    }).sort_values(by="reservations", ascending=False).head(top_n_reservations)

    total_pax_top_res = ranking_df['pax'].sum()
    st.write(f"Total PAX for top {top_n_reservations} employees (by Reservations): {total_pax_top_res:,}")
    st.subheader(f"Top {top_n_reservations} Employees by Reservations")

    fig_reservations = px.bar(
        ranking_df,
        x="reservations",
        y="user_name",
        orientation='h',
        text='reservations',
        color='reservations',
        color_continuous_scale='Blues'
    )
    fig_reservations.update_traces(textposition='outside')
    fig_reservations.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig_reservations, use_container_width=True)

    # ------------------ Top N by Revenue (Treemap) ------------------
    revenue_df = filtered_df.groupby("user_name", as_index=False).agg({
        'total_charges': 'sum',
        'pax': 'sum'
    }).sort_values(by="total_charges", ascending=False).head(top_n_revenue)

    total_pax_top_rev = revenue_df['pax'].sum()
    st.write(f"Total PAX for top {top_n_revenue} employees (by Revenue): {total_pax_top_rev:,}")
    st.subheader(f"Top {top_n_revenue} Employees by Revenue (Treemap)")

    fig_revenue_tree = px.treemap(
        revenue_df,
        path=['user_name'],
        values='total_charges',
        color='total_charges',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_revenue_tree, use_container_width=True)

    # ------------------ Top N by Revenue (Pie Chart) ------------------
    st.subheader(f"Top {top_n_revenue} Employees by Revenue (Pie Chart)")

    fig_revenue_pie = px.pie(
        revenue_df,
        names='user_name',
        values='total_charges',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig_revenue_pie, use_container_width=True)

    # ------------------ Top N Combined Metrics (Grouped Bar) ------------------
    multi_df = filtered_df.groupby("user_name", as_index=False).agg({
        'reservations': 'sum',
        'total_charges': 'sum',
        'pax': 'sum'
    }).sort_values('reservations', ascending=False).head(top_n_multi)

    total_pax_top_multi = multi_df['pax'].sum()
    st.write(f"Total PAX for top {top_n_multi} employees (Combined Metrics): {total_pax_top_multi:,}")
    st.subheader(f"Top {top_n_multi} Employees - Reservations, Revenue, PAX")

    fig_multi = px.bar(
        multi_df,
        x='user_name',
        y=['reservations', 'total_charges', 'pax'],
        barmode='group',
        text_auto=True,
        title="Top Employees: Combined Metrics"
    )
    st.plotly_chart(fig_multi, use_container_width=True)
