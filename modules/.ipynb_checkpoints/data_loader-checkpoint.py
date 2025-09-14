import pandas as pd
import os
import re
import streamlit as st
DATA_FOLDER = "data"
OUTPUT_FOLDER = "processed"

KEEP_COLS_SEAT = [
    "flight_date", "flight_no", "segment", "class_of_service",
    "seats_allocated", "seats_sold", "seats_available", "seat_factor"
]

# def load_seat_inventory(file_name: str) -> pd.DataFrame:
#     file_path = os.path.join(DATA_FOLDER, file_name)
#     df = pd.read_csv(file_path)

#     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

#     rename_map = {
#         "flight_date": "flight_date",
#         "flight_no": "flight_no",
#         "segment": "segment",
#         "cos": "class_of_service",
#         "seats_allocate": "seats_allocated",
#         "seats_sold": "seats_sold",
#         "fare_collection(usd)": "fare_usd",
#         "seat_factor": "seat_factor",
#         "seats_available": "seats_available"
#     }
#     df = df.rename(columns=rename_map)

#     numeric_cols = ["fare_usd", "seats_sold", "seats_allocated", "seats_available"]
#     for col in numeric_cols:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

#     if "flight_date" in df.columns:
#         df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

#     df = df[[col for col in KEEP_COLS_SEAT if col in df.columns]]
#     return df

def load_seat_inventory(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة الملف مع تجاوز أول 4 أسطر --------
    df = pd.read_csv(file_path, skiprows=4)

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3, :]

    # -------- تنظيف أسماء الأعمدة --------
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # -------- إعادة تسمية الأعمدة لتوحيد الأسماء --------
    rename_map = {
        "flight_date": "flight_date",
        "flight_no": "flight_no",
        "segment": "segment",
        "cos": "class_of_service",
        "seats_allocate": "seats_allocated",
        "seats_sold": "seats_sold",
        "fare_collection(usd)": "fare_usd",
        "seat_factor": "seat_factor",
        "seats_available": "seats_available"
    }
    df = df.rename(columns=rename_map)

    # -------- تحويل الأعمدة الرقمية --------
    numeric_cols = ["seats_allocated", "seats_available", "fare_usd"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------- حساب Sold Seats --------
    df["sold_seats"] = df["seats_allocated"] - df["seats_available"]
    df["seats_sold"] = df["seats_allocated"] - df["seats_available"]

    # -------- حساب Seat Factor كنسبة Sold Seats على Allocated --------
    df["seat_factor"] = df.apply(
        lambda row: row["sold_seats"] / row["seats_allocated"] if row["seats_allocated"] > 0 else 0,
        axis=1
    )

    # -------- تحويل Flight Date --------
    if "flight_date" in df.columns:
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

    # -------- الاحتفاظ بالأعمدة المهمة فقط --------
    df = df[[col for col in KEEP_COLS_SEAT if col in df.columns]]

    return df


def load_employee_performance(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.replace('\n', ' ')

    rename_map = {
        'Agent Name': 'agent_name',
        'Login ID': 'login_id',
        'User Name': 'user_name',
        'No. of Reservations': 'reservations',
        'No. of PAX': 'pax',
        'Total Charges(USD)': 'total_charges',
        'Total Discount(USD)': 'total_discount'
    }
    df = df.rename(columns=rename_map)

    for col in ['reservations', 'pax', 'total_charges', 'total_discount']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    return df

def load_payment_report(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة أول 5 أسطر لاستخراج التواريخ --------
    with open(file_path, 'r', encoding='utf-8') as f:
        header_lines = [next(f).strip() for _ in range(5)]

    from_date = None
    to_date = None
    for line in header_lines:
        # البحث عن From Date
        if "From Date" in line:
            match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if match:
                from_date = pd.to_datetime(match.group(1), dayfirst=True, errors='coerce')

        # البحث عن To Date
        if "To Date" in line:
            match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if match:
                to_date = pd.to_datetime(match.group(1), dayfirst=True, errors='coerce')

    # -------- قراءة البيانات مع تخطي أول 5 أسطر --------
    df = pd.read_csv(file_path, skiprows=5)

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3]

    # -------- تنظيف الأعمدة الرقمية --------
    if 'Net Amount' in df.columns:
        df['Net Amount'] = df['Net Amount'].astype(str).str.replace(',', '').str.strip()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')

    # -------- إضافة أعمدة التاريخ --------
    df['report_from_date'] = from_date
    df['report_to_date'] = to_date

    # -------- إزالة الصفوف الفارغة في الأعمدة المهمة --------
    df = df.dropna(subset=['Net Amount'])

    # -------- حفظ الملف بعد المعالجة --------
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, file_name.replace(".csv", "_processed.csv"))
    df.to_csv(output_path, index=False)
    print(f"Processed file saved at: {output_path}")

    return df

def load_enplanement_report(file_name: str) -> pd.DataFrame:
    """
    Load and clean EnplanementReport CSV file:
    - Skip first 5 rows (headers)
    - Remove last 3 rows (summary/empty)
    - Clean column names (remove newlines and extra spaces)
    - Convert numeric columns to integers
    - Split 'Booked Load (Adult/Infant)' into adult_booked and infant_booked
    - Ensure Flight Number, Segment, Departure Date are clean
    """
    file_path = os.path.join(DATA_FOLDER, file_name)
    
    # -------- Read CSV skipping first 5 rows --------
    df = pd.read_csv(file_path, skiprows=5)
    
    # -------- Remove last 3 rows --------
    if len(df) > 3:
        df = df.iloc[:-3]
    
    # -------- Clean column names --------
    df.columns = df.columns.str.strip().str.replace('\n', ' ', regex=True).str.replace('  ', ' ', regex=False)
    
    # -------- Rename columns to convenient names --------
    rename_map = {
        'Go Shows': 'go_shows',
        'No Shows': 'no_shows',
        'Flown Load': 'flown_load',
        'Booked Load (Adult/Infant)': 'booked_load',
        'Flight Number': 'flight_number',
        'Segment': 'segment',
        'Departure Date': 'departure_date'
    }
    df = df.rename(columns=rename_map)
    
    # -------- Split booked_load into adult_booked and infant_booked --------
    if 'booked_load' in df.columns:
        df[['adult_booked', 'infant_booked']] = df['booked_load'].astype(str).str.split(r'\\', expand=True)
        df['adult_booked'] = pd.to_numeric(df['adult_booked'], errors='coerce').fillna(0).astype(int)
        df['infant_booked'] = pd.to_numeric(df['infant_booked'], errors='coerce').fillna(0).astype(int)
        df = df.drop(columns=['booked_load'])
    
    # -------- Convert numeric columns --------
    numeric_cols = ['go_shows', 'no_shows', 'flown_load']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.extract(r'(\d+)')[0], errors='coerce').fillna(0).astype(int)
    
    # -------- Clean Flight Number, Segment, Departure Date --------
    if 'flight_number' in df.columns:
        df['flight_number'] = df['flight_number'].astype(str).str.strip().str.replace('\n', '', regex=True)
    if 'segment' in df.columns:
        df['segment'] = df['segment'].astype(str).str.strip().str.replace('\n', '', regex=True)
    if 'departure_date' in df.columns:
        df['departure_date'] = pd.to_datetime(df['departure_date'], errors='coerce')
    
    return df


   
def load_agent_productivity(file_name: str) -> pd.DataFrame:
    import os, re
    import pandas as pd

    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة أول 5 أسطر لاستخراج التواريخ --------
    with open(file_path, 'r', encoding='utf-8') as f:
        header_lines = [next(f).strip() for _ in range(5)]

    from_date = None
    to_date = None
    for line in header_lines:
        if "From Date" in line:
            match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if match:
                from_date = pd.to_datetime(match.group(1), dayfirst=True, errors='coerce')
        if "To Date" in line:
            match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if match:
                to_date = pd.to_datetime(match.group(1), dayfirst=True, errors='coerce')

    # -------- قراءة البيانات مع تخطي أول 6 أسطر --------
    df = pd.read_csv(file_path, skiprows=6)

    # -------- حذف أي أعمدة فارغة بدون اسم أو كل قيمها NaN --------
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(axis=1, how='all')

    # -------- تنظيف أسماء الأعمدة --------
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')

    # -------- إعادة تسمية الأعمدة لتوحيد الأسماء --------
    rename_map = {
        'Agent Code': 'agent_code',
        'Agent Name': 'agent_name',
        'Current Sale(USD)': 'current_sale_usd',
        'YTD Sale for the Month(USD)': 'ytd_sale_month_usd',
        'YTD Sale(USD)': 'ytd_sale_usd'
    }
    df = df.rename(columns=rename_map)

    # -------- تحويل الأعمدة الرقمية --------
    numeric_cols = ['current_sale_usd', 'ytd_sale_month_usd', 'ytd_sale_usd']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

    # -------- إضافة أعمدة التاريخ --------
    df['report_from_date'] = from_date
    df['report_to_date'] = to_date

    # -------- إزالة أي صفوف فارغة في الأعمدة الأساسية --------
    essential_cols = ['agent_code', 'agent_name']
    df = df.dropna(subset=[col for col in essential_cols if col in df.columns])

    # -------- حذف آخر 3 أسطر إذا كانت موجودة --------
    if len(df) > 3:
        df = df.iloc[:-3]

    # -------- حفظ الملف بعد المعالجة --------
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, file_name.replace(".csv", "_processed.csv"))
    df.to_csv(output_path, index=False)
    print(f"Processed file saved at: {output_path}")

    return df


def load_invoice_summary_report(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة الملف كسطور --------
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # -------- استخراج Year و Month من أول 9 أسطر --------
    year, month = None, None
    for line in lines[:9]:
        if "Year" in line:
            # إزالة أي فواصل أو نص بعد الرقم
            year = line.split(":")[-1].strip().split(",")[0]
        if "Month" in line:
            month = line.split(":")[-1].strip().split(",")[0]

    # -------- قراءة الجدول ابتداءً من السطر 10 --------
    df = pd.read_csv(file_path, skiprows=9)

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3, :]

    # -------- تنظيف أسماء الأعمدة فوراً --------
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", " ")
        .str.replace("  ", " ")
        .str.replace('"', '')
    )

    # -------- حذف الأعمدة الفارغة بالكامل --------
    df = df.loc[:, df.columns.str.strip() != ""]
    df = df.dropna(axis=1, how="all")

    # -------- تنظيف الأعمدة الرقمية --------
    numeric_cols = ["Invoice Total", "Fare", "Tax", "Surcharge"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", "")          
                .str.replace("[^0-9.-]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------- إضافة أعمدة السنة والشهر للمعالجة الداخلية فقط --------
    df["report_year"] = year
    df["report_month"] = month

    return df


def load_agent_user_privileges(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(file_path, skiprows=4)  # حذف أول 4 أسطر
    if len(df) > 3:
        df = df.iloc[:-3, :]  # حذف آخر 3 أسطر

    # إعادة تسمية الأعمدة
    df.columns = ['Agent Code', 'Agent Name', 'User ID', 'User Name', 'Role']

    # ملء الفراغات في الأعمدة التعريفية
    df[['Agent Code', 'Agent Name', 'User ID', 'User Name']] = df[['Agent Code', 'Agent Name', 'User ID', 'User Name']].ffill()

    # حذف الصفوف بدون Role
    df = df[df['Role'].notna()].reset_index(drop=True)

    return df

@st.cache_data
def load_agent_user_privileges(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة الملف كسطور --------
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # -------- حذف أول 4 أسطر --------
    data_lines = lines[4:]

    # -------- تحويل السطور إلى DataFrame --------
    import io
    data_str = "".join(data_lines)
    df = pd.read_csv(io.StringIO(data_str))

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3, :]

    # -------- تنظيف أسماء الأعمدة --------
    df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace('"', '')
    
    # -------- حذف الأعمدة الفارغة بالكامل --------
    df = df.loc[:, df.columns.str.strip() != ""]
    df = df.dropna(axis=1, how="all")

    # -------- ملء الفراغات في الأعمدة التعريفية --------
    key_cols = ["Agent Code", "Agent Name", "User ID", "User Name"]
    for col in key_cols:
        if col in df.columns:
            df[col] = df[col].ffill()  # fill forward القيم الفارغة بالأعلى

    # -------- دمج Roles لكل شخص --------
    if "Roles" in df.columns:
        df = df.groupby(key_cols, dropna=False)["Roles"] \
               .apply(lambda x: "\n".join(str(r).strip() for r in x if pd.notna(r))) \
               .reset_index()

        # حذف أي صفوف لا تحتوي على أي دور
        df = df[df["Roles"].str.strip() != ""].reset_index(drop=True)

    return df
