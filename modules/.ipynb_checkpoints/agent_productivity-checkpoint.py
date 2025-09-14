import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px

def show(df: pd.DataFrame):
    """
    عرض KPIs لوكلاء المبيعات مع حساب نسبة المبيعات الشهرية وتصنيف العملاء باستخدام Clustering
    """
    st.title("📊 Agent Productivity KPIs with Segmentation")

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
        st.markdown(f"**Report Period:** {from_date} - {to_date}")

    # -------- عرض الجدول كامل مع النسبة --------
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

    st.markdown("---")

    # -------- Agent Segmentation using KMeans --------
    st.subheader("🤖 Agent Segmentation (KMeans)")

    # اختيار عدد المجموعات
    k = st.slider("Select Number of Segments (Clusters)", min_value=2, max_value=5, value=3)

    features = df[['current_sale_usd', 'ytd_sale_month_usd', 'ytd_sale_usd']].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    df['Segment'] = clusters

    # ترتيب وتسميات الفئات حسب إجمالي current_sale_usd
    cluster_order = df.groupby('Segment')['current_sale_usd'].sum().sort_values(ascending=False).index.tolist()
    segment_labels = {cluster_order[0]: 'A', cluster_order[1]: 'B'}
    if k == 3:
        segment_labels[cluster_order[2]] = 'C'
    else:
        for i, c in enumerate(cluster_order[2:]):
            segment_labels[c] = f'Segment {i+3}'
    df['Segment Label'] = df['Segment'].map(segment_labels)

    st.subheader("📂 Agent Segmentation Table")
    st.dataframe(df[['agent_name','current_sale_usd','ytd_sale_month_usd','ytd_sale_usd','monthly_percentage','Segment Label']])

    st.subheader("📈 Agents Segmentation Plot")
    fig_seg = px.scatter(
        df,
        x='current_sale_usd',
        y='ytd_sale_usd',
        color='Segment Label',
        hover_data=['agent_name'],
        color_discrete_sequence=px.colors.qualitative.Set2,
        size='ytd_sale_usd',  # حجم النقطة يعكس إجمالي المبيعات السنوي
        size_max=20
    )
    fig_seg.update_layout(xaxis_title="Current Sale USD", yaxis_title="YTD Sale USD", legend_title="Segment")
    st.plotly_chart(fig_seg, use_container_width=True)
