from dotenv import load_dotenv
import os
import requests
import redis
from redis.commands.json.path import Path
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Load environment variables
load_dotenv()

class APIClient:
    """ Fetches data from a specified API URL. """
    def __init__(self, api_url):
        self.api_url = api_url
    
    def fetch_data(self):
        response = requests.get(self.api_url)
        return response.json()

class RedisHandler:
    """ Manages Redis operations. """
    def __init__(self, host, port, password=''):
        self.db = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def insert_json(self, key, json_data):
        self.db.json().set(key, Path.root_path(), json_data)

    def fetch_json(self, key):
        return self.db.json().get(key)

class DataProcessor:
    """ Processes data for visualization and analysis. """
    def __init__(self, data):
        self.data = data

    def _parse_years(self, term):
        """ Parses start and end years from a presidential term string. """
        current_year = datetime.datetime.now().year
        if 'present' in term:
            start_year = int(term.split('-')[0])
            return start_year, current_year
        else:
            years = term.split('-')
            start_year = int(years[0])
            end_year = int(years[1]) if len(years) > 1 else start_year
            return start_year, end_year

    def plot_chart(self):
        """ Generates a histogram of the years in office for each president. """
        years_in_office = []
        for item in self.data:
            start_year, end_year = self._parse_years(item['yearsInOffice'])
            if start_year and end_year:
                years_in_office.append(end_year - start_year)
        plt.hist(years_in_office, bins=np.arange(min(years_in_office), max(years_in_office) + 1, 1), alpha=0.7, color='blue')
        plt.title('Distribution of Years in Office')
        plt.xlabel('Years in Office')
        plt.ylabel('Number of Presidents')
        plt.show()

    def aggregate_data(self):
        """ Calculates the average years in office for all presidents. """
        years = []
        for item in self.data:
            start_year, end_year = self._parse_years(item['yearsInOffice'])
            if start_year and end_year:
                years.append(end_year - start_year)
        average_years = sum(years) / len(years) if years else 0
        return average_years

    def search_data(self, query):
        """ Searches for presidents by name. """
        return [item for item in self.data if query.lower() in item['name'].lower()]

# Usage
if __name__ == "__main__":
    api_client = APIClient("https://api.sampleapis.com/presidents/presidents")
    json_data = api_client.fetch_data()
    
    redis_host = os.getenv('REDIS_HOST')
    redis_port = int(os.getenv('REDIS_PORT'))
    redis_password = os.getenv('REDIS_PASSWORD')

    redis_handler = RedisHandler(host=redis_host, port=redis_port, password=redis_password)
    redis_handler.insert_json('presidents_data', json_data)

    fetched_data = redis_handler.fetch_json('presidents_data')

    data_processor = DataProcessor(fetched_data)
    data_processor.plot_chart()
    print(f"Average years in office: {data_processor.aggregate_data():.2f}")
    search_results = data_processor.search_data('Roosevelt')
    print(f"Search results for 'Roosevelt': {search_results}")
