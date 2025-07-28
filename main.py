import firebase_admin
from firebase_admin import credentials, db
import requests
import os
import json

# Load Firebase credentials from environment variable
firebase_credentials = os.environ.get("FIREBASE_CREDENTIALSs")
if not firebase_credentials:
    raise ValueError("Missing FIREBASE_CREDENTIALS environment variable.")

cred_dict = json.loads(firebase_credentials)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://weather-dbf64-default-rtdb.firebaseio.com/"
})

# OpenWeatherMap API Key from environment variable (optional: for safety)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "64bfa1e41dbb4642872996ac65f6f039")

def fetch_weather_and_update(city_name, city_key):
    """Fetch weather data for the city and update Firebase."""
    try:
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
        print(f"✅ Weather data for {city_name} updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching weather data for {city_name}: {e}")
        db.reference(f"/cities/{city_key}").update({"status": "error", "message": str(e)})

def monitor_new_cities():
    """Monitor Firebase for new cities to fetch weather data."""
    ref = db.reference("/cities")

    def listener(event):
        if event.data and isinstance(event.data, dict) and "location" in event.data:
            city_name = event.data["location"]
            city_key = event.path.lstrip("/")  # Extract city key
            fetch_weather_and_update(city_name, city_key)

    ref.listen(listener)

if __name__ == "__main__":
    print("🌍 Monitoring Firebase for new city entries...")
    monitor_new_cities()
