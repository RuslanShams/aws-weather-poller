import requests
import datetime
import json


class GetWeather:
    """
    During initialization, it takes 2 arguments:
    the name of the city and the access key to the openweathermap.org web service
    (c2dc29317d9f95df16834f3d8e0fc3a0 by default).
    Then use the get_weather method to fills a weather dictionary and return it.
    Optionally, you can use the weather_to_json method to write to a JSON file.
    """

    def __init__(self, s_city, appid='c2dc29317d9f95df16834f3d8e0fc3a0'):
        self.s_city = s_city
        self.appid = appid
        self.weather_res = {}
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
            data = res.json()
            self.city_id = data['list'][0]['id']
        except Exception as er:
            print("Exception (find):", er)

    def get_weather(self):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': self.city_id, 'units': 'metric', 'lang': 'ru', 'APPID': self.appid})
            data = res.json()
            current_datetime = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            self.weather_res = {"city": self.s_city, "time": current_datetime,
                                "conditions": data['weather'][0]['description'], "temp": data['main']['temp'],
                                "temp_min": data['main']['temp_min'], "temp_max": data['main']['temp_max']}
            return self.weather_res
        except Exception as er:
            print("Exception (weather):", er)

    def weather_to_json(self):
        try:
            with open("weather.json", "a+") as outfile:
                json.dump(self.weather_res, outfile, indent=2)
        except Exception as er:
            print("Exception (weather):", er)
