import threading
import multiprocessing
import concurrent.futures
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name, CITIES


def get_wather():
    futures = []
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        for city, url in CITIES.items():

            future = executor.submit(YandexWeatherAPI.get_forecasting, url)
            futures.append(future)

        for future in futures:
            try:
                result.append(future.result())
            except Exception as error:
                print(error)
    return result


def get_averge_temp(city_data):
    days = city_data["forecasts"]
    result_temp = []

    for day in days:
        view_precipitation(day)
        hours = day['hours']

        for hour in hours:
            if float(hour['hour']) >= 9.0 and float(hour['hour']) <= 19:
                temp = hour['temp']
                result_temp.append(temp)

        return sum(result_temp) / len(result_temp)


def view_precipitation(wathers_days):
    hours = wathers_days['hours']
    result = []

    for hour in hours:
        if float(hour['hour']) >= 9.0 and float(hour['hour']) <= 19:
            precipitation = hour['prec_type']

            if int(precipitation) == 0:
                result.append(hour)

    return len(result)


get_averge_temp(get_wather()[0])
