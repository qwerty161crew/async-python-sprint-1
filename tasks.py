from dataclasses import dataclass
import threading
import multiprocessing
import concurrent.futures
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name, CITIES

PRECIPITATIOM = [
    'drizzle', 'light-rain', 'rain', 'moderate-rain', 'heavy-rain', 'continuous-heavy-rain', 'showers',
    'wet-snow', 'light-snow', 'snow' 'snow-showers', 'hail', 'thunderstorm' 'thunderstorm-with-rain', 'thunderstorm-with-hail'
]


NOT_PRECIPITATIOM = [

]


class DataFetchingTask:
    def __init__(self, futures, result) -> None:
        self.futures = futures
        self.result = result

    def get_wather():
        futures = {}
        result = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:

            for city, url in CITIES.items():

                future = executor.submit(YandexWeatherAPI.get_forecasting, url)
                futures[city] = future
            for city, future in futures.items():
                try:
                    result[city] = future.result()
                except Exception:
                    pass
        return result


class DataCalculationTask:
    def __init__(self, result_precipitation, result_temp) -> None:
        self.result_precipitation = result_precipitation
        self.result_temp = result_temp

    def view_precipitation(wathers_days):
        days = wathers_days["forecasts"]
        result_precipitation = []
        error_date = []
        for day in days:
            hours = day['hours']
            for hour in hours:
                if float(hour['hour']) >= 9.0 and float(hour['hour']) <= 19.0:
                    condition = hour['condition']
                    if condition not in PRECIPITATIOM:
                        result_precipitation.append(condition)
                    error_date.append(condition)
        return len(result_precipitation)

    def get_averge_temp(cities_data):
        result_temp = []
        days = cities_data["forecasts"]

        for day in days:
            hours = day['hours']

            for hour in hours:
                if float(hour['hour']) >= 9.0 and float(hour['hour']) <= 19:
                    temp = hour['temp']
                    result_temp.append(temp)

        return round(sum(result_temp) / len(result_temp), 2)

    def favorable_city(cities_data):
        temps = []
        result_condition = []
        dates = []
        days = cities_data["forecasts"]
        result = []

        for day in days:
            hours = day['hours']
            dates.append(day['date'])

            for hour in hours:
                if float(hour['hour']) >= 9.0 and float(hour['hour']) <= 19:
                    temp = hour['temp']
                    condition = hour['condition']
                    temps.append(temp)

                    if condition not in PRECIPITATIOM:
                        result_condition.append(condition)

        result.append(sum(temps))
        result.append(len(result_condition))
        result.append(dates)
        print(result)
        return result


class DataAggregationTask:
    def __init__(self, average_temp, hours_without_precipitation, city, date) -> None:
        self.average_temp = average_temp
        self.hours_without_precipitation = hours_without_precipitation
        self.city = city
        self.date = date

    def aggregate_data(self):
        return 'Город: {CITY}'

class DataAnalyzingTask:
    pass


@dataclass
class DataWather:
    city: str
    wather: dict
    average_temp: float
    view_precipitation: int


def main():
    data = DataFetchingTask.get_wather()
    result_process_1 = {}
    result_process_2 = {}
    result_process_3 = {}
    result_1 = {}
    result_2 = {}
    result_3 = {}

    with concurrent.futures.ProcessPoolExecutor() as pool:
        for city, api_data in data.items():
            process_1 = pool.submit(
                DataCalculationTask.get_averge_temp, api_data)
            process_2 = pool.submit(
                DataCalculationTask.view_precipitation, api_data)
            process_3 = pool.submit(
                DataCalculationTask.favorable_city, api_data)

            result_process_1[city] = process_1
            result_process_2[city] = process_2
            result_process_3[city] = process_3

        for city, future in result_process_1.items():
            try:
                result_1[city] = future.result()
            except Exception:
                pass

        for city, future in result_process_2.items():
            try:
                result_2[city] = future.result()
            except Exception:
                pass
        for city, future in result_process_3.items():
            try:
                result_3[city] = future.result()
            except Exception:
                pass
    # print(result_3)


if __name__ == '__main__':
    main()
