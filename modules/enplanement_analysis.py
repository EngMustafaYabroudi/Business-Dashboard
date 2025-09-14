# modules/enplanement_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

def show(df: pd.DataFrame):
    """
    Passenger Enplanement Dashboard
    - Displays the Enplanement DataTable (Streamlit Table)
    - Shows KPIs summary
    - Plots Top N & Bottom N flights by Segment + Departure Date
    """

    st.title("🛫 Passenger Enplanement")

    # -------- Clean column names --------
    df.columns = df.columns.str.strip().str.replace('\n', ' ', regex=True).str.replace('  ', ' ', regex=False)

    # -------- Convert numeric columns --------
    numeric_cols = ['go_shows', 'no_shows', 'flown_load', 'adult_booked', 'infant_booked']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # -------- Display regular Streamlit table --------
    st.subheader("📋 Enplanement Data Table")
    st.dataframe(df.reset_index(drop=True), height=400, use_container_width=True)

    # -------- KPIs --------
    st.subheader("💡 KPIs Summary")
    total_go_shows = df['go_shows'].sum() if 'go_shows' in df.columns else 0
    total_no_shows = df['no_shows'].sum() if 'no_shows' in df.columns else 0
    total_flown = df['flown_load'].sum() if 'flown_load' in df.columns else 0
    total_adults = df['adult_booked'].sum() if 'adult_booked' in df.columns else 0
    total_infants = df['infant_booked'].sum() if 'infant_booked' in df.columns else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Go Shows", f"{total_go_shows}")
    col2.metric("No Shows", f"{total_no_shows}")
    col3.metric("Flown Load", f"{total_flown}")
    col4.metric("Booked Adults", f"{total_adults}")
    col5.metric("Booked Infants", f"{total_infants}")

    # -------- Prepare total passengers and labels --------
    if 'segment' in df.columns and 'departure_date' in df.columns:
        df['total_passengers'] = df[['go_shows', 'adult_booked', 'infant_booked']].sum(axis=1)
        df['label'] = df['segment'] + " | " + df['departure_date'].dt.strftime('%Y-%m-%d')
        summary = df.groupby('label')['total_passengers'].sum().reset_index()
    else:
        st.warning("Columns 'segment' and/or 'departure_date' not found in dataset.")
        return

    # -------- Top N and Bottom N sliders --------
    st.subheader("⚖️ Top/Bottom N Flights Settings")
    top_n = st.slider("Top N Flights (Highest Passengers)", min_value=1, max_value=20, value=5)
    bottom_n = st.slider("Bottom N Flights (Lowest Passengers)", min_value=1, max_value=20, value=5)

    # -------- Plot: Top N Flights --------
    top_summary = summary.nlargest(top_n, 'total_passengers')
    st.subheader(f"📈 Top {top_n} Flights by Total Passengers")
    fig_top = px.bar(
        top_summary,
        x='total_passengers',
        y='label',
        orientation='h',
        text='total_passengers',
        color='total_passengers',
        color_continuous_scale='Blues',
        labels={'label':'Segment | Departure Date','total_passengers':'Total Passengers'}
    )
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

    # -------- Plot: Bottom N Flights --------
    bottom_summary = summary.nsmallest(bottom_n, 'total_passengers')
    st.subheader(f"📉 Bottom {bottom_n} Flights by Total Passengers")
    fig_bottom = px.bar(
        bottom_summary,
        x='total_passengers',
        y='label',
        orientation='h',
        text='total_passengers',
        color='total_passengers',
        color_continuous_scale='Reds',
        labels={'label':'Segment | Departure Date','total_passengers':'Total Passengers'}
    )
    fig_bottom.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bottom, use_container_width=True)
