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
openEHRTool settings can be written in a file named openehrtool.cfg in the config dir. An example file called openehrtool.cfg.default is available in the same dir. The file is loaded at application boot or can be reloaded at runtime using the related method.

As an alternative, settings can be written at runtime in the application. Note that after rebooting ot stopping the app they are lost. 

### Available Settings
For the EHRBase server the following properties are needed:
* hostname : hostname or ip where the instance of ehrbase is running
* port : port of the running instance of ehrbase
* nodename : name given to the ehrbase instance following Java package naming
* username : username for the user to authenticate with basic authentication on ehrbase
* password : password for the user to authenticate with basic authentication on ehrbase
* (Optional) adusername : username for the admin user to authenticate with basic authentication on ehrbase
* (Optional) adpassword : password for the admin user to authenticate with basic authentication on ehrbase

The last two are optional but the "update template" method and the "dashboard" will not work properly if not set.

For the Redis server:
* hostname : hostname or ip where the instance of redis is running
* port : port of the running instance of redis
* eventsrecorded : max number of events recorded during a session in the log accessible via "Session log" menu item.

The session log is temporary. When the session is closed it is erased.

# How to Run

## Installing locally
openEHRTool needs Python 3. It has been tested with Python 3.8 but it should work as well with other versions.
After getting Python (3.8), install the required packages:
```
git clone https://github.com/sasurfer/openEHR-tool.git
cd openEHR-tool
pip install -r requirements.txt
```

In addition openEHRTool use Redis to show the last n transactions of the current session. Redis installation instuctions can be found [here](https://redis.io/docs/getting-started/installation). Once installed stop the running instance of Redis, if one is running, and launch it with the custom configuration available in the main directory:
```
redis-server ./redis.conf
```
### Development
Run with:
```
redis-server  ./redis.conf
python3 -m flask run -p <desired port>
ex:
redis-server  ./redis.conf
python3 -m flask run -p 9000
```
### Production
Launch through Gunicorn:
```
redis-server  ./redis.conf
gunicorn -w <number_of_workers> -b <ip>:<desired port> wsgi:app
ex:
redis-server  ./redis.conf
gunicorn -w 1 -b 127.0.0.1:9000 wsgi:app
```
use 0.0.0.0 as ip to bind to all external IPs on a non-privileged port.  Gunicorn version 20.1.0 has been used in testing.
## Using Docker
Use the docker files inside the cloned directory.
```
git clone https://github.com/sasurfer/openEHR-tool.git  
cd openEHR-tool
```
### Development
Run with:
```
docker-compose up
```
if a previous version was already used then rebuild the containers before running with:
```
docker-compose build
docker-compose up
```
### Production
Run with:
```
docker-compose -f docker-compose_prod.yml up
```
if a previous version was already used then rebuild the containers before running it:
```
docker-compose -f docker-compose_prod.yml build
docker-compose -f docker-compose_prod.yml up
```
