import streamlit as st
import pandas as pd

def show(df: pd.DataFrame):
    """
    عرض KPIs لوكلاء المبيعات من ملف Agent Productivity مع حساب نسبة المبيعات الشهرية
    """
    st.title("📊 Agent Productivity KPIs")

    if df is None or df.empty:
        st.warning("No data loaded.")
        return

    # -------- تنظيف الأعمدة الرقمية للتأكد --------
    numeric_cols = ['current_sale_usd', 'ytd_sale_month_usd', 'ytd_sale_usd']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # -------- حساب نسبة المبيعات الشهرية للسنوي لكل وكيل --------
    df['monthly_percentage'] = (df['ytd_sale_month_usd'] / df['ytd_sale_usd'] * 100).round(2)

    # -------- عرض فترة التقرير --------
    from_date = df['report_from_date'].iloc[0] if 'report_from_date' in df.columns else None
    to_date = df['report_to_date'].iloc[0] if 'report_to_date' in df.columns else None
    if from_date and to_date:
        st.markdown(f"**Report Period:** {from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}")

    # -------- عرض الجدول كامل مع النسبة، بدون الأعمدة غير المرغوبة --------
    display_df = df.drop(columns=[col for col in ['agent_code', 'report_from_date', 'report_to_date'] if col in df.columns])
    st.subheader("Full Agent Productivity Table")
    st.dataframe(display_df)

    # -------- إجمالي المبيعات --------
    total_current = df['current_sale_usd'].sum()
    total_ytd_month = df['ytd_sale_month_usd'].sum()
    total_ytd = df['ytd_sale_usd'].sum()

    st.metric("Total Current Sale (USD)", f"${total_current:,.2f}")
    st.metric("Total YTD Sale for the Month (USD)", f"${total_ytd_month:,.2f}")
    st.metric("Total YTD Sale (USD)", f"${total_ytd:,.2f}")

    # -------- أعلى 5 وكلاء حسب المبيعات الحالية --------
    st.subheader("Top 5 Agents by Current Sale")
    top_agents = df.sort_values(by='current_sale_usd', ascending=False).head(5)
    st.table(top_agents[['agent_name', 'current_sale_usd', 'monthly_percentage']])

    # -------- متوسط المبيعات لكل وكيل --------
    st.subheader("Average Sales per Agent")
    avg_sales = df[numeric_cols].mean()
    st.write(avg_sales)

    # -------- الوكلاء الذين تجاوزوا هدف معين --------
    st.subheader("Agents exceeding $100,000 in Current Sale")
    top_performers = df[df['current_sale_usd'] > 100000]
    if not top_performers.empty:
        st.table(top_performers[['agent_name', 'current_sale_usd', 'monthly_percentage']])
    else:
        st.info("No agents exceeded $100,000 in Current Sale.")
