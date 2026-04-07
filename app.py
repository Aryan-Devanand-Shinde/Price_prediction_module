from flask import Flask, request, jsonify, render_template
import requests
from requests.exceptions import RequestException
import numpy as np

# ✅ NEW (ADDED ONLY)
import pandas as pd
import re
from datetime import datetime

app = Flask(__name__)

# ✅ NEW (ADDED ONLY)
df = pd.read_excel(r"C:\Users\shind\Desktop\BE_PROJECT\PRICE PREDICTION MODEL\wholesale_commodity_prices.xlsx")
df['State'] = df['State'].astype(str).str.strip().str.lower()
df['Commodity'] = df['Commodity'].astype(str).str.strip().str.lower()


# ==============================
# 🌍 Reverse Geocode
# ==============================
def reverse_geocode_state(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"format": "jsonv2", "lat": lat, "lon": lon}
    headers = {"User-Agent": "PriceApp/1.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
    except RequestException:
        return "Unknown"

    return data.get("address", {}).get("state", "Unknown")


# ==============================
# 🌶️ Commodity Map
# ==============================
COMMODITY_MAP = {
    "onion": ["onion", "onion dry", "onion green"],
    "tomato": ["tomato", "tomato hybrid"],
    "potato": ["potato"],
    "cabbage": ["cabbage"],
    "carrot": ["carrot"],
    "chilli": ["chilli", "green chilli", "red chilli"],
    "brinjal": ["brinjal"],
    "cucumber": ["cucumber"],
    "cauliflower": ["cauliflower"],
    "beetroot": ["beetroot", "beet"],
    "bhindi": ["bhindi", "bhendi", "ladies finger"],
    "garlic": ["garlic"],
    "ginger": ["ginger"],
    "sweet potato": ["sweet potato"],
    "spring onion": ["spring onion"],
    "spinach": ["spinach"],
    "methi": ["methi", "fenugreek"],
    "coriander leaves": ["coriander leaves", "dhaniya"],
    "bottle gourd": ["bottle gourd", "lauki"],
    "ridge gourd": ["ridge gourd", "turai"],
    "bitter gourd": ["bitter gourd", "karela"],
    "snake gourd": ["snake gourd"],
    "drumstick": ["drumstick"],
    "pumpkin": ["pumpkin"],
    "capsicum": ["capsicum", "bell pepper"],
}


# ==============================
# 📦 Fetch Data
# ==============================
API_KEY = "579b464db66ec23bdd0000019cbc42efd27b401673aa06ae28eb5b4d"

def fetch_data(state):
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 1000,
        "filters[state]": state
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("API Error:", e)
        return []

    return data.get("records", [])


# ==============================
# 🔍 Filter Commodity
# ==============================
def filter_data(data, commodity):
    aliases = COMMODITY_MAP.get(commodity.lower(), [commodity.lower()])
    result = []

    for row in data:
        item = row.get("commodity", "").lower()

        if any(alias in item for alias in aliases):
            result.append({
                "date": row.get("arrival_date"),
                "district": row.get("district"),
                "market": row.get("market"),
                "commodity": row.get("commodity"),
                "price": row.get("modal_price")
            })

    return result


# ==============================
# 💰 NOTEBOOK PRICE LOGIC (UNCHANGED)
# ==============================
def compute_prices(filtered):
    all_prices = []

    for rec in filtered:
        try:
            price = float(rec.get("price", 0))

            if 200 <= price <= 6000:
                all_prices.append(price)

        except:
            continue

    if len(all_prices) == 0:
        return 0, 0

    prices = np.array(all_prices)

    if len(prices) > 10:
        low = np.percentile(prices, 5)
        high = np.percentile(prices, 95)
        prices = prices[(prices >= low) & (prices <= high)]

    base_price = np.percentile(prices, 10)
    max_price = np.percentile(prices, 90)

    return round(base_price, 2), round(max_price, 2)


# ==============================
# 📊 EXCEL FUNCTION (NEW ONLY)
# ==============================
def get_excel_prices(state, commodity):
    try:
        state_name = state.strip().lower()
        commodity_name = re.sub(r'[^a-zA-Z ]', '', commodity).strip().lower()
        current_month = datetime.now().month

        filtered = df[
            (df['State'] == state_name) &
            (df['Commodity'] == commodity_name) &
            (df['Month'] == current_month)
        ]

        if not filtered.empty:
            return float(filtered['MinPrice'].min()), float(filtered['MaxPrice'].max())
        else:
            return None, None

    except Exception as e:
        print("Excel Error:", e)
        return None, None


# ==============================
# 🏠 ROUTES
# ==============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)

    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        commodity = data.get("commodity", "chilli")

        state = reverse_geocode_state(lat, lon)

        if state == "Unknown":
            raise Exception("State detection failed")

        all_data = fetch_data(state)
        filtered = filter_data(all_data, commodity)

        # 🔥 ORIGINAL (UNCHANGED)
        base_price, max_price = compute_prices(filtered)

        # 🔥 NEW (ADDED ONLY)
        excel_min, excel_max = get_excel_prices(state, commodity)

        return jsonify({
            "status": "success",
            "state": state,
            "total_records": len(all_data),
            "filtered_count": len(filtered),
            "data": filtered[:10],

            # ORIGINAL
            "base_price": base_price,
            "max_price": max_price,
            "base_price_kg": round(base_price / 100, 2),
            "max_price_kg": round(max_price / 100, 2),

            # NEW
            "excel_min": excel_min,
            "excel_max": excel_max
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)