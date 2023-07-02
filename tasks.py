import json
import logging
import concurrent.futures
from external.client import YandexWeatherAPI
from utils import CITIES


PRECIPITATIOM = [
    'drizzle', 'light-rain', 'rain', 'moderate-rain',
    'heavy-rain', 'continuous-heavy-rain', 'showers',
    'wet-snow', 'light-snow', 'snow' 'snow-showers', 'hail',
    'thunderstorm' 'thunderstorm-with-rain', 'thunderstorm-with-hail'
]


NOT_PRECIPITATIOM = [

]


class DataFetchingTask:
    def get_wather() -> dict:
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
    def view_precipitation(wathers_days: dict) -> int:
        days = wathers_days["forecasts"]
        result_precipitation = []
        error_date = []
        for day in days:
            hours = day['hours']
            for hour in hours:
                if 9.0 <= float(hour['hour']) <= 19.0:
                    condition = hour['condition']
                    if condition not in PRECIPITATIOM:
                        result_precipitation.append(condition)
                    error_date.append(condition)
        return len(result_precipitation)

    def get_averge_temp(cities_data: dict) -> float:
        result_temp = []
        days = cities_data["forecasts"]

        for day in days:
            hours = day['hours']

            for hour in hours:
                if 9.0 <= float(hour['hour']) <= 19.0:
                    temp = hour['temp']
                    result_temp.append(temp)

        return round(sum(result_temp) / len(result_temp), 2)

    def get_days(cities_data: dict) -> dict:
        result_days = []
        days = cities_data["forecasts"]
        for day in days:
            result_days.append(day['date'])
        return result_days


class DataAggregationTask:
    def aggregate_stats(temp: dict, precipitation: dict, days: dict) -> dict:
        result = {}
        for city in temp.keys():
            result[city] = {
                'avg_temp': temp.get(city),
                'hour_not_precipitation': precipitation.get(city),
                'days': days.get(city),
            }

        return result


class DataAnalyzingTask:
    def analyzing_wather(aggregare_data: dict) -> dict:
        result_avg_temp = {}
        for city, data, in aggregare_data.items():
            avg_temp = data['avg_temp']
            result_avg_temp[city] = avg_temp
        favorite_city = [(value, key)
                         for key, value in result_avg_temp.items()]
        result = max(favorite_city)

        return {'лучшие погодные условия в городе': result}

    def save_result_json(aggragate_data, favorite_city):
        with open('result.json', 'w') as fp:
            json.dump(aggragate_data, fp, indent=4)
            json.dump(favorite_city, fp, indent=4)


def main() -> None:
    # Одно замечание было без сообщения
    # можете запустить код и посмотреть, правильно ли сделано?
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
            process_3 = pool.submit(DataCalculationTask.get_days, api_data)

            result_process_1[city] = process_1
            result_process_2[city] = process_2
            result_process_3[city] = process_3

        for city, future in result_process_1.items():
            try:
                result_1[city] = future.result()
            except KeyError:
                pass

        for city, future in result_process_2.items():
            try:
                result_2[city] = future.result()
            except KeyError:
                pass
        for city, future in result_process_3.items():
            try:
                result_3[city] = future.result()
            except KeyError:
                pass

    data_aggragate = DataAggregationTask.aggregate_stats(
        result_1, result_2, result_3)
    favorite_city = DataAnalyzingTask.analyzing_wather(data_aggragate)
    DataAnalyzingTask.save_result_json(data_aggragate, favorite_city)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(filename=__file__ + '.log',)])
    main()
