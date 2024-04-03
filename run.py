import csv
import datetime
import os
from pathlib import Path

import requests

BASE_PATH = Path(__file__).parent
ECHERHA_WORKLOAD_API = "https://back.echerha.gov.ua/api/v4/workload/1"


def country_by_id(countries):
    return {country["id"]: country["name"] for country in countries}


def normalized_file_name(country, queue_name):
    return f"{country.replace(' ', '_').lower()}_{queue_name.replace(' ', '_').lower()}.csv"


def append_or_create_dataset(queue_data, country):
    normalized_name = normalized_file_name(country, queue_data["title"])
    file_path = BASE_PATH / "datasets" / normalized_name

    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            csv.writer(file).writerow(["checkpoint_time", "wait_time", "vehicles_in_queue"])

    current_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    csv.writer(open(file_path, "a")).writerow([current_datetime, queue_data["wait_time"], queue_data["vehicle_in_active_queues_counts"]])


def process():
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "x-client-locale": "en",
        "x-user-agent": "UABorder/3.2.2 Web/1.1.0 User/guest"
    }
    response = requests.get(ECHERHA_WORKLOAD_API, headers=headers)
    data = response.json()

    countries = country_by_id(data["filters"]["countries"])

    for queue_data in data["data"]:
        country = countries[queue_data["country_id"]]
        append_or_create_dataset(queue_data, country)


if __name__ == "__main__":
    process()
