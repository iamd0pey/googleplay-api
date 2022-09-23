#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, config

import sys
import os
# import argparse
import json
import random

# GPAPI_GSFID = int(os.environ["GPAPI_GSFID"])
# GPAPI_AUTH_TOKEN = os.environ["GPAPI_GSFID"]

GPAPI_GSFID = None
GPAPI_AUTH_TOKEN = None

LOCALE = os.environ["GPAPI_LOCALE"]
TIMEZONE = os.environ["GPAPI_TIMEZONE"]

GOOGLE_EMAIL = os.environ["GOOGLE_EMAIL"]
GOOGLE_APP_PASSWORD = os.environ["GOOGLE_APP_PASSWORD"]

DOWNLOAD_PATH = os.environ["APK_DOWNLOAD_PATH"]

GOOGLE_ACCOUNTS_FILE = os.environ["GOOGLE_ACCOUNTS_FILE"]
# LOGIN_CREDENTIALS_LIST = os.environ["LOGIN_CREDENTIALS_LIST"]

def getAccounts():
    if not os.path.exists(GOOGLE_ACCOUNTS_FILE):
        return dict()

    with open(GOOGLE_ACCOUNTS_FILE) as file:
        return json.load(file)

def save(account, validate_login=True):
    if account['device_code_name'] is None:
        account['device_code_name'] = random.choice(config.getDevicesCodenames())

    email = account['email']
    device_code_name = account['device_code_name']

    print(f"Creating an account for device_code_name: {device_code_name}")

    if validate_login and not login(account):
        return False

    accounts = getAccounts()

    if not 'by_device' in accounts:
        accounts['by_device'] = {}

    if not device_code_name in accounts['by_device']:
        accounts['by_device'][device_code_name] = {'accounts': {}}

    accounts['by_device'][device_code_name]['accounts'][email] = account

    if not 'by_email' in accounts:
        accounts['by_email'] = {}

    if not email in accounts['by_email']:
        accounts['by_email'][email] = {'devices': {}}

    accounts['by_email'][email]['devices'][device_code_name] = account

    print("SAVE ACCOUNT")
    print(account)

    with open(GOOGLE_ACCOUNTS_FILE, "w") as file:
        json.dump(accounts, file, indent = 4)

    return True


def getAccountsForDevice(device_code_name):
    accounts = getAccounts()

    if device_code_name in accounts['by_device']:
        return accounts['by_device'][device_code_name]['accounts']

    return None


def random_login_for_device(device_code_name):
    accounts = getAccountsForDevice(device_code_name)
    print(accounts)
    print(accounts.keys())

    if accounts is None:
        print(f"\nAccount not found for device code name: {device_code_name}")
        return False

    email = random.choice(list(accounts.keys()))
    return login(accounts[email])


def login(account):
    print("\nLOGIN ACCOUNT:")
    print(account)
    api = GooglePlayAPI(account['locale'], account['timezone'], account['device_code_name'])

    if account['gsfid'] and account['authSubToken']:
        print("\n--> Attempting to login with the GPAPI_GSFID and GPAPI_GSFID from the .env file\n")
        api.login(None, None, account['gsfid'][0], account['authSubToken'])
    elif account['password']:
        print('\n--> Logging in with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD from the .env file\n')
        api.login(account['email'], account['password'], None, None)
        print("GPAPI_GSFID: " + str(api.gsfId))
        print("GPAPI_AUTH_TOKEN: " + str(api.authSubToken))
        account['gsfid'] = int(api.gsfId),
        account['authSubToken'] = api.authSubToken
        save(account, False)

    else:
        print("\n--> You need to login first with GOOGLE_EMAIL and GOOGLE_APP_PASSWORD that you need to set in the .env file.\n")
        exit(1)

    return api

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
