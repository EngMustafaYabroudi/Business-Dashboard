import pandas as pd
import os
import re
DATA_FOLDER = "data"

# أعمدة مهمة لمقاعد الطيران
KEEP_COLS_SEAT = [
    "flight_date", "flight_no", "segment", "class_of_service",
    "seats_allocated", "seats_sold", "seats_available", "seat_factor"
]

def load_seat_inventory(file_name: str) -> pd.DataFrame:
    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

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

    numeric_cols = ["fare_usd", "seats_sold", "seats_allocated", "seats_available"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "flight_date" in df.columns:
        df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")

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



OUTPUT_FOLDER = "processed"

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
    Load Enplanement Report CSV, extract report dates, clean numeric columns,
    skip header and footer lines.
    """
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

    # -------- قراءة البيانات مع تخطي أول 5 أسطر --------
    df = pd.read_csv(file_path, skiprows=5)

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3]

    # -------- تنظيف الأعمدة الرقمية --------
    numeric_cols = ['Booked Load (Adult/Infant)', 'Go Shows', 'No Recs. No Shows', 'Flown Load']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # -------- إضافة أعمدة التاريخ --------
    df['report_from_date'] = from_date
    df['report_to_date'] = to_date

    # -------- إزالة الصفوف الفارغة في الأعمدة المهمة --------
    important_col = 'Flown Load' if 'Flown Load' in df.columns else None
    if important_col:
        df = df.dropna(subset=[important_col])

    # -------- حفظ الملف بعد المعالجة --------
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, file_name.replace(".csv", "_processed.csv"))
    df.to_csv(output_path, index=False)
    print(f"Processed file saved at: {output_path}")

    return df

def load_enplanement_report(file_name: str) -> pd.DataFrame:
    """
    تحميل ومعالجة ملف EnplanementReport.csv:
    - حذف أول 5 أسطر (رؤوس غير ضرورية)
    - حذف آخر 3 أسطر (ملخص أو فارغ)
    - تنظيف أسماء الأعمدة
    - تحويل الأعمدة الرقمية للقيم الصحيحة
    """
    file_path = os.path.join(DATA_FOLDER, file_name)

    # -------- قراءة البيانات مع تخطي أول 5 أسطر --------
    df = pd.read_csv(file_path, skiprows=5)

    # -------- حذف آخر 3 أسطر --------
    if len(df) > 3:
        df = df.iloc[:-3]

    # -------- تنظيف أسماء الأعمدة --------
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')

    # -------- إعادة تسمية الأعمدة الرقمية --------
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
            # إزالة أي نصوص غير رقمية وتحويل للأعداد الصحيحة
            df[col] = pd.to_numeric(df[col].astype(str).str.extract(r'(\d+)')[0], errors='coerce').fillna(0).astype(int)

    return df
