import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from modules import load_factor, sales_class

def show(df):
    # ---------- عنوان رئيسي ----------
    st.markdown("<h1 style='font-size:32px; text-align:center;'>✈️ Seat Inventory & Collections</h1>", unsafe_allow_html=True)

    # ---------- تحسين توزيع التبويبات ----------
    st.markdown(
        """
        <style>
        div[data-baseweb="tab-list"] button {
            font-size: 18px;  /* تكبير خط التبويبات */
            padding: 12px 30px;  /* زيادة المسافة بين التبويبات */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- إنشاء البار العلوي (Tabs) ----------
    tab_names = [
        "Overview",
        "Load Factor",
        "Sales by Class"
    ]
    tabs = st.tabs(tab_names)

    # ================== Overview ==================
    with tabs[0]:
        st.subheader("📊 Overview")

        # ---------- تأكيد أن flight_date تاريخ ----------
        if not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
            df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

        # ---------- فلتر الوجهات ----------
        st.subheader("✈️ Filter by Segment")
        all_segments = sorted(df["segment"].unique().tolist())

        segment_filter_type = st.selectbox(
            "Choose Segment Filter Type",
            ["All Segments", "Custom Selection"],
            index=0,
            key="overview_segment_filter"
        )

        if segment_filter_type == "All Segments":
            selected_segments = all_segments
        else:
            selected_segments = st.multiselect(
                "Select Segments",
                options=all_segments,
                default=all_segments[:2],
                key="overview_multiselect_segments"
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
            key="overview_start_date"
        )
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="overview_end_date"
        )

        # ---------- تطبيق الفلاتر ----------
        df_filtered = df.copy()
        df_filtered = df_filtered[df_filtered["segment"].isin(selected_segments)]
        df_filtered = df_filtered[
            (df_filtered["flight_date"] >= pd.to_datetime(start_date)) &
            (df_filtered["flight_date"] <= pd.to_datetime(end_date))
        ]

        # ---------- الأعمدة المخفية ----------
        hide_cols = ["Baggage", "Sur Charge", "On Hold", "Fixed", "Over sell", "Curtailed", "Flight Status"]
        df_filtered = df_filtered.drop(columns=[c for c in hide_cols if c in df_filtered.columns])

        st.markdown("---")

        # ---------- جدول البيانات مع تكبير الخط ----------
        st.subheader("📂 Data Table (Filtered, Cleaned)")
        gb = GridOptionsBuilder.from_dataframe(df_filtered)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(
            editable=False,
            filter=True,
            sortable=True,
            resizable=True,
            wrapText=True,
            minWidth=150,
            cellStyle={'font-size': '16px'}
        )
        gb.configure_grid_options(headerHeight=40)
        grid_options = gb.build()
        AgGrid(
            df_filtered,
            gridOptions=grid_options,
            height=600,
            width='100%',
            fit_columns_on_grid_load=True
        )

        st.markdown("---")

        # ---------- KPIs ----------
        st.subheader("💡 KPIs by Class of Service (C / Y)")
        if "class_of_service" in df_filtered.columns:
            kpi_df = (
                df_filtered.groupby("class_of_service")
                .agg(total_seats_sold=("seats_sold", "sum"),
                     total_seats_allocated=("seats_allocated", "sum"))
                .reset_index()
            )
            kpi_df["avg_load_factor"] = (
                kpi_df["total_seats_sold"] / kpi_df["total_seats_allocated"] * 100
            ).fillna(0)

            total_row = pd.DataFrame({
                "class_of_service": ["Total"],
                "total_seats_sold": [kpi_df["total_seats_sold"].sum()],
                "total_seats_allocated": [kpi_df["total_seats_allocated"].sum()]
            })
            total_row["avg_load_factor"] = (
                total_row["total_seats_sold"] / total_row["total_seats_allocated"] * 100
            ).fillna(0)

            kpi_df = pd.concat([total_row, kpi_df], ignore_index=True)

            for _, row in kpi_df.iterrows():
                st.markdown(f"<h3>🎫 Class {row['class_of_service']}</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                col1.markdown(f"<h4>Total Seats Sold: {int(row['total_seats_sold']):,}</h4>", unsafe_allow_html=True)
                col2.markdown(f"<h4>Avg Load Factor: {row['avg_load_factor']:.1f}%</h4>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.warning("⚠️ Column 'class_of_service' not found in dataset.")

        st.info("🗑️ Columns hidden: " + ", ".join(hide_cols))

    # ================== Tabs للتقارير التفصيلية ==================
    with tabs[1]:
        load_factor.show(df)
    with tabs[2]:
        sales_class.show(df)
