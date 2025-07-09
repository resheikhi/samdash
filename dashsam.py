import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objs as go

def predict_daily_prices(ear, today_price, days=365):
    daily_rate = (1 + ear) ** (1 / 365) - 1
    prices = [today_price]
    for _ in range(days):
        new_price = prices[-1] * (1 + daily_rate)
        prices.append(new_price)
    return prices[1:], daily_rate  # بدون قیمت اولیه

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Prediction')
    processed_data = output.getvalue()
    return processed_data

st.title("پیش‌بینی قیمت صندوق درآمد ثابت با نرخ بهره موثر سالانه")

ear_input = st.number_input("نرخ بهره موثر سالانه (٪)", min_value=0.0, format="%.4f")
today_price_input = st.number_input("قیمت صندوق امروز", min_value=0.0, format="%.2f")

if st.button("محاسبه و نمایش نمودار"):
    ear = ear_input / 100
    total_days = 365
    prices, daily_rate = predict_daily_prices(ear, today_price_input, days=total_days)

    # محاسبه بازدهی ساده روزانه برای کل دوره 365 روز
    simple_returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    simple_returns.insert(0, 0)

    df = pd.DataFrame({
        "روز": list(range(1, len(prices)+1)),
        "قیمت صندوق": prices,
        "بازدهی روزانه ساده": simple_returns
    })

    # رسم نمودار برای 60 روز اول
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["روز"][:60],
        y=df["قیمت صندوق"][:60],
        mode='lines+markers',
        name='قیمت صندوق'
    ))
    fig.update_layout(
        title="نمودار پیش‌بینی قیمت صندوق تا ۲ ماه (۶۰ روز)",
        xaxis_title="روز",
        yaxis_title="قیمت صندوق"
    )

    st.plotly_chart(fig, use_container_width=True)

    # فقط ستون قیمت و بازدهی ساده در خروجی اکسل
    df_out = df[["قیمت صندوق", "بازدهی روزانه ساده"]]

    excel_data = to_excel(df_out)

    st.success("محاسبه انجام شد.")
    st.download_button(
        label="دانلود فایل اکسل",
        data=excel_data,
        file_name="predicted_prices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
