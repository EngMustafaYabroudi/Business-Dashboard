import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
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

    # ----- عرض الجدول -----
    st.subheader("Agent Users Table")
    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        wrapText=True,
        minWidth=150,
        cellStyle={'font-size': '14px'}
    )
    gb.configure_grid_options(headerHeight=40)
    grid_options = gb.build()

    AgGrid(
        df_filtered,
        gridOptions=grid_options,
        height=500,
        width='100%',
        fit_columns_on_grid_load=True
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
    st.write("### 🏆 Top 5 Users with Most Roles")
    df_filtered["Role Count"] = df_filtered["Roles"].apply(
        lambda x: len(str(x).split("\n")) if pd.notna(x) else 0
    )

    top_users = df_filtered.sort_values("Role Count", ascending=False).head(5)

    top_users["Roles List"] = top_users["Roles"].apply(
        lambda x: ", ".join(str(x).split("\n")) if pd.notna(x) else ""
    )

    st.table(
        top_users[["User ID", "User Name", "Agent Name", "Role Count", "Roles List"]]
    )
