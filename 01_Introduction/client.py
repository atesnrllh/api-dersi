import httpx

response = httpx.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 41.27976,
        "longitude": 36.3361,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 1,
    },
    timeout=15,
)
response.raise_for_status()
weather = response.json()["daily"]

print("Şehir: Samsun")
print("Tarih:", weather["time"][0])
print("En yüksek sıcaklık:", weather["temperature_2m_max"][0], "°C")
print("Günün en yüksek yağış olasılığı:", weather["precipitation_probability_max"][0], "%")


if weather["precipitation_probability_max"][0] >= 50:
    print("Dışarı çıkarken yanına şemsiye al.")
else:
    print("Bugün için en yüksek yağış olasılığı %50'nin altında.")