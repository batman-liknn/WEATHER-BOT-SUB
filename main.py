import os
import json
import firebase_admin
from firebase_admin import credentials, db
import requests

# Load credentials from environment variable
cred_data = json.loads(os.environ["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(cred_data)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://weather-dbf64-default-rtdb.firebaseio.com/"
})

# Replace with your OpenWeatherMap API key
OPENWEATHER_API_KEY = "64bfa1e41dbb4642872996ac65f6f039"

def fetch_weather_and_update(city_name, city_key): 
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
        print(f"✅ Weather data for {city_name} updated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching weather for {city_name}: {e}")
        db.reference(f"/cities/{city_key}").update({"status": "error", "message": str(e)})

def monitor_new_cities():
    ref = db.reference("/cities")

    def listener(event):
        if event.data and isinstance(event.data, dict) and "location" in event.data:
            city_name = event.data["location"]
            city_key = event.path.strip("/")
            fetch_weather_and_update(city_name, city_key)

    ref.listen(listener)

def add_city(city_key, city_name):
    """Add a city to trigger weather update."""
    ref = db.reference(f"/cities/{city_key}")
    ref.set({
        "location": city_name
    })
    print(f"📝 Added city '{city_name}' under key '{city_key}'")

if __name__ == "__main__":
    print("🌍 Monitoring Firebase for new city entries...")
    
    # 🧪 Uncomment to test by adding a city
    # add_city("city1", "Hyderabad")

    monitor_new_cities()
