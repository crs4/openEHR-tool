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


# How to Run

## Installing locally
openEHRTool needs Python 3. It has been tested with Python 3.8 but it should work as well with other versions.
After getting Python (3.8), install the required packages:
```
git clone https://github.com/sasurfer/openEHR-tool.git
cd openEHR-tool
pip install -r requirements.txt
```
### Development
Run with:
```
python3 -m flask run -p <desired port>
ex:
python3 -m flask run -p 9000
```
### Production
Launch through Gunicorn:
```
gunicorn -w <number_of_workers> -b <ip>:<desired port> wsgi:app
ex:
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
### Production
Run with:
```
docker-compose -f docker-compose_prod.yml up
```

