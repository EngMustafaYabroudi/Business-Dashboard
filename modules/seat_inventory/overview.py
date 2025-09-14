import streamlit as st
import pandas as pd

def show(df):
    st.title("📊 Overview")

    # ---------- تحويل التاريخ ----------
    if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # ---------- فلتر الوجهات و التاريخ جنب بعض ----------
    st.header("✈️ Filter by Segment & Date")
    col1, col2, col3 = st.columns(3)

    # فلتر Segment
    with col1:
        all_segments = sorted(df["segment"].unique())
        segment_filter_type = st.selectbox(
            "Segment Filter Type",
            ["All Segments", "Custom Selection"],
            index=0,
            key="overview_segment_filter"
        )
        selected_segments = all_segments if segment_filter_type == "All Segments" else st.multiselect(
            "Select Segments",
            options=all_segments,
            default=all_segments[:2],
            key="overview_multiselect_segments"
        )

    # فلتر Start Date
    with col2:
        min_date, max_date = df["flight_date"].min(), df["flight_date"].max()
        start_date = pd.to_datetime(
            st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="overview_start_date"
            )
        )

    # فلتر End Date
    with col3:
        end_date = pd.to_datetime(
            st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="overview_end_date"
            )
        )

    # ---------- تطبيق الفلاتر ----------
    df_filtered = df[
        (df["flight_date"] >= start_date) &
        (df["flight_date"] <= end_date)
    ]
    if selected_segments:
        df_filtered = df_filtered[df_filtered["segment"].isin(selected_segments)]

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    # ---------- جدول البيانات ----------
    st.header("📂 Data Table (Filtered & Cleaned)")
    st.dataframe(
        df_filtered.reset_index(drop=True),
        height=500,
        use_container_width=True
    )

    # ---------- KPIs لكل Class of Service أسفل الجدول ----------
    st.header("💡 KPIs by Class of Service")
    if "class_of_service" in df_filtered.columns:
        kpi_df = df_filtered.groupby("class_of_service").agg(
            total_seats_sold=("seats_sold", "sum"),
            total_seats_allocated=("seats_allocated", "sum")
        ).reset_index()
        kpi_df["avg_load_factor"] = (
            kpi_df["total_seats_sold"] / kpi_df["total_seats_allocated"] * 100
        ).fillna(0)

        # صف إجمالي
        total_row = pd.DataFrame({
            "class_of_service": ["Total"],
            "total_seats_sold": [kpi_df["total_seats_sold"].sum()],
            "total_seats_allocated": [kpi_df["total_seats_allocated"].sum()]
        })
        total_row["avg_load_factor"] = (
            total_row["total_seats_sold"] / total_row["total_seats_allocated"] * 100
        ).fillna(0)

        kpi_df = pd.concat([total_row, kpi_df], ignore_index=True)

        # عرض الـ KPIs
        for _, row in kpi_df.iterrows():
            st.markdown(f"<h3>🎫 Class {row['class_of_service']}</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.metric("Total Seats Sold", f"{int(row['total_seats_sold']):,}")
            col2.metric("Avg Load Factor", f"{row['avg_load_factor']:.1f}%")
            st.markdown("---")
    else:
        st.warning("⚠️ Column 'class_of_service' not found in dataset.")

    # ---------- KPI إجمالي ----------
    st.header("💡 Overall Metrics")
    total_seats_sold = df_filtered["seats_sold"].sum()
    total_seats_allocated = df_filtered["seats_allocated"].sum()
    avg_load_factor = (total_seats_sold / total_seats_allocated * 100) if total_seats_allocated > 0 else 0
    st.metric("Total Seats Sold", f"{total_seats_sold:,}")
    st.metric("Total Seats Allocated", f"{total_seats_allocated:,}")
    st.metric("Average Load Factor", f"{avg_load_factor:.1f}%")
