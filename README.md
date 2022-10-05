# openEHRTool

A tool meant to make it easier to interact with a **EHRBase** server. To take advantage of all the methods and the dashboard use a version of EHRBase >= 0.21.0 and add these lines to the .env.ehrbase file:
```
MANAGEMENT_ENDPOINTS_WEB_EXPOSURE=env,health,info,metrics,prometheus
MANAGEMENT_ENDPOINTS_WEB_BASEPATH=/management
MANAGEMENT_ENDPOINT_ENV_ENABLED=true
MANAGEMENT_ENDPOINT_HEALTH_ENABLED=true
MANAGEMENT_ENDPOINT_HEALTH_DATASOURCE_ENABLED=true
MANAGEMENT_ENDPOINT_INFO_ENABLED=true
MANAGEMENT_ENDPOINT_METRICS_ENABLED=true
MANAGEMENT_ENDPOINT_PROMETHEUS_ENABLED=false
MANAGEMENT_ENDPOINT_HEALTH_PROBES_ENABLED=true
ADMIN_API_ACTIVE=true
```
## Settings
openEHRTool settings can be written in a file named openehrtool.cfg in the config dir. In the same dir different examples are available and must be copied onto openehrtool.cfg in order to be read. That file is loaded at application boot or can be reloaded at runtime using the related method "Settings->Reload Settings".

The examples available are:
* openehrtool.cfg.example.local for locally installed openEHRTool (and Redis). Any platform
* openehrtool.cfg.example.total for docker "All in One" installation. See below for explanation on installation. Any platform
* openehrtool.cfg.example.linux  for docker "Separed" installation. openEHRTool separated from EHRBase. Linux host 
* openehrtool.cfg.example.mac for docker "Separated" installation. openEHRTool separated from EHRBase. MacOS host
* openehrtool.cfg.example.win for docker "Separated" installation. openEHRTool separated from EHRBase. Windows host

As an alternative, settings can be written at runtime in the application. Note that this way they are nor persisted and must be reentered when the application is stopped and rerun. 

### EHRBase-related Settings
For the EHRBase server the following properties are needed:
* hostname : hostname or ip where the instance of ehrbase is running
* port : port of the running instance of ehrbase
* nodename : name given to the ehrbase instance following Java package naming
* username : username for the user to authenticate with basic authentication on ehrbase
* password : password for the user to authenticate with basic authentication on ehrbase
* (Optional) adusername : username for the admin user to authenticate with basic authentication on ehrbase
* (Optional) adpassword : password for the admin user to authenticate with basic authentication on ehrbase

The last two are optional but the "update template" method and the "dashboard" will not work properly if not set.

### Redis-related settings
For the Redis server the following properties are needed:
* hostname : hostname or ip where the instance of redis is running
* port : port of the running instance of redis
* eventsrecorded : max number of events recorded during a session in the log accessible via "Session log" menu item.

The session log is temporary. When the session is closed it is erased.

# Requirements
* EHRBase preferably >= 0.21.0
* Redis. preferably >= 7.0.4
* Python 3 Preferably >= 3.8

Windows user will need to enable the Windows Subsystem for Linux a.k.a. WSL2 in order to install Redis and Docker Desktop. Installation instructions can be found [here](https://docs.microsoft.com/en-us/windows/wsl/install). Requirements for WSL2 are for Windows 10
* For x64 systems: Version 1903 or later, with Build 18362 or later.
* For ARM64 systems: Version 2004 or later, with Build 19041 or later.
whereas all versions of Windows 11 are supported.

# How to Install and Run

[//]: # (## <span style="color:red">Installing and running locally</span> )

## &#x1F335; Installing and running locally&#x1F335;
openEHRTool needs Python 3. It has been tested with Python 3.8 but it should work as well with other versions.
After getting Python (3.8), install the required packages:
For Linux or Windows:
```
git clone https://github.com/sasurfer/openEHR-tool.git
cd openEHR-tool
pip3 install -r requirements.txt
```
For macOS:
```
git clone https://github.com/sasurfer/openEHR-tool.git
cd openEHR-tool
pip3 install --user -r requirements.txt
```
In addition openEHRTool use Redis to show the last n transactions of the current session. Redis installation instuctions can be found [here](https://redis.io/docs/getting-started/installation). Once installed stop the running instance of Redis, if one is running.

For Windows users have to install a Linux OS inside Windows and then install Redis inside that. Instuctions can be found [here](https://redis.io/docs/getting-started/installation/install-redis-on-windows/).

In MacOS and Linux the redis-server can be launched with:
```
redis-server  ./redis.conf
```
In Windows enter the Linux subsystem and then launch:
```
redis-server /mnt/c/Users/{yourwindowsusername}/{relative_path_to_where_you_cloned_openEHRTool}/redis.conf
```
Substitute this command in the next sections if necessary. 
### Development
For Linux and MacOS define the environment before running the app:
```
export FLASK_ENV=development
```
For Windows:
```
set FLASK_ENV=development
```
Then run the app with:
```
redis-server  ./redis.conf
python3 -m flask run -p <desired port>
ex:
redis-server  ./redis.conf
python3 -m flask run -p 9000
```
If you need to make the app available in a network replace the last line with:
```
flask run --host='0.0.0.0' -p 9000
```
0.0.0.0 as ip binds to all external IPs on a non-privileged port
### Production
For Linux and MacOS define the environment before running the app:
```
export FLASK_ENV=production
```
For Windows:
```
set FLASK_ENV=production
```
Launch the app:
```
redis-server  ./redis.conf
gunicorn -w <number_of_workers> -b <ip>:<desired port> wsgi:app
ex:
redis-server  ./redis.conf
gunicorn -w 1 -b 127.0.0.1:9000 wsgi:app
```
Gunicorn version 20.1.0 has been used in testing.
If you need to make the app available in a network replace the last line with:
```
gunicorn -w 1 -b 0.0.0.0:9000 wsgi:app
```
0.0.0.0 as ip binds to all external IPs on a non-privileged port
## Using Docker 
Use the docker files inside the cloned directory.
```
git clone https://github.com/sasurfer/openEHR-tool.git  
cd openEHR-tool
```

[//]: # ( ### <span style="color:red"> Docker "All in One"</span> )

### &#x1F335; Docker "All in One" &#x1F335;
If you don't already have a working ehrbase server you can opt for the docker compose script that runs all the applications(EHRBase, openEHRTool and Redis) in the same docker subnet.

#### Development
Run with:
```
docker-compose -f docker-compose-total.yml
```
if you run an updated version of openEHRTool rebuild it and run it with:
```
docker-compose -f docker-compose-total.yml openehrtool build
docker-compose -f docker-compose-total.yml up
```
#### Production
Run with:
```
docker-compose -f docker-compose-total_prod.yml
```
if you run an updated version of openEHRTool rebuild it and run it with:
```
docker-compose -f docker-compose-total_prod.yml openehrtool build
docker-compose -f docker-compose-total_prod.yml up
```

[//]: # ( ### <span style="color:red"> Docker "Separated"</span> )

### &#x1F335; Docker "Separated" &#x1F335;
EHRBase is run in a network/docker-compose separated from openEHRTool.

#### Development
For linux run with:
```
docker-compose up
```
if a previous version was already used then rebuild the containers before running with:
```
docker-compose up --build
```
For macOS run with:
```
docker-compose -f docker-compose.yml.mac
```
and again if a previous version is there:
```
docker-compose -f docker-compose.yml.mac up --build
```
#### Production
For Linux run with:
```
docker-compose -f docker-compose_prod.yml up
```
if a previous version was already used then rebuild the containers before running it:
```
docker-compose -f docker-compose_prod.yml up --build
```
For macOS run with:
```
docker-compose -f docker-compose_prod.yml.mac
```
and again if a previous version is there:
```
docker-compose -f docker-compose_prod.yml.mac up --build
```


