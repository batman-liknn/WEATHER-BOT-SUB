import firebase_admin
from firebase_admin import credentials, db
import time
import requests

# ✅ Use local file for credentials
cred = credentials.Certificate("secrets/firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://weather-dbf64-default-rtdb.firebaseio.com/'
})

print("🌍 Monitoring Firebase for new city entries...")

def get_weather_data(city_name):
    api_key = "YOUR_API_KEY"  # Replace with real API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    params = {'q': city_name, 'appid': api_key, 'units': 'metric'}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def listener(event):
    city_name = event.data
    print(f"📩 New city received: {city_name}")
    if city_name:
        weather_data = get_weather_data(city_name)
        if weather_data:
            ref = db.reference('/weather')
            ref.set(weather_data)
            print(f"✅ Weather data for {city_name} updated in Firebase.")
        else:
            print("❌ Failed to get weather data.")

def monitor_new_cities():
    ref = db.reference('/city')
    ref.listen(listener)

if __name__ == "__main__":
    monitor_new_cities()
