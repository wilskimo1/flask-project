from flask import Blueprint, request, jsonify
import os
import requests

weather_bp = Blueprint("weather", __name__)

# 🌍 OpenWeather API Key from Environment Variable
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@weather_bp.route("/", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    state = request.args.get("state")  # Accept state (for US locations)
    country = request.args.get("country", "US")  # Default country to "US" if not provided
    zip_code = request.args.get("zip")  # Accept ZIP code
    lat = request.args.get("lat")  # Accept latitude
    lon = request.args.get("lon")  # Accept longitude

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "API Key is missing!"}), 500

    try:
        # 🌍 Construct API Query based on user input
        if zip_code:
            location_query = f"zip={zip_code},{country}"
        elif lat and lon:
            location_query = f"lat={lat}&lon={lon}"
        elif city and state and country == "US":
            location_query = f"q={city},{state},{country}"
        elif city:
            location_query = f"q={city},{country}"
        else:
            return jsonify({"error": "You must provide a city, zip code, or coordinates."}), 400

        # ✅ OpenWeather API URL
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?{location_query}&appid={OPENWEATHER_API_KEY}&units=imperial"

        response = requests.get(weather_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": f"Weather API error: {data.get('message', 'Unknown error')}"})

        # ✅ Extract necessary data
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }

        return jsonify(weather_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
