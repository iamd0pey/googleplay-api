import os
import sys
import json
from gpapi.googleplay import GooglePlayAPI

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""

    # PyInstaller creates a temp folder and stores path in _MEIPASS
    # Tries temp folder first, if failed uses original path returned as absolute path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

input("Press Enter To Start")

with open(resource_path("login.json")) as logins:
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

print("\nBrowse play store categories\n")
browse = server.browse()
for c in browse["category"]:
    nameCat = c["name"]
    data_url = c["dataUrl"]
    if "homeV2" not in data_url: #Only look at applications that have a valid category
        continue
    sampleCat = data_url[11:].split("&")[0]
    #print("\nBrowsing the {} category that has the parameter {}\n".format(nameCat, sampleCat))
    browseCat = server.home(cat=sampleCat) #Browse Applications for that category
    for child in browseCat:
        for cluster in child.get('child'):
            print(cluster.get("title"))
            for app in cluster.get('child'):
                print("Title: {} - Package: {} - Category: {}".format(app.get('title'), app.get('docid'), nameCat))



'''

'''
'''
# Replace these with your package and version code names
docid = "com.package.name"
versionCode = 1234

details = server.details(docid, versionCode)
title = details['title'].replace("\n", "-")

print(f"""App Details Below:

Name: {title}
Package: {details['docid']}
Version Code: {details['details']['appDetails']['versionCode']}
App Version: {details['details']['appDetails']['versionString']}
""")

print("Attempting to download {}".format(docid))
fl = server.download(docid, versionCode=versionCode)
with open(f"{docid}.apk", "wb") as apk_file:
    parts = int(fl['file']['total_size']) / fl['file']['chunk_size']
    for index, chunk in enumerate(fl.get("file").get("data")):
        apk_file.write(chunk)
        print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
    print("")
    print("Download successful")

print("Attempting to download {} splits".format(docid))
splits = fl.get('splits')
if splits:
    for split in splits:
        split_path = f"{docid}_{split['name']}.apk"
        with open(split_path, 'wb') as f:
            parts = int(split['file']['total_size']) / split['file']['chunk_size']
            for index, chunk in enumerate(split.get('file').get('data')):
                print(f"Downloading: {round((index/parts)*100)}% complete...", end="\r")
                f.write(chunk)
            print("")
    print("Download successful")
'''