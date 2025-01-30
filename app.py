import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv


# Load API key from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.form.get('city')  # Get city name from form input
    if not city:
        return render_template('index.html', error="Please enter a city name.")

    # Fetch weather data from OpenWeatherMap API
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    weather_response = requests.get(weather_url)

    if weather_response.status_code == 200:
        data = weather_response.json()
        
        # Extract weather data
        weather = {
            'city': city,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon']
        }

        # Fetch air quality data
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air_quality_response = requests.get(air_quality_url)

        if air_quality_response.status_code == 200:
            air_data = air_quality_response.json()
            air_quality = air_data['list'][0]['main']['aqi']  # Air quality index

            # Map the air quality index to a readable string
            if air_quality == 1:
                air_quality_text = "Good"
            elif air_quality == 2:
                air_quality_text = "Fair"
            elif air_quality == 3:
                air_quality_text = "Moderate"
            elif air_quality == 4:
                air_quality_text = "Poor"
            else:
                air_quality_text = "Very Poor"
            
            # Add air quality to weather dictionary
            weather['air_quality'] = str(air_quality) + " - " + air_quality_text
        else:
            weather['air_quality'] = "Unavailable"
        
        # Get the chance of rain (if exists)
        rain_chance = data.get('rain', {}).get('1h', 0)  # rainfall in last 1 hour
        weather['rain_chance'] = f"{rain_chance}%"
        
        return render_template('index.html', weather=weather)
    
    else:
        return render_template('index.html', error="City not found. Please try again.")

if __name__ == "__main__":
    app.run()
