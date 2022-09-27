from gpapi.googleplay import GooglePlayAPI, RequestError

import accounts
import json

def browse():
    login = accounts.random_login()

    if not 'api' in login:
        return {"error": f"Failed login on device {login['account']['device_code_name']} with account for {login['account']['email']}"}

    categories = login['api'].browse()

    with open('../data/categories.json', "w") as file:
        json.dump(categories, file, indent = 4, default=list)

    return {
        'file': '../data/categories.json'
    }

def list_ranks(category_id):
    login = accounts.random_login()

    if not 'api' in login:
        return {"error": f"Failed login on device {login['account']['device_code_name']} with account for {login['account']['email']}"}

    categories = login['api'].list_ranks(category_id, 'TOP_FREE')

    with open('../data/categories-list-ranks.json', "w") as file:
        json.dump(categories, file, indent = 4, default=list)

    return {
        'file': '../data/categories-list-ranks.json'
    }

def list(category_id):
    login = accounts.random_login()

    if not 'api' in login:
        return {"error": f"Failed login on device {login['account']['device_code_name']} with account for {login['account']['email']}"}

    try:
        categories = login['api'].list(category_id)
    except RequestError as e:
        return {'error': e}

    with open('../data/categories-list.json', "w") as file:
        json.dump(categories, file, indent = 4, default=list)

    return {
        'file': '../data/categories-list.json'
    }
