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
                    if condition is not PRECIPITATIOM:
                        result_precipitation.append(condition)

                    error_date.append(condition)
        print(len(result_precipitation))
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


class DataAggregationTask:
    def __init__(self, average_temp, hours_without_precipitation, wather, city, date) -> None:
        self.average_temp = average_temp
        self.hours_without_precipitation = hours_without_precipitation
        self.wather = wather
        self.city = city
        self.date = date

    def combining_data(self):
        self.wather = DataFetchingTask.get_wather()
        self.average_temp = DataCalculationTask.get_averge_temp(self.wather)
        self.hours_without_precipitation = DataCalculationTask.view_precipitation(
            self.wather)

    def __str__(self):
        return f'Средняя температура за период с 9 до 19 {self.average_temp}. Время без осадков составило: {self.hours_without_precipitation}'


class DataAnalyzingTask:
    pass


# DataCalculationTask.get_averge_temp(DataFetchingTask.get_wather()['MOSCOW'])


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
    result_1 = {}
    result_2 = {}

    with concurrent.futures.ProcessPoolExecutor() as pool:
        for city, api_data in data.items():
            process_1 = pool.submit(
                DataCalculationTask.get_averge_temp, api_data)
            process_2 = pool.submit(
                DataCalculationTask.view_precipitation, api_data)

            result_process_1[city] = process_1
            result_process_2[city] = process_2

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

    print(result_2)


if __name__ == '__main__':
    main()
