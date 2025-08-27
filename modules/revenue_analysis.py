import streamlit as st
import pandas as pd
import altair as alt

def show(df):
    st.title("💰 Revenue Analysis")

    # التأكد من وجود الأعمدة
    if "segment" not in df.columns or "fare_usd" not in df.columns:
        st.warning("🚨 Columns 'segment' or 'fare_usd' not found in this report")
        return

    # حساب الإيرادات لكل Route
    seg_rev = df.groupby("segment")["fare_usd"].sum().reset_index()
    seg_rev = seg_rev.sort_values(by="fare_usd", ascending=False)

    # رسم المخطط باستخدام Altair
    chart = alt.Chart(seg_rev).mark_bar(color="#1f77b4").encode(
        x=alt.X('segment:N', sort='-y', title='Route'),
        y=alt.Y('fare_usd:Q', title='Revenue (USD)'),
        tooltip=[alt.Tooltip('segment:N', title='Route'),
                 alt.Tooltip('fare_usd:Q', title='Revenue (USD)', format=',.2f')]
    ).properties(
        width=800,
        height=400,
        title="Revenue by Route"
    )

    # إضافة القيم فوق الأعمدة باللون الأبيض
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,  # رفع النص فوق العمود
        color='white',  # اللون أبيض
        fontSize=10
    ).encode(
        text=alt.Text('fare_usd:Q', format=',.0f')
    )

    st.altair_chart(chart + text, use_container_width=True)

    # ملخص سريع
    total_revenue = seg_rev['fare_usd'].sum()
    st.markdown(f"**Total Revenue (All Routes):** ${total_revenue:,.2f}")

    # ---------- فلتر تحت المخطط ----------
    st.markdown("---")
    st.subheader("💡 Revenue Lookup by Route")
    route_options = seg_rev['segment'].tolist()
    selected_route = st.selectbox("Select a Route", options=route_options)

    # عرض قيمة الإيراد للـ Route المختار
    revenue_value = seg_rev.loc[seg_rev['segment'] == selected_route, 'fare_usd'].values[0]
    st.info(f"**Revenue for {selected_route}:** ${revenue_value:,.2f}")
