import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def show(df):
    st.title("📈 Load Factor & Seats Analysis")

    # تحويل التاريخ إذا لم يكن datetime
    if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # ---------- فلتر الوجهات بطريقة السيليكت الثنائية ----------
    st.subheader("✈️ Filter by Segment")
    all_segments = sorted(df["segment"].unique().tolist())

    segment_filter_type = st.selectbox(
        "Choose Segment Filter Type",
        ["All Segments", "Custom Selection"],
        index=0,
        key="load_factor_segment_filter"
    )

    if segment_filter_type == "All Segments":
        selected_segments = all_segments
    else:
        selected_segments = st.multiselect(
            "Select Segments",
            options=all_segments,
            default=all_segments[:2],
            key="load_factor_multiselect_segments"
        )

    # ---------- فلتر التاريخ ----------
    st.subheader("📅 Filter by Date")
    min_date = df["flight_date"].min()
    max_date = df["flight_date"].max()
    start_date = st.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        key="load_factor_start_date"
    )
    end_date = st.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        key="load_factor_end_date"
    )

    # ---------- تطبيق الفلاتر ----------
    df_filtered = df[
        (df["flight_date"] >= pd.to_datetime(start_date)) &
        (df["flight_date"] <= pd.to_datetime(end_date))
    ]
    if selected_segments:
        df_filtered = df_filtered[df_filtered["segment"].isin(selected_segments)]

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    # ---------- حساب Load Factor لكل Segment ----------
    segment_summary = df_filtered.groupby("segment").agg(
        seats_sold_total=("seats_sold", "sum"),
        seats_allocated_total=("seats_allocated", "sum")
    ).reset_index()
    segment_summary["load_factor"] = (
        segment_summary["seats_sold_total"] / segment_summary["seats_allocated_total"] * 100
    ).fillna(0)

    # ترتيب من الأعلى للأسفل حسب Load Factor
    segment_summary = segment_summary.sort_values(by="load_factor", ascending=False)

    # ---------- رسم Load Factor ----------
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(segment_summary["segment"], segment_summary["load_factor"], color="skyblue")
    ax.set_ylabel("Load Factor (%)")
    ax.set_xlabel("Segment")
    ax.set_title("Load Factor per Segment (Sorted by Value)")
    ax.set_xticklabels(segment_summary["segment"], rotation=45, ha='right')

    st.pyplot(fig)

    # ---------- جدول أسفل المخطط ----------
    st.subheader("💺 Seats Summary by Segment")
    st.dataframe(segment_summary.style.format({
        "seats_sold_total": "{:,}",
        "seats_allocated_total": "{:,}",
        "load_factor": "{:.1f}%"
    }))

    # ---------- KPI إجمالي ----------
    total_seats_sold = df_filtered["seats_sold"].sum()
    total_seats_allocated = df_filtered["seats_allocated"].sum()
    avg_load_factor = (total_seats_sold / total_seats_allocated * 100) if total_seats_allocated > 0 else 0
    st.metric("💡 Avg Load Factor (All Selected Segments)", f"{avg_load_factor:.1f}%")
