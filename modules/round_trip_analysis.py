# modules/round_trip_analysis.py
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px

def show(df):
    st.title("✈️ Round-Trip Performance Analysis")

    # ---------- تنظيف الأعمدة ----------
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # الأعمدة الرقمية الأساسية
    numeric_cols = {
        "fare_usd": "fare_collection(usd)",
        "seats_sold": "seats_sold",
        "seats_allocated": "seats_allocate",
        "seats_available": "seats_available"
    }

    for new_col, orig_col in numeric_cols.items():
        if orig_col in df.columns:
            df[new_col] = pd.to_numeric(df[orig_col], errors="coerce").fillna(0)
        else:
            df[new_col] = 0

    # ---------- تحويل التاريخ ----------
    if "flight_date" in df.columns:
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")
    else:
        st.error("Column 'flight_date' not found in the CSV!")
        return

    # ---------- استخراج Origin و Destination ----------
    df["origin"] = df["segment"].str.split("/").str[0]
    df["destination"] = df["segment"].str.split("/").str[1]

    # ---------- إنشاء Round-Trip ID ----------
    df["round_trip_id"] = df.apply(
        lambda row: f"{min(row['origin'], row['destination'])}-{max(row['origin'], row['destination'])}-{row['flight_date'].date()}",
        axis=1
    )

    # ---------- حساب Load Factor و Avg Fare ----------
    df["load_factor"] = (df["seats_sold"] / df["seats_allocated"] * 100).fillna(0)
    df["avg_fare_per_seat"] = (df["fare_usd"] / df["seats_sold"]).fillna(0)

    # ---------- عرض الجدول ----------
    st.subheader("📊 Round-Trip Table (Filtered Data)")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(filter=True, sortable=True, resizable=True, wrapText=True)
    for col in df.columns:
        gb.configure_column(col, minWidth=120, maxWidth=400)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        height=600,
        width="100%",
        update_mode=GridUpdateMode.MODEL_CHANGED
    )

    df_filtered = pd.DataFrame(grid_response["data"])

    # ---------- KPIs ----------
    total_revenue = df_filtered["fare_usd"].sum()
    total_seats_sold = df_filtered["seats_sold"].sum()
    total_seats_allocated = df_filtered["seats_allocated"].sum()
    avg_load_factor = (total_seats_sold / total_seats_allocated * 100) if total_seats_allocated > 0 else 0
    avg_fare = (total_revenue / total_seats_sold) if total_seats_sold > 0 else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Revenue (USD)", f"{total_revenue:,.0f}")
    kpi2.metric("Total Seats Sold", f"{total_seats_sold:,}")
    kpi3.metric("Avg Load Factor", f"{avg_load_factor:.1f}%")
    kpi4.metric("Avg Fare / Seat (USD)", f"{avg_fare:,.2f}")

    st.markdown("---")

    # ---------- مخطط Load Factor ----------
    st.subheader("📈 Load Factor by Round-Trip Segment")
    fig1 = px.bar(
        df_filtered,
        x="round_trip_id",
        y="load_factor",
        color="origin",
        text="load_factor",
        height=400,
        labels={"load_factor": "Load Factor (%)", "round_trip_id": "Round-Trip"}
    )
    fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

    # ---------- مخطط Revenue ----------
    st.subheader("📈 Revenue by Round-Trip Segment")
    fig2 = px.bar(
        df_filtered,
        x="round_trip_id",
        y="fare_usd",
        color="origin",
        text="fare_usd",
        height=400,
        labels={"fare_usd": "Revenue (USD)", "round_trip_id": "Round-Trip"}
    )
    fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    # ---------- Scatter Avg Fare vs Load Factor ----------
    st.subheader("🎯 Avg Fare vs Load Factor")
    fig3 = px.scatter(
        df_filtered,
        x="avg_fare_per_seat",
        y="load_factor",
        color="origin",
        size="seats_sold",
        hover_data=["segment", "flight_date"],
        labels={"avg_fare_per_seat": "Avg Fare / Seat (USD)", "load_factor": "Load Factor (%)"}
    )
    st.plotly_chart(fig3, use_container_width=True)
