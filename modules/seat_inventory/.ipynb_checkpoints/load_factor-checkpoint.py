import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def show(df):
    st.subheader("📈 Load Factor Analysis")

    # تحويل التاريخ
    if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # فلتر الوجهات
    st.subheader("✈️ Filter by Segment")
    all_segments = sorted(df["segment"].unique())
    segment_filter_type = st.selectbox(
        "Choose Segment Filter Type",
        ["All Segments", "Custom Selection"],
        index=0,
        key="load_factor_segment_filter"
    )
    selected_segments = all_segments if segment_filter_type == "All Segments" else st.multiselect(
        "Select Segments",
        options=all_segments,
        default=all_segments[:2],
        key="load_factor_multiselect_segments"
    )

    # فلتر التاريخ
    st.subheader("📅 Filter by Date")
    min_date, max_date = df["flight_date"].min(), df["flight_date"].max()
    start_date = pd.to_datetime(st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="load_factor_start_date"))
    end_date = pd.to_datetime(st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="load_factor_end_date"))

    # تطبيق الفلاتر
    df_filtered = df[(df["flight_date"] >= start_date) & (df["flight_date"] <= end_date)]
    if selected_segments:
        df_filtered = df_filtered[df_filtered["segment"].isin(selected_segments)]

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    # حساب Load Factor لكل Segment
    summary = df_filtered.groupby("segment").agg(
        seats_sold_total=("seats_sold","sum"),
        seats_allocated_total=("seats_allocated","sum")
    ).reset_index()
    summary["load_factor"] = (summary["seats_sold_total"] / summary["seats_allocated_total"] * 100).fillna(0)
    summary = summary.sort_values("load_factor", ascending=False)

  

    # جدول أسفل المخطط
    st.subheader("💺 Seats Summary by Segment")
    st.dataframe(summary.style.format({
        "seats_sold_total":"{:,}",
        "seats_allocated_total":"{:,}",
        "load_factor":"{:.1f}%"
    }))

    # KPI إجمالي
    total_sold = df_filtered["seats_sold"].sum()
    total_alloc = df_filtered["seats_allocated"].sum()
    avg_load = (total_sold / total_alloc * 100) if total_alloc > 0 else 0
    st.metric("💡 Avg Load Factor (All Segments)", f"{avg_load:.1f}%")
