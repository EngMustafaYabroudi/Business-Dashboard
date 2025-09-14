import streamlit as st
import pandas as pd

def show(df: pd.DataFrame):
    st.title("📋 Agent User Privileges")

    # ----- استخراج قائمة الأدوار الفريدة -----
    all_roles = []
    for roles in df['Roles'].dropna():
        all_roles.extend(str(roles).split("\n"))
    all_roles = sorted(set([r.strip() for r in all_roles if r.strip()]))

    # ----- فلاتر -----
    filter_agent = st.multiselect(
        "Filter by Agent Name", 
        options=df['Agent Name'].unique(), 
        default=None
    )
    filter_user = st.multiselect(
        "Filter by User ID", 
        options=df['User ID'].unique(), 
        default=None
    )
    filter_role = st.multiselect(
        "Filter by Role", 
        options=all_roles, 
        default=None
    )

    df_filtered = df.copy()

    if filter_agent:
        df_filtered = df_filtered[df_filtered['Agent Name'].isin(filter_agent)]
    if filter_user:
        df_filtered = df_filtered[df_filtered['User ID'].isin(filter_user)]
    if filter_role:
        df_filtered = df_filtered[df_filtered['Roles'].apply(
            lambda x: any(r in str(x).split("\n") for r in filter_role)
        )]

    # ----- جدول عادي للبيانات -----
    st.subheader("Agent Users Table")
    st.dataframe(
        df_filtered[["User ID", "User Name", "Agent Name", "Roles"]],
        height=400,
        use_container_width=True
    )

    st.markdown("---")

    # ----- إحصائيات -----
    st.subheader("📊 Summary Statistics")
    total_users = df_filtered['User ID'].nunique()

    # استخراج كل الأدوار من العمود "Roles"
    all_roles_filtered = []
    for roles in df_filtered['Roles'].dropna():
        all_roles_filtered.extend(str(roles).split("\n"))

    all_roles_filtered = [r.strip() for r in all_roles_filtered if r.strip()]
    role_counts = pd.Series(all_roles_filtered).value_counts()

    total_roles = len(role_counts)

    st.markdown(f"""
    <div style="font-size: 14px; line-height: 1.6;">
        <b>Unique Users:</b> {total_users}<br>
        <b>Unique Roles:</b> {total_roles}
    </div>
    """, unsafe_allow_html=True)

    # عرض الأدوار مع عدد مرات التكرار
    st.write("### Roles Frequency")
    st.dataframe(role_counts.reset_index().rename(columns={"index": "Role", 0: "Count"}))

    # ----- Top 5 Users بعدد الصلاحيات -----
    df_filtered["Role Count"] = df_filtered["Roles"].apply(
        lambda x: len(str(x).split("\n")) if pd.notna(x) else 0
    )

    top_users = df_filtered.sort_values("Role Count", ascending=False).head(5)

   # افترض أن df هو جدولك الأصلي
    # تحسين عرض Roles List: كل دور في سطر جديد داخل الخلية
    top_users["Roles List"] = top_users["Roles"].apply(
        lambda x: "<br>".join(str(x).split("\n")) if pd.notna(x) else ""
    )
    
    # إنشاء جدول HTML responsive
    def render_html_table(df):
        html = "<table style='width:100%; border-collapse: collapse;'>"
        
        # رؤوس الجدول
        html += "<thead><tr>"
        for col in df.columns:
            html += f"<th style='border: 1px solid #ddd; padding: 8px; text-align:left;'>{col}</th>"
        html += "</tr></thead>"
        
        # بيانات الجدول
        html += "<tbody>"
        for _, row in df.iterrows():
            html += "<tr>"
            for col in df.columns:
                html += f"<td style='border: 1px solid #ddd; padding: 8px; vertical-align:top;'>{row[col]}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        
        return html
    
    st.subheader("🏆 Top 5 Users with Most Roles")
    st.markdown(render_html_table(top_users[["User ID", "User Name", "Agent Name", "Role Count", "Roles List"]]), unsafe_allow_html=True)
