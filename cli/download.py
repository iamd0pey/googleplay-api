#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, config

import sys
import os
# import argparse
import json
import accounts
from time import sleep
import random

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

# DOWNLOAD_PATH = os.environ["APK_DOWNLOAD_PATH"]
DOWNLOAD_PATH = '../data/apks'

SLEEP_SECONDS_MIN = 600
SLEEP_SECONDS_MAX = 900

DOWNLOAD_APKS_LIMIT = -1
DOWNLOADS_PROGRESS_FILENAME = 'downloads-progress.json'
DOWNLOADS_PROGRESS_DIFF_FILENAME = 'downloads-progress-diff.json'

DOWNLOADED_FILE = f"{DOWNLOAD_PATH}/downloaded.json"
DOWNLOADED_FILE_DEFAULT_KEYS =  {
    'by_device': {},
    'by_email': {},
}

DEVICES = {
    'GB': [
        'op_5t',
        'op_8_pro',
    ],
    'US': [
        'op_7t',
        'rm_note_5',
    ],
}

def randomSleep():
    # keep a slow pace to avoid being blacklisted.
    seconds = random.randint(SLEEP_SECONDS_MIN, SLEEP_SECONDS_MAX)

    while seconds > 0:
        print(f"\tSleeping for {seconds} seconds...", end="\r")
        sleep(1)
        seconds -= 1

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

def downloadApkForDevice(app_id, device_code_name, email, category_id = 'UNCATEGORIZED'):
    login = accounts.login_for_device(device_code_name, email)

    # if 'error' in login:
    #     return {'error': login['error']}

    return _downloadAppApk(app_id, login, category_id)

def downloadApkForCountryDevice(app_id, country_code, email, category_id = 'UNCATEGORIZED'):

    device_code_name = random.choice(DEVICES[country_code.upper()])

    login = accounts.login_for_device(device_code_name, email)

    if 'error' in login:
        raise login['error']

    return _downloadAppApk(app_id, login, category_id)

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
        'exception': None,
        'metadata': metadata,
        'already_downloaded_for': {},
    }

    if 'api' in login:
        download_result['login_failed'] = False

        print(f"--> Download APK for {app_id} on device {device_code_name} with account {email} for category {category_id}\n")

        try:
            downloaded = readJsonFile(DOWNLOADED_FILE, DOWNLOADED_FILE_DEFAULT_KEYS)

            # if device_code_name in downloaded['by_device'] and app_id in downloaded['by_device'][device_code_name]:
            #     download_result['already_downloaded_for'] = downloaded['by_device'][device_code_name][app_id]
            #     download_result['download_failed'] = True
            #     return download_result

            download = api.download(app_id)

            saveApkFrom(download, app_id, category_id)

            saveAdditionalFilesFrom(download, app_id, category_id)

            saveSplitsFrom(download, app_id, category_id)

            download_result['download_failed'] = False

            metadata_file = buildApkFilePath(app_id, category_id, "metadata", "json")

            writeToJsonFile(metadata_file, metadata)

            if not device_code_name in downloaded['by_device']:
                downloaded['by_device'][device_code_name] = {}

            if not app_id in downloaded['by_device'][device_code_name]:
                downloaded['by_device'][device_code_name][app_id] = {}

            downloaded['by_device'][device_code_name][app_id] = metadata

            if not email in downloaded['by_email']:
                downloaded['by_email'][email] = {}

            if not app_id in downloaded['by_email'][email]:
                downloaded['by_email'][email][app_id] = {}

            downloaded['by_email'][email][app_id] = metadata

            writeToJsonFile(DOWNLOADED_FILE, downloaded)

        except Exception as e:
            # raise(e)
            message = f"downloadApk() Exception: {e}"
            print(message)
            download_result['exception'] = message

    return download_result


def dowanloadApksByCategory(category_id):
    filename = f"../data/scrapped/apps/{category_id}.json"

    if not os.path.exists(filename):
        return {'error': f"File not found: {filename}"}

    with open(filename) as file:
        data = json.load(file)

    default = {
        'category_id': category_id,
        'category_total': 0,
        'total_downloaded': 0,
        'total_remaining': 0,
        'total_download_failures': 0,
        'excluded': {
            'paid_apps': [],
            'outdated_apps': [],
            'less_then_1000_installs': [],
        },
        'download_failures': {},
        'downloaded_app_ids': [],
        'remaining_app_ids': [],
    }

    file_path = f"{DOWNLOAD_PATH}/{category_id}/{DOWNLOADS_PROGRESS_FILENAME}"

    progress = readJsonFile(file_path, default)

    app_ids = []

    progress['category_id'] = category_id
    progress['excluded']['paid_apps'] = []
    progress['excluded']['outdated_apps'] = []
    progress['excluded']['less_then_1000_installs'] = []

    apps = data['apps'].items()

    for app_id, app in apps:
        if not app['free'] or app['price'] > 0:
            progress['excluded']['paid_apps'].append(app_id)

            if app_id in progress['remaining_app_ids']:
                progress['remaining_app_ids'].remove(app_id)

            if app_id in progress['download_failures']:
                progress['download_failures'].pop(app_id)

            continue

        # 1577836800 => 1 January 2020 00:00:00 GMT+00:00
        if app['updated'] < 1577836800:
            progress['excluded']['outdated_apps'].append(app_id)

            if app_id in progress['remaining_app_ids']:
                progress['remaining_app_ids'].remove(app_id)

            if app_id in progress['download_failures']:
                progress['download_failures'].pop(app_id)

            continue

        if app['realInstalls'] < 1000:
            progress['excluded']['less_then_1000_installs'].append(app_id)

            if app_id in progress['remaining_app_ids']:
                progress['remaining_app_ids'].remove(app_id)

            if app_id in progress['download_failures']:
                progress['download_failures'].pop(app_id)

            continue

        app_ids.append(app_id)

    progress['category_total'] = len(app_ids)


    if progress['total_downloaded'] == 0:
        progress['remaining_app_ids'] = app_ids
        progress['total_remaining'] = progress['category_total']

    total_to_download = len(progress['remaining_app_ids'])

    remaining_app_ids = enumerate(progress['remaining_app_ids'])

    for index, app_id in remaining_app_ids:
        if DOWNLOAD_APKS_LIMIT > 0 and index > DOWNLOAD_APKS_LIMIT:
            return {'progress': progress}

        print(f"\n\n---> Starting Downloading ({index}/{total_to_download}) APK for {app_id} on category {category_id} <---")

        result = downloadApkWithRandomLogin(app_id, category_id)

        if result['login_failed'] == True or result['download_failed'] == True:
            progress['download_failures'][app_id] = result
            progress['total_download_failures'] = len(progress['download_failures'])
        else:
            progress['downloaded_app_ids'].append(app_id)

        # No matter if downloaded succeeded or failed we want to remove the app
        # id  and update the totals accordingly.
        progress['remaining_app_ids'].remove(app_id)
        progress['total_downloaded'] = len(progress['downloaded_app_ids'])
        progress['total_remaining'] = len(progress['remaining_app_ids'])

        # print("\n-> PROGRESS: ", progress)

        writeToJsonFile(file_path, progress)

        # keep a slow pace to avoid being blacklisted.
        randomSleep()

    return {
        'dir': DOWNLOAD_PATH,
        'progress': progress,
    }


def fixDownloadedApksByCategory(category_id):
    default = {
        'category_id': category_id,
        'category_total': 0,
        'total_downloaded': 0,
        'total_remaining': 0,
        'total_download_failures': 0,
        'download_failures': {},
        'downloaded_app_ids': [],
        'remaining_app_ids': [],
    }

    progress_file_path = f"{DOWNLOAD_PATH}/{category_id}/{DOWNLOADS_PROGRESS_FILENAME}"
    fixed_progress_file_path = f"{DOWNLOAD_PATH}/{category_id}/fixed-{DOWNLOADS_PROGRESS_FILENAME}"

    downloaded = readJsonFile(DOWNLOADED_FILE, DOWNLOADED_FILE_DEFAULT_KEYS)

    progress = readJsonFile(progress_file_path, default)
    fixed_app_ids = readJsonFile(fixed_progress_file_path, default)

    fix_app_ids = []

    progress['category_id'] = category_id

    for app_id in progress['downloaded_app_ids']:
        apks_path = f"{DOWNLOAD_PATH}/{category_id}/{app_id}"
        print('apks_path: ', apks_path)

        files = os.listdir(apks_path)

        if 'base.apk' not in files:
            print('files: ', files)
            fix_app_ids.append(app_id)

    fixed_app_ids['category_total'] = progress['category_total']
    fixed_app_ids['remaining_app_ids'] = fix_app_ids

    total_to_download = len(fix_app_ids)

    remaining_app_ids = enumerate(fixed_app_ids['remaining_app_ids'])

    for index, app_id in remaining_app_ids:
        if DOWNLOAD_APKS_LIMIT > 0 and index > DOWNLOAD_APKS_LIMIT:
            return {'progress': fixed_app_ids}

        print(f"\n\n---> Starting fixing APK Download ({index}/{total_to_download}) for {app_id} on category {category_id} <---")

        app = {}

        device_apps = downloaded['by_device'].items()

        # When exists, we need to get the device account used for the download,
        # otherwise we risk not being able to download the apk due to account or
        # device restrictions and/or incompatibilities.
        for device_id, apps in device_apps:
            for package_name, app_data in apps.items():
                if package_name == app_id and app_data['category_id'] == category_id:
                    device_accounts = accounts.getAccountsForDevice(app_data['device_code_name'])
                    print('device_id: ', device_id)
                    print('app_data: ', app_data)

                    if device_accounts is None:
                        device_account = accounts.getRandomAccount()
                        print('device_account1: ', device_account)
                    else:
                        email = random.choice(list(device_accounts))
                        device_account =  device_accounts[email]
                        print('device_account2: ', device_account)

                    break

        result = downloadApkForDevice(app_id, device_account['device_code_name'], device_account['email'], category_id)

        if result['login_failed'] == True or result['download_failed'] == True:
            fixed_app_ids['download_failures'][app_id] = result
            fixed_app_ids['total_download_failures'] = len(fixed_app_ids['download_failures'])
        else:
            fixed_app_ids['downloaded_app_ids'].append(app_id)

        # No matter if downloaded succeeded or failed we want to remove the app
        # id  and update the totals accordingly.
        fixed_app_ids['remaining_app_ids'].remove(app_id)
        fixed_app_ids['total_downloaded'] = len(fixed_app_ids['downloaded_app_ids'])
        fixed_app_ids['total_remaining'] = len(fixed_app_ids['remaining_app_ids'])

        writeToJsonFile(fixed_progress_file_path, fixed_app_ids)

        # keep a slow pace to avoid being blacklisted.
        randomSleep()

    return {
        'dir': DOWNLOAD_PATH,
        'progress': fixed_app_ids,
    }

def downloadApksFromDiff(diff_file, email):

    diff = readJsonFile(diff_file, {})

    # print(diff)

    country_code = diff['country'].upper()
    category_id = diff['category'].upper()
    date = diff['date']

    # progress_file = f"{DOWNLOAD_PATH}/{category_id}/{DOWNLOADS_PROGRESS_FILENAME}"
    progress_diff_file = f"{DOWNLOAD_PATH}/{category_id}/{country_code}-{date}-{DOWNLOADS_PROGRESS_DIFF_FILENAME}"

    default = {
        'country': country_code,
        'category_id': category_id,
        'date': date,
        'category_total': 0,
        'total_downloaded': 0,
        'total_remaining': 0,
        'total_download_failures': 0,
        'excluded': {
            'paid_apps': [],
            'outdated_apps': [],
            'less_then_1000_installs': [],
        },
        'download_failures': {},
        'downloaded_app_ids': [],
        'remaining_app_ids': diff['in_download_failures'] + diff['to_download'],
    }

    progress = readJsonFile(progress_diff_file, default)

    # progress['remaining_app_ids'] = diff['to_download']
    print("\n---> Starting to download apks in the diff for remaining downloads")

    for app_id in  progress['remaining_app_ids'][:]:

        result = downloadApkForCountryDevice(app_id, country_code, email, category_id)

        if result['login_failed'] == True or result['download_failed'] == True:
            progress['download_failures'][app_id] = result
            progress['total_download_failures'] = len(progress['download_failures'])
        else:
            progress['downloaded_app_ids'].append(app_id)

        # No matter if downloaded succeeded or failed we want to remove the app
        # id  and update the totals accordingly.
        progress['remaining_app_ids'].remove(app_id)
        progress['total_downloaded'] = len(progress['downloaded_app_ids'])
        progress['total_remaining'] = len(progress['remaining_app_ids'])

        # print("\n-> PROGRESS: ", progress)

        writeToJsonFile(progress_diff_file, progress)

        # keep a slow pace to avoid being blacklisted.
        randomSleep()


    return {
        'dir': DOWNLOAD_PATH,
        'progress': progress,
    }
