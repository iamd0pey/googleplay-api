from gpapi.googleplay import GooglePlayAPI

import accounts
import json

def lookup(term):
    login = accounts.random_login()

    if not 'api' in login:
        return {"error": f"Failed login on device {login['account']['device_code_name']} with account for {login['account']['email']}"}

    api = login['api']

    suggestions = api.searchSuggest(term[0:3])

    result = api.search(term)

    data = {
        'suggestions': suggestions,
        'result': result
    }

    path = '../data/search.json'

    with open(path, "w") as file:
        json.dump(data, file, indent = 4, default=list)

    for doc in result:
        if 'docid' in doc:
            print("doc: {}".format(doc["docid"]))
        for cluster in doc["child"]:
            print("\tcluster: {}".format(cluster["docid"]))
            for app in cluster["child"]:
                print("\t\tapp: {}".format(app["docid"]))

    return {
        'file': path,
    }
