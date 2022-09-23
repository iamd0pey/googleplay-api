#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, RequestError, config

import sys
import os
import argparse
import json
import click

# GPAPI_GSFID = int(os.environ["GPAPI_GSFID"])
# GPAPI_AUTH_TOKEN = os.environ["GPAPI_GSFID"]

GPAPI_GSFID = None
GPAPI_AUTH_TOKEN = None

LOCALE = os.environ["GPAPI_LOCALE"]
TIMEZONE = os.environ["GPAPI_TIMEZONE"]

GOOGLE_EMAIL = os.environ["GOOGLE_EMAIL"]
GOOGLE_APP_PASSWORD = os.environ["GOOGLE_APP_PASSWORD"]

DOWNLOAD_PATH = os.environ["APK_DOWNLOAD_PATH"]

LOGIN_CREDENTIALS_FILE = os.environ["LOGIN_CREDENTIALS_FILE"]
LOGIN_CREDENTIALS_LIST = os.environ["LOGIN_CREDENTIALS_LIST"]


def buildApkFilePath(app_id, filename, extension):
    folder = f"{DOWNLOAD_PATH}/{app_id}"

    os.makedirs(folder, exist_ok = True)

    return f"{folder}/{filename}.{extension}"


def parseCliArgs():
    ap = argparse.ArgumentParser(description='Download apk files')
    ap.add_argument('--app-id', dest='app_id', help='com.example.app', required=True)

    args = ap.parse_args()

    return {"app_id": args.app_id}

def getLoginCredentials():
    if not os.path.exists(LOGIN_CREDENTIALS_FILE):
        return dict()

    with open(LOGIN_CREDENTIALS_FILE) as file:
        return json.load(file)

def saveLoginCredentials():
    data = getLoginCredentials()
    data.update(credentials)

    with open(LOGIN_CREDENTIALS_FILE, "w") as file:
        json.dump(data, file, indent = 4)

def login():
    credentials = getLoginCredentials()
    # print(dir(credentials))
    print("CREDENTIALS")
    print(repr(credentials))
    # print("DEVICE")
    # print(api.deviceBuilder.device['build.hardware'])
    print("CONFIG")
    print(config.getDevicesCodenames())
    exit()

    api = GooglePlayAPI(LOCALE, TIMEZONE, api.deviceBuilder.device['build.hardware'])

    if credentials['gsfid'] and credentials['authSubToken']:
        print("\n--> Attempting to login with the GPAPI_GSFID and GPAPI_GSFID from the .env file\n")
        api.login(None, None, credentials['gsfid'], credentials['authSubToken'])
    elif GOOGLE_APP_PASSWORD:
        print('\n--> Logging in with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD from the .env file\n')
        api.login(GOOGLE_EMAIL, GOOGLE_APP_PASSWORD, None, None)
        print("GPAPI_GSFID: " + str(api.gsfId))
        print("GPAPI_AUTH_TOKEN: " + str(api.authSubToken))

    else:
        print("\n--> You need to login first with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD that you need to set in the .env file.\n")
        exit(1)

# def login(api):
#     if GPAPI_GSFID and GPAPI_AUTH_TOKEN:
#         print("\n--> Attempting to login with the GPAPI_GSFID and GPAPI_GSFID from the .env file\n")
#         api.login(None, None, GPAPI_GSFID, GPAPI_AUTH_TOKEN)
#     elif GOOGLE_APP_PASSWORD:
#         print('\n--> Logging in with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD from the .env file\n')
#         api.login(GOOGLE_EMAIL, GOOGLE_APP_PASSWORD, None, None)
#         print("GPAPI_GSFID: " + str(api.gsfId))
#         print("GPAPI_AUTH_TOKEN: " + str(api.authSubToken))
#     else:
#         print("\n--> You need to login first with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD that you need to set in the .env file.\n")
#         exit(1)

def saveApkFrom(download, app_id):
    print("\n--> Attempting to download the APK")
    with open(buildApkFilePath(app_id, "base", "apk"), "wb") as apk_file:
        parts = int(download['file']['total_size']) / download['file']['chunk_size']
        for index, chunk in enumerate(download.get("file").get("data")):
            apk_file.write(chunk)
            print(f"\tDownloading: {round((index/parts)*100)}% complete...", end="\r")

        print("\n\tDownload successful\n")

def saveAdditionalFilesFrom(download, app_id):
    print('\n--> Attempting to download additional files')
    for obb in download['additionalData']:
        # name = DOWNLOAD_PATH + obb['type'] + '.' + str(obb['versionCode']) + '.' + app_id + '.obb'
        filename = obb['type'] + '.' + str(obb['versionCode'])
        filepath = buildApkFilePath(app_id, filename, 'obb')

        with open(filepath, 'wb') as second:
            parts = int(obb['file']['total_size']) / obb['file']['chunk_size']
            for index, chunk in enumerate(obb.get("file").get("data")):
                print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
                second.write(chunk)

            print("\n\tAdditional Download successful\n")

def saveSplitsFrom(download, app_id):
    print("\n--> Attempting to download splits")
    splits = download.get('splits')
    if splits:
        for split in splits:
            # split_path = DOWNLOAD_PATH + f"{app_id}_{split['name']}.apk"
            filepath = buildApkFilePath(app_id, split['name'], 'apk')

            with open(filepath, 'wb') as f:
                parts = int(split['file']['total_size']) / split['file']['chunk_size']
                for index, chunk in enumerate(split.get('file').get('data')):
                    print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
                    f.write(chunk)

        print("\n\tSplits Download successful\n")

def downloadApk(api, app_id):
    api.log(app_id)

    download = api.download(app_id)

    saveApkFrom(download, app_id)

    saveAdditionalFilesFrom(download, app_id)

    saveSplitsFrom(download, app_id)

def search(api):
    print("\nSearch suggestion for \"fir\"\n")
    print(api.searchSuggest("fir"))

    result = api.search("firefox")
    for doc in result:
        if 'docid' in doc:
            print("doc: {}".format(doc["docid"]))
        for cluster in doc["child"]:
            print("\tcluster: {}".format(cluster["docid"]))
            for app in cluster["child"]:
                print("\t\tapp: {}".format(app["docid"]))

def main():

    cli_args = parseCliArgs()

    print(f"\n---> Started processing for {cli_args['app_id']} <---\n")

    api = login()

    # search(api = api)

    # try:
    # /downloadApk(app_id = cli_args["app_id"], api = api)
    # except Exception as e:
        # print(e)
        # exit(1)

    print(f"\n---> Finished processing for {cli_args['app_id']} <---\n")

if __name__ == "__main__":
    # Run the script from the main directory of the project by using this command:
    # pipenv run python -m scripts.crawl_apps_by_developers
    main()
