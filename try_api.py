from skycast import create_app
from skycast.services.geocoding import search_cities
from skycast.services.forecast import get_forecast

app = create_app()
with app.app_context():
    city = search_cities("Delhi")[0]
    print(f"{city.name}, {city.country} ({city.latitude}, {city.longitude})")

    weather = get_forecast(city.latitude, city.longitude)
    print("Now:", weather.current.temperature, "°C, humidity", weather.current.humidity, "%")
    print("Next hour:", weather.hourly[0].temperature, "°C")
    print("Tomorrow max/min:", weather.daily[1].temp_max, "/", weather.daily[1].temp_min)