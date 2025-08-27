# modules/enplanement_analysis.py

import streamlit as st
import pandas as pd

def show(df: pd.DataFrame):
    st.title("🛫 Enplanement Report")

    # -------- عرض أسماء الأعمدة للتأكد --------
    st.subheader("📌 Columns in DataFrame")
    st.write(df.columns.tolist())

    # -------- إعادة تسمية الأعمدة لتسهيل الاستخدام --------
    rename_map = {
        'Go Shows': 'go_shows',
        'No Shows': 'no_shows',
        'Flown Load': 'flown_load'
    }
    df = df.rename(columns=rename_map)

    # -------- تنظيف الأعمدة الرقمية --------
    numeric_cols = ['go_shows', 'no_shows', 'flown_load']
    for col in numeric_cols:
        if col in df.columns:
            # إزالة أي رموز غير رقمية مع السماح بالأرقام فقط
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r'[^\d]', '', regex=True)
                .replace('', '0')  # تحويل الفراغات إلى صفر
            )
            # تحويل القيم المستخرجة إلى أعداد صحيحة
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # -------- عرض الجدول --------
    st.subheader("📋 Enplanement Data")
    st.dataframe(df, use_container_width=True)

    # -------- إحصائيات أساسية --------
    total_flights = df.shape[0]
    total_go_shows = df['go_shows'].sum() if 'go_shows' in df.columns else 0
    total_no_shows = df['no_shows'].sum() if 'no_shows' in df.columns else 0
    total_flown = df['flown_load'].sum() if 'flown_load' in df.columns else 0

    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Flights", f"{total_flights}")
    col2.metric("Total Go Shows", f"{total_go_shows}")
    col3.metric("Total No Shows", f"{total_no_shows}")
    col4.metric("Total Flown Load", f"{total_flown}")
