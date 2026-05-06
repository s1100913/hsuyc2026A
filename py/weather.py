import json

with open('weather.json', 'r', encoding='utf-8') as file:
    JsonData = json.load(file)

City = input("請輸入縣市: ")
City = City.replace("台","臺")

location_data = JsonData["records"]["location"][0]
Weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
Rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

print(f"{City}的天氣是：{Weather}，降雨機率：{Rain}%")
