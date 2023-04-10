'''

This is a program to search every application in each category.

'''



import os
import sys
import json
from gpapi.googleplay import GooglePlayAPI
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

with open(resource_path("/config/login.json")) as logins:
    device_log_ins = json.load(logins)
    current_log_in = device_log_ins['test_device'] # Change this to change device


server = GooglePlayAPI("en_US", "Europe/Portugal", current_log_in['deviceName'])

logger.info("logging...")
server.login(
    email=current_log_in['username'],
    password=current_log_in['password'],
)
logger.debug("login complete!")

browse = server.browse()
for c in browse["category"]:
    nameCat = c["name"]
    data_url = c["dataUrl"]
    
    if "homeV2" not in data_url: #Only look at applications that have a valid category
        continue
    
    sampleCat = data_url[11:].split("&")[0]
    browseCat = server.home(cat=sampleCat) #Browse Applications for that category
    
    logger.debug("Sample Category: {}".format(sampleCat))
    
    for child in browseCat:
        for cluster in child.get('child'):
            logger.debug("Cluster: {}".format(cluster.get("title")))
            
            print(cluster.get("title"))
            for app in cluster.get('child'):
                print("Title: {} - Package: {} - Category: {}".format(app.get('title'), app.get('docid'), nameCat))