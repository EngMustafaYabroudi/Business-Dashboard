import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def show(df):
    st.title("🎟️ Sales by Class of Service")

    # ---------- تحويل التاريخ إذا لم يكن datetime ----------
    if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # ---------- فلتر الوجهات ----------
    st.subheader("✈️ Filter by Segment")
    all_segments = sorted(df["segment"].unique().tolist())

    segment_filter_type = st.selectbox(
        "Choose Segment Filter Type",
        ["All Segments", "Custom Selection"],
        index=0
    )

    if segment_filter_type == "All Segments":
        selected_segments = all_segments
    else:
        selected_segments = st.multiselect(
            "Select Segments",
            options=all_segments,
            default=all_segments[:2]
        )

    # ---------- فلتر التاريخ ----------
    st.subheader("📅 Filter by Date")
    min_date = df["flight_date"].min()
    max_date = df["flight_date"].max()
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

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

    # ---------- حساب المبيعات حسب Class of Service ----------
    if "class_of_service" in df_filtered.columns and "seats_sold" in df_filtered.columns and "seats_allocated" in df_filtered.columns:
        class_sales = df_filtered.groupby("class_of_service")[["seats_sold","seats_allocated"]].sum()
        class_sales = class_sales.sort_values(by="seats_sold", ascending=False)

        # ---------- إضافة نسبة كل Class ----------
        total_seats = class_sales["seats_allocated"].sum()
        class_sales["occupancy_rate (%)"] = (class_sales["seats_sold"] / total_seats * 100).round(1)

        # ---------- رسم المخطط ----------
        fig, ax = plt.subplots(figsize=(8,5))
        class_sales[["seats_sold","seats_allocated"]].plot(kind="bar", stacked=True, ax=ax, color=["skyblue","lightgreen"])
        ax.set_ylabel("Seats")
        ax.set_xlabel("Class of Service")
        ax.set_title("Seats Sold vs Available by Class")
        ax.legend(["Seats Sold", "Seats Available"])

        # ---------- عرض عدد المقاعد فوق كل عمود ----------
        for i, val in enumerate(class_sales["seats_sold"]):
            ax.text(i, val + max(class_sales["seats_allocated"])*0.01, f"{int(val)}", ha='center', va='bottom', fontsize=8, color='black')

        st.pyplot(fig)

        # ---------- عرض الجدول ----------
        st.subheader("💺 Seats Summary by Class")
        st.dataframe(class_sales.style.format({
            "seats_sold": "{:,}",
            "seats_allocated": "{:,}",
            "occupancy_rate (%)": "{:.1f}%"
        }))
    else:
        st.warning("⚠️ Required columns not found in dataset.")
