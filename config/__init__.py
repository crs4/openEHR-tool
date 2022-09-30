import os
import sys
import config.settings

# create settings object corresponding to specified env
flaskenv=os.getenv('FLASK_ENV')
#print(flaskenv)
APP_ENV = os.environ.get('APP_ENV')
#print(APP_ENV)
if(APP_ENV is None):
    if flaskenv is not None:
        if flaskenv=='development':
            APP_ENV='Dev'
            os.environ['APP_ENV']=APP_ENV
        elif flaskenv=='production':
            APP_ENV='Production'
            os.environ['APP_ENV']=APP_ENV
        else:
            APP_ENV='Base'
            os.environ['APP_ENV']=APP_ENV
    else:
        APP_ENV='Base'
        os.environ['APP_ENV']=APP_ENV

_current = getattr(sys.modules['config.settings'], '{0}Config'.format(APP_ENV))()

# copy attributes to the environment
for atr in [f for f in dir(_current) if not '__' in f]:
    os.environ[atr]=str(getattr(_current,atr))
    # environment can override anything
    #val = os.environ.get(atr, getattr(_current, atr))
    #setattr(sys.modules[__name__], atr, val)
