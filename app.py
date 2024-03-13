from argparse import FileType
from flask import Flask
from flask import request,render_template,redirect,url_for
from requests import session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
from config import readconfig,logging_configurations
import config
from myutils import myutils
import sys
import redis
import json
from werkzeug.exceptions import default_exceptions
from datetime import datetime
import traceback

default_hostname="localhost"
default_port="8080"
default_username="ehrbase-user"
default_password="SuperSecretPassword"
default_nodename="local.ehrbase.org"
default_adusername="ehrbase-admin"
default_adpassword="EvenMoreSecretPassword"
default_redishostname='localhost'
default_redisport="6379"
default_reventsrecorded = 100
hostname=""
port=""
username=""
password=""
lastehrid=""
lastcompositionid=""
nodename=""
adusername=""
adpassword=""
redishostname=""
redisport=""
reventsrecorded = 0
currentposition=0
sessiontotalevents=0
lastaql=""
r=''
client=''

def init_redis(redishostname,redisport):
    global r
    r = redis.Redis(host=redishostname, port=redisport,db=0,decode_responses=True)
    return r

def insertlogline(line):
    global currentposition,sessiontotalevents,r
    now = datetime.now()
    timestamp = now.strftime("%Y/%m/%d-%H:%M:%S-")
    if(currentposition==reventsrecorded):
        currentposition=0
    mykey='c'+str(currentposition)
    try:
        r.set(mykey,timestamp+line)
        currentposition+=1
        sessiontotalevents+=1
    except:
        render_template('error.html',error='Redis not initialised or not working properly',errorcode=500,info=str(sys.exc_info()))


def create_app():
    global hostname,port,username,password,lastehrid,lastcompositionid,nodename,adusername, \
        adpassword,redishostname,redisport,reventsrecorded,currentposition,sessiontotalevents,auth, \
            adauth,r,client
    app = Flask(__name__)
    app.app_context()
    app.config.from_object('config')
    app.logger.info(f"Running with APP_ENV={os.getenv('APP_ENV')}")
    app.logger.info(f"Running with FLASK_ENV={os.getenv('FLASK_ENV')}")
    #running_env=os.getenv('FLASK_ENV')
    #print(running_env)
    app.logger.info(f"Running with DEBUG={os.getenv('DEBUG')}")
    app.logger.info(f"Running with TESTING={os.getenv('TESTING')}")
    app.logger.info(f"Running with SEND_FILE_MAX_AGE_DEFAULT={os.getenv('SEND_FILE_MAX_AGE_DEFAULT')}")


    import ehrbase_routines

    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        to=traceback.format_exc()
        return render_template('error.html',error=str(e),errorcode=code,info=str(sys.exc_info()),traceback='\n'.join(to))
    for ex in default_exceptions:
        app.register_error_handler(ex, handle_error)


    settingsfile='./config/openehrtool.cfg'
    #get vars from env
    env_varset = [os.environ.get('EHRBASESERVER_hostname', None), 
                  os.environ.get('EHRBASESERVER_port', None),
                  os.environ.get('EHRBASESERVER_nodename', None),
                  os.environ.get('EHRBASEUSERS_username', None),
                  os.environ.get('EHRBASEUSERS_password', None),
                  os.environ.get('EHRBASEUSERS_adusername', None),
                  os.environ.get('EHRBASEUSERS_adpassword', None),
                  os.environ.get('REDISSERVER_hostname', None),
                  os.environ.get('REDISSERVER_port', None),
                  os.environ.get('REDISSERVER_eventsrecorded', None)]
    if (os.path.exists(settingsfile)):
        varset=readconfig.readconfigfromfile(settingsfile)
        #build varset from environment variables
        for i in ([0,1,2,3,4] +([5,6] if len(varset)==10 else []) +[-3,-2,-1]):
            if env_varset[i] is None:
                env_varset[i] = varset[i]
    varset = tuple(env_varset)
    if (len([v for v in varset if v is not None])>0):
        if(len(varset)==10):
            hostname,port,nodename,username,password,adusername,adpassword,redishostname,redisport,reventsrecorded=varset        
            reventsrecorded=int(reventsrecorded)
            global adauth
            adauth= myutils.getauth(adusername,adpassword)  
        else:
            hostname,port,nodename,username,password,redishostname,redisport,reventsrecorded=varset  
            reventsrecorded=int(reventsrecorded)      
        auth = myutils.getauth(username,password)
        r=init_redis(redishostname,redisport)
        with app.app_context():
            client=ehrbase_routines.init_ehrbase()
    else:
        r=""
        client=""

    @app.route("/")
    @app.route('/about.html')
    def about():
        return render_template('about.html')

    @app.route("/fsettings.html",methods=["GET"])
    #load settings from file
    def fset():
        global hostname,port,username,password,nodename,adusername,adpassword,redishostname,redisport,reventsrecorded, \
            client
        #get vars from env
        env_varset = [os.environ.get('EHRBASESERVER_hostname', None), 
                    os.environ.get('EHRBASESERVER_port', None),
                    os.environ.get('EHRBASESERVER_nodename', None),
                    os.environ.get('EHRBASEUSERS_username', None),
                    os.environ.get('EHRBASEUSERS_password', None),
                    os.environ.get('EHRBASEUSERS_adusername', None),
                    os.environ.get('EHRBASEUSERS_adpassword', None),
                    os.environ.get('REDISSERVER_hostname', None),
                    os.environ.get('REDISSERVER_port', None),
                    os.environ.get('REDISSERVER_eventsrecorded', None)]
        if (os.path.exists(settingsfile)):
                varset=readconfig.readconfigfromfile(settingsfile)
                #build varset from environment variables
                for i in ([0,1,2,3,4] +([5,6] if len(varset)==10 else []) +[-3,-2,-1]):
                    if env_varset[i] is None:
                        env_varset[i] = varset[i]
        varset = tuple(env_varset)
        if (len([v for v in varset if v is not None])>0):
            if(len(varset)==10):
                hostname,port,nodename,username,password,adusername,adpassword,redishostname,redisport,reventsrecorded=varset        
                global adauth
                adauth= myutils.getauth(adusername,adpassword)
                reventsrecorded=int(reventsrecorded)
            else:
                hostname,port,nodename,username,password,redishostname,redisport,reventsrecorded=varset  
                reventsrecorded=int(reventsrecorded)      
            global auth,r
            auth = myutils.getauth(username,password)  
            r=init_redis(redishostname,redisport)
            client=ehrbase_routines.init_ehrbase()
            result='Settings Reloaded Successfully'
            app.logger.info("Settings reloaded from file")
        else:
            result='Settings File "config/openehrtool.cfg" not found'
            app.logger.warning(result)
        return render_template('about.html',result=result)


    @app.route("/settings.html",methods=["GET"])
    #change settings from html page
    def ehrbase():
        global hostname,port,username,password,nodename,lastehrid,lastcompositionid, \
            adusername,adpassword,redishostname,redisport,reventsrecorded,client

        status='failed'
        if request.args.get("pippo")=="Submit":
            hostname=request.args.get("hname","")
            port=request.args.get("port","")
            username=request.args.get("uname","")
            password=request.args.get("pword","")
            nodename=request.args.get("nodename","")

            redishostname=request.args.get("rhname","")
            redisport=request.args.get("rport","")
            reventsrecorded=request.args.get("revents","")
            if(hostname==""):
                hostname=default_hostname
            if(port==""):
                port=default_port
            if(username==""):
                username=default_username 
            if(password==""):
                password=default_password   
            if(nodename==""):
                nodename=default_nodename
            if(redishostname==""):
                redishostname=default_redishostname
            if(redisport==""):
                redisport=default_redisport       
            if(reventsrecorded==""):
                reventsrecorded=default_reventsrecorded   
            else:
                reventsrecorded=int(reventsrecorded)  
            if(request.args.get('admin')=='yes'):
                adusername=request.args.get("aduname")
                adpassword=request.args.get("adpword","")        
                if(adusername==""):
                    adusername=default_adusername 
                if(adpassword==""):
                    adpassword=default_adpassword           
                global adauth
                adauth= myutils.getauth(adusername,adpassword)
            global auth,r
            client=ehrbase_routines.init_ehrbase()
            auth = myutils.getauth(username,password)
            r=init_redis(redishostname,redisport)
            app.logger.info("settings changed from within app")
            status='success'
            return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                        adus=adusername,adpas=adpassword,rho=redishostname,rpo=redisport,rr=reventsrecorded,status=status)
        return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                        adus=adusername,adpas=adpassword,rho=redishostname,rpo=redisport,rr=reventsrecorded,status=status)

    @app.route("/ssettings.html",methods=["GET"])
    #see current settings 
    def ssettings():
        global hostname,port,username,password,nodename,lastehrid,lastcompositionid, \
            adusername,adpassword,redishostname,redisport,reventsrecorded,client
        return render_template('ssettings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                        adus=adusername,adpas=adpassword,rho=redishostname,rpo=redisport,rr=reventsrecorded)


    @app.route("/gtemp.html",methods=["GET"])
    #get template
    def gtemp():
        global hostname,port,username,password,auth,nodename,mymsg,currentposition
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        yourresults=""
        singletemplate='false'
        singletemplate2='false'
        yourtemp=""
        yourjson='{}'
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'gtempbase.html','gtemp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.args.get("pippo")=="Get Template": 
            template_name=request.args.get("tname","")
            tformat=request.args.get("format","")
            msg=ehrbase_routines.gettemp(client,auth,hostname,port,username,password,tformat,template_name)
            if(msg['status']=="success"):            
                if(tformat=='OPT'):
                    singletemplate='true'
                    singletemplate2='false'
                    temp=msg['template']
                    yourresults=str(msg['status'])+ " "+ str(msg['status_code'])
                    yourtemp=temp
                    insertlogline('Get template:template '+template_name+' retrieved successfully in OPT format')
                    return render_template('gtemp.html',temp=temp,singletemplate=singletemplate,yourresults=yourresults,singletemplate2=singletemplate2,yourtemp=yourtemp)
                else:
                    singletemplate2='true'
                    singletemplate='false'
                    temp=msg['template']
                    yourresults=str(msg['status'])+ " "+ str(msg['status_code'])
                    yourjson=temp
                    insertlogline('Get template:template '+template_name+' retrieved successfully in WebTemplate format')   
                    return render_template('gtemp.html',temp=temp,singletemplate=singletemplate,singletemplate2=singletemplate2,yourresults=yourresults,yourjson=yourjson)
            else:
                if (tformat=='OPT'):
                    a='OPT'
                else:
                    a='WebTemplate'
                insertlogline('Get template:template '+template_name+' retrieval failure in'+a+' format')   
                singletemplate='false'
                singletemplate2='false'
                yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                                str(msg['text']) + "\n" +\
                                str(msg['headers'])
                return render_template('gtemp.html',singletemplate=singletemplate,singletemplate2=singletemplate2, yourresults=yourresults)
        else:
            return render_template('gtemp.html',singletemplate=singletemplate,singletemplate2=singletemplate2,yourresults=yourresults)

    @app.route("/ltemp.html",methods=["GET"])
    #get list of templates
    def ltemp():
        global hostname,port,username,password,auth,nodename,mymsg,currentposition
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        yourresults=""
        yourjson=''
        status='failed'
        if request.args.get("pippo2")=="Get List":
            msg=ehrbase_routines.listtemp(client,auth,hostname,port,username,password)
            if msg['status']=='success':
                status='success'
                yourjson=msg['json']
                yourresults='List of templates successfully retrieved'
                insertlogline('Get template:template list retrieved successfully')   
            else:
                status='failure'
                yourresults=f"status={msg['status']}\nstatus_code={msg['status_code']}\n\
                text={msg['text']}"
                insertlogline('Get template:template list retrieval failure')   
            return render_template('ltemp.html',yourresults=yourresults,yourjson=yourjson,status=status)
        else:
            return render_template('ltemp.html',yourresults=yourresults,yourjson=yourjson,status=status)


    @app.route("/ptemp.html",methods=['GET', 'POST'])
    #post template
    def pwrite():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))    
        yourresults=""
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                render_template('ptemp.html',yourfile="you uploaded "+secure_filename(uploaded_file.filename))
                uploaded_file.stream.seek(0) # seek to the beginning of file
                template=uploaded_file.read()
                msg=ehrbase_routines.posttemp(client,auth,hostname,port,username,password,template)
                yourresults=str(msg['status'])+" "+str(msg['status_code'])+ "\n"+ \
                    str(msg['headers'])+"\n"+ \
                        str(msg['text'])           
                if(msg['status']=='success'):
                    template_name=msg['headers']['ETag']
                    insertlogline('Post template: template '+template_name+' posted successfully')     
                else:            
                    insertlogline('Post template:template from file '+uploaded_file.filename+' posting failure')       
                return render_template('ptemp.html',yourresults=yourresults)
            else:
                yourresults='Please choose a file first'
                return render_template('ptemp.html',yourresults=yourresults)
        else:
            return render_template('ptemp.html',yourresults=yourresults)


    @app.route("/utemp.html",methods=['GET', 'POST'])
    #update template (admin)
    def pupdate():
        global hostname,port,adusername,adpassword,adauth,nodename,uploaded_file,template,tempname
        if(hostname=="" or port=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        if(adusername=="" or adpassword==""):
            return render_template('/utemp.html',warning='WARNING: NO ADMIN CREDENTIALS PROVIDED '), {"Refresh": "3; url="+url_for('ehrbase') }
        yourresults=""
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'utempbase.html','utemp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.method == 'POST':
            uploaded_file = request.files['file']
            tempname=uploaded_file.filename
            if uploaded_file.filename != '':           
                uploaded_file.stream.seek(0) # seek to the beginning of file
                template=uploaded_file.read()
                yourresults="you chose "+secure_filename(uploaded_file.filename)+"\n"
                return render_template('utemp.html',yourresults=yourresults)
            else:
                yourresults='Please choose a file first'
                return render_template('utemp.html',yourresults=yourresults)
        else :
            if (request.args.get("pippo")=="Update Template"):
                templateid=request.args.get("tname","")
                if(templateid != "" and template):
                    msg=ehrbase_routines.updatetemp(client,adauth,hostname,port,adusername,adpassword,template,templateid)
                    yourresults="you uploaded "+secure_filename(uploaded_file.filename)+"\n"
                    
                    if(msg['status']=='success'):
                        yourresults="you updated successfully "+secure_filename(uploaded_file.filename)+"\n"
                        insertlogline('Put template (admin):template '+templateid+' updated successfully')
                    else:
                        yourresults="you updated unsuccessfully "+secure_filename(uploaded_file.filename)+"\n"
                        insertlogline('Put template (admin):template from file' + tempname +'and templateid '+templateid +' updating failure')
                    yourresults=yourresults+str(msg['status']+''+str(msg['headers']))                      
                    return render_template('utemp.html',yourresults=yourresults)
        return render_template('utemp.html',yourresults=yourresults)


    @app.route("/dtemp.html",methods=["GET"])
    #delete template (admin)
    def dtemp():
        global hostname,port,adusername,adpassword,auth,adauth,nodename,mymsg,username,password
        if(hostname=="" or port=="" or adusername=="" or adpassword=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        yourresults=""
        yourjson='{}'
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'dtempbase.html','dtemp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.args.get("pippo")=="Delete Template": 
            template_name=request.args.get("tname","")
            msg=ehrbase_routines.deltemp(client,adauth,hostname,port,adusername,adpassword,template_name)
            if(msg['status']=='success'):
                yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nTemplate "+template_name+ " successfully deleted"
                insertlogline('Delete template (admin):template '+template_name+' deleted successfully')
            else:
                yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nTemplate "+template_name+ " unsuccessfully deleted"
                insertlogline('Delete template (admin):template '+template_name+' deletion failure')            
            return render_template('dtemp.html',yourresults=yourresults)
        elif request.args.get("pippo")=="Delete all":
            msg=ehrbase_routines.delalltemp(client,adauth,hostname,port,adusername,adpassword)
            if(msg['status']=='success'):
                yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nAll Templates successfully deleted"
                insertlogline('Delete template: all templates deleted successfully')
                return render_template('dtemp.html',yourresults=yourresults)
            else:
                yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nAll Templates unsuccessfully deleted"
                insertlogline('Delete template: all templates deletion failure')
                if msg['status_code']==422:
                    yourjson=msg['error422']    
                    return render_template('dtemp.html',yourresults=yourresults,yourjson=yourjson) 
                else:
                    insertlogline('Delete template: all templates deletion failure')            
                    return render_template('dtemp.html',yourresults=yourresults) 
        else:
            return render_template('dtemp.html',yourresults=yourresults)


    @app.route("/pehr.html",methods=["GET"])
    #create ehr
    def pehr():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        global lastehrid
        if request.args.get("sform1")=="Submit": #EHRID specified or not
            ehrid=request.args.get("ehrtext","")
            msg=ehrbase_routines.createehrid(client,auth,hostname,port,username,password,ehrid)
            if(msg['status']=="success"):
                ehrid=msg["ehrid"]
                yourresults=f"EHR created successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
                lastehrid=ehrid
                ehr=msg['text']
                insertlogline('Post EHR:ehr '+ehrid+' posted successfully')
            else:
                yourresults=f"EHR creation failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"
                ehr={}
                insertlogline('Post EHR: ehr posting failure')
            return render_template('pehr.html',yourresults=yourresults,ehr=ehr)    
        elif request.args.get("sform2")=="Submit":   #subjectID and subjectNamespace and maybe EHRID
            eid=request.args.get("eid","")
            sid=request.args.get("sid","")
            sna=request.args.get("sna","")
            if(sid=="" or sna==""):
                return render_template('pehr.html')        
            msg=ehrbase_routines.createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
            if(msg['status']=="success"):
                ehrid=msg["ehrid"]
                yourresults=f"EHR created successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
                lastehrid=ehrid
                ehr=msg['text']
                insertlogline('Post EHR:'+ehrid+' posted successfully')
            else:
                yourresults=f"EHR creation failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
                ehr={}
                insertlogline('Post EHR: ehr posting failure')
            return render_template('pehr.html',yourresults=yourresults,ehr=ehr)
        else:
            return render_template('pehr.html')  

    @app.route("/gehr.html",methods=["GET"])
    #get ehr
    def gehr():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastehrid
        status="failed"
        if request.args.get("fform1")=="Submit": 
            ehrid=request.args.get("ename","") 
            if(ehrid==""):
                return render_template('gehr.html',lastehr=lastehrid)
            msg=ehrbase_routines.getehrid(client,auth,hostname,port,username,password,ehrid)
            if(msg['status']=="success"):
                ehrid=msg["ehrid"]
                yourresults=f"EHR retrieved successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
                ehr=msg['text']
                lastehrid=ehrid
                status='success'
                insertlogline('Get EHR by ehrid: ehr '+ehrid+' retrieved successfully')
            else:
                ehr={}
                yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
                insertlogline('Get EHR by ehrid: ehr '+ehrid+' retrieval failure')
            return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid,status=status)
        elif request.args.get("fform2")=="Submit": 
            sid=request.args.get("sid","") 
            sna=request.args.get("sna","")
            if(sid=="" or sna==""):
                return render_template('gehr.html',lastehr=lastehrid)
            msg=ehrbase_routines.getehrsub(client,auth,hostname,port,username,password,sid,sna)
            if(msg['status']=="success"):
                ehrid=msg["ehrid"]
                yourresults=f"EHR retrieved successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
                ehr=msg['text']
                lastehrid=ehrid
                status='success'
                insertlogline('Get EHR by SubjectId and SubjectNamespace: Sid,Sna='+sid+','+sna+'  ehr '+ehrid+' retrieved successfully')
            else:
                ehr={}
                yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"
                insertlogline('Get EHR by SubjectId and SubjectNamespace: Sid,Sna='+sid+','+sna+' ehr retrieval failure')        
            return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid,status=status)
        return render_template('gehr.html',lastehr=lastehrid,status=status)

    @app.route("/dehr.html",methods=["GET"])
    #delete ehr
    def dehr():
        global hostname,port,adusername,adpassword,auth,adauth,nodename
        if(hostname=="" or port=="" or adusername=="" or adpassword=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        status="failed"
        yourresults=''
        if request.args.get("fform1")=="Delete": 
            ehrid=request.args.get("ename","") 
            if(ehrid==""):
                return render_template('dehr.html')
            msg=ehrbase_routines.delehrid(client,adauth,hostname,port,adusername,adpassword,ehrid)
            if(msg['status']=="success"):
                ehrid=msg["ehrid"]
                yourresults=f"EHR deleted successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
                status='success'
                insertlogline('Delete EHR by ehrid: ehr '+ehrid+' deleted successfully')
            else:
                yourresults=f"EHR deletion failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
                insertlogline('Delete EHR by ehrid: ehr '+ehrid+' deletion failure')
            return render_template('dehr.html',yourresults=yourresults)
        else:
            return render_template('dehr.html')

    @app.route("/pehrstatus.html",methods=['GET', 'POST'])
    #post template
    def pehrstatus():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))    
        yourresults=""
        compjson=''
        status='failure'
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                render_template('ptemp.html',yourfile="you uploaded "+secure_filename(uploaded_file.filename))
                uploaded_file.stream.seek(0) # seek to the beginning of file
                ehrstatus=uploaded_file.read()
                msg=ehrbase_routines.postehrstatus(client,auth,hostname,port,username,password,ehrstatus)
                          
                if(msg['status']=='success'):
                    status='success'
                    compjson=msg['text']
                    ehrsid=json.loads(compjson)['ehr_status']['uid']['value']
                    ehrid=json.loads(compjson)['ehr_id']['value']
                    insertlogline('Post EHR:ehr '+ehrid+' posted successfully')
                    insertlogline('Post EHR_STATUS: EHR_STATUS '+ehrsid+ 'from file '+uploaded_file.filename+' posted successfully')
                    yourresults=f"EHR {ehrid} created.\nEHR_STATUS {ehrsid} posted successfully.\nstatus_code={msg['status_code']} \n \
                    headers={msg['headers']}"
                else:
                    yourresults=f"EHR creation failure.\nstatus_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"
                    insertlogline('Post EHR: ehr posting failure')
                    insertlogline('Post EHR_STATUS: EHR_STATUS from file '+uploaded_file.filename+' posting failure')
                return render_template('pehrstatus.html',yourresults=yourresults,status=status,compjson=compjson)
            else:
                yourresults='Please choose a file first'
                return render_template('pehrstatus.html',yourresults=yourresults,status=status,compjson=compjson)
        else:
            return render_template('pehrstatus.html',yourresults=yourresults,status=status,compjson=compjson)



    @app.route("/gehrstatus.html",methods=["GET"])
    #get ehr_status
    def gehrstatus():
        global hostname,port,username,password,auth,nodename
        compjson=""
        status='failed'
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastehrid
        if request.args.get("fform1")=="Submit":
            outtype=request.args.get("outtype","") 
            eid=request.args.get("ename","")
            if outtype=='VAT':
                vat=request.args.get("vat","")
                vid=''
            else: # outtype=='VBV':
                vat=''
                vid=request.args.get("vid","")
            app.logger.debug(f'outtype={outtype} eid={eid} vat={vat} vid={vid}')
            if(eid==""):
                return render_template('gehrstatus.html',lastehr=lastehrid,compjson=compjson)
            msg=ehrbase_routines.getehrstatus(client,auth,hostname,port,username,password,eid,outtype,vat,vid)
            if(msg['status']=="success"):
                status='success'
                compjson=msg['text']
                ehrsid=json.loads(compjson)['uid']['value']
                if outtype=='VAT':
                    insertlogline('Get EHR_STATUS at time: EHR_STATUS '+ehrsid+' from ehrid='+eid+' at time='+vat+' retrieved successfully')
                    yourresults=f"EHR_STATUS at time retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\nEHR_STATUS_UID={ehrsid}\n headers={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get EHR_STATUS by version: EHR_STATUS '+ehrsid+' from ehrid='+eid+' by version retrieved successfully')
                    yourresults=f"EHR_STATUS by version retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\n EHR_STATUS_UID={ehrsid}\n headers={msg['headers']}"
                lastehrid=eid
            else:
                status='failed'                  
                if outtype=='VAT':
                    insertlogline('Get EHR_STATUS at time: EHR_STATUS from ehrid='+eid+' at time='+vat+' retrieval failure')
                    yourresults=f"EHR_STATUS at time retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\n \n headers={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get EHR_STATUS by version: EHR_STATUS '+vid+' from ehrid='+eid+' by version retrieval failure')
                    yourresults=f"EHR_STATUS by version retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\n versionUID={vid}\n headers={msg['headers']}"    
            return render_template('gehrstatus.html',yourresults=yourresults,
                    lastehr=lastehrid,compjson=compjson,status=status)
        else:
            return render_template('gehrstatus.html',lastehr=lastehrid,status=status,compjson=compjson)

    @app.route("/gehrstatusversioned.html",methods=["GET"])
    #get ehr_status versioned
    def gehrstatusversioned():
        global hostname,port,username,password,auth,nodename
        compjson=""
        status='failed'
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastehrid
        if request.args.get("fform1")=="Submit":
            outtype=request.args.get("outtype","") 
            eid=request.args.get("ename","")
            if outtype=='INFO' or outtype=='REVHIST':
                vid=''
                vat=''
            elif outtype=='VAT':
                vat=request.args.get("vat","")
                vid=''
            else: # outtype=='VBV':
                vat=''
                vid=request.args.get("vid","")
            app.logger.debug(f'outtype={outtype} eid={eid} vat={vat} vid={vid}')
            if(eid==""):
                return render_template('gehrstatusversioned.html',lastehr=lastehrid,compjson=compjson)
            msg=ehrbase_routines.getehrstatusversioned(client,auth,hostname,port,username,password,eid,outtype,vat,vid)
            if(msg['status']=="success"):
                status='success'
                compjson=msg['text']
                if outtype!='REVHIST':
                    ehrsid=json.loads(compjson)['uid']['value']
                if outtype=='INFO':
                    insertlogline('Get EHR_STATUS Versioned info: EHR_STATUS '+ehrsid+' from ehrid='+eid+' at time='+vat+' retrieved successfully')
                    yourresults=f"EHR_STATUS Versioned info retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\nEHR_STATUS_UID={ehrsid}\n headers={msg['headers']}" 
                elif outtype=='REVHIST':
                    insertlogline('Get EHR_STATUS Versioned revision history: EHR_STATUS from ehrid='+eid+' at time='+vat+' retrieved successfully')
                    yourresults=f"EHR_STATUS Versioned revision history retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\nheaders={msg['headers']}"     
                elif outtype=='VAT':
                    insertlogline('Get EHR_STATUS Versioned at time: EHR_STATUS '+ehrsid+' from ehrid='+eid+' at time='+vat+' retrieved successfully')
                    yourresults=f"EHR_STATUS Versioned at time retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\nEHR_STATUS_UID={ehrsid}\n headers={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get EHR_STATUS Versioned by version: EHR_STATUS '+ehrsid+' from ehrid='+eid+' by version retrieved successfully')
                    yourresults=f"EHR_STATUS Versioned by version retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid}\n EHR_STATUS_UID={ehrsid}\n headers={msg['headers']}"
                lastehrid=eid
            else:
                status='failed'
                if outtype=='INFO':
                    insertlogline('Get EHR_STATUS Versioned info: EHR_STATUS from ehrid='+eid+' at time='+vat+' retrieval failure')
                    yourresults=f"EHR_STATUS Versioned info retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\nheaders={msg['headers']}" 
                elif outtype=='REVHIST':
                    insertlogline('Get EHR_STATUS Versioned revision history: EHR_STATUS from ehrid='+eid+' at time='+vat+' retrieval failure')
                    yourresults=f"EHR_STATUS Versioned revision history retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\nheaders={msg['headers']}"
                elif outtype=='VAT':
                    insertlogline('Get EHR_STATUS Versioned at time: EHR_STATUS from ehrid='+eid+' at time='+vat+' retrieval failure')
                    yourresults=f"EHR_STATUS at time retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\nheaders={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get EHR_STATUS Versioned by version: EHR_STATUS '+vid+' from ehrid='+eid+' by version retrieval failure')
                    yourresults=f"EHR_STATUS by version retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid}\n versionUID={vid}\n headers={msg['headers']}"    
            return render_template('gehrstatusversioned.html',yourresults=yourresults,
                    lastehr=lastehrid,compjson=compjson,status=status)
        else:
            return render_template('gehrstatusversioned.html',lastehr=lastehrid,status=status,compjson=compjson)

    @app.route("/uehrstatus.html",methods=["GET","POST"])
    #update ehrstatus 
    def uehrstatus():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        compjson=""
        status='failure'
        global lastehrid,filename,uploaded_file,comp
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            app.logger.debug(f'uploaded filename={filename}')
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                comp=uploaded_file.read()
                return render_template('uehrstatus.html',yourfile=f"you have chosen {filename}",laste=lastehrid,compjson=compjson,status=status)
            else:
                yourresults="Please, choose the file first"
                return render_template('uehrstatus.html',yourresults=yourresults,laste=lastehrid,compjson=compjson,status=status)                
        else:
            if request.args.get("fform1")=="Submit":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('uehrstatus.html',yourresults=yourresults,laste=lastehrid,compjson=compjson,status=status)
                filetype=request.args.get("filetype","")
                eid=request.args.get("ename","")
                vid=request.args.get("vid","")
                if(eid=="" or vid==""):
                    return render_template('uehrstatus.html',yourfile=f"you have chosen {filename}",laste=lastehrid,compjson=compjson,status=status)
                if len(vid.split('::'))==1:
                    return render_template('uehrstatus.html',yourfile=f"you have chosen {filename}",laste=lastehrid,compjson=compjson,status=status)
                msg=ehrbase_routines.updateehrstatus(client,auth,hostname,port,username,password,comp,eid,vid)
                if(msg['status']=="success"):
                    status='success'
                    compjson=msg['text']
                    ehrsid=json.loads(compjson)['uid']['value']
                    yourresults=f"EHR_STATUS updated successfully.\n status_code={msg['status_code']} new versionuid={ehrsid}\n text={msg['text']}\n headers={msg['headers']}"
                    insertlogline('Put EHR_STATUS: EHR_STATUS (newid='+vid+') updated successfully to '+ehrsid)
                else:
                    yourresults=f"EHR_STATUS update failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
                    insertlogline('Put EHR_STATUS: EHR_STATUS '+vid+' from file '+filename+'  updating failure')
                return render_template('uehrstatus.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,laste=lastehrid,compjson=compjson,status=status)        
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('uehrstatus.html',yourfile="",laste=lastehrid,status=status,compjson=compjson)
                else:
                    return render_template('uehrstatus.html',yourfile=f"you have chosen {filename}",laste=lastehrid,status=status,compjson=compjson)

    @app.route("/gdir.html",methods=["GET"])
    #get directory FOLDER
    def gdir():
        global hostname,port,username,password,auth,nodename,lastehrid
        compxml=""
        compjson=""
        status='failed'
        yourresults=''
        myformat="JSON"
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        if request.args.get("fform1")=="Submit":
            outtype=request.args.get("outtype","") 
            eid=request.args.get("ename","")
            path=request.args.get("path","")
            filetype=request.args.get("filetype","")
            myformat=filetype
            if outtype=='VAT':
                vat=request.args.get("vat","")
                vid=''
            else: # outtype=='VBV':
                vat=''
                vid=request.args.get("vid","")
            app.logger.debug(f'outtype={outtype} eid={eid} path={path} vat={vat} vid={vid}')
            if(eid==""):
                return render_template('gdir.html',lastehr=lastehrid,status=status,compxml=compxml,yourresults=yourresults,format=myformat)
            msg=ehrbase_routines.getdir(client,auth,hostname,port,username,password,eid,outtype,vat,vid,path,filetype)
            if(msg['status']=='success'):
                status='success'
                if 'xml' in msg:
                    compxml=msg['xml']
                else:
                    compjson=msg['json']
                if outtype=='VAT':
                    dirid=msg['headers']['ETag']
                    insertlogline('Get Directory FOLDER at time:Directory FOLDER '+dirid+' for ehr='+eid+' retrieved successfully at time='+vat+' path='+path+' format='+myformat)
                    yourresults=f"Directory FOLDER {dirid} retrieved successfully format={myformat}\n \
                time={vat}\n \
                path={path}\n \
                ehr={eid}\nstatus_code={msg['status_code']} \n \
                headers={msg['headers']}"
                else:
                    insertlogline('Get Directory FOLDER by version:Directory FOLDER '+vid+' for ehr='+eid+' retrieved successfully path='+path+' format='+myformat)
                    yourresults=f"Directory FOLDER by version {vid} retrieved successfully format={myformat}\n \
                path={path} \n \
                ehr={eid}\nstatus_code={msg['status_code']} \n \
                headers={msg['headers']}"                    
            else:
                if outtype=='VAT':
                    yourresults=f"Get Directory FOLDER at time retrieval failure.\nstatus_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}\n time={vat} \n path={path}\n ehrid={eid}\nformat={myformat}"
                    insertlogline('Get Directory FOLDER at time:Directory FOLDER retrieving failure for ehr='+eid+' at time='+vat+' path='+path)
                else:
                    yourresults=f"Get Directory FOLDER by version retrieval failure.\nstatus_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}\n version={vid} \n path={path}\n ehrid={eid}\nformat={myformat}"
                    insertlogline('Get Directory FOLDER by version:Directory FOLDER retrieving failure for ehr='+eid+' versionid='+vid+' path='+path)
            return render_template('gdir.html',yourresults=yourresults,lastehr=lastehrid,status=status,compxml=compxml,compjson=compjson,format=myformat)
        else:
            return render_template('gdir.html',lastehr=lastehrid,yourresults=yourresults,status=status,compxml=compxml,compjson=compjson,format=myformat)

    @app.route("/dfolder.html",methods=["GET"])
    #delete directory FOLDER (admin)
    def dfolder():
        global hostname,port,adusername,adpassword,adauth,nodename,lastehrid
        yourresults=''
        if(hostname=="" or port=="" or adusername=="" or adpassword=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        if request.args.get("fform1")=="Submit":
            eid=request.args.get("ename","")
            vid=request.args.get("vid","")
            if(eid=="" or vid==""):
                return render_template('dfolder.html',lastehr=lastehrid,yourresults=yourresults)
            vid=vid.split('::')[0]
            msg=ehrbase_routines.delfolder(client,adauth,hostname,port,adusername,adpassword,eid,vid)
            if(msg['status']=='success'):
                insertlogline('Delete Directory FOLDER (admin):Directory FOLDER '+vid+' for ehr='+eid+' deleted successfully')
                yourresults=f"Directory FOLDER {vid} deleted successfully\n \
                ehr={eid}\nstatus_code={msg['status_code']} \nheaders={msg['headers']}"       
            else:
                yourresults=f"Delete Directory FOLDER\nstatus_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}\nehrid={eid}"
                insertlogline('Delete Directory FOLDER (admin):Directory FOLDER deleting failure for ehr='+eid+' versionUid='+vid)
            return render_template('dfolder.html',yourresults=yourresults,lastehr=lastehrid)
        else:
            return render_template('dfolder.html',lastehr=lastehrid,yourresults=yourresults)


    @app.route("/ddir.html",methods=["GET"])
    #delete directory FOLDER
    def ddir():
        global hostname,port,username,password,auth,nodename,lastehrid
        yourresults=''
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        if request.args.get("fform1")=="Submit":
            eid=request.args.get("ename","")
            vid=request.args.get("vid","")
            if(eid=="" or vid==""):
                return render_template('ddir.html',lastehr=lastehrid,yourresults=yourresults)
            msg=ehrbase_routines.deldir(client,auth,hostname,port,username,password,eid,vid)
            if(msg['status']=='success'):
                insertlogline('Delete Directory FOLDER:Directory FOLDER '+vid+' for ehr='+eid+' deleted successfully')
                yourresults=f"Directory FOLDER {vid} deleted succcessfully\n \
                ehr={eid}\nstatus_code={msg['status_code']} \nheaders={msg['headers']}"       
            else:
                yourresults=f"Delete Directory FOLDER\nstatus_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}\nehrid={eid}"
                insertlogline('Delete Directory FOLDER:Directory FOLDER deleting failure for ehr='+eid+' versionUid='+vid)
            return render_template('ddir.html',yourresults=yourresults,lastehr=lastehrid)
        else:
            return render_template('ddir.html',lastehr=lastehrid,yourresults=yourresults)


    @app.route("/pdir.html",methods=['GET', 'POST'])
    #post directory folder
    def pdir():
        global hostname,port,username,password,auth,nodename,filename,uploaded_file,dir
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))    
        yourresults=""
        compxml=''
        compjson=''
        status='failure'
        myformat='JSON'
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                dir=uploaded_file.read()
                return render_template('pdir.html',yourfile=f"you have chosen {filename}",laste=lastehrid,status=status,format=myformat)
            else:
                yourresults='Please choose a file first'
                return render_template('pdir.html',yourresults=yourresults,status=status)
        else:
            if request.args.get("fform1")=="Submit":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('pdir.html',yourresults=yourresults,laste=lastehrid,status=status,format=myformat)
                eid=request.args.get("ename","")
                filetype=request.args.get("filetype","")
                myformat=filetype
                if(eid==""):
                    return render_template('pdir.html',yourfile=f"you have chosen {filename}",laste=lastehrid,format=myformat)
                msg=ehrbase_routines.postdir(client,auth,hostname,port,username,password,eid,dir,filetype)
                if(msg['status']=='success'):
                    status='success'
                    if 'xml' in msg:
                        compxml=msg['xml']
                        dirid=msg['headers']['ETag']
                    else:
                        compjson=msg['json']
                        dirid=json.loads(compjson)['uid']['value']
                    insertlogline('Post Directory FOLDER:Directory FOLDER '+dirid+' for ehr='+eid+' from file '+filename+' posted successfully')
                    yourresults=f"directory FOLDER {dirid} created\n \
                    ehr={eid}\nstatus_code={msg['status_code']} \n \
                    headers={msg['headers']}"
                else:
                    yourresults=f"directory FOLDER for EHR={eid} creation failure\nstatus_code={msg['status_code']}\nheaders={msg['headers']}\ntext={msg['text']}"
                    insertlogline('Post Directory FOLDER: Directory FOLDER EHR='+eid+' from file '+filename+' posting failure')                                     
                return render_template('pdir.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,status=status,lastehr=lastehrid,compxml=compxml,compjson=compjson,format=myformat)
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('pdir.html',yourfile="",laste=lastehrid,status=status,format=myformat)
                else:
                    return render_template('pdir.html',yourfile=f"you have chosen {filename}",status=status,laste=lastehrid,compxml=compxml,compjson=compjson,format=myformat)

    @app.route("/udir.html",methods=['GET', 'POST'])
    #update directory folder
    def udir():
        global hostname,port,username,password,auth,nodename,filename,dir,uploaded_file
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))    
        yourresults=""
        compxml=''
        compjson=''
        status='failure'
        myformat='JSON'
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                dir=uploaded_file.read()
                return render_template('udir.html',yourfile=f"you have chosen {filename}",laste=lastehrid,status=status,format=myformat)
            else:
                yourresults='Please choose a file first'
                return render_template('udir.html',yourresults=yourresults,status=status)
        else:
            if request.args.get("fform1")=="Submit":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('udir.html',yourresults=yourresults,laste=lastehrid,status=status)
                eid=request.args.get("ename","")
                vid=request.args.get("vid","")
                filetype=request.args.get("filetype","")
                if filetype=='XML':
                    myformat='XML'
                else:
                    myformat='JSON'             
                if(eid==""):
                    return render_template('udir.html',yourfile=f"you have chosen {filename}",laste=lastehrid,format=myformat)
                msg=ehrbase_routines.updatedir(client,auth,hostname,port,username,password,eid,vid,dir,filetype)
                if(msg['status']=='success'):
                    status='success'
                    if 'xml' in msg:
                        compxml=msg['xml']
                        dirid=msg['headers']['ETag']
                    else:
                        compjson=msg['json']
                        dirid=json.loads(compjson)['uid']['value']
                    insertlogline('Put Directory FOLDER:Directory FOLDER (new='+dirid+') for ehr='+eid+' updated successfully')
                    yourresults=f"Directory FOLDER (new={dirid}) updated successfully\n \
                    ehr={eid}\nstatus_code={msg['status_code']} \n \
                    headers={msg['headers']}"
                else:
                    yourresults=f"Directory FOLDER for EHR={eid} updating failure\nversionuid={vid}\nstatus_code={msg['status_code']}\nheaders={msg['headers']}\ntext={msg['text']}"
                    insertlogline('Put Directory FOLDER:Directory FOLDER '+vid+' ehr='+eid+' from file '+uploaded_file.filename+' updating failure')
                return render_template('udir.html',yourresults=yourresults,status=status,compxml=compxml,compjson=compjson,format=myformat)
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('udir.html',yourfile="",laste=lastehrid,status=status,format=myformat)
                else:
                    return render_template('udir.html',yourfile=f"you have chosen {filename}",status=status,laste=lastehrid,compxml=compxml,format=myformat)



    @app.route("/pcomp.html",methods=["GET","POST"])
    #post composition
    def pcomp():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        global lastehrid,lastcompositionid,filename,uploaded_file,comp
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'pcompbase.html','pcomp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            app.logger.debug(f'uploaded filename={filename}')
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                comp=uploaded_file.read()
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
            else:
                yourresults='Please choose a file first'
                return render_template('pcomp.html',yourresults=yourresults,laste=lastehrid)
        else:
            if request.args.get("fform1")=="POST THE COMPOSITION":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('pcomp.html',yourresults=yourresults,laste=lastehrid)
                filetype=request.args.get("filetype","")
                eid=request.args.get("ename","")
                tid=request.args.get("tname","")
                check=request.args.get("check","")
                checkresults=""
                checkinfo=""
                if(eid=="" or tid==""):
                    return render_template('pcomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
                msg=ehrbase_routines.postcomp(client,auth,hostname,port,username,password,comp,eid,tid,filetype,check)
                if(msg['status']=="success"):
                    yourresults=f"Composition inserted successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                    lastcompositionid=msg['compositionid']
                    insertlogline('Post Composition: composition '+lastcompositionid+' for ehr='+eid+' from file '+filename+' posted successfully')
                    if(check=="Yes"):
                        checkresults=msg['check']
                        checkinfo=msg['checkinfo']
                else:
                    yourresults=f"Composition insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
                    insertlogline('Post Composition: composition from file '+filename+' for ehr='+eid+' posting failure')
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,laste=lastehrid,checkresults=checkresults,checkinfo=checkinfo)        
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('pcomp.html',yourfile="",laste=lastehrid)
                else:
                    return render_template('pcomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)

    @app.route("/ucomp.html",methods=["GET","POST"])
    #update composition 
    def ucomp():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        global lastehrid,lastcompositionid,filename,uploaded_file,comp
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'ucompbase.html','ucomp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            app.logger.debug(f'uploaded filename={filename}')
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                comp=uploaded_file.read()
                return render_template('ucomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
            else:
                yourresults='Please choose a file first'
                return render_template('ucomp.html',yourfile="",laste=lastehrid,yourresults=yourresults)
        else:
            if request.args.get("fform1")=="POST THE COMPOSITION":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('ucomp.html',yourresults=yourresults,laste=lastehrid)
                filetype=request.args.get("filetype","")
                eid=request.args.get("ename","")
                tid=request.args.get("tname","")
                compid=request.args.get("cname","")
                check=request.args.get("check","")
                checkresults=""
                checkinfo=""
                if(eid=="" or tid=="" or compid==""):
                    return render_template('ucomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
                if len(compid.split('::'))==1:
                    return render_template('ucomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
                msg=ehrbase_routines.updatecomp(client,auth,hostname,port,username,password,comp,eid,tid,compid,filetype,check)
                if(msg['status']=="success"):
                    yourresults=f"Composition updated successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                    lastcompositionid=msg['compositionid']
                    insertlogline('Put Composition: composition (newid='+lastcompositionid+') updated successfully')
                    if(check=="Yes"):
                        checkresults=msg['check']
                        checkinfo=msg['checkinfo']
                else:
                    yourresults=f"Composition update failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
                    insertlogline('Put Composition: composition {compid} from file '+filename+'  updating failure')
                return render_template('ucomp.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,laste=lastehrid,checkresults=checkresults,checkinfo=checkinfo)        
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('ucomp.html',yourfile="",laste=lastehrid)
                else:
                    return render_template('ucomp.html',yourfile=f"you have chosen {filename}",laste=lastehrid)


    @app.route("/gcomp.html",methods=["GET"])
    #get composition
    def gcomp():
        global hostname,port,username,password,auth,nodename
        compflat="{}"
        compxml=""
        compjson=""
        status='failed'
        myformat='xml'
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastcompositionid,lastehrid
        if request.args.get("fform1")=="Submit":
            filetype=request.args.get("filetype","") 
            compid=request.args.get("cname","") 
            eid=request.args.get("ename","") 
            app.logger.debug(f'filetype={filetype} compid={compid} eid={eid}')
            if(compid=="" or eid==""):
                return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat)
            msg=ehrbase_routines.getcomp(client,auth,hostname,port,username,password,compid,eid,filetype)
            # compjson=""
            # compxml=""
            if(msg['status']=="success"):
                status='success'
                if('xml' in msg):
                    myformat='xml'
                    compxml=msg['xml']
                elif('flat' in msg):
                    myformat='flat'
                    compflat=msg['flat']
                elif('structured' in msg):
                    myformat='structured'
                    compjson=msg['structured']            
                else:
                    myformat='json'
                    compjson=msg['json']
                ehrid=msg["ehrid"]
                compositionid=msg['compositionid']
                insertlogline('Get Composition: composition '+compositionid+' from ehrid='+ehrid+' retrieved successfully in format '+myformat)
                yourresults=f"Composition retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={msg['ehrid']} versionUID={msg['compositionid']}\n headers={msg['headers']}"
                lastehrid=ehrid
                lastcompositionid=compositionid
            else:
                status='failed'
                ehrid=msg["ehrid"]
                compositionid=msg['compositionid']
                if(filetype=='XML'):
                    myformat='xml'
                elif(filetype=='JSON'):
                    myformat='json'
                elif(filetype=='STRUCTURED'):
                    myformat='structured'
                else:
                    myformat='flat'
                insertlogline('Get Composition: composition '+compid+' from ehrid='+ehrid+' retrieval failure in format '+myformat)
                yourresults=f"Composition retrieval failure. status_code={msg['status_code']} \n \
                    headers={msg['headers']}\n text={msg['text']}"        
            return render_template('gcomp.html',yourresults=yourresults,last=lastcompositionid,
                    lastehr=lastehrid,compxml=compxml,compjson=compjson,compflat=compflat,status=status,format=myformat)
        else:
            return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat,status=status,format=myformat)

    @app.route("/gcompversioned.html",methods=["GET"])
    #get composition versioned
    def gcompversioned():
        global hostname,port,username,password,auth,nodename
        compjson=""
        status='failed'
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastcompositionid,lastehrid
        if request.args.get("fform1")=="Submit":
            outtype=request.args.get("outtype","") 
            compid=request.args.get("cname","") 
            eid=request.args.get("ename","")
            if outtype=='INFO' or outtype=='REVHIST':
                vid=''
                vat=''
            elif outtype=='VAT':
                vat=request.args.get("vat","")
                vid=''
            elif outtype=='VBV':
                vat=''
                vid=request.args.get("vid","")
            app.logger.debug(f'outtype={outtype} compid={compid} eid={eid} vat={vat} vid={vid}')
            if(compid=="" or eid==""):
                return render_template('gcompversioned.html',lastc=lastcompositionid,lastehr=lastehrid,compjson=compjson)
            compid=compid.split('::')[0]
            msg=ehrbase_routines.getcompversioned(client,auth,hostname,port,username,password,compid,eid,outtype,vat,vid)
            if(msg['status']=="success"):
                status='success'
                compjson=msg['text']
                if outtype=='INFO':
                    insertlogline('Get Composition Versioned info: composition '+compid+' from ehrid='+eid+' info retrieved successfully')
                    yourresults=f"Composition Versioned info retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']}"
                elif outtype=='REVHIST':
                    insertlogline('Get Composition Versioned revision history: composition '+compid+' from ehrid='+eid+' revision history retrieved successfully')
                    yourresults=f"Composition Versioned revision history retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']}"
                elif outtype=='VAT':
                    insertlogline('Get Composition Versioned at time: composition '+compid+' from ehrid='+eid+' at time='+vat+' retrieved successfully')
                    yourresults=f"Composition Versioned at time retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get Composition Versioned by version: composition '+compid+' from ehrid='+eid+' by version retrieved successfully')
                    yourresults=f"Composition Versioned by version retrieved successfully. status_code={msg['status_code']} \n \
                EHRID={eid} versionUID={vid}\n headers={msg['headers']}"
                lastehrid=eid
                lastcompositionid=compid
            else:
                status='failed'                  
                if outtype=='INFO':
                    insertlogline('Get Composition Versioned info: composition '+compid+' from ehrid='+eid+' info retrieval failure')
                    yourresults=f"Composition Versioned info retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']}"
                elif outtype=='REVHIST':
                    insertlogline('Get Composition Versioned revision history: composition '+compid+' from ehrid='+eid+' revision history retrieval failure')
                    yourresults=f"Composition Versioned revision history retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']}"
                elif outtype=='VAT':
                    insertlogline('Get Composition Versioned at time: composition '+compid+' from ehrid='+eid+' at time='+vat+' retrieval failure')
                    yourresults=f"Composition Versioned at time retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid} compositionid={compid}\n headers={msg['headers']} time={vat}"
                else: #outtype=='VBV'
                    insertlogline('Get Composition Versioned by version: composition '+compid+' from ehrid='+eid+' by version retrieval failure')
                    yourresults=f"Composition Versioned by version retrieval failure. status_code={msg['status_code']} \n \
                EHRID={eid} versionUID={vid}\n headers={msg['headers']}"    
            return render_template('gcompversioned.html',yourresults=yourresults,lastc=lastcompositionid,
                    lastehr=lastehrid,compjson=compjson,status=status)
        else:
            return render_template('gcompversioned.html',lastc=lastcompositionid,lastehr=lastehrid,status=status,compjson=compjson)

    @app.route("/dcompuser.html",methods=["GET"])
    #delete composition
    def dcompuser():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        status="failed"
        yourresults=''
        if request.args.get("fform1")=="Delete": 
            compid=request.args.get("cname","") 
            eid=request.args.get("ename","") 
            app.logger.debug(f'compid={compid} eid={eid}')
            if(compid=="" or eid==""): 
                return render_template('dcompuser.html')
            if len(compid.split('::'))==1:
                return render_template('dcompuser.html',yourresults='Please use a Composition VersionUID not an ID')
            msg=ehrbase_routines.delcompuser(client,auth,hostname,port,username,password,compid,eid)
            if(msg['status']=="success"):
                yourresults=f"Composition deleted successfully. \nstatus_code={msg['status_code']} \nversionUid={compid} \nehrid={eid}"
                status='success'
                insertlogline('Delete Composition: composition '+compid+' from ehr='+eid+' deleted successfully')
            else:
                yourresults=f"Composition deletion failure. \nstatus_code={msg['status_code']} \nheaders={msg['headers']} \ntext={msg['text']}"        
                insertlogline('Delete Composition: composition '+compid+' from ehr='+eid+' deletion failure')
            return render_template('dcompuser.html',yourresults=yourresults)
        else:
            return render_template('dcompuser.html')
        
    @app.route("/dcomp.html",methods=["GET"])
    #delete composition (admin)
    def dcomp():
        global hostname,port,adusername,adpassword,auth,adauth,nodename
        if(hostname=="" or port=="" or adusername=="" or adpassword=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        status="failed"
        yourresults=''
        if request.args.get("fform1")=="Delete": 
            compid=request.args.get("cname","") 
            eid=request.args.get("ename","") 
            app.logger.debug(f'compid={compid} eid={eid}')
            if(compid=="" or eid==""): 
                return render_template('dcomp.html')
            compid=compid.split('::')[0]
            msg=ehrbase_routines.delcomp(client,adauth,hostname,port,adusername,adpassword,compid,eid)
            if(msg['status']=="success"):
                yourresults=f"Composition deleted successfully. \nstatus_code={msg['status_code']} \nid={compid} \nehrid={eid}"
                status='success'
                insertlogline('Delete Composition (admin): composition '+compid+' from ehr='+eid+' deleted successfully. ADMIN Method')
            else:
                yourresults=f"Composition deletion failure. \nstatus_code={msg['status_code']} \nheaders={msg['headers']} \ntext={msg['text']}"        
                insertlogline('Delete Composition (admin): composition '+compid+' from ehr='+eid+' deletion failure. ADMIN Method')
            return render_template('dcomp.html',yourresults=yourresults)
        else:
            return render_template('dcomp.html')

    @app.route("/gcontrib.html",methods=["GET"])
    #get contribution
    def gcontrib():
        global hostname,port,username,password,auth,nodename,lastehrid
        compjson=""
        status='failed'
        yourresults=''
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        if request.args.get("fform1")=="Submit": 
            eid=request.args.get("ename","")
            vid=request.args.get("vid","")
            app.logger.debug(f'eid={eid} vid={vid}')
            if(eid==""):
                return render_template('gcontrib.html',lastehr=lastehrid,status=status,yourresults=yourresults)
            msg=ehrbase_routines.getcontrib(client,auth,hostname,port,username,password,eid,vid)
            if(msg['status']=='success'):
                status='success'
                compjson=msg['json']
                insertlogline('Get Contribution by id:Contribution '+vid+' for ehr='+eid+' retrieved successfully')
                yourresults=f"Contribution {vid} retrieved successfully\n \
                ehr={eid}\nstatus_code={msg['status_code']} \n \
                headers={msg['headers']}"                  
            else:
                yourresults=f"Get Contribution by id retrieval failure.\nstatus_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}\ncontribution_id={vid}\nehrid={eid}"
                insertlogline('Get Contribution by id:Contribution retrieving failure for ehr='+eid+' contribution_id='+vid)
            return render_template('gcontrib.html',yourresults=yourresults,lastehr=lastehrid,status=status,compjson=compjson)
        else:
            return render_template('gcontrib.html',lastehr=lastehrid,yourresults=yourresults,status=status,compjson=compjson)




    @app.route("/pcontrib.html",methods=['GET', 'POST'])
    #post contribution
    def pcontrib():
        global hostname,port,username,password,auth,nodename,filename,uploaded_file,contrib
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))    
        yourresults=""
        compjson=''
        status='failure'
        if request.method == 'POST':
            uploaded_file = request.files['file']
            filename=uploaded_file.filename
            if filename != '':
                filename=secure_filename(filename)
                uploaded_file.stream.seek(0)
                contrib=uploaded_file.read()
                return render_template('pcontrib.html',yourfile=f"you have chosen {filename}",laste=lastehrid,status=status)
            else:
                yourresults='Please choose a file first'
                return render_template('pcontrib.html',yourresults=yourresults,status=status)
        else:
            if request.args.get("fform1")=="Submit":
                if(filename==""):
                    yourresults="Please, choose the file first"
                    return render_template('pcontrib.html',yourresults=yourresults,laste=lastehrid,status=status)
                eid=request.args.get("ename","")
                if(eid==""):
                    return render_template('pcontrib.html',yourfile=f"you have chosen {filename}",laste=lastehrid)
                msg=ehrbase_routines.postcontrib(client,auth,hostname,port,username,password,eid,contrib)
                if(msg['status']=='success'):
                    status='success'
                    compjson=msg['json']
                    contrid=msg['headers']['ETag']
                    insertlogline('Post Contribution: Contribution '+contrid+' for ehr='+eid+' from file '+filename+' posted successfully')
                    yourresults=f"Contribution created\n \
                    contribution_id={contrid}\n \
                    ehr={eid}\nstatus_code={msg['status_code']} \n \
                    headers={msg['headers']}"
                else:
                    yourresults=f"Contribution for EHR={eid} creation failure\nstatus_code={msg['status_code']}\nheaders={msg['headers']}\ntext={msg['text']}"
                    insertlogline('Post Contribution: Contribution for EHR='+eid+' from file '+filename+' posting failure')                                     
                return render_template('pcontrib.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,status=status,lastehr=lastehrid,compjson=compjson)
            else:
                if("filename" not in vars()):
                    filename=""
                    return render_template('pcontrib.html',yourfile="",laste=lastehrid,status=status)
                else:
                    return render_template('pcontrib.html',yourfile=f"you have chosen {filename}",status=status,laste=lastehrid,compjson=compjson)





    @app.route("/paql.html",methods=["GET"])
    #post aql query
    def paql():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        aqltext={}
        yourresults=''
        if request.args.get("pippo")=="Store query":
            aqltext=request.args.get("aqltext","")
            version=request.args.get("version","")
            qtype=request.args.get("qtype","")
            qname=request.args.get("nquery","")
            app.logger.debug(f'aqltext={aqltext} ') 
            if(aqltext=="" or qname==""):
                app.logger.warning("no text in aql")
                render_template('paql.html',aqltext=aqltext)
            reversed_nodename=".".join(reversed(nodename.split(".")))
            qname=reversed_nodename+"::"+qname+"/"
            app.logger.info(aqltext)
            msg=ehrbase_routines.postaql(client,auth,hostname,port,username,password,aqltext,qname,version,qtype)
            if(msg['status']=="success"):
                insertlogline('Post AQL Query: query '+qname+' version='+version+' type='+qtype+' posted successfully')
                yourresults=f"Query {msg['name']} version={msg['version']} inserted successfully\nstatus_code={msg['status_code']}\ntext={msg['text']}\n,headers={msg['headers']}"
            else:
                insertlogline('Post AQL Query: query '+qname+' version='+version+' type='+qtype+' posting failure')
                yourresults=f"Query insertion failure\nstatus_code={msg['status_code']}\nheaders={msg['headers']}\ntext={msg['text']}"               
            return render_template('paql.html',yourresults=yourresults,aqltext=aqltext)
        else: 
            return render_template('paql.html',aqltext=aqltext,yourresults=yourresults)

    @app.route("/gaql.html",methods=["GET"])
    #get aql query
    def gaql():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        mymsg=ehrbase_routines.createPageFromBase4querylist(client,auth,hostname,port,username,password,'gaqlbase.html','gaql.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        aql=""
        aqlpresent='false'
        yourresults=""
        if request.args.get("pippo")=="Get query":
            qdata=request.args.get("qdata","")
            if "$v" not in qdata: #no query choosable
                yourresults=f"No queries available"
                return render_template('gaql.html',yourresults=yourresults,aql=aql,aqlpresent=aqlpresent)        
            qdatas=qdata.split('$v')
            qname=qdatas[0]
            version=qdatas[1]
            #reversed_nodename=".".join(reversed(nodename.split(".")))
            #if(qname != "" and "::" not in qname):
            #    qname=reversed_nodename+"::"+qname+"/"
            msg=ehrbase_routines.getaql(client,auth,hostname,port,username,password,qname,version)
            if(msg['status']=="success"):
                insertlogline('Get AQL Query: query '+qname+' version'+version+' retrieved successfully')
                yourresults=f"Query retrieved successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
                if('aql' in msg):
                    aqlpresent='true'
                    aql=msg['aql']
            else:
                insertlogline('Get AQL Query: query '+qname+' version='+version+' retrieval failure')
                yourresults=f"Query retrieval failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
            return render_template('gaql.html',aql=aql,aqlpresent=aqlpresent,yourresults=yourresults)
        elif request.args.get("pippo2")=="Get query list":
            yourresults=str(mymsg['status'])+ " "+ str(mymsg['status_code']) +"\n"+ \
                        str(mymsg['text'])
            aqlpresent='false'
            aql=""
            return render_template('gaql.html',aql=aql,aqlpresent=aqlpresent,yourresults=yourresults)
        else: 
            return render_template('gaql.html',aql=aql,aqlpresent=aqlpresent,yourresults=yourresults)

    @app.route("/raql.html",methods=["GET"])
    #run aql query
    def raql():
        global hostname,port,username,password,auth,nodename,qname,version,aqltext2,lastaql
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastehrid
        resultsave='false'
        temp=""
        yourresults=""
        status='failure'
        res=''
        if("lastaql" not in locals()):
            lastaql=''
        if request.args.get("pippo")=="Run pasted query": 
            aqltext=request.args.get("aqltext","")
            qmethod=request.args.get("qmethod","")
            limit=request.args.get("limit","")
            offset=request.args.get("offset","")
            # fetch=request.args.get("fetch","")
            eid=request.args.get("ehrid","") 
            qparam=request.args.get("qparam","")
            resultsave='false'
            qname=""
            version=""
            if(aqltext==""):
                app.logger.info("no text in aql")
                render_template('raql.html',lastehr=lastehrid,resultsave=resultsave,temp=temp,res=res,status=status,lastaql=lastaql)
            else:
                lastaql=aqltext              
                aqltext=aqltext.translate({ord(ch):' ' for ch in '\n\r'})
            app.logger.info(f'AQLTEXT={aqltext}')
            msg=ehrbase_routines.runaql(client,auth,hostname,port,username,password,aqltext,qmethod,limit,offset,eid,qparam,qname,version)
            if(msg['status']=="success"):
                status='success'
                app.logger.debug(f"aqltext={aqltext} msg[text]={msg['text']} msg['status_code']={msg['status_code']} msg['headers']={msg['headers']}")
                insertlogline('Run AQL Query: pasted query run successfully')
                if msg['text'] != '':
                    app.logger.debug('f msg[text] not empty')
                    msgtext=json.loads(msg['text'])
                    if('rows' in msgtext):
                        temp=msgtext['rows']
                        res=msgtext
                        status='success'
                        if(len(temp)>0):
                            resultsave='true'    
                        else:
                            resultsave='false'
                else:
                    app.logger.debug('f msg[text] empty')
                    resultsave='false'
                    temp={}
                yourresults=f"Query run successfully.\n status_code={msg['status_code']}\n headers={msg['headers']}"
            else:
                insertlogline('Run AQL Query: pasted query run failure')
                resultsave='false'
                yourresults=f"Query run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"
            app.logger.debug(f'YR={yourresults} aqltext={aqltext} lastehrid={lastehrid} resultsave={resultsave} temp={temp}')               
            return render_template('raql.html',yourresults=yourresults,aqltext=aqltext,lastehr=lastehrid,resultsave=resultsave,temp=temp,res=res,status=status,lastaql=lastaql)
        else:
            return render_template('raql.html',lastehr=lastehrid,aqltext={},resultsave=resultsave,temp=temp,res=res,status=status,lastaql=lastaql)

    @app.route("/raqlstored.html",methods=["GET"])
    #run stored aql query
    def raqlstored():
        global hostname,port,username,password,auth,nodename,qname,version,aqltext2,myvalue,lastaql
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
        global lastehrid
        resultsave='false'
        temp=""
        yourresults=""
        status='failure'
        res=''
        myvalue='hide'
        aqltext2=''
        if("lastaql" not in locals()):
            lastaql=''
#       qname=""
#       version=""
        mymsg=ehrbase_routines.createPageFromBase4querylist(client,auth,hostname,port,username,password,'raqlbasestored.html','raqlstored.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.args.get("pippo")=="Select":
            qdata=request.args.get("qdata","")
            if "$v" not in qdata: #no query choosable
                aqltext2=f"No queries available"
                yourresults='Please select or create a query first'
                return render_template('raqlstored.html',yourresults=yourresults,lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2,res=res,status=status,myvalue=myvalue)
            else:
                qdatas=qdata.split('$v')
                qname=qdatas[0]
                version=qdatas[1]
                msg=ehrbase_routines.getaql(client,auth,hostname,port,username,password,qname,version)
                if(msg['status']=="success"):
                    insertlogline('Get AQL Query: query '+qname+' version'+version+' retrieved successfully')
                    yourresultspre=f"Query {qname} v{version} retrieved successfully"
                    #aqlpresent='true'
                    aqltext2=msg['aql']
                    lastaql=aqltext2
                    myvalue='show'
                    return render_template('raqlstored.html',yourresultspre=yourresultspre,aqltext2=aqltext2,lastehr=lastehrid,resultsave=resultsave,temp=temp,res=res,status=status,myvalue=myvalue)    
                else:
                    insertlogline('Get AQL Query: query '+qname+' version='+version+' retrieval failure')
                    yourresultspre=f"Query {qname} v{version} retrieval failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
                    myvalue='hide'
                    return render_template('raqlstored.html',yourresultspre=yourresultspre,aqltext2=aqltext2,lastehr=lastehrid,resultsave=resultsave,temp=temp,res=res,status=status,myvalue=myvalue)   
        elif(request.args.get("pippo2")=="Run"):
            app.logger.debug(f'aqltext2={aqltext2}')
            if(aqltext2 is None or aqltext2=='No queries available'):
                yourresults='Please select or create a query first'
                return render_template('raqlstored.html',yourresults=yourresults,lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2,res=res,status=status,myvalue=myvalue)
            qmethod=request.args.get("qmethod","")
            limit=request.args.get("limit","")
            aqltext2=request.args.get("aqltext","")
            lastaql=aqltext2
            #aqltext=aqltext2
            resultsave='false'
            offset=request.args.get("offset","")
            # fetch=request.args.get("fetch","")
            eid=request.args.get("ehrid","") 
            qparam=request.args.get("qparam","")
            #reversed_nodename=".".join(reversed(nodename.split(".")))
            if(aqltext2==""):
                return render_template('raqlstored.html',lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2,res=res,status=status,lastaql=lastaql,myvalue=myvalue)
            msg=ehrbase_routines.runaql(client,auth,hostname,port,username,password,aqltext2,qmethod,limit,offset,eid,qparam,qname,version)    
            if(msg['status']=="success"):
                insertlogline('Run AQL Stored Query: query '+qname+' version'+version+' run successfully')
                msgtext=json.loads(msg['text'])
                if('rows' in msgtext):
                    temp=msgtext['rows']
                    res=msgtext
                    status='success'
                    if(len(temp)>0):
                        app.logger.debug('len temp>0')
                        resultsave='true'          
                yourresults=f"Query {qname} v{version} run successfully.\n status_code={msg['status_code']}\n headers={msg['headers']}"
            else:
                insertlogline('Run AQL Query: query '+qname+' version'+version+' run failure')
                resultsave='false'
                yourresults=f"Query {qname} v{version}run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
            app.logger.debug(f'resultsave={resultsave}')
            return render_template('raqlstored.html',yourresults=yourresults,lastehr=lastehrid,aqltext2=aqltext2,resultsave=resultsave,temp=temp,res=res,status=status,myvalue=myvalue,lastaql=lastaql)
        else:
            return render_template('raqlstored.html',lastehr=lastehrid,resultsave=resultsave,temp=temp,res=res,status=status,myvalue=myvalue,aqltext2=aqltext2,lastaql=lastaql)


    @app.route("/dashboard.html",methods=["GET"])
    #show dashboard
    def dashtemp():
        return render_template('dashboard_waiting.html')

    @app.route("/dashboard_final.html",methods=["GET"])
    def dashboard():
        global hostname,port,username,password,auth,nodename,adusername,adpassword
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
            return redirect(url_for("ehrbase"))
    #    if request.args.get("pippo")=="Update":
        msg=ehrbase_routines.get_dashboard_info(client,auth,hostname,port,username,password,adauth,adusername,adpassword)

        if('success' in msg['status']):
            info=health=aql=db=gen_properties=end_properties=terminology=plugin=env={}
            parameters={}
            parameters['info']=info
            parameters['health']=health
            parameters['aql']=aql
            parameters['db']=db
            parameters['gen_properties']=gen_properties
            parameters['end_properties']=end_properties
            parameters['terminology']=terminology
            parameters['plugin']=plugin
            parameters['env']=env
            if msg['success1']:#AQL queries stored
                parameters['total_aql_queries']=msg['aql']
            if msg['success2']:#total EHRS
                parameters['total_ehrs']=msg['ehr']
            if msg['success3']:#EHRS in use, templates in use, compositions
                parameters['total_ehrs_in_use']=msg['uehr']
                parameters['total_templates_in_use']=msg['utemplate']
                parameters['total_compositions']=msg['composition']
            if msg['success4']:#total_templates
                parameters['total_templates']=msg['template']
                parameters['bar_labels']=msg['bar_label']
                parameters['bar_values']=msg['bar_value']
                parameters['bar_max']=msg['bar_max']
                parameters['pie_labels']=msg['pie_label']
                parameters['pie_values']=msg['pie_value']  
            if msg['success5']:#info
                parameters['info']=msg['info']
            if 'success6' in msg:
                if msg['success6']:
                    parameters['env']=msg['env']
                    parameters['end_properties']=msg['end_properties']
                    parameters['db']=msg["db"]
                    parameters['aql']=msg["aqlinfo"]
                    parameters['gen_properties']=msg["gen_properties"]
                    parameters['terminology']=msg["terminology"]
                    parameters['plugin']=msg["plugin"]
            if 'success7' in msg:
                if msg['success7']:
                    parameters['db']=msg["db"]
                    parameters['health']=msg['health']
            
            return render_template('dashboard.html',**parameters)
        else:
            myerror='Error. No data available\n text:'+str(msg['text'])+' headers='+str(msg['headers'])
            return render_template('dashboard.html',error=myerror)


    @app.route("/pbatch1.html",methods=["GET","POST"])
    #post batch of compositions to different ehrs
    def pbatch():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        global lastehrid,lastcompositionid,numberoffiles,uploaded_files,filenames,comps
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'pbatch1base.html','pbatch1.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))    
        if request.method == 'POST':
            uploaded_files = request.files.getlist('file')
            comps=[]
            filenameslist=[]
            for uf in uploaded_files:
                app.logger.info(f'Uploaded file: {uf.filename}')
                filenameslist.append(uf.filename)
                uf.stream.seek(0)
                composition=uf.read()
                comps.append(composition)
            filenames=",".join(filenameslist)
            numberoffiles=len(uploaded_files)    
            return render_template('pbatch1.html',yourfile=f"you have chosen {numberoffiles} files")
        else:
            if request.args.get("pippolippo")=="POST THE COMPOSITIONS":
                sidpath=""
                snamespace=""
                random=False
                inlist=False
                if(request.args.get('random')=='yes'):
                    random=True
                    if(request.args.get('inlist')=='yes'):
                        inlist=True
                else:
                    sidpath=request.args.get("sidpath","")
                    snamespace=request.args.get("snamespace","")
                    if(sidpath=="" or snamespace==""):
                        app.logger.warning("path to id or namespace not given")
                        return render_template('pbatch1.html')
                tid=request.args.get("tname","")
                filetype=request.args.get("filetype","")
                check=request.args.get("check","")  
                if(tid==""):
                    app.logger.warning("Template id not given")
                    return render_template('pbatch1.html')
                if('comps' not in locals() and 'comps' not in globals()):
                    app.logger.warning("Compositions not loaded")
                    return render_template('pbatch1.html')
                if(filetype=='XML'):
                    myformat='xml'
                elif(filetype=='JSON'):
                    myformat='json'
                else:
                    myformat='flat'    
                msg=ehrbase_routines.postbatch1(client,auth,hostname,port,username,password,uploaded_files,tid,check,sidpath,snamespace,filetype,random,comps,inlist)
                if(msg['status']=="success"):
                    yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                        +"EHRIDs=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n" 
                
                    insertlogline('Post Batch Compositions different id:'+str(numberoffiles) + ' compositions with template '+tid+' and format '+myformat+ ' posted successfully')
                    if(check=="Yes"):
                        yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                        +str(msg['csuccess'])+"/"+str(numberoffiles)+" checked successfully\n" \
                            +"EHRIDs=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                            +"filenamecheckFailed="+str(msg['filenamecheckfailed'])
                else:
                    yourresults=f"Composition insertion failure.\n" \
                            + str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                            +"EHRIDs=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                                + msg['error']
                    insertlogline('Post Batch Compositions different id:'+str(numberoffiles) + ' compositions with template '+tid+' and format '+myformat+' posting failure')            
                    if(check=="Yes"):
                        yourresults=f"Composition insertion failure.\n" \
                            + str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                            +str(msg['csuccess'])+"/"+str(numberoffiles)+" checked successfully\n" \
                            +"EHRIDs=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                            +"filenamecheckFailed="+str(msg['filenamecheckfailed']) + "\n"  \
                            + msg['error']
                return render_template('pbatch1.html',yourfile=f"you have chosen {filenames}",yourresults=yourresults)        
            else:
                if("filenames" not in locals()):
                    filenames=""
                    return render_template('pbatch1.html',yourfile="")
                else:
                    return render_template('pbatch1.html',yourfile=f"you have chosen {numberoffiles} files")


    @app.route("/pbatch2.html",methods=["GET","POST"])
    #post batch of compositions tp the same ehr
    def pbatchsameehr():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))  
        yourresults=""  
        global lastehrid,lastcompositionid,numberoffiles,uploaded_files,filenames,comps
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'pbatch2base.html','pbatch2.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))    
        if request.method == 'POST':
            uploaded_files = request.files.getlist('file')
            comps=[]
            filenameslist=[]
            for uf in uploaded_files:
                app.logger.info(f'Uploaded file: {uf.filename}')
                filenameslist.append(uf.filename)
                uf.stream.seek(0)
                composition=uf.read()
                comps.append(composition)
            filenames=",".join(filenameslist)
            numberoffiles=len(uploaded_files)   
            return render_template('pbatch2.html',yourfile=f"you have chosen {numberoffiles} files")
        else:
            if request.args.get("pippolippo")=="POST THE COMPOSITIONS":
                random=False
                eid=""
                if(request.args.get('random')=='yes'):
                    random=True
                else:
                    eid=request.args.get("eid","")
                    if(eid==""):
                        app.logger.warning("ehrid not given")
                        return render_template('pbatch2.html')
                tid=request.args.get("tname","")
                filetype=request.args.get("filetype","")
                check=request.args.get("check","")  
                if(tid==""):
                    app.logger.warning("Template id not given")
                    return render_template('pbatch2.html')
                if('comps' not in locals() and 'comps' not in globals()):
                    app.logger.warning("Compositions not loaded")
                    return render_template('pbatch2.html')
                if(filetype=='XML'):
                    myformat='xml'
                elif(filetype=='JSON'):
                    myformat='json'
                else:
                    myformat='flat'               
                msg=ehrbase_routines.postbatch2(client,auth,hostname,port,username,password,uploaded_files,tid,check,eid,filetype,random,comps)
                if(msg['status']=="success"):
                    yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                        +"EHRID=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n" 
                    insertlogline('Post Batch Compositions same id:'+str(numberoffiles) + ' compositions with template '+tid+' and format '+myformat+ ' posted successfully')                         
                    if(check=="Yes"):
                        yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                        +str(msg['csuccess'])+"/"+str(numberoffiles)+" checked successfully\n" \
                            +"EHRID=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                            +"filenamecheckFailed="+str(msg['filenamecheckfailed'])
                else:
                    yourresults=f"Composition insertion failure.\n" \
                            + str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                            +"EHRID=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                                + msg['error']
                    insertlogline('Post Batch Compositions same id:'+str(numberoffiles) + ' compositions with template '+tid+' and format '+myformat+ ' posting failure')                             
                    if(check=="Yes"):
                        yourresults=f"Composition insertion failure.\n" \
                            + str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                            +str(msg['csuccess'])+"/"+str(numberoffiles)+" checked successfully\n" \
                            +"EHRID=" +str(msg['ehrid'])+"\n"  \
                            +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                            +"filenameFailed="+str(msg['filenamefailed'])+"\n"  \
                            +"filenamecheckFailed="+str(msg['filenamecheckfailed']) + "\n"  \
                            + msg['error']
                return render_template('pbatch1.html',yourfile=f"you have chosen {filenames}",yourresults=yourresults)        
            else:
                if("filenames" not in locals()):
                    filenames=""
                    return render_template('pbatch2.html',yourfile="")
                else:
                    return render_template('pbatch2.html',yourfile=f"you have chosen {numberoffiles} files")



    @app.route("/ecomp.html",methods=["GET"])
    #get example composition
    def excomp():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        yourresults=""
        success='false'
        compflat="{}"
        compxml=""
        compjson=""
        status='failed'
        myformat='xml'
        mymsg=ehrbase_routines.mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'ecompbase.html','ecomp.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.args.get("pippo")=="Submit": 
            template_name=request.args.get("tname","")
            filetype=request.args.get("filetype","") 
            app.logger.debug(f'filetype={filetype} template_name={template_name}')
            msg=ehrbase_routines.examplecomp(client,auth,hostname,port,username,password,template_name,filetype)

            if(msg['status']=="success"):
                status='success'
                success='true'
                if('xml' in msg):
                    myformat='xml'
                    compxml=msg['xml']
                elif('flat' in msg):
                    myformat='flat'
                    compflat=msg['flat']
                elif('structured' in msg):
                    myformat='structured'
                    compjson=msg['structured']               
                else:
                    myformat='json'
                    compjson=msg['json']

                yourresults=str(msg['status'])+ " "+ str(msg['status_code'])
                insertlogline('Get Example Composition: example composition from template '+template_name+' created successfully in format '+myformat)           
            else:   
                status='failed'
                success='false'
                if(filetype=='XML'):
                    myformat='xml'
                elif(filetype=='JSON'):
                    myformat='json'
                elif(filetype=='STRUCTURED'):
                    myformat='structured'
                else:
                    myformat='flat'        
                yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                                str(msg['text']) + "\n" +\
                                str(msg['headers'])
                insertlogline('Get Example Composition: example composition from template '+template_name+' creation failure in format '+myformat)                
            return render_template('ecomp.html',success=success,status=status,yourresults=yourresults,compxml=compxml,compjson=compjson,compflat=compflat,format=myformat)
        else:
            return render_template('ecomp.html',success=success,status=status,yourresults=yourresults,compxml=compxml,compjson=compjson,compflat=compflat,format=myformat)


    @app.route("/cform.html",methods=["GET"])
    #create form 
    def cform():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        yourresults=""
        mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'cformbase.html','cform.html')
        if(mymsg['status']=='failure'):
            return redirect(url_for("ehrbase"))
        if request.args.get("pippo")=="Submit": 
            template_name=request.args.get("tname","")
            msg=ehrbase_routines.createform(client,auth,hostname,port,username,password,template_name)

            if(msg['status']=="success"):    
                insertlogline('Form Creation:form from template '+template_name+' creation successful')                
                return redirect(url_for("form",formname=template_name))
            else:   
                yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                                str(msg['text']) + "\n" +\
                                str(msg['headers'])
                insertlogline('Form Creation:form from template '+template_name+' creation failure')                
                return render_template('cform.html',yourresults=yourresults)
        else:
            return render_template('cform.html',yourresults=yourresults)


    @app.route("/form.html/<formname>",methods=["GET"])
    #show form
    def form(formname):
        if(formname.endswith(".html")):
            if(formname != 'form.html'):
                return redirect("/"+formname)
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))
        global lastehrid,lastcompositionid
        yourresults=""
        checkresults=""
        checkinfo=""
        if request.args.get("pippo")=="Submit Composition": 
            msg=ehrbase_routines.postform(client,auth,hostname,port,username,password,formname)
            if(msg['status']=="success"):
                yourresults=f"Composition inserted successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                lastcompositionid=msg['compositionid']
                insertlogline('Post Composition from Form:composition '+lastcompositionid+' from template '+formname+' created successfully')                
                if('check' in msg):
                    checkresults=msg['check']
                    checkinfo=msg['checkinfo']
            else:
                insertlogline('Post Composition from Form:composition '+lastcompositionid+' from template '+formname+' creation failure')                
                yourresults=f"Composition insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"            
            return render_template('form.html',formname=formname,yourresults=yourresults,last=lastehrid,checkresults=checkresults,checkinfo=checkinfo)        
        else:       
            return render_template('form.html',formname=formname,yourresults=yourresults,last=lastehrid)


    @app.route("/lform.html",methods=["GET","POST"])
    #load form
    def lform():
        global hostname,port,username,password,auth,nodename
        if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
            return redirect(url_for("ehrbase"))

        if request.method == 'POST': 
            uploaded_file = request.files['file']
            uploaded_file.stream.seek(0) # seek to the beginning of file
            formloaded=uploaded_file.read().decode("utf-8")
            formfixed=ehrbase_routines.fixformloaded(formloaded)
            template_name=ehrbase_routines.retrievetemplatefromform(formfixed)
            with open('./templates/form.html','w') as ff:
                ff.write(formfixed)
            insertlogline('Get Form:form from template '+template_name+' successfully loaded')         
            return redirect(url_for("form",formname=template_name))
        else:
            return render_template('lform.html')



    @app.route("/slog.html",methods=["GET"])
    #show log of activities
    def slog():
        results=""
        #retrieve log lines
        posfilled=r.dbsize()
        fkeys=[]
        for i in range(0,posfilled):
            fkeys.append('c'+str(i))
        fvalues_noorder=r.mget(fkeys)

        #rearrange in time order with first operation first
#        fvalues=myutils.reorderbytime(fvalues_noorder,posfilled,sessiontotalevents,currentposition,reventsrecorded)
        fvalues=myutils.reorderbytime2(fvalues_noorder)

        if request.args.get("pippolippo")=="SUBMIT YOUR CHOICE":
            if request.args.get('search')=='custom':#custom search
                order2=request.args.get("order","")
                logsearch=request.args.get("logsearch","")
                andornot=request.args.get("andornot","")
                fv1=fvalues
                if(order2=='last'):
                    fv1.reverse()
                
                fv2=fv1
                fv3=myutils.findvaluesfromsearch(fv2,logsearch,andornot)
                results='\n'.join(fv3)
                return render_template('showlog.html',yourresults=results,rediseventsrecorded=reventsrecorded)
            else:
                order=request.args.get("order","")
                meth=request.args.get("methods","")
                typ=request.args.get("type","")
                out=request.args.get("outcome","")

                fv1=fvalues
                if(order=='last'):
                    fv1.reverse()

                fv2=fv1
                if(meth=='get'):
                    fv2=[f for f in fv1 if f[20:].startswith("Get ")]
                elif(meth=="post"):
                    fv2=[f for f in fv1 if f[20:].startswith("Post ")]
                elif(meth=='put'):
                    fv2=[f for f in fv1 if f[20:].startswith("Put ")]
                elif(meth=='del'):
                    fv2=[f for f in fv1 if f[20:].startswith("Delete ")]
                elif(meth=='run'):
                    fv2=[f for f in fv1 if f[20:].startswith("Run ")]

                fv3=fv2
                app.logger.debug(f'fv3={fv3}')
                if(typ=='template'):
                    fv3=[f for f in fv2 if f[20:].split(':')[0].split()[1]=='template']
                elif(typ=='ehr'):
                    fv3=[f for f in fv2 if f[20:].split(':')[0].split()[1]=='EHR']
                elif(typ=='composition'):
                    fv3=[f for f in fv2 if 'Composition' in f[20:].split(':')[0]]
                elif(typ=='query'):
                    fv3=[f for f in fv2 if f[20:].split(':')[0].split()[1]=='AQL']
                elif(typ=='form'):
                    fv3=[f for f in fv2 if 'Form' in f[20:].split(':')[0]]
                elif(typ=='ehrstatus'):
                    fv3=[f for f in fv2 if f[20:].split(':')[0].split()[1]=='EHR_STATUS']
                elif(typ=='cont'):
                    fv3=[f for f in fv2 if 'Contribution' in f[20:].split(':')[0]]
                elif(typ=='dir'):
                    fv3=[f for f in fv2 if 'Directory' in f[20:].split(':')[0]]
                

                fv4=fv3
                if(out=='successful'):
                    fv4=[f for f in fv3 if 'successful' in f[20:]]
                elif(out=='unsuccessful'):
                    fv4=[f for f in fv3 if 'failure' in f[20:]]
                
                results='\n'.join(fv4)
                return  render_template('showlog.html',yourresults=results,rediseventsrecorded=reventsrecorded)
        else:
            return  render_template('showlog.html',yourresults=results,rediseventsrecorded=reventsrecorded)

    @app.route("/errortest.html",methods=["GET"])
    #show error
    def perror():
        e='Bad things happened'
        code='500'
        return render_template('error.html',error=str(e),errorcode=code)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=9000, debug=True)
    
