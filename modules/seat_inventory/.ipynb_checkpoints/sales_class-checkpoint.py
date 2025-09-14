import streamlit as st
import pandas as pd
import plotly.express as px

def show(df: pd.DataFrame):
    st.title("🎟️ Sales by Class of Service")

    if df is None or df.empty:
        st.warning("No data available.")
        return

    # ---------- تحويل الأعمدة الضرورية ----------
    if "flight_date" in df.columns:
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")
    if "seats_sold" in df.columns:
        df["seats_sold"] = pd.to_numeric(df["seats_sold"], errors="coerce").fillna(0)
    if "segment" not in df.columns:
        st.warning("Missing 'segment' column in data.")
        return

    # ---------- فلتر الوجهات ----------
    st.subheader("✈️ Filter by Segment")
    all_segments = sorted(df["segment"].dropna().unique())
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
    df_valid_dates = df.dropna(subset=["flight_date"])
    min_date, max_date = df_valid_dates["flight_date"].min(), df_valid_dates["flight_date"].max()

    start_date = pd.to_datetime(st.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="sales_class_start_date"
    ))
    end_date = pd.to_datetime(st.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="sales_class_end_date"
    ))

    # ---------- تطبيق الفلاتر ----------
    df_filtered = df_valid_dates[
        (df_valid_dates["segment"].isin(selected_segments)) &
        (df_valid_dates["flight_date"] >= start_date) &
        (df_valid_dates["flight_date"] <= end_date)
    ]

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    # ---------- جدول المبيعات ----------
    st.subheader("📂 Sales Table by Segment & Date")
    display_df = df_filtered[["flight_date", "segment", "seats_sold"]].copy()
    display_df = display_df.sort_values(by="flight_date")
    st.dataframe(display_df)

    # ---------- رسم بياني تفاعلي ----------
    st.subheader("📈 Seats Sold Over Time")
    df_grouped = df_filtered.groupby(["flight_date", "segment"])["seats_sold"].sum().reset_index()
    fig = px.line(
        df_grouped,
        x="flight_date",
        y="seats_sold",
        color="segment",
        markers=True,
        labels={"flight_date": "Date", "seats_sold": "Seats Sold", "segment": "Segment"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------- إحصاءات سريعة ----------
    st.subheader("📊 Summary Statistics")
    total_seats = df_filtered["seats_sold"].sum()
    max_seats_row = df_filtered.loc[df_filtered["seats_sold"].idxmax()]
    min_seats_row = df_filtered.loc[df_filtered["seats_sold"].idxmin()]
    mean_seats = df_filtered["seats_sold"].mean()
    st.metric("Total Seats Sold", int(total_seats))
    st.metric("Max Seats Sold in a Day", f"{int(max_seats_row['seats_sold'])} on {max_seats_row['flight_date'].date()}")
    st.metric("Min Seats Sold in a Day", f"{int(min_seats_row['seats_sold'])} on {min_seats_row['flight_date'].date()}")
    st.metric("Average Seats Sold per Day", round(mean_seats, 2))
