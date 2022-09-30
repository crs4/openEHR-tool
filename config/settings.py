class BaseConfig():
    TESTING = False
    DEBUG = False
    SEND_FILE_MAX_AGE_DEFAULT=0
    FLASK_ENV='development'

class DevConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    FLASK_ENV='production'


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
