from tkinter import FALSE
from turtle import up
from flask import Flask
from flask import request,render_template,redirect,url_for
import ehrbase_routines
from werkzeug.utils import secure_filename

default_hostname="localhost"
default_port="8080"
default_username="ehrbase-user"
default_password="SuperSecretPassword"
default_nodename="local.ehrbase.org"
default_adusername="ehrbase-admin"
default_adpassword="EvenMoreSecretPassword"
hostname=""

app = Flask(__name__)

@app.route("/")
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route("/settings.html",methods=["GET"])
def ehrbase():
    global hostname,port,username,password,nodename,lastehrid,lastcompositionid
    global adusername,adpassword
    hostname=""
    port=""
    username=""
    password=""
    lastehrid=""
    lastcompositionid=""
    nodename=""
    adusername=""
    adpassword=""
    #print(request.args.keys())
    if request.args.get("pippo")=="Submit":
        hostname=request.args.get("hname","")
        port=request.args.get("port","")
        username=request.args.get("uname","")
        password=request.args.get("pword","")
        nodename=request.args.get("nodename","")
 
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
        print(f'hostname={hostname} port={port} username={username} password={password} nodename={nodename}')            
        global auth
        print(request.args)
        if(request.args.get('admin')=='yes'):
            adusername=request.args.get("aduname")
            adpassword=request.args.get("adpword","")        
            if(adusername==""):
                adusername=default_adusername 
            if(adpassword==""):
                adpassword=default_adpassword  
            print(f'adusername={adusername} adpassword={adpassword}')            
            global adauth
            adauth= ehrbase_routines.getauth(adusername,adpassword)
        global auth
        auth = ehrbase_routines.getauth(username,password)
        return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename,
                    adus=adusername,adpas=adpassword)
    return render_template('settings.html')

@app.route("/gtemp.html",methods=["GET"])
def gtemp():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    yourresults=""
    singletemplate='false'
    yourtemp=""
    print(request.args)
    if request.args.get("pippo")=="Submit": 
        template_name=request.args.get("tname","")
        print(f'template={template_name}')
        msg=ehrbase_routines.gettemp(auth,hostname,port,username,password,template_name)

        if(msg['status']=="success"):
            if(template_name!=""):
                singletemplate='true'
                temp=msg['template']
                yourresults=str(msg['status'])+ " "+ str(msg['status_code'])
                yourtemp=temp
                return render_template('gtemp.html',temp=temp,singletemplate=singletemplate,yourresults=yourresults,yourtemp=yourtemp)
            else:
                singletemplate='false'
                yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                    str(msg['text'])
                return render_template('gtemp.html',singletemplate=singletemplate,yourresults=yourresults)
        else:   
            singletemplate='false'
            yourresults=str(msg['status'])+ " "+ str(msg['status_code']) +"\n"+ \
                            str(msg['text']) + "\n" +\
                            str(msg['headers'])
            return render_template('gtemp.html',singletemplate=singletemplate, yourresults=yourresults)
    else:
        return render_template('gtemp.html',singletemplate=singletemplate, yourresults=yourresults)

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
          #  myfile = uploaded_file.file # will point to tempfile itself
            template=uploaded_file.read()
            # print(type(template))
            # print(type(template.decode("utf-8")))
            # print(template[-10:])
            msg=ehrbase_routines.posttemp(auth,hostname,port,username,password,template)
            yourresults=str(msg['status'])+" "+str(msg['status_code'])+ "\n"+ \
                str(msg['headers'])+"\n"+ \
                    str(msg['text'])
            return render_template('ptemp.html',yourresults=yourresults)
    else:
        return render_template('ptemp.html',yourresults=yourresults)


@app.route("/utemp.html",methods=['GET', 'POST'])
def pupdate():
    global hostname,port,adusername,adpassword,adauth,nodename,uploaded_file,template
    if(hostname=="" or port=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    if(adusername=="" or adpassword==""):
        return render_template('/utemp.html',warning='WARNING: NO ADMIN CREDENTIALS PROVIDED '), {"Refresh": "3; url="+url_for('ehrbase') }
    yourresults=""
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
           
            uploaded_file.stream.seek(0) # seek to the beginning of file
          #  myfile = uploaded_file.file # will point to tempfile itself
            template=uploaded_file.read()
            # print(type(template))
            # print(type(template.decode("utf-8")))
            # print(template[-10:])
 #           print(msg)
            yourresults="you chose "+secure_filename(uploaded_file.filename)+"\n"
            return render_template('utemp.html',yourresults=yourresults)
    else :
        print(request.args)
        print(request.args.get("pippo"))
        if (request.args.get("pippo")=="Update Template"):
            templateid=request.args.get("tname","")
            if(templateid != "" and template):
                msg=ehrbase_routines.updatetemp(adauth,hostname,port,adusername,adpassword,template,templateid)
                yourresults="you uploaded "+secure_filename(uploaded_file.filename)+"\n"+msg
                return render_template('utemp.html',yourresults=yourresults)
    return render_template('utemp.html',yourresults=yourresults)



@app.route("/pehr.html",methods=["GET"])
def pehr():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))  
    yourresults=""  
    global lastehrid
    if request.args.get("sform1")=="Submit": #EHRID specified or not
        ehrid=request.args.get("ehrtext","")
        msg=ehrbase_routines.createehrid(auth,hostname,port,username,password,ehrid)
        print(f"back to function {msg}")
        if(msg['status']=="success"):
            ehrid=msg["ehrid"]
            yourresults=f"EHR created successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
            lastehrid=ehrid
            ehr=msg['text']
        else:
            yourresults=f"EHR creation failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"
            ehr={}
        return render_template('pehr.html',yourresults=yourresults,ehr=ehr)    
    elif request.args.get("sform2")=="Submit":   #subjectID and subjectNamespace and maybe EHRID
        eid=request.args.get("eid","")
        sid=request.args.get("sid","")
        sna=request.args.get("sna","")
        if(sid=="" or sna==""):
            return render_template('pehr.html')        
        msg=ehrbase_routines.createehrsub(auth,hostname,port,username,password,sid,sna,eid)
        if(msg['status']=="success"):
            print(f'msg={msg}')
            ehrid=msg["ehrid"]
            yourresults=f"EHR created successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
            lastehrid=ehrid
            ehr=msg['text']
        else:
            yourresults=f"EHR creation failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
            ehr={}
        return render_template('pehr.html',yourresults=yourresults,ehr=ehr)
    else:
        print(request.args.keys())
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
        print(f'ehrid={ehrid}')
        msg=ehrbase_routines.getehrid(auth,hostname,port,username,password,ehrid)
        if(msg['status']=="success"):
            ehrid=msg["ehrid"]
            yourresults=f"EHR retrieved successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
            ehr=msg['text']
            lastehrid=ehrid
            status='success'
        else:
            ehr={}
            yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
        return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid,status=status)
    elif request.args.get("fform2")=="Submit": 
        sid=request.args.get("sid","") 
        sna=request.args.get("sna","")
        print(f"sid={sid} sna={sna}")
        if(sid=="" or sna==""):
            return render_template('gehr.html',lastehr=lastehrid)
        msg=ehrbase_routines.getehrsub(auth,hostname,port,username,password,sid,sna)
        if(msg['status']=="success"):
            ehrid=msg["ehrid"]
            yourresults=f"EHR retrieved successfully. status_code={msg['status_code']} EHRID={msg['ehrid']}"
            ehr=msg['text']
            lastehrid=ehrid
            status='success'
        else:
            ehr={}
            yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
        return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid,status=status)
    return render_template('gehr.html',lastehr=lastehrid,status=status)

@app.route("/pcomp.html",methods=["GET","POST"])
def pcomp():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))  
    yourresults=""  
    global lastehrid,lastcompositionid,filename,uploaded_file,comp
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename=uploaded_file.filename
        print(filename)
        if filename != '':
            filename=secure_filename(filename)
            uploaded_file.stream.seek(0)
            comp=uploaded_file.read()
            print(filename)
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
            msg=ehrbase_routines.postcomp(auth,hostname,port,username,password,comp,eid,tid,filetype,check)
            if(msg['status']=="success"):
                yourresults=f"Composition inserted successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                lastcompositionid=msg['compositionid']
                if(check=="Yes"):
                    checkresults=msg['check']
                    checkinfo=msg['checkinfo']
            else:
                yourresults=f"Composition insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
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
    format='xml'
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    global lastcompositionid,lastehrid
    if request.args.get("fform1")=="Submit":
        filetype=request.args.get("filetype","") 
        compid=request.args.get("cname","") 
        eid=request.args.get("ename","") 
        print(filetype,compid,eid)
        if(compid=="" or eid==""):
            return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat)
        print(f'compid={compid}')
        msg=ehrbase_routines.getcomp(auth,hostname,port,username,password,compid,eid,filetype)
        # compjson=""
        # compxml=""
        if(msg['status']=="success"):
            status='success'
            if('xml' in msg):
                format='xml'
                compxml=msg['xml']
            elif('flat' in msg):
                format='flat'
                compflat=msg['flat']
            else:
                format='json'
                compjson=msg['json']
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"Composition retrieved successfully. status_code={msg['status_code']} \n \
            EHRID={msg['ehrid']} versionUID={msg['compositionid']}\n headers={msg['headers']}"
            lastehrid=ehrid
            lastcompositionid=compositionid
        else:
            status='failed'
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"Composition retrieval failure. status_code={msg['status_code']} \n \
                headers={msg['headers']}\n text={msg['text']}"        
        return render_template('gcomp.html',yourresults=yourresults,last=lastcompositionid,
                lastehr=lastehrid,compxml=compxml,compjson=compjson,compflat=compflat,status=status,format=format)
    else:
        return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat,status=status,format=format)

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
        print(f'aqltext={aqltext} ') 
        if(aqltext=="" or qname==""):
            print("no text in aql")
            render_template('paql.html')
        myaqltext="{'q':'"+aqltext+"'}"
        reversed_nodename=".".join(reversed(nodename.split(".")))
        qname=reversed_nodename+"::"+qname+"/"
        print(myaqltext)
        msg=ehrbase_routines.postaql(auth,hostname,port,username,password,myaqltext,qname,version,qtype)
        if(msg['status']=="success"):
            yourresults=f"Query inserted successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            yourresults=f"Query insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('paql.html',yourresults=yourresults,aqltext=aqltext)
    else: 
        return render_template('paql.html',aqltext={})

@app.route("/gaql.html",methods=["GET"])
def gaql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    aqlpresent='false'
    aql=""
    if request.args.get("pippo")=="Submit":
        qname=request.args.get("qname","")
        version=request.args.get("version","")
        reversed_nodename=".".join(reversed(nodename.split(".")))
        if(qname != "" and "::" not in qname):
            qname=reversed_nodename+"::"+qname+"/"
        msg=ehrbase_routines.getaql(auth,hostname,port,username,password,qname,version)
        if(msg['status']=="success"):
            yourresults=f"Query retrieved successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
            if('aql' in msg):
                aqlpresent='true'
                aql=msg['aql']
        else:
            yourresults=f"Query retrieval failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('gaql.html',yourresults=yourresults,aql=aql,aqlpresent=aqlpresent)
    else: 
        return render_template('gaql.html',aql=aql,aqlpresent=aqlpresent)

@app.route("/raql.html",methods=["GET"])
def runaql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    global lastehrid
    if request.args.get("pippo")=="Run pasted query": 
        aqltext=request.args.get("aqltext","")
        qmethod=request.args.get("qmethod","")
        limit=request.args.get("limit","")
        # offset=request.args.get("offset","")
        # fetch=request.args.get("fetch","")
        eid=request.args.get("ehrid","") 
        qparam=request.args.get("qparam","")
        qname=""
        version=""
        if(aqltext==""):
            print("no text in aql")
            render_template('raql.html',lastehr=lastehrid)
        print(aqltext)
#        msg=ehrbase_routines.runaql(auth,hostname,port,username,password,aqltext,qmethod,offset,fetch,eid,qparam,qname,version)
        msg=ehrbase_routines.runaql(auth,hostname,port,username,password,aqltext,qmethod,limit,eid,qparam,qname,version)
        if(msg['status']=="success"):
            yourresults=f"Query run successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            yourresults=f"Query run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('raql.html',yourresults=yourresults,aqltext=aqltext,lastehr=lastehrid)
    elif(request.args.get("pippo2")=="Run stored query"):
        qname=request.args.get("nquery","")
        qmethod=request.args.get("qmethod","")
        version=request.args.get("version","")
        limit=request.args.get("limit","")
        aqltext=""
        # offset=request.args.get("offset","")
        # fetch=request.args.get("fetch","")
        eid=request.args.get("ehrid","") 
        qparam=request.args.get("qparam","")
        reversed_nodename=".".join(reversed(nodename.split(".")))
        if(qname==""):
            return render_template('raql.html',lastehr=lastehrid)
        if(qname != "" and "::" not in qname):
            qname=reversed_nodename+"::"+qname+"/"
#        msg=ehrbase_routines.runaql(auth,hostname,port,username,password,aqltext,qmethod,offset,fetch,eid,qparam,qname,version)
        msg=ehrbase_routines.runaql(auth,hostname,port,username,password,aqltext,qmethod,limit,eid,qparam,qname,version)
        if(msg['status']=="success"):
            yourresults=f"Query run successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            yourresults=f"Query run failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid,aqltext={})
    else:
        return render_template('raql.html',lastehr=lastehrid,aqltext={})

@app.route("/dashboard.html",methods=["GET"])
def dashboard():
    global hostname,port,username,password,auth,nodename,adusername,adpassword
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
#    if request.args.get("pippo")=="Update":
    msg=ehrbase_routines.get_dashboard_info(auth,hostname,port,username,password,adauth,adusername,adpassword)

    if('success' in msg['status']):
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

        if(msg['status']=='success'):
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
            print(msg)
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
            return render_template('dashboard.html',total_ehrs=total_ehrs,
                total_templates=total_templates, total_templates_in_use=total_templates_in_use,
                total_compositions=total_compositions,
                total_aql_queries=total_aql_queries,bar_labels=bar_labels,
                bar_values=bar_values,pie_labels=pie_labels,
                pie_values=pie_values,bar_max=bar_max)
    else:
        return render_template('dashboard.html')


@app.route("/pbatch1.html",methods=["GET","POST"])
def pbatch():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))  
    yourresults=""  
    global lastehrid,lastcompositionid,numberoffiles,uploaded_files,filenames,comps
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        comps=[]
        print(uploaded_files)
        filenameslist=[]
        for uf in uploaded_files:
            print(uf.filename)
            filenameslist.append(uf.filename)
            uf.stream.seek(0)
            composition=uf.read()
            comps.append(composition)
        filenames=",".join(filenameslist)
        numberoffiles=len(uploaded_files) 
        print(len(comps))   
        return render_template('pbatch1.html',yourfile=f"you have chosen {numberoffiles} files")
    else:
        if request.args.get("pippolippo")=="POST THE COMPOSITIONS":
            sidpath=""
            snamespace=""
            random=False
            if(request.args.get('random')=='yes'):
                random=True
            else:
                sidpath=request.args.get("sidpath","")
                snamespace=request.args.get("snamespace","")
                if(sidpath=="" or snamespace==""):
                    print("path to id or namespace not given")
                    return render_template('pbatch1.html')
            tid=request.args.get("tname","")
            filetype=request.args.get("filetype","")
            check=request.args.get("check","")  
            if(tid==""):
                print("Template id not given")
                return render_template('pbatch1.html')
            if('comps' not in locals() and 'comps' not in globals()):
                print("Compositions not loaded")
                return render_template('pbatch1.html')
                
            msg=ehrbase_routines.postbatch1(auth,hostname,port,username,password,uploaded_files,tid,check,sidpath,snamespace,filetype,random,comps)
            if(msg['status']=="success"):
                yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                    +"EHRIDs=" +str(msg['ehrid'])+"\n"  \
                         +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                         +"filenameFailed="+str(msg['filenamefailed'])+"\n" 
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
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        comps=[]
        print(uploaded_files)
        filenameslist=[]
        for uf in uploaded_files:
            print(uf.filename)
            filenameslist.append(uf.filename)
            uf.stream.seek(0)
            composition=uf.read()
            comps.append(composition)
        filenames=",".join(filenameslist)
        numberoffiles=len(uploaded_files) 
        print(len(comps))   
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
                    print("ehrid not given")
                    return render_template('pbatch2.html')
            tid=request.args.get("tname","")
            filetype=request.args.get("filetype","")
            check=request.args.get("check","")  
            if(tid==""):
                print("Template id not given")
                return render_template('pbatch2.html')
            if('comps' not in locals() and 'comps' not in globals()):
                print("Compositions not loaded")
                return render_template('pbatch2.html')
                
            msg=ehrbase_routines.postbatch2(auth,hostname,port,username,password,uploaded_files,tid,check,eid,filetype,random,comps)
            if(msg['status']=="success"):
                yourresults=str(msg['nsuccess'])+"/"+str(numberoffiles)+" Compositions inserted successfully.\n" \
                    +"EHRID=" +str(msg['ehrid'])+"\n"  \
                         +"VersionUIDs=" +str(msg['compositionid'])+"\n"  \
                         +"filenameFailed="+str(msg['filenamefailed'])+"\n" 
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



@app.route("/test.html",methods=["GET"])
def gtest():
    global hostname,port,username,password,auth,nodename
    # if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
    #     return redirect(url_for("ehrbase"))
    template_name=request.args.get("tname","")
    print(f'template={template_name}')
    #temp=ehrbase_routines.gettemp(auth,hostname,port,username,password,template_name)
    success='success'
    success='failure'
    #return render_template('test.html',temp=temp,success=success)
    mycontent="<test>start</test><uno>true</uno>"
    return render_template('test.html',success=success,mycontent=mycontent)












if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
