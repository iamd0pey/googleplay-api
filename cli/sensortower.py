from datetime import date
from pathlib import Path
import json
import requests

CATEGORY_URL = "https://app.sensortower.com/api/android/rankings/get_category_rankings"

# each count in the limit equals to 3 apps
def list_top_free(category, country, limit=200, offset=0):

    today = date.today().isoformat()

    url = f"{CATEGORY_URL}?category={category.lower()}&country={country.upper()}&date={today}T00%3A00%3A00.000Z&device=PHONE&limit={limit}&offset={offset}"

    response = requests.get(url)

    if response.status_code == 200:
        category_dir = f"../data/categories/{country}/{category.lower()}"

        Path(category_dir).mkdir(parents=True, exist_ok=True)

        category_file = f"{category_dir}/{today}-top-free-{limit}.json"

        data = {
            'country': country.upper(),
            'category': category.upper(),
            'count': -1,
            'top_free': [],
            'apps': {}
        }

        # Each row contains 3 apps:
        #  * 0 - top free app
        #  * 1 - top paid app
        #  * 2 - top grossing app
        # for index, row in enumerate(response.json()):
        for row in response.json():
            app = row[0]
            data['top_free'].append(app['app_id'])
            data['apps'][app['app_id']] = app

        data['count'] = len(data['top_free'])

        with open(category_file, "w") as file:
            json.dump(data, file, indent = 4, default=list)

        return {
            'file': category_file
        }

    return {
        'error': f"Failed the request. Status Code: {response.status_code}, URL: {url}"
    }
