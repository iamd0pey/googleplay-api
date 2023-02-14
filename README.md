# Google play python API

This project contains an unofficial API for google play interactions. The code mainly comes from
[GooglePlayAPI project](https://github.com/egirault/googleplay-api/) which is not
maintained anymore. The code was updated with some important changes:

* ac2dm authentication with checkin and device info upload
* updated search and download calls
* select the device you want to fake from a list of pre-defined values (check `device.properties`)
(defaults to a OnePlus One)

# Build

This is the recommended way to build the package, since setuptools will take care of
generating the `googleplay_pb2.py` file needed by the library (check the `setup.py`)

```
$ python setup.py build
```

# Usage

Check scripts in `test` directory for more examples on how to use this API.

```
from gpapi.googleplay import GooglePlayAPI

mail = "mymail@google.com"
passwd = "mypasswd"

api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename="hero2lte")
api.login(email=mail, password=passwd)

result = api.search("firefox")

for doc in result:
    if 'docid' in doc:
        print("doc: {}".format(doc["docid"]))
    for cluster in doc["child"]:
        print("\tcluster: {}".format(cluster["docid"]))
        for app in cluster["child"]:
            print("\t\tapp: {}".format(app["docid"]))
```

For first time logins, you should only provide email and password.
The module will take care of initalizing the api, upload device information
to the google account you supplied, and retrieving 
a Google Service Framework ID (which, from now on, will be the android ID of your fake device).

For the next logins you **should** save the gsfId and the authSubToken, and provide them as parameters
to the login function. If you login again with email and password, this is the equivalent of
re-initalizing your android device with a google account, invalidating previous gsfId and authSubToken.

## Notes

First create a login.json with the following information

```
{
	"test_device": {
		"username": "<google_email_account>",
		"password": "<app_password>",
		"deviceName": "<codename_device>",
		"gsfId" : <gsf_id>
	}
}
```

### Password

To create password first add two factor authentication to the google account.
Then create a application password in the button below two factor authentication in the google account.

### deviceName

There is a list of device names in /gpapi/device.properties, choose one and then add the codename, for "Nexus 5 (api 27)" the code name is "hammerhead"

### gsfId

To get this value go to Nexus 5 details, in my case, and then search for GSF.version.


## Build the project

```
docker build -t googleplay_api .
```

## Run the Project

```
cd ~/googleplay-api
docker run -ti --mount type=bind,source="$(pwd)"/test,target=/scripts_gpapi --mount type=bind,source="$(pwd)"/apks,target=/apks googleplay_api:latest
```

## Other Useful Commands

### Docker remove all images
docker rmi -f $(docker images -aq)

### Docker remove containers
docker container prune

### Docker remove volumes
docker volume prune



NOTE: If you have a question feel free to open an issue.
