import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show(df):
    st.title("📈 Trends & Forecast")

    st.write("🔹 هنا يمكنك إضافة تفاصيل التحليل البياني للاتجاهات والتوقعات (Trend & Forecast).")
    
    # ---------- مثال على فلتر تاريخ ----------
    if "flight_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["flight_date"]):
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    if "flight_date" in df.columns:
        min_date = df["flight_date"].min()
        max_date = df["flight_date"].max()
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="trend_forecast_start_date"  # <- key فريد
        )
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="trend_forecast_end_date"  # <- key فريد
        )
        
        # تطبيق الفلتر
        df_filtered = df[
            (df["flight_date"] >= pd.to_datetime(start_date)) &
            (df["flight_date"] <= pd.to_datetime(end_date))
        ]
    else:
        df_filtered = df.copy()
    
    st.write("📊 بيانات الفلتر جاهزة للعرض:", df_filtered.head())

    # ---------- مكان لإضافة الرسوم البيانية لاحقاً ----------
    st.info("🔹 هنا يمكنك إضافة الرسوم البيانية والتحليلات الخاصة بالتوجهات والتوقعات.")
