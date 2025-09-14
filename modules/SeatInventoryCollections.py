import streamlit as st
from modules.seat_inventory import overview, load_factor, sales_class
from modules.seat_inventory import predict  # تبويب جديد

def show(df):
    st.title("✈️ Seat Inventory & Collections")
    tabs = st.tabs(["Overview", "Load Factor", "Sales by Class", "Predict"])  # أضفت تبويب جديد

    with tabs[0]:
        overview.show(df)
    with tabs[1]:
        load_factor.show(df)
    with tabs[2]:
        sales_class.show(df)
    with tabs[3]:
        predict.show(df)  