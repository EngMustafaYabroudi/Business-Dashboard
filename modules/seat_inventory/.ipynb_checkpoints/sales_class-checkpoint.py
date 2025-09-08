import streamlit as st
import pandas as pd

def show(df):
    st.subheader("🎟️ Sales by Class of Service")

    # ---------- تحويل التاريخ ----------
    if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # ---------- فلتر الوجهات ----------
    st.subheader("✈️ Filter by Segment")
    all_segments = sorted(df["segment"].unique())
    segment_filter_type = st.selectbox(
        "Choose Segment Filter Type",
        ["All Segments", "Custom Selection"],
        index=0,
        key="sales_class_segment_filter"
    )
    selected_segments = all_segments if segment_filter_type == "All Segments" else st.multiselect(
        "Select Segments",
        options=all_segments,
        default=all_segments[:2],
        key="sales_class_multiselect_segments"
    )

    # ---------- فلتر التاريخ ----------
    st.subheader("📅 Filter by Date")
    min_date, max_date = df["flight_date"].min(), df["flight_date"].max()
    start_date = pd.to_datetime(st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="sales_class_start_date"))
    end_date = pd.to_datetime(st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="sales_class_end_date"))
