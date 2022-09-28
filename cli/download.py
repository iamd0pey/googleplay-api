#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, config

import sys
import os
# import argparse
import json
import accounts
from time import sleep
from random import randint

# import logging
# log = logging.getLogger()
# log.setLevel(logging.INFO)
# log.addHandler(logging.StreamHandler()) #Exporting logs to the screen


# GPAPI_GSFID = int(os.environ["GPAPI_GSFID"])
# GPAPI_AUTH_TOKEN = os.environ["GPAPI_GSFID"]

GPAPI_GSFID = None
GPAPI_AUTH_TOKEN = None

LOCALE = os.environ["GPAPI_LOCALE"]
TIMEZONE = os.environ["GPAPI_TIMEZONE"]

GOOGLE_EMAIL = os.environ["GOOGLE_EMAIL"]
GOOGLE_APP_PASSWORD = os.environ["GOOGLE_APP_PASSWORD"]

DOWNLOAD_PATH = os.environ["APK_DOWNLOAD_PATH"]

SLEEP_SECONDS_MIN = 5
SLEEP_SECONDS_MAX = 10

DOWNLOAD_APKS_LIMIT = 3
DOWNLOADS_PROGRESS_PATH = '../data'
DOWNLOADS_PROGRESS_FILENAME = 'downloads-progress.json'

def buildApkFilePath(app_id, category_id, filename, extension):
    folder = f"{DOWNLOAD_PATH}/{category_id}/{app_id}"

    os.makedirs(folder, exist_ok = True)

    return f"{folder}/{filename}.{extension}"

def readJsonFile(filename, default = []):
    if not os.path.exists(filename):
        return default

    with open(filename) as file:
        return json.load(file)

def writeToJsonFile(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent = 4) #, default=list)

def saveApkFrom(download, app_id, category_id = 'UNCATEGORIZED'):
    print("\n--> Attempting to download the APK")
    with open(buildApkFilePath(app_id, category_id, "base", "apk"), "wb") as apk_file:
        parts = int(download['file']['total_size']) / download['file']['chunk_size']
        for index, chunk in enumerate(download.get("file").get("data")):
            apk_file.write(chunk)
            print(f"\tDownloading: {round((index/parts)*100)}% complete...", end="\r")

        print("\n\tDownload successful\n")

def saveAdditionalFilesFrom(download, app_id, category_id = 'UNCATEGORIZED'):
    print('\n--> Attempting to download additional files')
    for obb in download['additionalData']:
        # name = DOWNLOAD_PATH + obb['type'] + '.' + str(obb['versionCode']) + '.' + app_id + '.obb'
        filename = obb['type'] + '.' + str(obb['versionCode'])
        filepath = buildApkFilePath(app_id, category_id, filename, 'obb')

        with open(filepath, 'wb') as second:
            parts = int(obb['file']['total_size']) / obb['file']['chunk_size']
            for index, chunk in enumerate(obb.get("file").get("data")):
                print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
                second.write(chunk)

            print("\n\tAdditional Download successful\n")

def saveSplitsFrom(download, app_id, category_id = 'UNCATEGORIZED'):
    print("\n--> Attempting to download splits")
    splits = download.get('splits')
    if splits:
        for split in splits:
            # split_path = DOWNLOAD_PATH + f"{app_id}_{split['name']}.apk"
            filepath = buildApkFilePath(app_id, category_id, split['name'], 'apk')

            with open(filepath, 'wb') as f:
                parts = int(split['file']['total_size']) / split['file']['chunk_size']
                for index, chunk in enumerate(split.get('file').get('data')):
                    print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
                    f.write(chunk)

        print("\n\tSplits Download successful\n")

def downloadApkWithRandomLogin(app_id, category_id = 'UNCATEGORIZED'):
    login = accounts.random_login()
    return _downloadAppApk(app_id, login, category_id)

def downloadApkForDevice(app_id, device_code_name, email):
    login = accounts.login_for_device(device_code_name, email)

    if 'error' in login:
        return {'error': login['error']}

    return _downloadAppApk(app_id, login)

def _downloadAppApk(app_id, login, category_id = 'UNCATEGORIZED'):
    api = login['api']
    email = login['account']['email']
    device_code_name = login['account']['device_code_name']

    metadata = {
        'app_id': app_id,
        'email': email,
        'device_code_name': device_code_name,
        'category_id': category_id,
    }

    download_result = {
        'login_failed': True,
        'download_failed': True,
        'metadata': metadata,
        'already_downloaded_for': {},
    }

    if 'api' in login:
        download_result['login_failed'] = False

        print(f"--> Download APK for {app_id} on device {device_code_name} with account {email}\n")

        # if _downloadApk(login['api'], app_id, category_id):
            # download_result['download_failed'] = False

    # return download_result


# def _downloadApk(api, app_id, category_id = 'UNCATEGORIZED'):

    # print(vars(api))

        try:
            downloaded_file = f"{DOWNLOAD_PATH}/downloaded.json"

            default = {
                'by_device': {},
                'by_email': {},
            }

            downloaded = readJsonFile(downloaded_file, default)

            if device_code_name in downloaded['by_device'] and downloaded['by_device'][device_code_name]['app_id'] == app_id:
                download_result['already_downloaded_for'] = downloaded['by_device'][device_code_name]
                download_result['download_failed'] = True
                return download_result

            download = api.download(app_id)

            saveApkFrom(download, app_id, category_id)

            saveAdditionalFilesFrom(download, app_id, category_id)

            saveSplitsFrom(download, app_id, category_id)

            download_result['download_failed'] = False

            metadata_file = buildApkFilePath(app_id, category_id, "metadata", "json")

            writeToJsonFile(metadata_file, metadata)

            downloaded['by_device'][device_code_name] = metadata
            downloaded['by_email'][email] = metadata

            writeToJsonFile(downloaded_file, downloaded)

        except Exception as e:
            # raise(e)
            print(f"downloadApk() Exception: {e}")

    return download_result
    # return False


def dowanloadApksByCategory(category_id):
    filename = f"../data/scrapped/apps/{category_id}.json"

    if not os.path.exists(filename):
        return {'error': f"File not found: {filename}"}

    with open(filename) as file:
        data = json.load(file)

    app_ids = list(data['apps'].keys())

    # total_apps_ids = len(app_ids)

    # print("\napps_ids:", app_ids)
    # print("\ntotal_apps_ids:", total_apps_ids)


    file_path = f"{DOWNLOADS_PROGRESS_PATH}/{category_id}_{DOWNLOADS_PROGRESS_FILENAME}"

    default = {
        'category_total': 0,
        'total_downloaded': 0,
        'total_remaining': 0,
        'total_download_failures': 0,
        'download_failures': {},
        'downloaded_app_ids': [],
        'remaining_app_ids': [],
    }

    progress = readJsonFile(file_path, default)

    progress['category_total'] = len(app_ids)


    if progress['total_downloaded'] == 0:
        progress['remaining_app_ids'] = app_ids
        progress['total_remaining'] = progress['category_total']

    # print(type(app_ids))
    # print(type(progress['remaining_app_ids']))
    # return

    total_to_download = len(progress['remaining_app_ids'])

    for index, app_id in enumerate(progress['remaining_app_ids']):
        if DOWNLOAD_APKS_LIMIT > 0 and index > DOWNLOAD_APKS_LIMIT:
            return {'progress': progress}

        print(f"\n\n---> Starting Downloading ({index}/{total_to_download}) APK for APP: {app_id} <---")

        result = downloadApkWithRandomLogin(app_id, category_id)

        if result['login_failed'] == True or result['download_failed'] == True:
            progress['download_failures'][app_id] = result
            progress['total_download_failures'] = len(progress['download_failures'])
        else:
            progress['downloaded_app_ids'].append(app_id)

        # Not matter if downloaded succeeded or failed we want to remove the app
        # id  and update the totals accordingly.
        progress['remaining_app_ids'].remove(app_id)
        progress['total_downloaded'] = len(progress['downloaded_app_ids'])
        progress['total_remaining'] = len(progress['remaining_app_ids'])

        # print("\n-> PROGRESS: ", progress)

        writeToJsonFile(file_path, progress)

        # keep a slow pace to avoid being blacklisted.
        sleep(randint(SLEEP_SECONDS_MIN, SLEEP_SECONDS_MAX))


    return {
        'dir': DOWNLOAD_PATH,
        'progress': progress,
    }


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
