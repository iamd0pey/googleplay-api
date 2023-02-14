import os
import sys
import json
from gpapi.googleplay import GooglePlayAPI

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

with open(resource_path("login.json")) as logins:
    device_log_ins = json.load(logins)
    current_log_in = device_log_ins['test_device'] # Change this to change device


#server = GooglePlayAPI("en_US", "America/Toronto", current_log_in['deviceName'])
server = GooglePlayAPI("en_US", "Europe/Portugal", current_log_in['deviceName'])
server.login(
    email=current_log_in['username'],
    password=current_log_in['password'],
)

f = open("applications.txt", "w+")
applications = []
count_apps = 0

print("\nBrowse play store categories\n")
browse = server.browse()
for c in browse["category"]:

    nameCat = c["name"]
    data_url = c["dataUrl"]

    if "homeV2" not in data_url: #Only look at applications that have a valid category
        continue

    sampleCat = data_url[11:].split("&")[0]
    browseCat = server.home(cat=sampleCat) #Browse Applications for that category

    for child in browseCat:
        for cluster in child.get('child'):
            for app in cluster.get('child'):
                app_entry = {}
                app_entry['Title'] = app.get('title')
                app_entry['Category'] = nameCat
                app_entry['PackageName'] = app.get("details").get("appDetails").get("packageName")
                app_entry['NumDownloads'] = app.get("details").get("appDetails").get("numDownloads")
                app_entry['VersionCode'] = app.get("details").get("appDetails").get("versionCode")
                app_entry['VersionString'] = app.get("details").get("appDetails").get("versionString")
                app_entry['UploadDate'] = app.get("details").get("appDetails").get("uploadDate")
                app_entry['Cluster'] = cluster.get("title")
                applications.append(app_entry)
                count_apps = count_apps + 1
                #print(app_entry)
                
print("Applications collected: {}", str(count_apps))
f.write(applications)
f.close()