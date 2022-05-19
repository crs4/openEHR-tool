from flask import Flask
from flask import request,render_template,redirect,url_for,jsonify
import ehrbase_routines
from werkzeug.utils import secure_filename

default_hostname="localhost"
default_port="8080"
default_username="ehrbase-user"
default_password="SuperSecretPassword"
hostname=""

app = Flask(__name__)

@app.route("/")
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route("/ehrbase.html",methods=["GET"])
def ehrbase():
    global hostname,port,username,password,lastehrid,lastcompositionid
    hostname=""
    port=""
    username=""
    password=""
    lastehrid=""
    lastcompositionid=""
    #print(request.args.keys())
    if request.args.get("pippo")=="Submit":
        hostname=request.args.get("hname","")
        port=request.args.get("port","")
        username=request.args.get("uname","")
        password=request.args.get("pword","")
        if(hostname==""):
            hostname=default_hostname
        if(port==""):
            port=default_port
        if(username==""):
            username=default_username 
        if(password==""):
            password=default_password   
        print(f'hostname={hostname} port={port} username={username} password={password}')            
        global auth
        auth = ehrbase_routines.init_session(username,password)
        return render_template('ehrbase.html',ho=hostname,po=port,us=username,pas=password)

    
    return render_template('ehrbase.html')

@app.route("/gtemp.html",methods=["GET"])
def gtemp():
    if(hostname=="" or port=="" or username=="" or password==""):
        return redirect(url_for("ehrbase"))
    template_name=request.args.get("tname","")
    print(f'template={template_name}')
    temp=ehrbase_routines.gettemp(auth,hostname,port,username,password,template_name)
    return render_template('gtemp.html',temp=temp)


@app.route("/ptemp.html",methods=['GET', 'POST'])
def pupload():
    if(hostname=="" or port=="" or username=="" or password==""):
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
    if(hostname=="" or port=="" or username=="" or password==""):
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
    if(hostname=="" or port=="" or username=="" or password==""):       
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
    if(hostname=="" or port=="" or username=="" or password==""):
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
            if(eid=="" or tid==""):
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",last=lastehrid)

            msg=ehrbase_routines.postcomp(auth,hostname,port,username,password,comp,eid,tid,filetype)
            print(msg)
            if(msg['status']=="success"):
                yourresults=f"Composition inserted successfully.\n status_code={msg['status_code']} VersionUID={msg['compositionid']}\n text={msg['text']}\n headers={msg['headers']}"
                lastcompositionid=msg['compositionid']
            else:
                yourresults=f"Composition insertion failure.\n status_code={msg['status_code']}\n headers={msg['headers']}\n text={msg['text']}"        
            return render_template('pcomp.html',yourfile=f"you have chosen {filename}",yourresults=yourresults,last=lastcompositionid)        
        else:
            if("filename" not in vars()):
                filename=""
                return render_template('pcomp.html',yourfile="",last=lastehrid)
            else:
                return render_template('pcomp.html',yourfile=f"you have chosen {filename}",last=lastehrid)


@app.route("/gcomp.html",methods=["GET"])
def gcomp():
    if(hostname=="" or port=="" or username=="" or password==""):       
        return redirect(url_for("ehrbase"))
    global lastcompositionid,lastehrid
    if request.args.get("fform1")=="submit":
        filetype=request.args.get("filetype","") 
        compid=request.args.get("cname","") 
        eid=request.args.get("ename","") 
        print(filetype,compid,eid)
        if(compid=="" or eid==""):
            return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid)
        print(f'compid={compid}')
        msg=ehrbase_routines.getcomp(auth,hostname,port,username,password,compid,eid,filetype)
        compjson=""
        compxml=""
        if(msg['status']=="success"):
            if('xml' in msg):
                compxml=msg['xml']
            elif('flat' in msg):
                compjson=msg['flat']
            else:
                compjson=msg['json']
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"EHR retrieved successfully. status_code={msg['status_code']} \n \
            EHRID={msg['ehrid']} versionUID={msg['compositionid']}\n headers={msg['headers']}"
            lastehrid=ehrid
            lastcompositionid=compositionid

        else:
            ehrid=msg["ehrid"]
            compositionid=msg['compositionid']
            yourresults=f"EHR retrieval failure. status_code={msg['status_code']} \n \
                headers={msg['headers']}\n text={msg['text']}"        
        return render_template('gcomp.html',yourresults=yourresults,last=lastcompositionid,
                lastehr=lastehrid,compxml=compxml,compjson=compjson)
    else:
        return render_template('gcomp.html',last=lastcompositionid,lastehr=lastehrid)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
