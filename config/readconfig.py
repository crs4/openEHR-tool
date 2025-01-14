import configparser

def readconfigfromfile(filename):
    global hostname,port,protocol,https_mapping,username,password,nodename,adusername,adpassword, \
        redishostname,redisport,ehrbase_version
    config = configparser.ConfigParser()
    config.read(filename)
    hostname=config['EHRBASESERVER']['hostname']
    port=config['EHRBASESERVER']['port']
    nodename=config['EHRBASESERVER']['nodename']
    protocol=config['EHRBASESERVER']['protocol']
    https_mapping=config['EHRBASESERVER']['https_mapping']
    ehrbase_version=config['EHRBASESERVER']['version']
    username=config['EHRBASEUSERS']['username']
    password=config['EHRBASEUSERS']['password']
    redishostname=config['REDISSERVER']['hostname']
    redisport=config['REDISSERVER']['port']
    reventsrecorded=config['REDISSERVER']['eventsrecorded']
    if('adusername' in config['EHRBASEUSERS']):
        adusername=config['EHRBASEUSERS']['adusername']
        adpassword=config['EHRBASEUSERS']['adpassword']
        return hostname,port,nodename,protocol,https_mapping,ehrbase_version,username,password,adusername,adpassword,redishostname,redisport,reventsrecorded
  
    return hostname,port,nodename,protocol,https_mapping,ehrbase_version,username,password,redishostname,redisport,reventsrecorded