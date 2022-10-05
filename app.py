from argparse import FileType
from flask import Flask
from flask import request,render_template,redirect,url_for
from requests import session
import ehrbase_routines
from werkzeug.utils import secure_filename
import os
from config import readconfig,logging_configurations
from myutils import myutils
import sys
import redis
import json

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

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
running_env=os.getenv('FLASK_ENV')
if(running_env == 'development'):
    os.environ['DEBUG']='True'
else:
    os.environ['DEBUG']='False'
running_debug=os.getenv('DEBUG')
app.logger.info(f'Running with FLASK_ENV={running_env}')
app.logger.info(f'Running with DEBUG={running_debug}')
def init_redis(redishostname,redisport):
    r = redis.Redis(host=redishostname, port=redisport,db=0,decode_responses=True)
    return r

def insertlogline(line):
    global currentposition,sessiontotalevents
    if(currentposition==reventsrecorded):
        currentposition=0
    mykey='c'+str(currentposition)
    r.set(mykey,line)
    currentposition+=1
    sessiontotalevents+=1


settingsfile='./config/openehrtool.cfg'
if (os.path.exists(settingsfile)):
    varset=readconfig.readconfigfromfile(settingsfile)
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
    client=ehrbase_routines.init_ehrbase()
else:
    r=""
    client=""

@app.route("/")
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route("/fsettings.html",methods=["GET"])
def fset():
    global hostname,port,username,password,nodename,adusername,adpassword,redishostname,redisport,reventsrecorded, \
      client
    if (os.path.exists(settingsfile)):
        varset=readconfig.readconfigfromfile(settingsfile)
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
def ehrbase():
    global hostname,port,username,password,nodename,lastehrid,lastcompositionid, \
        adusername,adpassword,redishostname,redisport,reventsrecorded,client

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
        client=ehrbase_routines.init_ehrbase()
        app.logger.info("settings changed from within app")
        return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                    adus=adusername,adpas=adpassword,rho=redishostname,rpo=redisport,rr=reventsrecorded)
    return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                    adus=adusername,adpas=adpassword,rho=redishostname,rpo=redisport,rr=reventsrecorded)

@app.route("/gtemp.html",methods=["GET"])
def gtemp():
    global hostname,port,username,password,auth,nodename,mymsg,currentposition
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    yourresults=""
    singletemplate='false'
    singletemplate2='false'
    yourtemp=""
    tempjson=""
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
    elif request.args.get("pippo2")=="Get List":
        singletemplate='false'
        singletemplate2='false'
        yourresults=str(mymsg['status'])+ " "+ str(mymsg['status_code']) +"\n"+ \
                    str(mymsg['text'])
        return render_template('gtemp.html',singletemplate=singletemplate,singletemplate2=singletemplate2,yourresults=yourresults)
    else:
        return render_template('gtemp.html',singletemplate=singletemplate,singletemplate2=singletemplate2,yourresults=yourresults)

@app.route("/ptemp.html",methods=['GET', 'POST'])
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
        return render_template('ptemp.html',yourresults=yourresults)


@app.route("/utemp.html",methods=['GET', 'POST'])
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
    else :
        if (request.args.get("pippo")=="Update Template"):
            templateid=request.args.get("tname","")
            if(templateid != "" and template):
                msg=ehrbase_routines.updatetemp(client,adauth,hostname,port,adusername,adpassword,template,templateid)
                yourresults="you uploaded "+secure_filename(uploaded_file.filename)+"\n"
                
                if(msg['status']=='success'):
                    yourresults="you updated successfully "+secure_filename(uploaded_file.filename)+"\n"
                    insertlogline('Put template:template '+templateid+' updated successfully')
                else:
                    yourresults="you updated unsuccessfully "+secure_filename(uploaded_file.filename)+"\n"
                    insertlogline('Put template:template from file' + tempname +'and templateid '+templateid +' updating failure')
                yourresults=yourresults+str(msg['status']+''+str(msg['headers']))                      
                return render_template('utemp.html',yourresults=yourresults)
    return render_template('utemp.html',yourresults=yourresults)


@app.route("/dtemp.html",methods=["GET"])
def dtemp():
    global hostname,port,username,password,auth,nodename,mymsg
    if(hostname=="" or port=="" or adusername=="" or adpassword=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    yourresults=""
    mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'dtempbase.html','dtemp.html')
    if(mymsg['status']=='failure'):
        return redirect(url_for("ehrbase"))
    if request.args.get("pippo")=="Delete Template": 
        template_name=request.args.get("tname","")
        msg=ehrbase_routines.deltemp(client,adauth,hostname,port,adusername,adpassword,template_name)
        if(msg['status']=='success'):
            yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nTemplate "+template_name+ " successfully deleted"
            insertlogline('Delete template:template '+template_name+' deleted successfully')
        else:
            yourresults=msg['status']+ " "+ str(msg['status_code']) + "\nTemplate "+template_name+ " successfully deleted"
            insertlogline('Delete template:template '+template_name+' deletion failure')            
        return render_template('dtemp.html',yourresults=yourresults)
    else:
        return render_template('dtemp.html',yourresults=yourresults)


@app.route("/pehr.html",methods=["GET"])
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

@app.route("/pcomp.html",methods=["GET","POST"])
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
            return render_template('pcomp.html',yourfile=f"you have chosen {filename}",last=lastehrid)
    else:
        if request.args.get("fform1")=="POST THE COMPOSITION":
            if(filename==""):
                yourresults="Please, choose the file first"
                return render_template('pcomp.html',yourresults=yourresults,last=lastehrid)
            filetype=request.args.get("filetype","")
            eid=request.args.get("ename","")
            tid=request.args.get("tname","")
            check=request.args.get("check","")
            checkresults=""
            checkinfo=""
            if(eid=="" or tid==""):
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",last=lastehrid)
            msg=ehrbase_routines.postcomp(client,auth,hostname,port,username,password,comp,eid,tid,filetype,check)
            if(msg['status']=="success"):
                yourresults=f"Composition inserted successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                lastcompositionid=msg['compositionid']
                insertlogline('Post Composition: composition '+lastcompositionid+' posted successfully')
                if(check=="Yes"):
                    checkresults=msg['check']
                    checkinfo=msg['checkinfo']
            else:
                yourresults=f"Composition insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
                insertlogline('Post Composition: composition from file '+filename+'  posting failure')
            return render_template('pcomp.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,last=lastcompositionid,checkresults=checkresults,checkinfo=checkinfo)        
        else:
            if("filename" not in vars()):
                filename=""
                return render_template('pcomp.html',yourfile="",last=lastehrid)
            else:
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",last=lastehrid)


@app.route("/gcomp.html",methods=["GET"])
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
            else:
                myformat='json'
                compjson=msg['json']
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            insertlogline('Get Composition: composition '+compositionid+' di ehrid='+ehrid+' retrieved successfully in format '+myformat)
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
            else:
                myformat='flat'
            insertlogline('Get Composition: composition '+compid+' di ehrid='+ehrid+' retrieval failure in format '+myformat)
            yourresults=f"Composition retrieval failure. status_code={msg['status_code']} \n \
                headers={msg['headers']}\n text={msg['text']}"        
        return render_template('gcomp.html',yourresults=yourresults,last=lastcompositionid,
                lastehr=lastehrid,compxml=compxml,compjson=compjson,compflat=compflat,status=status,format=myformat)
    else:
        return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat,status=status,format=myformat)

@app.route("/paql.html",methods=["GET"])
def paql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    if request.args.get("pippo")=="Store query":
        aqltext=request.args.get("aqltext","")
        version=request.args.get("version","")
        qtype=request.args.get("qtype","")
        qname=request.args.get("nquery","")
        app.logger.debug(f'aqltext={aqltext} ') 
        if(aqltext=="" or qname==""):
            app.logger.warning("no text in aql")
            render_template('paql.html')
        myaqltext="{'q':'"+aqltext+"'}"
        reversed_nodename=".".join(reversed(nodename.split(".")))
        qname=reversed_nodename+"::"+qname+"/"
        app.logger.info(myaqltext)
        msg=ehrbase_routines.postaql(client,auth,hostname,port,username,password,myaqltext,qname,version,qtype)
        if(msg['status']=="success"):
            insertlogline('Post AQL Query: query '+qname+' version='+version+' type='+qtype+' posted successfully')
            yourresults=f"Query inserted successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            insertlogline('Post AQL Query: query '+qname+' version='+version+' type='+qtype+' posting failure')
            yourresults=f"Query insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('paql.html',yourresults=yourresults,aqltext=aqltext)
    else: 
        return render_template('paql.html',aqltext={})

@app.route("/gaql.html",methods=["GET"])
def gaql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    mymsg=ehrbase_routines.createPageFromBase4querylist(client,auth,hostname,port,username,password,'gaqlbase.html','gaql.html')
    if(mymsg['status']=='failure'):
        return redirect(url_for("ehrbase"))
    aql=""
    aqlpresent='false'
    if request.args.get("pippo")=="Submit":
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
        return render_template('gaql.html',yourresults=yourresults,aql=aql,aqlpresent=aqlpresent)
    else: 
        return render_template('gaql.html',aql=aql,aqlpresent=aqlpresent)

@app.route("/raql.html",methods=["GET"])
def runaql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    global lastehrid,aqltext,aqltext2,qname,version
    resultsave='false'
    temp=""
    yourresults=""
    mymsg=ehrbase_routines.createPageFromBase4querylist(client,auth,hostname,port,username,password,'raqlbase.html','raql.html')
    if(mymsg['status']=='failure'):
        return redirect(url_for("ehrbase"))

    if request.args.get("pippo")=="Select":
        qdata=request.args.get("qdata","")
        if "$v" not in qdata: #no query choosable
            aqltext2=f"No queries available"
            yourresults='Please select or create a query first'
            return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2,aqltext={})
        else:
            qdatas=qdata.split('$v')
            qname=qdatas[0]
            version=qdatas[1]
            msg=ehrbase_routines.getaql(client,auth,hostname,port,username,password,qname,version)
            if(msg['status']=="success"):
                insertlogline('Get AQL Query: query '+qname+' version'+version+' retrieved successfully')
                yourresults=f"Query {qname} v{version} retrieved successfully"
                aqlpresent='true'
                aqltext2=msg['aql']
                return render_template('raql.html',yourresults=yourresults,aqltext=aqltext2,lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2)     
            else:
                insertlogline('Get AQL Query: query '+qname+' version='+version+' retrieval failure')
                yourresults=f"Query {qname} v{version} retrieval failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
                return render_template('raql.html',yourresults=yourresults,aqltext=aqltext,aqltext2=aqltext2,lastehr=lastehrid,resultsave=resultsave,temp=temp)     
    elif request.args.get("pippo")=="Run pasted query": 
        aqltext=request.args.get("aqltext","")
        qmethod=request.args.get("qmethod","")
        limit=request.args.get("limit","")
        # offset=request.args.get("offset","")
        # fetch=request.args.get("fetch","")
        eid=request.args.get("ehrid","") 
        qparam=request.args.get("qparam","")
        resultsave='false'
        qname=""
        version=""
        if(aqltext==""):
            app.logger.info("no text in aql")
            render_template('raql.html',lastehr=lastehrid,resultsave=resultsave,temp=temp)
        app.logger.info(aqltext)
        msg=ehrbase_routines.runaql(client,auth,hostname,port,username,password,aqltext,qmethod,limit,eid,qparam,qname,version)
        if(msg['status']=="success"):
            insertlogline('Run AQL Query: pasted query run successfully')
            msgtext=json.loads(msg['text'])
            if('rows' in msgtext):
                temp=msgtext['rows']
                if(len(temp)>0):
                    resultsave='true'            
            yourresults=f"Query run successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            insertlogline('Run AQL Query: pasted query run failure')
            resultsave='false'
            yourresults=f"Query run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('raql.html',yourresults=yourresults,aqltext=aqltext,lastehr=lastehrid,resultsave=resultsave,temp=temp)
    elif(request.args.get("pippo2")=="Run"):
        if(aqltext2 is None or aqltext2=='No queries available'):
            yourresults='Please select or create a query first'
            return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2,aqltext={})
        qmethod=request.args.get("qmethod","")
        limit=request.args.get("limit","")
        aqltext=aqltext2
        resultsave='false'
        # offset=request.args.get("offset","")
        # fetch=request.args.get("fetch","")
        eid=request.args.get("ehrid","") 
        qparam=request.args.get("qparam","")
        reversed_nodename=".".join(reversed(nodename.split(".")))
        if(qname==""):
            return render_template('raql.html',lastehr=lastehrid,resultsave=resultsave,temp=temp,aqltext2=aqltext2)
        msg=ehrbase_routines.runaql(client,auth,hostname,port,username,password,aqltext2,qmethod,limit,eid,qparam,qname,version)    
        if(msg['status']=="success"):
            insertlogline('Run AQL Stored Query: query '+qname+' version'+version+' run successfully')
            msgtext=json.loads(msg['text'])
            if('rows' in msgtext):
                temp=msgtext['rows']
                if(len(temp)>0):
                    resultsave='true'          
            yourresults=f"Query {qname} v{version} run successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
            return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid,aqltext=aqltext2,aqltext2=aqltext2,resultsave=resultsave,temp=temp)
        else:
            insertlogline('Run AQL Query: query '+qname+' version'+version+' run failure')
            resultsave='false'
            yourresults=f"Query {qname} v{version}run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
            return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid,aqltext={},aqltext2=aqltext2,resultsave=resultsave,temp=temp)
    else:
        return render_template('raql.html',lastehr=lastehrid,aqltext={},resultsave=resultsave,temp=temp)


@app.route("/dashboard.html",methods=["GET"])
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
        info=disk=aql=db=gen_properties=end_properties=terminology=plugin=env={}
        if(msg['status']=='success1'):#only AQL queries stored
            total_aql_queries=msg['aql']
            return render_template('dashboard.html',total_aql_queries=total_aql_queries,
             info=info,disk=disk,aql=aql,db=db,gen_properties=gen_properties,end_properties=end_properties,
             terminology=terminology,plugin=plugin,env=env)
        elif(msg['status']=='success2'):#and total EHRS
            total_ehrs=msg['ehr']
            return render_template('dashboard.html',total_ehrs=total_ehrs,total_aql_queries=total_aql_queries,
             info=info,disk=disk,aql=aql,db=db,gen_properties=gen_properties,end_properties=end_properties,
             terminology=terminology,plugin=plugin,env=env)
        elif(msg['status']=='success3'):#and EHRS in use, templates in use, compositions
            total_ehrs=msg['ehr']
            total_ehrs_in_use=msg['uehr']
            total_templates_in_use=msg['utemplate']
            total_compositions=msg['composition']
            total_aql_queries=msg['aql']
            return render_template('dashboard.html',total_ehrs=total_ehrs,total_templates_in_use=total_templates_in_use,
                total_ehrs_in_use=total_ehrs_in_use,total_compositions=total_compositions, total_aql_queries=total_aql_queries,
                 info=info,disk=disk,aql=aql,db=db,gen_properties=gen_properties,end_properties=end_properties,
             terminology=terminology,plugin=plugin,env=env)
        elif(msg['status']=='success4'):#and total templates
            total_ehrs=msg['ehr']
            total_ehrs_in_use=msg['uehr']
            total_compositions=msg['composition']
            total_templates=msg['template']
            total_templates_in_use=msg['utemplate']
            total_aql_queries=msg['aql']
            bar_labels=msg['bar_label']
            bar_values=msg['bar_value']
            bar_max=msg['bar_max']
            pie_labels=msg['pie_label']
            pie_values=msg['pie_value']
            return render_template('dashboard.html',total_ehrs=total_ehrs,
                total_templates=total_templates, total_templates_in_use=total_templates_in_use,
                total_compositions=total_compositions,
                total_aql_queries=total_aql_queries,bar_labels=bar_labels,
                bar_values=bar_values,pie_labels=pie_labels,
                pie_values=pie_values,bar_max=bar_max,
                total_ehrs_in_use=total_ehrs_in_use,
                 info=info,disk=disk,aql=aql,db=db,gen_properties=gen_properties,end_properties=end_properties,
             terminology=terminology,plugin=plugin,env=env)
        else: #management endpoint allowed
            total_ehrs=msg['ehr']
            total_ehrs_in_use=msg['uehr']
            total_compositions=msg['composition']
            total_templates=msg['template']
            total_templates_in_use=msg['utemplate']
            total_aql_queries=msg['aql']
            bar_labels=msg['bar_label']
            bar_values=msg['bar_value']
            bar_max=msg['bar_max']
            pie_labels=msg['pie_label']
            pie_values=msg['pie_value']
            #other parameters
            info=msg['info']
            env=msg['env']
            terminology=msg['terminology']
            plugin=msg['plugin']
            end_properties=msg['end_properties']
            gen_properties=msg['gen_properties']
            aql=msg['aqlinfo']
            db=msg['db']
            disk=msg['disk']
            return render_template('dashboard.html',total_ehrs=total_ehrs,
                total_templates=total_templates, total_templates_in_use=total_templates_in_use,
                total_compositions=total_compositions,
                total_aql_queries=total_aql_queries,bar_labels=bar_labels,
                bar_values=bar_values,pie_labels=pie_labels,
                pie_values=pie_values,bar_max=bar_max,info=info,
                end_properties=end_properties,terminology=terminology,
                env=env,plugin=plugin,aql=aql,db=db,disk=disk,
                gen_properties=gen_properties,
                total_ehrs_in_use=total_ehrs_in_use)
    else:
        myerror='Error. No data available\n text:'+str(msg['text'])+' headers='+str(msg['headers'])
        return render_template('dashboard.html',error=myerror)


@app.route("/pbatch1.html",methods=["GET","POST"])
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
def excomp():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    yourresults=""
    success='false'
    yourjson='{}'
    mymsg=ehrbase_routines.mymsg=ehrbase_routines.createPageFromBase4templatelist(client,auth,hostname,port,username,password,'ecompbase.html','ecomp.html')
    if(mymsg['status']=='failure'):
        return redirect(url_for("ehrbase"))
    if request.args.get("pippo")=="Submit": 
        template_name=request.args.get("tname","")
        msg=ehrbase_routines.examplecomp(client,auth,hostname,port,username,password,template_name)

        if(msg['status']=="success"):
            success='true'
            yourjson=msg['composition']
            yourresults=str(msg['status'])+ " "+ str(msg['status_code'])
            insertlogline('Get Example Composition: example composition from template '+template_name+' created successfully')
            return render_template('ecomp.html',success=success,yourresults=yourresults,yourjson=yourjson)
        else:   
            success='false'
            yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                            str(msg['text']) + "\n" +\
                            str(msg['headers'])
            insertlogline('Get Example Composition: example composition from template '+template_name+' creation failure')                
            return render_template('ecomp.html',success=success,yourresults=yourresults)
    else:
        return render_template('ecomp.html',success=success,yourresults=yourresults)


@app.route("/cform.html",methods=["GET"])
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
def slog():
    results=""
    #retrieve log lines
    posfilled=r.dbsize()
    fkeys=[]
    for i in range(0,posfilled):
        fkeys.append('c'+str(i))
    fvalues_noorder=r.mget(fkeys)

    #rearrange in time order with first operation first
    fvalues=myutils.reorderbytime(fvalues_noorder,posfilled,sessiontotalevents,currentposition,reventsrecorded)

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
                fv2=[f for f in fv1 if f.startswith("Get ")]
            elif(meth=="post"):
                fv2=[f for f in fv1 if f.startswith("Post ")]
            elif(meth=='put'):
                fv2=[f for f in fv1 if f.startswith("Put ")]
            elif(meth=='del'):
                fv2=[f for f in fv1 if f.startswith("Delete ")]
            elif(meth=='run'):
                fv2=[f for f in fv1 if f.startswith("Run ")]

            fv3=fv2
            if(typ=='template'):
                fv3=[f for f in fv2 if f.split(':')[0].split()[1]=='template']
            elif(typ=='ehr'):
                fv3=[f for f in fv2 if f.split(':')[0].split()[1]=='EHR']
            elif(typ=='composition'):
                fv3=[f for f in fv2 if 'Composition' in f.split(':')[0]]
            elif(typ=='query'):
                fv3=[f for f in fv2 if f.split(':')[0].split()[1]=='AQL']
            elif(typ=='form'):
                fv3=[f for f in fv2 if 'Form' in f.split(':')[0]]

            fv4=fv3
            if(out=='successful'):
                fv4=[f for f in fv3 if 'successful' in f]
            elif(out=='unsuccessful'):
                fv4=[f for f in fv3 if 'failure' in f]
            
            results='\n'.join(fv4)
            return  render_template('showlog.html',yourresults=results,rediseventsrecorded=reventsrecorded)
    else:
        return  render_template('showlog.html',yourresults=results,rediseventsrecorded=reventsrecorded)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
