from flask import Blueprint, request, jsonify
import os
import requests

weather_bp = Blueprint("weather", __name__)

# 🌍 OpenWeather API Key from Environment Variable
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@weather_bp.route("/", methods=["GET"])
def get_weather():
    """Fetches weather data based on City or City + State combination."""
    
    city = request.args.get("city")
    state = request.args.get("state")  # Optional state (for US locations)
    country = "US"  # Default country to US

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "API Key is missing!"}), 500

    if not city:
        return jsonify({"error": "Please provide a city name."}), 400  # 🚨 City is REQUIRED

    try:
        # ✅ If state is provided, use "city,state,US"
        if state:
            location_query = f"q={city},{state},{country}"
        else:
            location_query = f"q={city},{country}"  # ✅ City-only search
        
        # ✅ OpenWeather API URL
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?{location_query}&appid={OPENWEATHER_API_KEY}&units=imperial"

        response = requests.get(weather_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": f"Weather API error: {data.get('message', 'Unknown error')}"})

        # ✅ Extract necessary data
        weather_info = {
            "city": data.get("name", "Unknown Location"),
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
