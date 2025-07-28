import os
import json
import firebase_admin
from firebase_admin import credentials, db
import requests

# Load Firebase credentials from environment variable
firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
if not firebase_json:
    raise ValueError("Missing FIREBASE_CREDENTIALS_JSON environment variable.")

# Parse JSON string into dictionary
cred_data = json.loads(firebase_json)

# Initialize Firebase app
cred = credentials.Certificate(cred_data)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://weather-dbf64-default-rtdb.firebaseio.com/"
})

# OpenWeatherMap API key
OPENWEATHER_API_KEY = "64bfa1e41dbb4642872996ac65f6f039"  # Replace with your real one if needed

def fetch_weather_and_update(city_name, city_key):
    try:
        print(f"🔄 Fetching weather for {city_name}...")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        weather_data = response.json()
        formatted_data = {
            "location": weather_data.get("name"),
            "weather": weather_data["weather"][0]["description"],
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "status": "success"
        }

        db.reference(f"/cities/{city_key}").update(formatted_data)
        print(f"✅ Updated weather for {city_name}")
    except Exception as e:
        print(f"❌ Failed for {city_name}: {e}")
        db.reference(f"/cities/{city_key}").update({"status": "error", "message": str(e)})

def monitor_new_cities():
    ref = db.reference("/cities")

    def listener(event):
        if event.data and isinstance(event.data, dict) and "location" in event.data:
            city_name = event.data["location"]
            city_key = event.path.lstrip("/")  # remove leading slash
            fetch_weather_and_update(city_name, city_key)

    print("🌍 Monitoring Firebase for new city entries...")
    ref.listen(listener)

if __name__ == "__main__":
    monitor_new_cities()
