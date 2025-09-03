import streamlit as st
from modules.seat_inventory import overview, load_factor, sales_class

def show(df):
    st.title("✈️ Seat Inventory & Collections")
    tabs = st.tabs(["Overview", "Load Factor", "Sales by Class"])

    with tabs[0]:
        overview.show(df)
    with tabs[1]:
        load_factor.show(df)
    with tabs[2]:
        sales_class.show(df)
