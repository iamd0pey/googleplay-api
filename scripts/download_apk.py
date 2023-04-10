import os
import sys
import json
from gpapi.googleplay import GooglePlayAPI

APKS_DIR = "/apks"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""

    # PyInstaller creates a temp folder and stores path in _MEIPASS
    # Tries temp folder first, if failed uses original path returned as absolute path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)


def apks_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, APKS_DIR,relative_path)



input("Press Enter To Start")

with open(resource_path("/config/login.json")) as logins:
    device_log_ins = json.load(logins)
    current_log_in = device_log_ins['test_device'] # Change this to change device

#server = GooglePlayAPI("en_US", "America/Toronto", current_log_in['deviceName'])
server = GooglePlayAPI("en_US", "Europe/Portugal", current_log_in['deviceName'])


print("Logging in...")
server.login(
    email=current_log_in['username'],
    password=current_log_in['password'],
)
print("Complete!")
docid = sys.argv[1]

print('\nDownloading apk\n')
download = server.download(docid, expansion_files=True)
print(apks_path(download['docId'] + '.apk'))
with open(apks_path(download['docId'] + '.apk'), 'wb') as first:
    for chunk in download.get('file').get('data'):
        first.write(chunk)

print('\nDownloading additional files\n')
for obb in download['additionalData']:
    name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
    print(apks_path(name))
    with open(apks_path(name), 'wb') as second:
        for chunk in obb.get('file').get('data'):
            second.write(chunk)

print('\nDownload successful\n')
