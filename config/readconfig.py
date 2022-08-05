import configparser

def readconfigfromfile(filename):
    global hostname,port,username,password,nodename,adusername,adpassword, \
        redishostname,redisport
    config = configparser.ConfigParser()
    config.read(filename)
    hostname=config['EHRBASESERVER']['hostname']
    port=config['EHRBASESERVER']['port']
    nodename=config['EHRBASESERVER']['nodename']
    username=config['EHRBASEUSERS']['username']
    password=config['EHRBASEUSERS']['password']
    redishostname=config['REDISSERVER']['hostname']
    redisport=config['REDISSERVER']['port']
    reventsrecorded=config['REDISSERVER']['eventsrecorded']
    if('adusername' in config['EHRBASEUSERS']):
        adusername=config['EHRBASEUSERS']['adusername']
        adpassword=config['EHRBASEUSERS']['adpassword']
        return hostname,port,nodename,username,password,adusername,adpassword,redishostname,redisport,reventsrecorded
  
    return hostname,port,nodename,username,password,redishostname,redisport,reventsrecorded