#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, config

import sys
import os
# import argparse
import json
import accounts
from time import sleep
from random import randint


# GPAPI_GSFID = int(os.environ["GPAPI_GSFID"])
# GPAPI_AUTH_TOKEN = os.environ["GPAPI_GSFID"]

GPAPI_GSFID = None
GPAPI_AUTH_TOKEN = None

LOCALE = os.environ["GPAPI_LOCALE"]
TIMEZONE = os.environ["GPAPI_TIMEZONE"]

GOOGLE_EMAIL = os.environ["GOOGLE_EMAIL"]
GOOGLE_APP_PASSWORD = os.environ["GOOGLE_APP_PASSWORD"]

DOWNLOAD_PATH = os.environ["APK_DOWNLOAD_PATH"]

SLEEP_SECONDS_MIN = 1
SLEEP_SECONDS_MAX = 3

DOWNLOAD_APKS_LIMIT = 2

def buildApkFilePath(app_id, filename, extension):
    folder = f"{DOWNLOAD_PATH}/{app_id}"

    os.makedirs(folder, exist_ok = True)

    return f"{folder}/{filename}.{extension}"

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

def downloadAppApk(app_id):
    result = accounts.random_login()

    if 'api' in result:
        downloadApk(result['api'], app_id)
        return True

    return False

def downloadApk(api, app_id):
    api.log(app_id)

    # @TODO try catch gpapi.googleplay.RequestError
    download = api.download(app_id)

    saveApkFrom(download, app_id)

    saveAdditionalFilesFrom(download, app_id)

    saveSplitsFrom(download, app_id)

def dowanloadApksByCategory(category_id):
    filename = f"../data/scrapped/apps/{category_id}.json"

    if not os.path.exists(filename):
        return {'error': f"File not found: {filename}"}

    with open(filename) as file:
        data = json.load(file)

    app_ids = data['apps'].keys()

    total_apps_ids = len(app_ids)

    # print("\napps_ids:", app_ids)
    print("\ntotal_apps_ids:", total_apps_ids)

    apks_downloaded = []

    for index, app_id in enumerate(app_ids):
        if DOWNLOAD_APKS_LIMIT > 0 and index > DOWNLOAD_APKS_LIMIT:
            return {'apks_downloaded': apks_downloaded}

        print(f"\n\n---> Starting Downloading APK for the APP: {app_id} <---")

        downloadAppApk(app_id)

        apks_downloaded.append(app_id)

        # keep a slow pace to avoid being blacklisted.
        sleep(randint(SLEEP_SECONDS_MIN, SLEEP_SECONDS_MAX))


    return {'apks_downloaded': apks_downloaded}


# def main():

#     # cli_args = parseCliArgs()

#     print(f"\n---> Started processing for {cli_args['app_id']} <---\n")

#     api = login()

#     # search(api = api)

#     # try:
#     # /downloadApk(app_id = cli_args["app_id"], api = api)
#     # except Exception as e:
#         # print(e)
#         # exit(1)

#     print(f"\n---> Finished processing for {cli_args['app_id']} <---\n")

# if __name__ == "__main__":
#     # Run the script from the main directory of the project by using this command:
#     # pipenv run python -m scripts.crawl_apps_by_developers
#     main()
