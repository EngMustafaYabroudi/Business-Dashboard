import os
import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.initializers import Orthogonal
from sklearn.preprocessing import MinMaxScaler

def show(df):
    st.subheader("🔮 Daily Seats Sold Statistics & Forecast")

    # التحقق من وجود الأعمدة الصحيحة
    if "seats_sold" not in df.columns or "flight_date" not in df.columns:
        st.warning("❌ Missing 'seats_sold' or 'flight_date' columns in the DataFrame.")
        return

    # ---------------- Daily sold seats ----------------
    daily_sold = df.groupby("flight_date")["seats_sold"].sum().reset_index()
    daily_sold["flight_date"] = pd.to_datetime(
        daily_sold["flight_date"], errors="coerce"
    ).dt.date

    # ---------------- إحصاءات عن الأيام ----------------
    max_row = daily_sold.loc[daily_sold["seats_sold"].idxmax()]
    min_row = daily_sold.loc[daily_sold["seats_sold"].idxmin()]
    mean_sold = daily_sold["seats_sold"].mean()
    median_sold = daily_sold["seats_sold"].median()
    mode_sold = daily_sold["seats_sold"].mode().tolist()

    stats_table = pd.DataFrame({
        "Statistic": ["Max Day", "Min Day", "Mean", "Median", "Mode"],
        "Value": [
            f"{int(max_row['seats_sold'])} on {max_row['flight_date']}",
            f"{int(min_row['seats_sold'])} on {min_row['flight_date']}",
            round(mean_sold, 1),
            round(median_sold, 1),
            ", ".join([str(int(m)) for m in mode_sold])
        ]
    })

    # ---------------- عرض النتائج ----------------
    st.markdown("### 📊 Daily Seats Sold")
    st.dataframe(daily_sold)

    st.markdown("### 📈 Statistics Summary")
    st.table(stats_table)

    st.markdown("### 📉 Seats Sold Over Time")
    st.line_chart(
        daily_sold.rename(columns={"flight_date": "index"}).set_index("index")["seats_sold"]
    )

    # ---------------- اختيار النموذج ----------------
    model_choice = st.radio("اختر نموذج التنبؤ:", ["Prophet", "LSTM"])

    if model_choice == "Prophet":
        # ---------------- Prophet Forecast ----------------
        st.markdown("### 🔮 Seats Sold Forecast (Next 30 Days)")

        prophet_df = daily_sold.rename(columns={"flight_date": "ds", "seats_sold": "y"})
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
        prophet_df = prophet_df.dropna(subset=["ds", "y"])

        model = Prophet(daily_seasonality=True)
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        forecast_table = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].rename(columns={
            "ds": "Date",
            "yhat": "Predicted Total Sold Seats",
            "yhat_lower": "Lower Bound",
            "yhat_upper": "Upper Bound"
        })

        start_date = pd.to_datetime("2025-09-11")
        forecast_future_only = forecast_table[forecast_table["Date"] >= start_date]
        st.dataframe(forecast_future_only.head(10))

        fig1 = model.plot(forecast)
        st.pyplot(fig1)

        fig2 = model.plot_components(forecast)
        st.pyplot(fig2)

    else:
        # ---------------- LSTM Forecast ----------------
        st.markdown("### 🔮 Seats Sold Forecast with LSTM")

        # تجهيز البيانات
        data = daily_sold["seats_sold"].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)

        sequence_length = 30
        last_sequence = data_scaled[-sequence_length:].reshape(1, sequence_length, 1)

        # ---------------- تحميل الموديل ----------------
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "models", "lstm_seats_sold_model.keras")
        
        try:
            model = load_model(MODEL_PATH, custom_objects={"Orthogonal": Orthogonal})
        except Exception as e1:
            st.warning(f"⚠️ فشل التحميل مع Orthogonal: {e1}")
            try:
                model = load_model(MODEL_PATH, compile=False)
                model.compile(optimizer="adam", loss="mean_squared_error")
            except Exception as e2:
                st.error(f"❌ لم يتم تحميل الموديل: {e2}")
                return

        # ---------------- التنبؤ للأيام القادمة ----------------
        future_days = 100
        predictions = []
        temp_input = list(data_scaled[-sequence_length:])

        for _ in range(future_days):
            x_input = np.array(temp_input[-sequence_length:]).reshape(1, sequence_length, 1)
            yhat = model.predict(x_input, verbose=0)
            temp_input.append(yhat[0])
            predictions.append(yhat[0])

        predictions = scaler.inverse_transform(predictions)

        # تجهيز جدول التوقعات
        future_dates = pd.date_range(
            start=pd.to_datetime(daily_sold["flight_date"].max()) + pd.Timedelta(days=1),
            periods=future_days
        )
        forecast_table = pd.DataFrame({
            "Date": future_dates,
            "Predicted Seats Sold": predictions.flatten()
        })

        st.dataframe(forecast_table.head(30))

        # رسم النتائج
        st.line_chart(pd.DataFrame({
            "Actual": daily_sold.set_index("flight_date")["seats_sold"],
            "Forecast": forecast_table.set_index("Date")["Predicted Seats Sold"]
        }))
