
# from flask import Flask, request, jsonify, render_template
# import requests
# from requests.exceptions import RequestException
# import numpy as np   # 🔥 REQUIRED

# app = Flask(__name__)

# # ==============================
# # 🌍 Reverse Geocode
# # ==============================
# def reverse_geocode_state(lat, lon):
#     url = "https://nominatim.openstreetmap.org/reverse"
#     params = {"format": "jsonv2", "lat": lat, "lon": lon}
#     headers = {"User-Agent": "PriceApp/1.0"}

#     try:
#         r = requests.get(url, params=params, headers=headers, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#     except RequestException:
#         return "Unknown"

#     return data.get("address", {}).get("state", "Unknown")


# # ==============================
# # 🌶️ Commodity Map
# # ==============================
# COMMODITY_MAP = {

#     # 🧅 Vegetables
#     "onion": ["onion", "onion dry", "onion green"],
#     "tomato": ["tomato", "tomato hybrid"],
#     "potato": ["potato"],
#     "cabbage": ["cabbage"],
#     "carrot": ["carrot"],
#     "chilli": ["chilli", "green chilli", "red chilli"],
#     "brinjal": ["brinjal"],
#     "cucumber": ["cucumber"],
#     "cauliflower": ["cauliflower"],
#     "beetroot": ["beetroot", "beet"],
#     "bhindi": ["bhindi", "bhendi", "ladies finger"],
#     "garlic": ["garlic"],
#     "ginger": ["ginger"],
#     "sweet potato": ["sweet potato"],
#     "spring onion": ["spring onion"],
#     "spinach": ["spinach"],
#     "methi": ["methi", "fenugreek"],
#     "coriander leaves": ["coriander leaves", "dhaniya"],
#     "bottle gourd": ["bottle gourd", "lauki"],
#     "ridge gourd": ["ridge gourd", "turai"],
#     "bitter gourd": ["bitter gourd", "karela"],
#     "snake gourd": ["snake gourd"],
#     "drumstick": ["drumstick"],
#     "pumpkin": ["pumpkin"],
#     "capsicum": ["capsicum", "bell pepper"],

#     # 🍎 Fruits
#     "apple": ["apple"],
#     "banana": ["banana"],
#     "orange": ["orange"],
#     "grapes": ["grapes"],
#     "watermelon": ["watermelon"],
#     "muskmelon": ["muskmelon"],
#     "mango": ["mango"],
#     "pineapple": ["pineapple"],
#     "papaya": ["papaya"],
#     "lemon": ["lemon"],
#     "guava": ["guava"],
#     "strawberry": ["strawberry"],

#     # 🌾 Grains
#     "wheat": ["wheat"],
#     "rice": ["rice"],
#     "maize": ["maize"],
#     "barley": ["barley"],
#     "bajra": ["bajra"],
#     "jowar": ["jowar"],

#     # 🌱 Pulses
#     "chana": ["gram", "chana"],
#     "moong": ["moong"],
#     "urad": ["urad"],
#     "masoor": ["masoor"],
#     "arhar": ["arhar", "tur", "toor"],

#     # 🌶️ Spices
#     "red chilli": ["red chilli"],
#     "turmeric": ["turmeric"],
#     "coriander": ["coriander"],
#     "cumin": ["cumin"],
#     "mustard": ["mustard"],

#     # 🥜 Oil Seeds
#     "groundnut": ["groundnut", "peanut"],
#     "sunflower": ["sunflower"],
#     "soybean": ["soybean"],
#     "sesame": ["sesame"],

#     # 🍬 Others
#     "sugarcane": ["sugarcane"],
#     "jaggery": ["jaggery"],
#     "tea": ["tea"],
#     "coffee": ["coffee"],
# }


# # ==============================
# # 📦 Fetch Data
# # ==============================
# API_KEY = "579b464db66ec23bdd0000019cbc42efd27b401673aa06ae28eb5b4d"

# def fetch_data(state):
#     url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

#     params = {
#         "api-key": API_KEY,
#         "format": "json",
#         "limit": 1000,
#         "filters[state]": state
#     }

#     try:
#         r = requests.get(url, params=params)
#         r.raise_for_status()
#         data = r.json()
#     except Exception as e:
#         print("API Error:", e)
#         return []

#     return data.get("records", [])


# # ==============================
# # 🔍 Filter Commodity
# # ==============================
# def filter_data(data, commodity):
#     aliases = COMMODITY_MAP.get(commodity.lower(), [commodity.lower()])
#     result = []

#     for row in data:
#         item = row.get("commodity", "").lower()

#         if any(alias in item for alias in aliases):
#             result.append({
#                 "date": row.get("arrival_date"),
#                 "district": row.get("district"),
#                 "market": row.get("market"),
#                 "commodity": row.get("commodity"),
#                 "price": row.get("modal_price")
#             })

#     return result


# # ==============================
# # 💰 NOTEBOOK PRICE LOGIC (FINAL)
# # ==============================
# def compute_prices(filtered):
#     all_prices = []

#     for rec in filtered:
#         try:
#             price = float(rec.get("price", 0))

#             # 🔥 SAME FILTER AS NOTEBOOK
#             if 200 <= price <= 6000:
#                 all_prices.append(price)

#         except:
#             continue

#     if len(all_prices) == 0:
#         return 0, 0

#     prices = np.array(all_prices)

#     # 🔥 REMOVE OUTLIERS (ONLY IF ENOUGH DATA)
#     if len(prices) > 10:
#         low = np.percentile(prices, 5)
#         high = np.percentile(prices, 95)
#         prices = prices[(prices >= low) & (prices <= high)]

#     # 🔥 FINAL CALCULATION (EXACT NOTEBOOK)
#     base_price = np.percentile(prices, 10)
#     max_price = np.percentile(prices, 90)

#     return round(base_price, 2), round(max_price, 2)


# # ==============================
# # 🏠 ROUTES
# # ==============================
# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/predict", methods=["POST"])
# def predict():
#     data = request.get_json(force=True)

#     try:
#         lat = float(data.get("latitude"))
#         lon = float(data.get("longitude"))
#         commodity = data.get("commodity", "chilli")

#         state = reverse_geocode_state(lat, lon)

#         if state == "Unknown":
#             raise Exception("State detection failed")

#         all_data = fetch_data(state)
#         filtered = filter_data(all_data, commodity)

#         # 🔥 USE NOTEBOOK FUNCTION
#         base_price, max_price = compute_prices(filtered)

#         return jsonify({
#             "status": "success",
#             "state": state,
#             "total_records": len(all_data),
#             "filtered_count": len(filtered),
#             "data": filtered[:10],

#             "base_price": base_price,
#             "max_price": max_price,
#             "base_price_kg": round(base_price / 100, 2),
#             "max_price_kg": round(max_price / 100, 2)
#         })

#     except Exception as e:
#         print("ERROR:", str(e))
#         return jsonify({"status": "error", "message": str(e)}), 400


# # ==============================
# # ▶ RUN APP
# # ==============================
# if __name__ == "__main__":
#     app.run(debug=True)
