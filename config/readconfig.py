import configparser

def readconfigfromfile(filename):
    global hostname,port,username,password,nodename,adusername,adpassword
    config = configparser.ConfigParser()
    config.read(filename)
    hostname=config['SERVER']['hostname']
    port=config['SERVER']['port']
    nodename=config['SERVER']['nodename']
    username=config['USERS']['username']
    password=config['USERS']['password']
    if('adusername' in config['USERS']):
        adusername=config['USERS']['adusername']
        adpassword=config['USERS']['adpassword']
        return hostname,port,nodename,username,password,adusername,adpassword
    return hostname,port,nodename,username,password