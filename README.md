# openEHRTool

A tool meant to make it easier to interact with a **EHRBase** server. 

To take advantage of all the methods and the dashboard use a version of EHRBase >= 0.32.0 and add these lines to the .env.ehrbase file:
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
MANAGEMENT_ENDPOINT_ENV_SHOWVALUES=ALWAYS
ADMIN_API_ACTIVE=true
ADMINAPI_ALLOWDELETEALL=true
```
## Settings
openEHRTool settings can be written in a file named openehrtool.cfg in the config dir. In the same dir different examples are available and must be copied onto openehrtool.cfg in order to be read. That file is loaded at application boot or can be reloaded at runtime using the related method "Settings->Reload Settings".

The examples available are:
* openehrtool.cfg.example.local for locally installed openEHRTool (and Redis). Any platform
* openehrtool.cfg.example.total for docker "All in One" installation. See below for explanation on installation. Any platform
* openehrtool.cfg.example.linux.1 and openehrtool.cfg.example.linux.2  for docker "Separed" installation. openEHRTool separated from EHRBase. Linux host. (openehrtool.cfg.example.linux.1 refers to docker-compose_prod.yml.linux.1/docker-compose.yml.linux.1 whereas openehrtool.cfg.example.linux.2 refers to docker-compose_prod.yml.linux.2/docker-compose.yml.linux.2)
* openehrtool.cfg.example.mac for docker "Separated" installation. openEHRTool separated from EHRBase. MacOS host. (It applies to both mac.1 and mac.2 docker-compose)
* openehrtool.cfg.example.win for docker "Separated" installation. openEHRTool separated from EHRBase. Windows host (It applies to both win.1 and win.2 docker-compose)

As an alternative, settings can be written at runtime in the application. Note that this way they are nor persisted and must be reentered when the application is stopped and rerun. 

Thanks to @Meelzak settings can be set also through the following environment variables:
* EHRBASESERVER_hostname 
* EHRBASESERVER_port 
* EHRBASESERVER_nodename 
* EHRBASEUSERS_username 
* EHRBASEUSERS_password 
* EHRBASEUSERS_adusername 
* EHRBASEUSERS_adpassword 
* REDISSERVER_hostname
* REDISSERVER_port
* REDISSERVER_eventsrecorded

### Networking problems
If you are using Docker on Linux, in the "Separated" mode, you can start with the docker-compose file that ends in linux.1 and if you experience networking problems(unable to connect or sluggishness) you can try linux.2 . The version 1 adopts the host network mode so the openEHRTool container behave as if it was run from the host machine. The version 2 is similar to the other OS and it publishes ports to the host machine. 

If you are using Docker on Mac or Windows, in the "Separated" mode, you can start with the docker-compose file that ends in mac.1 or win.1 respectively and if you experience networking problems (unable to connect or sluggishness) you can first try the second compose mac.2 or win.2 . If the change does not solve the problem then connect the network where resides openEHR-tool to the EHRBase network. First find the network of ehrbase:
```
docker ps | grep ehrbase

output example:
419459a16bda   ehrbase/ehrbase-postgres:latest   "docker-entrypoint.s…"   7 weeks ago   Up 5 hours   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ehrbase-0210_ehrdb_1
e2c60fa51110   ehrbase/ehrbase:0.21.0            "/bin/sh -c ./docker…"   7 weeks ago   Up 5 hours   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ehrbase-0210_ehrbase_1
```
then inspect the container to obtain the network name:
```
docker inspect e2c60fa51110 | grep -i networkmode

output example:
"NetworkMode": "ehrbase-0210_ehrbase-net",
```
then edit docker-compose.yml.mac.2 or docker-compose.yml.win.2, depending on you OS,replacing in the second to last line:
```
name: ehrbase_ehrbase-net
```
with your EHRBase network name:
```
name: ehrbase-0210_ehrbase-net
```
Now you can rebuild your containers. On MacOS:
```
docker-compose -f docker-compose.yml.mac.2 up --build
```
on Windows:
```
docker-compose -f docker-compose.yml.win.2 up --build
```
The right configuration file now is openehrtool.cfg.example.total so make sure to copy it onto openehrtool.cfg before running or otherwise reload the configuration after doing the copy.

### EHRBase-related Settings
For the EHRBase server the following properties are needed:
* hostname : hostname or ip where the instance of ehrbase is running
* port : port of the running instance of ehrbase
* nodename : name given to the ehrbase instance following Java package naming
* username : username for the user to authenticate with basic authentication on ehrbase
* password : password for the user to authenticate with basic authentication on ehrbase
* (Optional) adusername : username for the admin user to authenticate with basic authentication on ehrbase
* (Optional) adpassword : password for the admin user to authenticate with basic authentication on ehrbase

The admin credentials are optional but if they are not available the methods in the ADMIN section will not work and the "dashboard" will not have access to all the information it needs to fill its sections.

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
## Running in Docker 
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
docker-compose -f docker-compose-total.yml openehrtool up --build
```
#### Production
Run with:
```
docker-compose -f docker-compose-total_prod.yml
```
if you run an updated version of openEHRTool rebuild it and run it with:
```
docker-compose -f docker-compose-total_prod.yml openehrtool up --build
```

[//]: # ( ### <span style="color:red"> Docker "Separated"</span> )

### &#x1F335; Docker "Separated" &#x1F335;
EHRBase is run in a network/docker-compose separated from openEHRTool.

#### Development
For linux choose which composer to run between docker-compose.yml.linux.1 and docker-compose.yml.linux.2 and then run:
Note: In the following we show the lines to run for linux.1 but they apply to linux.2 too. Remember to adopt the right cfg file. There is one separate configuration file .cfg for each of them):
```
docker-compose -f docker-compose.yml.linux1 
```
if a previous version was already used then rebuild the containers before running with:
```
docker-compose -f docker-compose.yml.linux1 up --build
```
For macOS run with:
```
docker-compose -f docker-compose.yml.mac.1 up
```
and again if a previous version is there:
```
docker-compose -f docker-compose.yml.mac.1 up --build
```
#### Production
For Linux run with:
```
docker-compose -f docker-compose_prod.yml.linux1 up
```
if a previous version was already used then rebuild the containers before running it:
```
docker-compose -f docker-compose_prod.yml.linux1 up --build
```
For macOS run with:
```
docker-compose -f docker-compose_prod.yml.mac.1
```
and again if a previous version is there:
```
docker-compose -f docker-compose_prod.yml.mac.1 up --build
```

## &#x1F335; Testing (for developers)&#x1F335;
In order to launch testing set the env variable APP_ENV:
```
export APP_ENV=Test
```
and then launch pytest:
```
python -m pytest --capture=tee-sys  -v
```
# Available methods: #
Methods in:
<ul>
<li> https://specifications.openehr.org/releases/ITS-REST/latest/ehr.html</li>
<li>https://specifications.openehr.org/releases/ITS-REST/latest/query.html</li>
<li>https://specifications.openehr.org/releases/ITS-REST/latest/definition.html except for ADL2 Template methods</li>

# Screenshots: #
![homepage](/../screenshots/screenshots/homepage.png?raw=true "Homepage")
![dashboard](/../screenshots/screenshots/dashboard.png?raw=true "Dashboard")
![get_template](/../screenshots/screenshots/gettemplate.png?raw=true "Get Template")
![examplecomp](/../screenshots/screenshots/examplecomp.png?raw=true "Composition example from Template")
![postcomp](/../screenshots/screenshots/postcomp.png?raw=true "Post a Composition")
![runaql](/../screenshots/screenshots/runquery.png?raw=true "Run AQL (query)")
![sessionlog](/../screenshots/screenshots/sessionlog.png?raw=true "Session Activities")
