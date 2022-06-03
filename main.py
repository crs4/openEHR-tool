from flask import Flask
from flask import request,render_template,redirect,url_for,jsonify
import ehrbase_routines
from werkzeug.utils import secure_filename

default_hostname="localhost"
default_port="8080"
default_username="ehrbase-user"
default_password="SuperSecretPassword"
default_nodename="local.ehrbase.org"
hostname=""

app = Flask(__name__)

@app.route("/")
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route("/settings.html",methods=["GET"])
def ehrbase():
    global hostname,port,username,password,nodename,lastehrid,lastcompositionid
    hostname=""
    port=""
    username=""
    password=""
    lastehrid=""
    lastcompositionid=""
    nodename=""
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
        auth = ehrbase_routines.init_session(username,password)
        return render_template('settings.html',ho=hostname,po=port,us=username,pas=password,no=nodename)

    
    return render_template('settings.html')

@app.route("/gtemp.html",methods=["GET"])
def gtemp():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):
        return redirect(url_for("ehrbase"))
    template_name=request.args.get("tname","")
    print(f'template={template_name}')
    temp=ehrbase_routines.gettemp(auth,hostname,port,username,password,template_name)
    return render_template('gtemp.html',temp=temp)


@app.route("/ptemp.html",methods=['GET', 'POST'])
def pupload():
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
 #           print(msg)
            yourresults="you uploaded "+secure_filename(uploaded_file.filename)+"\n"+msg
            return render_template('ptemp.html',yourresults=yourresults)
    else:
        return render_template('ptemp.html',yourresults=yourresults)



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
        else:
            ehr={}
            yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
        return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid)
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
        else:
            ehr={}
            yourresults=f"EHR retrieval failure. status_code={msg['status_code']} headers={msg['headers']} text={msg['text']}"        
        return render_template('gehr.html',yourresults=yourresults,ehr=ehr,lastehr=lastehrid)
    return render_template('gehr.html',lastehr=lastehrid)

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
        compjson=""
        compxml=""
        if(msg['status']=="success"):
            if('xml' in msg):
                compxml=msg['xml']
            elif('flat' in msg):
                compflat=msg['flat']
            else:
                compjson=msg['json']
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"Composition retrieved successfully. status_code={msg['status_code']} \n \
            EHRID={msg['ehrid']} versionUID={msg['compositionid']}\n headers={msg['headers']}"
            lastehrid=ehrid
            lastcompositionid=compositionid
 
        else:
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"Composition retrieval failure. status_code={msg['status_code']} \n \
                headers={msg['headers']}\n text={msg['text']}"        
        return render_template('gcomp.html',yourresults=yourresults,last=lastcompositionid,
                lastehr=lastehrid,compxml=compxml,compjson=compjson,compflat=compflat)
    else:
        return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid,compflat=compflat)

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
        return render_template('paql.html')

@app.route("/gaql.html",methods=["GET"])
def gaql():
    global hostname,port,username,password,auth,nodename
    if(hostname=="" or port=="" or username=="" or password=="" or nodename==""):       
        return redirect(url_for("ehrbase"))
    if request.args.get("pippo")=="Submit":
        qname=request.args.get("qname","")
        version=request.args.get("version","")
        reversed_nodename=".".join(reversed(nodename.split(".")))
        if(qname != "" and "::" not in qname):
            qname=reversed_nodename+"::"+qname+"/"
        msg=ehrbase_routines.getaql(auth,hostname,port,username,password,qname,version)
        if(msg['status']=="success"):
            yourresults=f"Query retrieved successfully.\n status_code={msg['status_code']}\n text={msg['text']}\n headers={msg['headers']}"
        else:
            yourresults=f"Query retrieval failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"               
        return render_template('gaql.html',yourresults=yourresults)
    else: 
        return render_template('gaql.html')

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
        return render_template('raql.html',yourresults=yourresults,lastehr=lastehrid)
    else:
        return render_template('raql.html',lastehr=lastehrid)




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
