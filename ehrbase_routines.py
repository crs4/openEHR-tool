from re import U
import requests

from url_normalize import url_normalize
from lxml import etree
import json
from json_tools import diff
import string,random
import sys
from flask import request
from myutils import myutils


def init_ehrbase():
    from app import app
    app.logger.debug('inside init_ehrbase')
    client=requests.Session()
    return client


def createPageFromBase4templatelist(client,auth,hostname,port,username,password,basefile,targetfile):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside createPageFromBase4templatelist')
    client.auth = (username,password)
    myresp={}
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4')
    response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    app.logger.debug('Get list templates')
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    if(response.status_code<210 and response.status_code>199):
        myresp['text']=response.text
        myresp['status']='success'
        myresp['headers']=response.headers
        myresp['status_code']=  response.status_code
        results=json.loads(response.text)
        templates=[r['template_id'] for r in results]
        if(len(templates)==0):
            templates=['No templates available']
        myresp['templates']=templates
        drmstart=['<select  class="form-select" type="text" id="tname" name="tname">']
        drmoptions=['<option>'+t+'</option>' for t in templates]
        drmstop=['</select>']
        drm=[]
        drm=drmstart+drmoptions+drmstop
        drmstring='\n'.join(drm)
        with open('./templates/'+basefile,'r') as ff:
            lines=ff.readlines()
        with open('./templates/'+targetfile,'w') as fg:
            docopy=True
            for line in lines:
                if('<!--dropdownmenustart-->' in line):
                    docopy=False
                    fg.write(drmstring)
                elif('<!--dropdownmenustop-->' in line):
                    docopy=True
                else:
                    if(docopy):
                        fg.write(line)
        return myresp
    else:
        myresp['text']=response.text
        myresp['status']='failure'
        myresp['headers']=response.headers  
        myresp['status_code']=  response.status_code   
        app.logger.warning("GET templates for createPageFromBase4templatelist failure")
        return myresp    

def gettemp(client,auth,hostname,port,username,password,tformat,template):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    myresp={}
    app.logger.debug('inside gettemp')
    app.logger.info(f'Get Template: template={template} format={tformat}')
    if(tformat=="OPT"):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4/'+template)
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    else: #format webtemplate
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL+'template/'+template)
        app.logger.debug('myurl')
        app.logger.debug(myurl)        
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/openehr.wt+json'})
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    if(response.status_code<210 and response.status_code>199):
        if(tformat=="OPT"):
            root = etree.fromstring(response.text)
            responsexml = etree.tostring(root,  encoding='unicode', method='xml', pretty_print=True)
            responsexml=responsexml.replace("#","%23")
            myresp['template']=responsexml
        else:
            nohash=response.text.replace("#","%23")
            myresp['template']=json.dumps(json.loads(nohash),sort_keys=True, indent=4, separators=(',', ': '))
        myresp['text']=response.text
        myresp['status']='success'
        myresp['headers']=response.headers
        myresp['status_code']=  response.status_code  
        app.logger.info(f'GET success for template={template} in format={tformat}')
        return myresp
    else:
        myresp['text']=response.text
        myresp['status']='failure'
        myresp['headers']=response.headers  
        myresp['status_code']=  response.status_code  
        app.logger.warning(f'GET Template failure for template={template} in format={tformat}') 
        return myresp

def posttemp(client,auth,hostname,port,username,password,uploaded_template):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside posttemp')
    client.auth = (username,password)
    root=etree.fromstring(uploaded_template)
    telement=root.find("{http://schemas.openehr.org/v1}template_id")
    template_name=""
    if(telement):   
        for i in telement:
            template_name=i.text
        app.logger.info(f'POST Template : template={template_name}')
    else:
        app.logger.info('POST Template')
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4/')
    response=client.post(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/XML'},
        data=etree.tostring(root))
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    myresp['headers']=response.headers
    myresp['status_code']=response.status_code
    myresp['text']=response.text
    if(response.status_code<210 and response.status_code>199):
        myresp['status']='success'
        app.logger.info(f'Template POST template={template_name} success')
    else:
        myresp['status']='failure'
        app.logger.warning(f'POST Template failure for template={template_name}')
    return myresp

def updatetemp(client,adauth,hostname,port,adusername,adpassword,uploaded_template,templateid):
    from app import app
    app.logger.debug('inside updatetemp')
    app.logger.info(f'Updating template: template={templateid}')
    EHR_SERVER_URL = "http://"+hostname+":"+port+"/ehrbase/"
    client.auth = (adusername,adpassword)
    root=etree.fromstring(uploaded_template)    
    myurl=url_normalize(EHR_SERVER_URL  + 'rest/admin/template/'+templateid)
    response=client.put(myurl,params={'format': 'XML'},headers={'Authorization':adauth,'Content-Type':'application/xml',
                 'prefer':'return=minimal','accept':'application/xml' },
                 data=etree.tostring(root))
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    myresp['headers']=response.headers
    myresp['status_code']=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp['status']='success'
        app.logger.info(f'Update PUT success for template={templateid}')        
        return myresp
    else:
        myresp['status']='failure'
        app.logger.warning(f'Update Template PUT failure for template={templateid}')    
        return myresp

def deltemp(client,adauth,hostname,port,adusername,adpassword,templateid):
    from app import app
    app.logger.debug('inside deletetemp')
    app.logger.info(f'Deleting template: template={templateid}')
    EHR_SERVER_URL = "http://"+hostname+":"+port+"/ehrbase/"
    client.auth = (adusername,adpassword)   
    myurl=url_normalize(EHR_SERVER_URL  + 'rest/admin/template/'+templateid)
    response=client.delete(myurl,headers={'Authorization':adauth })
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    myresp['headers']=response.headers
    myresp['status_code']=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp['status']='success'
        app.logger.info(f'Delete Template success for template={templateid}')        
        return myresp
    else:
        myresp['status']='failure'
        app.logger.warning(f'Delete Template failure for template={templateid}')    
        return myresp

def createehrid(client,auth,hostname,port,username,password,eid):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    app.logger.debug('inside createehrid')
    withehrid=True
    if(eid==""):
        withehrid=False    
    if(not withehrid):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
        app.logger.info("Create ehr without ehrid")
        response=client.post(myurl, params={},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid)
        app.logger.info(f"Create ehr with ehrid: ehrid={eid}")
        response=client.put(myurl, params={},headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        if(withehrid):
            ehrid=response.headers['Location'].split("ehr/")[4]
            app.logger.info(f'EHR creation PUT success with given ehrid={eid}')
            if(eid != ehrid):
                app.logger.debug('ehrid given and obtained do not match')
        else:
            ehrid=response.headers['Location'].split("ehr/")[4]
            app.logger.info(f'EHR creation POST success with ehrid={ehrid}')
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers
        if(withehrid):
            ministr=' PUT with ehrid='+eid
        else:
            ministr=" POST"     
        app.logger.warning('EHR creation"+ministr+" failure')    
    myresp['status_code']=response.status_code 
    app.logger.debug(myresp)
    return myresp

def createehrsub(client,auth,hostname,port,username,password,sid,sna,eid):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside createehrsub')
    client.auth = (username,password)
    body1='''
    {
    "_type" : "EHR_STATUS",
    "name" : {
        "_type" : "DV_TEXT",
        "value" : "EHR Status"
    },
    "subject" : {
        "_type" : "PARTY_SELF",
        "external_ref" : {
            "_type" : "PARTY_REF",
    '''
    body2=f'   "namespace" : "{sna}",'
    body3='''
            "type" : "PERSON",
            "id" : {
            "_type" : "GENERIC_ID",
    '''
    body4=f'	"value" : "{sid}",\n'
    body5='''
          "scheme" : "id_scheme"
            }
        }
    },
    "archetype_node_id" : "openEHR-EHR-EHR_STATUS.generic.v1",
    "is_modifiable" : true,
    "is_queryable" : true
    }
    '''
    body=body1+body2+body3+body4+body5
    app.logger.debug(body)
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
    withehrid=True
    if(eid==""):
        withehrid=False
    if(not withehrid):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
        response=client.post(myurl, params={},headers={'Authorization':auth, \
                'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'},
                data=body)
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid)
        response=client.put(myurl, params={},headers={'Authorization':auth, \
                'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'},
                data=body)       
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        if(withehrid):
            ehrid=response.headers['Location'].split("ehr/")[4]
            app.logger.info(f'EHR creation PUT success with given ehrid={eid}')
            if(eid != ehrid):
                app.logger.debug('ehrid given and obtain do not match')
        else:            
            ehrid=response.headers['Location'].split("ehr/")[4]
            app.logger.info(f'EHR creation POST success with ehrid={ehrid}')
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['headers']=response.headers
        myresp['text']=response.text
        if(withehrid):
            ministr=' PUT with ehrid='+eid
        else:
            ministr=" POST"     
        app.logger.warning('EHR creation"+ministr+" failure')    
    myresp['status_code']=response.status_code 
    return myresp

def getehrid(client,auth,hostname,port,username,password,ehrid):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside getehrid')
    client.auth = (username,password)
    app.logger.debug("launched getehr")
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+ehrid)
    response=client.get(myurl, params={},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
        app.logger.info(f"EHR GET success for ehrid={ehrid}")
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers     
        app.logger.warning(f"EHR GET failure for ehrid={ehrid}")
    myresp['status_code']=response.status_code 
    return myresp

def getehrsub(client,auth,hostname,port,username,password,sid,sna):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside getehrsub')
    client.auth = (username,password)
    app.logger.debug(f'sid={sid} sna={sna}')
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
    response=client.get(myurl, params={'subject_id':sid,'subject_namespace':sna},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        ehrid=response.headers['Location'].split("ehr/")[3]
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
        app.logger.info(f"EHR GET success for subject_id={sid} subject_namespace={sna} => ehrid={ehrid}")
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers       
        app.logger.warning(f"EHR GET failure for subject_id={sid} subject_namespace={sna}")  
    myresp['status_code']=response.status_code 
    return myresp



def postcomp(client,auth,hostname,port,username,password,composition,eid,tid,filetype,check):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside postcomp')
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL + 'ehr/'+eid+'/composition')
        root=etree.fromstring(composition)
        response = client.post(myurl,
                       params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml', \
                           'accept':'application/xml'}, data=etree.tostring(root)) 
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            app.logger.info(f"POST composition success. format={filetype} template={tid}  ehr={eid}")
            if(check=="Yes"):
                checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                    app.logger.info(f"check success. Retrieved and posted Compositions match")
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo 
                    app.logger.warning(f"check failure. Retrieved and posted Compositions do not match")  
        else:
            app.logger.warning(f"POST composition failure. format={filetype} template={tid}  ehr={eid}")
            myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition')
        comp = json.loads(composition)
        compositionjson=json.dumps(comp)
        response = client.post(myurl,params={'format': 'RAW'},headers={'Authorization':auth,'Content-Type':'application/json', \
             'accept':'application/json'}, data=compositionjson) 
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            app.logger.info(f"POST composition success. format={filetype} template={tid}  ehr={eid}")
            if(check=="Yes"):
                checkinfo= compcheck(client,auth,hostname,port,compositionjson,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                    app.logger.info(f"check success. Retrieved and posted Compositions match")
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo
                    app.logger.warning(f"check failure. Retrieved and posted Compositions do not match")
        else:
            myresp["status"]="failure"
            app.logger.warning(f"POST composition failure. format={filetype} template={tid}  ehr={eid}")
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp       
    else:#FLAT JSON
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'composition')
        comp = json.loads(composition)
        compositionjson=json.dumps(comp)
        response = client.post(myurl,
                       params={'ehrId':eid,'templateId':tid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=representation'},
                       data=compositionjson
                      )           
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            app.logger.info(f"POST composition success. format={filetype} template={tid}  ehr={eid}")
            if(check=="Yes"):
                checkinfo= compcheck(client,auth,hostname,port,compositionjson,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                    app.logger.info(f"check success. Retrieved and posted Compositions match")
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo
                    app.logger.warning(f"check failure. Retrieved and posted Compositions do not match")
        else:
            myresp["status"]="failure"
            app.logger.warning(f"POST composition failure. format={filetype} template={tid}  ehr={eid}")
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp

def getcomp(client,auth,hostname,port,username,password,compid,eid,filetype):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside getcomp')
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        #root=etree.fromstring(composition)
        response=client.get(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml','accept':'application/xml'})
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            root = etree.fromstring(response.text)
 #          root.indent(tree, space="\t", level=0)
            myresp['xml'] = etree.tostring(root,  encoding='unicode', method='xml', pretty_print=True)
            myresp["status"]="success"
            app.logger.info(f"Composition GET success compositionid={compid} ehrid={eid} format={filetype}")
        else:
            myresp["status"]="failure"
            app.logger.warning(f"Composition GET failure compositionid={compid} ehrid={eid} format={filetype}")
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        response = client.get(myurl, params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/json'} )
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['json']=response.text
            app.logger.info(f"GET Composition success for compositionid={compid} ehrid={eid} format={filetype}")
        else:
            myresp["status"]="failure"
            app.logger.info(f"GET Composition failure for compositionid={compid} ehrid={eid} format={filetype}")
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp
    else:#FLAT JSON
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'composition/'+compid)
        response = client.get(myurl,
                       params={'ehrId':eid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=representation'},
                      )           
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['flat']=json.dumps(json.loads(response.text)['composition'],sort_keys=True, indent=4, separators=(',', ': '))
            app.logger.info(f"GET Composition success for compositionid={compid} ehrid={eid} format={filetype}")
        else:
            myresp["status"]="failure"
            app.logger.warning(f"GET Composition failure for compositionid={compid} ehrid={eid} format={filetype}")
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp


def postaql(client,auth,hostname,port,username,password,aqltext,qname,version,qtype):
    from app import app
    app.logger.debug('inside postaql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    if(qtype==""):
        qtype="AQL"
    if(version==""):
        version="1.0.0"
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname+"/"+version)
    response = client.put(myurl,params={'type':qtype,'format':'RAW'},headers={'Authorization':auth,'Content-Type':'text/plain'},data=aqltext)
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    app.logger.debug(f"aqltext={aqltext} qname={qname} qtype={qtype} version={version}")
    myresp={}
    myresp["status_code"]=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp["status"]="success"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        app.logger.info(f"AQL POST success")
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        app.logger.warning("AQL POST failure")
    return myresp

def createPageFromBase4querylist(client,auth,hostname,port,username,password,basefile,targetfile):
    from app import app
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug('inside createPageFromBase4querylist')
    client.auth = (username,password)
    myresp={}
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query')
    response = client.get(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'})
    app.logger.debug('Get list queries')
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    if(response.status_code<210 and response.status_code>199):
        myresp['text']=response.text
        myresp['status']='success'
        myresp['headers']=response.headers
        myresp['status_code']=  response.status_code
        results=json.loads(response.text)['versions']
        names=[r['name'] for r in results]
        versions=[r['version'] for r in results]
        
        if(len(names)==0):
            qdata=['No queries available']
        else:
            qdata=[]
            for n,v in zip(names,versions):
                qdata.append(n+'$v'+v)
        myresp['qdata']=qdata
        drmstart=['<select  class="form-select" type="text" id="qdata" name="qdata">']
        drmoptions=['<option>'+q+'</option>' for q in qdata]
        drmstop=['</select>']
        drm=[]
        drm=drmstart+drmoptions+drmstop
        drmstring='\n'.join(drm)
        with open('./templates/'+basefile,'r') as ff:
            lines=ff.readlines()
        with open('./templates/'+targetfile,'w') as fg:
            docopy=True
            for line in lines:
                if('<!--dropdownmenustart-->' in line):
                    docopy=False
                    fg.write(drmstring)
                elif('<!--dropdownmenustop-->' in line):
                    docopy=True
                else:
                    if(docopy):
                        fg.write(line)
        return myresp
    else:
        myresp['text']=response.text
        myresp['status']='failure'
        myresp['headers']=response.headers  
        myresp['status_code']=  response.status_code   
        app.logger.warning("GET queries for createPageFromBase4tquerylist failure")
        return myresp   

def getaql(client,auth,hostname,port,username,password,qname,version):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside getaql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    if(version!=""):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname+"/"+version)
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname)
    response = client.get(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'})
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    app.logger.debug(f"qname={qname} version={version}")
    myresp={}
    myresp["status_code"]=response.status_code
    textok=True
    if 'versions' in response.text:
        if len(json.loads(response.text)['versions'])==0:
            textok=False
    if(response.status_code<210 and response.status_code>199 and textok):
        myresp["status"]="success"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        if ('q' in myresp['text']):
            myresp['aql']=json.loads(myresp['text'])['q']
        app.logger.info("AQL GET success")
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        app.logger.warning("AQL GET failure")
    return myresp  

def runaql(client,auth,hostname,port,username,password,aqltext,qmethod,limit,eid,qparam,qname,version):
    from app import app
    app.logger.debug('inside runaql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    app.logger.debug(f"aqltext={qmethod} qmethod={qmethod} limit={limit} ehrid={eid} qparam={qparam} qname={qname} version={version}")
    client.auth = (username,password)
    if(aqltext !=""): #PASTED QUERY
        if(qmethod=="GET"):    
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')            
            params={}
            params['q']=aqltext
            if(limit != ""):
                params['limit']=limit
            # if(offset != ""):
            #     params['offset']=offset
            # if(fetch != ""):
            #     params['fetch']=fetch
            if(eid != ""):
                params['ehrid']=eid
            if(qparam != ""):
                qplist=qparam.split(",")
                myqp={}
                for qp in qplist:
                    key=qp.split("=")[0]
                    value=qp.split("=")[1]
                    try:
                        val = int(value)
                    except ValueError:
                        val=value
                    myqp[key]=val
                params["query_parameters"]=myqp
            app.logger.debug(f"params={params}")
            response = client.get(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                params=params)
        else: #POST
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')            
            data={}
            data['q']=aqltext
            if(limit != ""):
                data['limit']=limit 
            # if(offset != ""):
            #     data['offset']=offset
            # if(fetch != ""):
            #     data['fetch']=fetch
            if( eid !="" or qparam != ""):
                qv={} 
                if(eid != ""):
                    qv['ehrid']=eid
                if(qparam != ""):
                    qplist=qparam.split(",")
                    for qp in qplist:
                        key=qp.split("=")[0]
                        value=qp.split("=")[1]
                        try:
                            val = int(value)
                        except ValueError:
                            val=value
                            qv[key]=val
                data["query_parameters"]=qv
            app.logger.debug(f"data={data}")
            response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['text']=response.text
            myresp["headers"]=response.headers
            app.logger.info(f"RUN AQL success. qmethod={qmethod}")
        else:
            myresp["status"]="failure"
            myresp['text']=response.text
            myresp["headers"]=response.headers
            app.logger.info(f"RUN AQL failure. qmethod={qmethod}")
        return myresp  
    else: #STORED QUERY
        if(qmethod=="GET"):  
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/'+qname+"/"+version)            
            params={}
            if(limit != ""):
                params['limit']=limit             
            # if(offset != ""):
            #     params['offset']=offset
            # if(fetch != ""):
            #     params['fetch']=fetch
            if(eid != ""):
                params['ehrid']=eid
            if(qparam != ""):
                qplist=qparam.split(",")
                myqp={}
                for qp in qplist:
                    key=qp.split("=")[0]
                    value=qp.split("=")[1]
                    try:
                        val = int(value)
                    except ValueError:
                        val=value
                    myqp[key]=val
                params["query_parameters"]=myqp
            app.logger.debug(f"params={params}")
            response = client.get(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                params=params)
        else: #POST
            myurl=url_normalize(EHR_SERVER_BASE_URL   + 'query/'+qname+"/"+version)       
            data={}
            if(limit != ""):
                data['limit']=limit 
            # if(offset != ""):
            #     data['offset']=offset
            # if(fetch != ""):
            #     data['fetch']=fetch
            if( eid !="" or qparam != ""):
                qv={} 
                if(eid != ""):
                    qv['ehrid']=eid
                if(qparam != ""):
                    qplist=qparam.split(",")
                    for qp in qplist:
                        key=qp.split("=")[0]
                        value=qp.split("=")[1]
                        try:
                            val = int(value)
                        except ValueError:
                            val=value
                            qv[key]=val
                data["query_parameters"]=qv
            app.logger.debug(f"data={data}")
            response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['text']=response.text
            myresp["headers"]=response.headers
            app.logger.info(f"RUN stored AQL success. qmethod={qmethod} qname={qname} version={version}")
        else:
            myresp["status"]="failure"
            myresp['text']=response.text
            myresp["headers"]=response.headers
            app.logger.warning(f"RUN stored AQL failure. qmethod={qmethod} qname={qname} version={version}")
        return myresp  


def compcheck(client,auth,hostname,port,composition,eid,filetype,compid):
    from app import app
    app.logger.debug('      inside compcheck')
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        response=client.get(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml','accept':'application/xml'})
        origcompositiontree=etree.fromstring(composition)
        if(response.status_code<210 and response.status_code>199):
            retrievedcompositiontree= etree.fromstring(response.text)
            comparison_results=myutils.compare_xmls(origcompositiontree,retrievedcompositiontree)
            ndiff=myutils.analyze_comparison_xml(comparison_results)
            if(ndiff>0):
                return comparison_results
            else:
                return None            
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        response = client.get(myurl, params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/json'} )
        origcomposition=json.loads(composition)
        if(response.status_code<210 and response.status_code>199):       
            retrievedcomposition=json.loads(response.text)
            origchanged=myutils.change_naming(origcomposition)
            retrchanged=myutils.change_naming(retrievedcomposition)
            comparison_results=myutils.compare_jsons(origchanged,retrchanged)
            ndiff=myutils.analyze_comparison_json(comparison_results)
            if(ndiff>0):
                return comparison_results
            else:
                return None                  
    else:
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'composition/'+compid)
        response = client.get(myurl,
                       params={'ehrId':eid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=representation'},
                      )           
        origcomposition=json.loads(composition)
        if(response.status_code<210 and response.status_code>199):
            retrievedcomposition=json.loads(response.text)['composition']
            origchanged=myutils.change_naming(origcomposition)
            retrchanged=myutils.change_naming(retrievedcomposition)
            comparison_results=myutils.compare_jsons(origchanged,retrchanged)
            ndiff=myutils.analyze_comparison_json(comparison_results)
            if(ndiff>0):
                return comparison_results
            else:
                return None
            
    
    
def get_dashboard_info(client,auth,hostname,port,username,password,adauth,adusername,adpassword):
    from app import app
    app.logger.debug('inside get_dashboard info')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)            
    #get aql stored
    myresp={}
    myresp['status']='failure'
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/')
    responseaql = client.get(myurl, headers={'Authorization':auth,'Content-Type': 'application/json'})                     
    app.logger.debug('Get AQL stored')
    app.logger.debug('Response Url')
    app.logger.debug(responseaql.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(responseaql.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(responseaql.text)
    app.logger.debug('Response Headers')
    app.logger.debug(responseaql.headers)
    if(responseaql.status_code<210 and responseaql.status_code>199):
        resultsaql=json.loads(responseaql.text)['versions']
        myresp['aql']=len(resultsaql) 
        myresp['status']='success1'
        app.logger.debug('Dashboard: GET AQL stored success')
    else:
        myresp['text']=responseaql.text
        myresp['headers']=responseaql.headers
        app.logger.warning("Dashboard: GET AQL failure")
        return myresp
    # get total ehrs  
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')
    data={}
    aqltext="select e/ehr_id/value FROM EHR e"
    data['q']=aqltext
    response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)  
    if(response.status_code<210 and response.status_code>199):
        results=json.loads(response.text)['rows']
        myresp['ehr']=len(results) 
        myresp['status']='success2'
        app.logger.debug('Dashboard: GET list ehrs success')
    else:
        myresp['text']=response.text
        myresp['headers']=response.headers
        app.logger.warning('Dashboard: GET list ehrs failure')
        return myresp

    #get ehrid,compid, templateid list
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')
    data={}
    aqltext="select e/ehr_id/value,c/uid/value,c/archetype_details/template_id/value from EHR e contains COMPOSITION c"
    data['q']=aqltext
    response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
  
    if(response.status_code<210 and response.status_code>199):
        results=json.loads(response.text)['rows']
        myresp['composition']=len(results)
        myresp['status']='success3'
        app.logger.debug('Dashboard: GET list ehrs,compositions,templates used success')
    else:
        myresp['text']=response.text
        myresp['headers']=response.headers
        app.logger.warning('Dashboard: GET list ehrs,compositions,templates used failure')
        return myresp 
    #calculate total ehr in use    
    ehr=set(r[0] for r in results)
    myresp['uehr']=len(ehr)     
    #total templates in use
    templates_in_use=set(r[2] for r in results)
    myresp['utemplate']=len(templates_in_use)     
    #get templates
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4')
    response2=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    app.logger.debug('Response Url')
    app.logger.debug(response2.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response2.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response2.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response2.headers)
  
    if(response2.status_code<210 and response2.status_code>199):
        app.logger.debug(f"Dashboard: GET all templates success")
        resultstemp=json.loads(response2.text)
        myresp['template']=len(resultstemp)
        templates=[rt['template_id'] for rt in resultstemp]
        myresp['status']='success4'
        #compositions per ehr
        c=[0]*len(ehr)
        for i,e in enumerate(ehr):
            c[i]=0
            for r in results:
                if(r[0]==e):
                    c[i]+=1
        cpe={i:c.count(i) for i in c}
        #compositions per template
        d={}
        for i,t in enumerate(templates_in_use):
            for r in results:
                if(r[2]==t):
                    if t in d:
                        d[t]+=1
                    else:
                        d[t]=1
                
        #fill bar and pie variables
        myresp['bar_label']=list(cpe.keys())
        myresp['bar_value']=list(cpe.values())  
        myresp['bar_max']=max(myresp['bar_value'],default=0)      
        myresp['pie_label']=list(d.keys())
        myresp['pie_value']=list(d.values())
    else:
        app.logger.warning(f"Dashboard: Get all templates failure")
        myresp['text']=response2.text
        myresp['headers']=response2.headers
        return myresp               

#   additional info from management/env management/info if available and admin credentials provided
# The first,second,third,fourth and sixth for env,info in .env.ehrbase must be set 
#MANAGEMENT_ENDPOINTS_WEB_EXPOSURE=env,health,info,metrics,prometheus
#MANAGEMENT_ENDPOINTS_WEB_BASEPATH=/management
#MANAGEMENT_ENDPOINT_ENV_ENABLED=true
#MANAGEMENT_ENDPOINT_HEALTH_ENABLED=true
#MANAGEMENT_ENDPOINT_HEALTH_DATASOURCE_ENABLED=true
#MANAGEMENT_ENDPOINT_INFO_ENABLED=true
#MANAGEMENT_ENDPOINT_METRICS_ENABLED=true

    if(adusername!=""):        
        client.auth = (adusername,adpassword)
        EHR_SERVER = "http://"+hostname+":"+port+"/ehrbase/"
        myurl=url_normalize(EHR_SERVER  + 'management/info')
        resp = client.get(myurl,headers={'Authorization':adauth,'Content-Type':'application/JSON'})
        app.logger.debug('Response Url')
        app.logger.debug(resp.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(resp.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(resp.text)
        app.logger.debug('Response Headers')
        app.logger.debug(resp.headers)     
        if(resp.status_code<210 and resp.status_code>199):
            app.logger.debug("Dashboard: GET management info success")
            myresp['status']='success5'
            info=json.loads(resp.text)['build']
            myinfo={}
            myinfo['openehr_sdk']=info['openEHR_SDK']['version']
            myinfo['ehrbase_version']=info['version']
            myinfo['archie']=info['archie']['version']
            myresp['info']=myinfo
        else:
            app.logger.warning("Dashboard: GET management info failure")
            myresp['text']=resp.text
            myresp['headers']=resp.headers
            return myresp 
    
        myurl=url_normalize(EHR_SERVER  + 'management/env')
        resp2 = client.get(myurl,headers={'Authorization':adauth,'Content-Type':'application/JSON'})
        app.logger.debug('Response Url')
        app.logger.debug(resp2.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(resp2.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(resp2.text)
        app.logger.debug('Response Headers')
        app.logger.debug(resp2.headers)         
        if(resp2.status_code<210 and resp2.status_code>199):
            app.logger.debug("Dashboard: GET management env success")
            env=json.loads(resp2.text)
            myresp['status']='success6'
            myenv={}
            myenv["activeProfiles"]=env["activeProfiles"]    
            myenv['Java']= env["propertySources"][2]["properties"]["java.specification.vendor"]["value"] + " " \
                            + env["propertySources"][2]['properties']["java.home"]["value"] 
            myenv['JavaVM']=   env["propertySources"][2]['properties']["java.vm.name"]["value"]+ \
                        " "+ env["propertySources"][2]['properties']['java.vm.vendor']['value'] + \
                        " " + env["propertySources"][2]['properties']["java.vm.version"]["value"]                                
            myenv["OS"]=env["propertySources"][2]['properties']['os.name']['value'] +  \
                    " "+ env["propertySources"][2]['properties']["os.arch"]["value"]+ \
                    " "+  env["propertySources"][2]['properties']["os.version"]["value"] 
            myresp['env']=myenv
            gen_properties={}
            end_properties={}
            gen_properties["CACHE_ENABLED"]=env["propertySources"][3]["properties"]["CACHE_ENABLED"]["value"]
            end_properties["MANAGEMENT_ENDPOINTS_WEB_EXPOSURE"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINTS_WEB_EXPOSURE"]
            end_properties["MANAGEMENT_ENDPOINTS_WEB_BASEPATH"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINTS_WEB_BASEPATH"]
            end_properties["MANAGEMENT_ENDPOINT_INFO_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_INFO_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_PROMETHEUS_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_PROMETHEUS_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_HEALTH_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_HEALTH_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_METRICS_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_METRICS_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_ENV_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_ENV_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_HEALTH_PROBES_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_HEALTH_PROBES_ENABLED"]
            end_properties["MANAGEMENT_ENDPOINT_HEALTH_DATASOURCE_ENABLED"]=env["propertySources"][3]["properties"]["MANAGEMENT_ENDPOINT_HEALTH_DATASOURCE_ENABLED"]
            myresp['end_properties']=end_properties
            db={}
            db["username"]=env["propertySources"][3]["properties"]["DB_USER"]["value"]
            db["password"]=env["propertySources"][3]["properties"]["DB_PASS"]["value"]
            db["url"]=env["propertySources"][3]["properties"]["DB_URL"]["value"]
            myresp["db"]=db
            aql={}
            if "ENV_AQL_ARRAY_DEPTH" in env["propertySources"][3]["properties"]:
                aql["ENV_AQL_ARRAY_DEPTH"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_DEPTH"]["value"]
                aql["ENV_AQL_ARRAY_IGNORE_NODE"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_IGNORE_NODE"]["value"]
                aql["ENV_AQL_ARRAY_DEPTH"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_DEPTH"]["value"]
                aql["ENV_AQL_ARRAY_IGNORE_NODE"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_IGNORE_NODE"]["value"]
            else:
                aql["ENV_AQL_ARRAY_DEPTH"]='Unknown'
                aql["ENV_AQL_ARRAY_IGNORE_NODE"]='Unknown'
                aql["ENV_AQL_ARRAY_DEPTH"]='Unknown'
                aql["ENV_AQL_ARRAY_IGNORE_NODE"]='Unknown'

            aql["server.aqlConfig.useJsQuery"]=env["propertySources"][4]["properties"]["server.aqlConfig.useJsQuery"]["value"]
            aql["server.aqlConfig.ignoreIterativeNodeList"]=env["propertySources"][4]['properties']["server.aqlConfig.ignoreIterativeNodeList"]["value"]
            aql["server.aqlConfig.iterationScanDepth"]=env["propertySources"][4]['properties']["server.aqlConfig.iterationScanDepth"]["value"]
            myresp["aqlinfo"]=aql
            gen_properties["SERVER_NODENAME"]=env["propertySources"][3]['properties']["SERVER_NODENAME"]["value"]
            gen_properties["HOSTNAME"]=env["propertySources"][3]['properties']["HOSTNAME"]["value"]
            gen_properties["LANG"]=env["propertySources"][3]['properties']["LANG"]["value"]
            gen_properties["SECURITY_AUTHTYPE"]=env["propertySources"][3]['properties']["SECURITY_AUTHTYPE"]["value"]
            if( "SYSTEM_ALLOW_TEMPLATE_OVERWRITE") in env["propertySources"][3]['properties']:
                gen_properties["SYSTEM_ALLOW_TEMPLATE_OVERWRITE"]=env["propertySources"][3]['properties']["SYSTEM_ALLOW_TEMPLATE_OVERWRITE"]["value"]
            else:
                gen_properties["SYSTEM_ALLOW_TEMPLATE_OVERWRITE"]='Unknown'
            myresp["gen_properties"]=gen_properties
            terminology={}
            terminology["validation.external-terminology.enabled"]=env["propertySources"][5]['properties']["validation.external-terminology.enabled"]["value"]
            terminology["validation.external-terminology.provider.fhir.type"]=env["propertySources"][5]['properties']["validation.external-terminology.provider.fhir.type"]["value"]
            terminology["validation.external-terminology.provider.fhir.url"]=env["propertySources"][5]['properties']["validation.external-terminology.provider.fhir.url"]["value"]
            myresp["terminology"]=terminology
            plugin={}
            plugin["plugin-manager.plugin-dir"]=env["propertySources"][5]['properties']["plugin-manager.plugin-dir"]["value"]
            plugin["plugin-manager.plugin-config-dir"]=env["propertySources"][5]['properties']["plugin-manager.plugin-config-dir"]["value"]
            plugin["plugin-manager.enable"]=env["propertySources"][5]['properties']["plugin-manager.enable"]["value"]
            plugin["plugin-manager.plugin-context-path"]=env["propertySources"][5]['properties']["plugin-manager.plugin-context-path"]["value"]
            myresp['plugin']=plugin   
        else:
            app.logger.warning(f"Dashboard: GET management env failure")
            myresp['text']=resp2.text
            myresp['headers']=resp2.headers
            return myresp 
    
        myurl=url_normalize(EHR_SERVER  + 'management/health')
        resp3 = client.get(myurl,headers={'Authorization':adauth,'Content-Type':'application/JSON'})
        app.logger.debug('Response Url')
        app.logger.debug(resp3.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(resp3.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(resp3.text)
        app.logger.debug('Response Headers')
        app.logger.debug(resp3.headers)       
        if(resp3.status_code<210 and resp3.status_code>199):
            app.logger.info("Dashboard: GET management health success")
            health=json.loads(resp3.text)
            myresp["db"]["db"]=health["components"]["db"]["details"]["database"]
            disk={}
            disk["total_space"]=health["components"]["diskSpace"]["details"]["total"]
            disk["free_space"]=health["components"]["diskSpace"]["details"]["free"]
            myresp["disk"]=disk
            myresp['status']='success7'
        else:
            app.logger.warning("Dashboard: GET management health failure")
            myresp['text']=resp3.text
            myresp['headers']=resp3.headers
            return myresp             
        return myresp


def postbatch1(client,auth,hostname,port,username,password,uploaded_files,tid,check,sidpath,snamespace,filetype,myrandom,comps,inlist):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside postbatch1')
    ehrslist=[]
    number_of_files=len(uploaded_files)
    if(inlist==True):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        client.auth = (username,password)            
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')
        data={}
        aqltext="select e/ehr_id/value FROM EHR e"
        data['q']=aqltext
        response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
        app.logger.debug('Response Url')
        app.logger.debug(response.url)
        app.logger.debug('Response Status Code')
        app.logger.debug(response.status_code)
        app.logger.debug('Response Text')
        app.logger.debug(response.text)
        app.logger.debug('Response Headers')
        app.logger.debug(response.headers)
        if(response.status_code<210 and response.status_code>199):
            app.logger.debug("Postbatch1: get all Ehrs success")
            results=json.loads(response.text)['rows']
            ehrslist=[r[0] for r in results]       
            if len(ehrslist)==0:
                inlist=False
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"  
        succ=0
        csucc=0
        compids=[]
        eids=[]
        myresp={}
        filenamefailed=[]
        filenamecheckfailed=[]
        for uf,composition in zip(uploaded_files,comps):
            root=etree.fromstring(composition)
            #create EHRID
            if(myrandom):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,composition)
                app.logger.debug(f'sid found={sid}')
                if(sid==-1):
                    app.logger.warning(f"Chosen field={sidpath} not found in file. Couldn't obtain a valid subject_id")
                    myresp['status']='failed'
                    myresp['error']='Error while getting the SubjectID. Chosen Field not found in file' + uf.filename
                    myresp['success']=succ
                    myresp['csuccess']=csucc
                    myresp['filenamefailed']=filenamefailed
                    myresp['filenamecheckfailed']=filenamecheckfailed
                    myresp['compositionid']=compids
                    myresp['ehrid']=eids
                    return myresp
            eid=""
            if(inlist==False):
                resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
                if(resp10['status']!='success'):
                    if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                        #get ehr summary by subject_id , subject_namespace
                        payload = {'subject_id':sid,'subject_namespace':sna}
                        ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                        eid=json.loads(ehrs.text)["ehr_id"]["value"]
                        app.logger.debug('ehr already existent')
                        eids.append(eid)
                        app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
                else:
                    eid=resp10['ehrid']
                    eids.append(eid)
            else:
                eid=random.choice(ehrslist)
                eids.append(eid)
            myurl=url_normalize(EHR_SERVER_BASE_URL + 'ehr/'+eid+'/composition')
            response = client.post(myurl,
                       params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml', \
                           'accept':'application/xml'}, data=etree.tostring(root)) 
            app.logger.debug('Response Url')
            app.logger.debug(response.url)
            app.logger.debug('Response Status Code')
            app.logger.debug(response.status_code)
            app.logger.debug('Response Text')
            app.logger.debug(response.text)
            app.logger.debug('Response Headers')
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                app.logger.info(f'postbatch1: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch1: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch1: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch1: POST failure filename={uf.filename} ehrid={eid}')
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc==number_of_files):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            app.logger.info(f"{succ}/{number_of_files} files successfully POSTed")
            if(succ==number_of_files):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eids
        myresp['compositionid']=compids
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        myresp['error']=""
        return myresp
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        succ=0
        csucc=0
        eids=[]
        compids=[]
        myresp={}
        filenamefailed=[]
        filenamecheckfailed=[]
        for uf,composition in zip(uploaded_files,comps):
#            uf.stream.seek(0)
#            composition=uf.read()
            comp = json.loads(composition)
            compositionjson=json.dumps(comp)
            #create EHRID
            if(myrandom):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,comp)
                app.logger.debug(f'sid found={sid}')
                if(sid==-1):
                    app.logger.warning(f"Chosen field={sidpath} not found in file. Couldn't obtain a valid subject_id")
                    myresp['status']='failed'
                    myresp['error']='Error while getting the SubjectID. Chosen Field not found in file' + uf.filename
                    myresp['nsuccess']=succ
                    myresp['csuccess']=csucc
                    myresp['filenamefailed']=filenamefailed
                    myresp['filenamecheckfailed']=filenamecheckfailed
                    myresp['compositionid']=compids
                    myresp['ehrid']=eids
                    return myresp
            eid=""
            if(inlist==False):            
                resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
                if(resp10['status']!='success'):
                    if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                        #get ehr summary by subject_id , subject_namespace
                        payload = {'subject_id':sid,'subject_namespace':sna}
                        ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                        eid=json.loads(ehrs.text)["ehr_id"]["value"]
                        app.logger.debug('ehr already existent')
                        eids.append(eid)
                        app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
                else:
                    eid=resp10['ehrid']
                    eids.append(eid)
            else:
                eid=random.choice(ehrslist)
                eids.append(eid)                  
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition')
            response = client.post(myurl,params={'format': 'RAW'},headers={'Authorization':auth,'Content-Type':'application/json', \
             'accept':'application/json'}, data=compositionjson)   
            app.logger.debug('Response Url')
            app.logger.debug(response.url)
            app.logger.debug('Response Status Code')
            app.logger.debug(response.status_code)
            app.logger.debug('Response Text')
            app.logger.debug(response.text)
            app.logger.debug('Response Headers')
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                app.logger.info(f'postbatch1: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch1: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch1: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch1: POST failure filename={uf.filename} ehrid={eid}')
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            app.logger.info(f"{succ}/{number_of_files} files successfully POSTed")
            if(succ!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eids                
        myresp['compositionid']=compids
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        myresp['error']=""
        return myresp

    else:#FLAT JSON
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        succ=0
        csucc=0
        compids=[]
        eids=[]
        myresp={}
        filenamefailed=[]
        filenamecheckfailed=[]
        for uf,composition in zip(uploaded_files,comps):
            comp = json.loads(composition)
            compositionjson=json.dumps(comp) 
            #create EHRID
            if(myrandom):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,comp)
                app.logger.debug(f'sid found={sid}')
                if(sid==-1):
                    app.logger.warning(f"Chosen field={sidpath} not found in file. Couldn't obtain a valid subject_id")
                    myresp['status']='failed'
                    myresp['error']='Error while getting the SubjectID. Chosen Field not found in file' + uf.filename
                    myresp['nsuccess']=succ
                    myresp['csuccess']=csucc
                    myresp['filenamefailed']=filenamefailed
                    myresp['filenamecheckfailed']=filenamecheckfailed
                    myresp['compositionid']=compids
                    myresp['ehrid']=eids
                    return myresp
            eid=""
            if(inlist==False):
                resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
                if(resp10['status']!='success'):
                    if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                        #get ehr summary by subject_id , subject_namespace
                        payload = {'subject_id':sid,'subject_namespace':sna}
                        ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                        eid=json.loads(ehrs.text)["ehr_id"]["value"]
                        app.logger.debug('ehr already existent')
                        eids.append(eid)
                        app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
                else:
                    eid=resp10['ehrid']
                    eids.append(eid)
            else:
                eid=random.choice(ehrslist)
                eids.append(eid)                    
            EHR_SERVER_BASE_URL_FLAT = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"    
            myurl=url_normalize(EHR_SERVER_BASE_URL_FLAT  + 'composition')
            response = client.post(myurl,
                       params={'ehrId':eid,'templateId':tid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=minimal'},
                       data=compositionjson
                      )
            app.logger.debug('Response Url')
            app.logger.debug(response.url)
            app.logger.debug('Response Status Code')
            app.logger.debug(response.status_code)
            app.logger.debug('Response Text')
            app.logger.debug(response.text)
            app.logger.debug('Response Headers')
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                app.logger.info(f'postbatch1: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')                
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch1: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch1: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch1: POST failure filename={uf.filename} ehrid={eid}')
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            app.logger.info(f"{succ}/{number_of_files} files successfully POSTed and checked")
            if(succ!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eids
        myresp['compositionid']=compids           
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        myresp['error']=""
        return myresp


def findpath(filetype,sidpath,composition):
    from app import app
    app.logger.debug('      inside findpath')
    elements=sidpath.split("/")
    elements=[el.lower().replace("_"," ") for el in elements]
    if(filetype=="XML"):
        root=etree.fromstring(composition)
        tree = etree.ElementTree(root)
        matches=[]
        for value in tree.iter('value'):
            if(elements[-1] in value.text.lower()):
                matches.append(tree.getelementpath(value))                
        if(len(matches)==1):
            sidp='value'.join(matches[0].rsplit('name', 1))
            return tree.findtext(sidp)
        elif(len(matches)>1):
            mm=[]
            for match in matches:
                pelements=match.split["/"]
                count=0
                for pe in pelements:
                    for el in elements[:-1]:
                        if(el==pe):
                            count+=1
                mm.append(count)
            max_item = max(mm)
            index=mm.index(max_item)
            sidp='value'.join(matches[index].rsplit('name', 1))
            return tree.findtext(sidp)
        else:
            return -1
    elif(filetype=="JSON"):
        matches=[]
        findjson("value", elements[-1], composition, "", matches) 
        if(len(matches)==1):
            elm=matches[0].split('/')
            elm[-2]='value'
            mystring=composition
            for e in elm:
                es=e.split("[")
                if len(es)>1:
                    mystring=mystring[es[0]]
                    es2=es[1].split(']')
                    mystring=mystring[int(es2[0])]
                else:
                    mystring=mystring[e]
      #      context/other_context/items[0]/items[0]/name/value
#   jsonstring['context']['other_context']['items'][0]['items'][0]['value']['value']
            return mystring
        elif(len(matches)>1):
            mm=[]
            for match in matches:
                pelements=match.split["/"]
                count=0
                for pe in pelements:
                    for el in elements[:-1]:
                        if(el==pe):
                            count+=1
                mm.append(count)
            max_item = max(mm)
            index=mm.index(max_item)
            elm=matches[index].split('/')
            elm[-2]='value'
            mystring=composition
            for e in elm:
                es=e.split("[")
                if len(es)>1:
                    mystring=mystring[es[0]]
                    es2=es[1].split(']')
                    mystring=mystring[int(es2[0])]
                else:
                    mystring=mystring[e]            
            return mystring
        else:
            return -1
    else:#FLAT JSON
        matches=[]
        for c in composition:
            if(elements[-1] in c.lower().replace("_"," ")):
                    matches.append(c)
        if(len(matches)==1):
            return composition[matches[0]]
        elif(len(matches)>1):
            mm=[]
            for match in matches:
                pelements=match.split["/"]
                count=0
                for pe in pelements:
                    for el in elements:
                        if(el==pe):
                            count+=1
                mm.append(count)
            max_item = max(mm)
            index=mm.index(max_item)
            return composition[matches[index]]
        else:
            return -1

def findjson(keytofind, valuetofind, JSON, path, all_paths):
    from app import app
    app.logger.debug('      inside findjson')
    if keytofind in JSON and type(JSON[keytofind])==str and valuetofind in JSON[keytofind].lower():
        path = path + keytofind 
        all_paths.append(path)
    for i,key in enumerate(JSON):
        if(type(JSON) is list):
            findjson(keytofind, valuetofind, key, path + '['+str(i)+']/',all_paths)
        else:
            if isinstance(JSON[key], dict):
                findjson(keytofind, valuetofind, JSON[key], path + key + '/',all_paths)
            elif(type(JSON[key]) is list):
                findjson(keytofind, valuetofind, JSON[key], path + key,all_paths)



def randomstring(N=10,chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(N))


def postbatch2(client,auth,hostname,port,username,password,uploaded_files,tid,check,eid,filetype,random,comps):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside postbatch2')
    number_of_files=len(uploaded_files)
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"  
        succ=0
        csucc=0
        compids=[]
        filenamefailed=[]
        filenamecheckfailed=[]
        #create EHRID
        if(random):
            sid=randomstring()
            sna='fakenamespace'
            eid=""
            resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    app.logger.debug('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(client,auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                myerror="couldn't create ehrid="+eid+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                app.logger.debug(myerror)
                myresp['error']=myerror
                myresp['status']='failed'
                myresp['success']=succ
                myresp['csuccess']=csucc
                myresp['filenamefailed']=filenamefailed
                myresp['filenamecheckfailed']=filenamecheckfailed
                myresp['compositionid']=compids
                myresp['ehrid']=eid          
            else:
                eid=resp10['ehrid']

        for uf,composition in zip(uploaded_files,comps):
#            uf.stream.seek(0)
#            composition=uf.read()
            root=etree.fromstring(composition)
            myurl=url_normalize(EHR_SERVER_BASE_URL + 'ehr/'+eid+'/composition')
            response = client.post(myurl,
                       params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml', \
                           'accept':'application/xml'}, data=etree.tostring(root)) 
            app.logger.debug(response.text)
            app.logger.debug(response.status_code)
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                app.logger.info(f'postbatch2: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch2: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch2: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch2: POST failure filename={uf.filename} ehrid={eid}')
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            if(succ!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eid
        myresp['compositionid']=compids
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        return myresp
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        succ=0
        csucc=0
        compids=[]
        myresp={}
        filenamefailed=[]
        filenamecheckfailed=[]
        #create EHRID
        if(random):
            sid=randomstring()
            sna='fakenamespace'
            eid=""
            resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    app.logger.debug('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(client,auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                myerror=f"couldn't create ehrid={eid}"+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                app.logger.debug(myerror)
                myresp['error']=myerror
                myresp['status']='failed'
                myresp['success']=succ
                myresp['csuccess']=csucc
                myresp['filenamefailed']=filenamefailed
                myresp['filenamecheckfailed']=filenamecheckfailed
                myresp['compositionid']=compids
                myresp['ehrid']=eid          
            else:
                eid=resp10['ehrid']

        for uf,composition in zip(uploaded_files,comps):
#            uf.stream.seek(0)
#            composition=uf.read()
            comp = json.loads(composition)
            compositionjson=json.dumps(comp)
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition')
            response = client.post(myurl,params={'format': 'RAW'},headers={'Authorization':auth,'Content-Type':'application/json', \
             'accept':'application/json'}, data=compositionjson)   
            app.logger.debug('Response Url')
            app.logger.debug(response.url)
            app.logger.debug('Response Status Code')
            app.logger.debug(response.status_code)
            app.logger.debug('Response Text')
            app.logger.debug(response.text)
            app.logger.debug('Response Headers')
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                app.logger.info(f'postbatch2: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch2: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch2: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:       
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch2: POST failure filename={uf.filename} ehrid={eid}')
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            app.logger.info(f"{succ}/{number_of_files} files successfully POSTed")
            if(succ!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eid               
        myresp['compositionid']=compids
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        myresp['error']=""
        return myresp
    else:#FLAT JSON
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        succ=0
        csucc=0
        compids=[]
        myresp={}
        filenamefailed=[]
        filenamecheckfailed=[]
        EHR_SERVER_BASE_URL_FLAT = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"    
        #create EHRID
        if(random):
            sid=randomstring()
            sna='fakenamespace'
            eid=""
            resp10=createehrsub(client,auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    app.logger.debug('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    app.logger.debug(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(client,auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'EHR with this ID already exists' in json.loads(resp10['text'])['message']):
                    pass
                else:
                    myerror=f"couldn't create ehrid={eid}"+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                    app.logger.debug(myerror)
                    myresp['error']=myerror
                    myresp['status']='failed'
                    myresp['success']=succ
                    myresp['csuccess']=csucc
                    myresp['filenamefailed']=filenamefailed
                    myresp['filenamecheckfailed']=filenamecheckfailed
                    myresp['compositionid']=compids
                    myresp['ehrid']=eid          
            else:
                eid=resp10['ehrid']

        for uf,composition in zip(uploaded_files,comps):
            comp = json.loads(composition)
            compositionjson=json.dumps(comp) 
            myurl=url_normalize(EHR_SERVER_BASE_URL_FLAT  + 'composition')
            response = client.post(myurl,
                       params={'ehrId':eid,'templateId':tid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=minimal'},
                       data=compositionjson
                      )
            app.logger.debug('Response Url')
            app.logger.debug(response.url)
            app.logger.debug('Response Status Code')
            app.logger.debug(response.status_code)
            app.logger.debug('Response Text')
            app.logger.debug(response.text)
            app.logger.debug('Response Headers')
            app.logger.debug(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                app.logger.info(f'postbatch2: POST success composition={cid} format={filetype} filename={uf.filename} ehrid={eid}')                
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(client,auth,hostname,port,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                        app.logger.info(f'postbatch2: successfully checked composition={cid} filename={uf.filename} ehrid={eid}')
                    else:
                        filenamecheckfailed.append(uf.filename)
                        app.logger.warning(f'postbatch2: unsuccessfully checked composition={cid} filename={uf.filename} ehrid={eid}')
            else:
                filenamefailed.append(uf.filename)
                app.logger.warning(f'postbatch2: POST failure filename={uf.filename} ehrid={eid}') 
        if(check=='Yes'):
            app.logger.info(f"{csucc}/{number_of_files} files successfully POSTed and checked")
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
            app.logger.info(f"{succ}/{number_of_files} files successfully POSTed and checked")
            if(succ!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        myresp['ehrid']=eid
        myresp['compositionid']=compids           
        myresp['nsuccess']=succ
        myresp['csuccess']=csucc
        myresp['filenamefailed']=filenamefailed
        myresp['filenamecheckfailed']=filenamecheckfailed
        myresp['error']=""
        return myresp


def examplecomp(client,auth,hostname,port,username,password,template_name):
    from app import app
    client.auth = (username,password)
    app.logger.debug('inside examplecomp')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"
    myurl=url_normalize(EHR_SERVER_BASE_URL+'template/'+template_name+'/example')  
    response = client.get(myurl,
                       params={'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json'}
                        )
    app.logger.debug('Response Url')
    app.logger.debug(response.url)
    app.logger.debug('Response Status Code')
    app.logger.debug(response.status_code)
    app.logger.debug('Response Text')
    app.logger.debug(response.text)
    app.logger.debug('Response Headers')
    app.logger.debug(response.headers)
    myresp={}
    myresp["status_code"]=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp["status"]="success"
        myresp['composition']=response.text
        app.logger.info(f'GET Example composition success template={template_name}')
    else:
        myresp["status"]="failure"
        app.logger.warning(f'GET Example composition failure template={template_name}')
    myresp['text']=response.text
    myresp["headers"]=response.headers
    return myresp


def createform(client,auth,hostname,port,username,password,template_name):
    from app import app
    app.logger.debug('inside createform')
    resp=examplecomp(client,auth,hostname,port,username,password,template_name)
    if(resp['status']=='failure'):
        return resp
    else:
        flatcomp=json.loads(resp['composition'])
        listcontext=[]
        listcontent=[]
        listcontext,listcontent,listcontextvalues,listcontentvalues=fillListsfromComp(flatcomp)
        contexttoadd=[]
        contenttoadd=[]
        varcontext=[]
        varcontent=[]
        # varlistctx=[]
        # varlistcnt=[]
        contexttoadd,varcontext,ivarstart=fillforms(listcontext,listcontextvalues,0)
        contenttoadd,varcontent,ivarend=fillforms(listcontent,listcontentvalues,ivarstart)
        createformfile(contexttoadd,varcontext,contenttoadd,varcontent,template_name)
        msg={}
        msg['status']='success'
        return msg

def createformfile(contexttoadd,varcontext,contenttoadd,varcontent,template_name):
    from app import app
    app.logger.debug('      inside createformfile')
    c1=[]
    c3=[]
    c5=[]
    contextstart='HERE NORE CONTEXT'
    contentstart='HERE THE CONTENT'
    with open('./templates/base.html','r') as bf:
        context=bf.readlines()
    icontext=0
    for i,line in enumerate(context):
        if(contextstart in line):
            c1=context[:i]
            icontext=i
        if(contentstart in line):
            c3=context[icontext+1:i]
            c5=context[i+1:]

    varline='<!-- '
    varctx=','.join(','.join(b) for b in varcontext)
    varline2=','
    varcnt=','.join(','.join(b) for b in varcontent)
    varend=' -->'
        
    formstring=''
    with open('./templates/form.html','w') as ff:
        ff.write("\n".join(c1))
        ff.write("\n".join(contexttoadd))
        ff.write("\n".join(c3))
        ff.write("\n".join(contenttoadd))
        ff.write("\n".join(c5))
        ff.write(varline+template_name+varend)
        ff.write(varline+str(varctx)+varline2+str(varcnt)+varend)

def fillforms(listc,listcvalues,ivarstart):
    from app import app
    app.logger.debug('      inside fillforms')
    startrow='<div class="row">'
    endrow='</div>'
    startcol='   <div class="col">'
    endcol='   </div>'
    label1='<label  class="form-label" for="category">'
    label3='</label><br>'
    control1='<input  class="form-control" type="text" id="'
    control3='" name="'
    control5='" placeholder="'
    control7='">'
    ctoadd=[]
    varc=[]
    #fill context or content
    i=ivarstart
    j=0
    for c,v in zip(listc,listcvalues):
        if(j%2==0):
            if(j%2!=0):
                ctoadd.append(endrow)
            ctoadd.append(startrow)
        ctoadd.append(startcol)
        mylabel=c[0].split('|')[0]
        ctoadd.append(label1+mylabel+label3)
        for ci,vi in zip(c,v):
            segment=ci.split('/')[-1].split('|')
            piece=""
            if(len(segment)>1):
                piece=segment[1]
            else:
                piece=segment[0]
            ctoadd.append(control1+'var'+str(i)+control3+
                'var'+str(i)+control5+piece+' ex '+ str(vi) +control7)
            varc.append(['var'+str(i),ci])
            i=i+1
        j=j+1
        ctoadd.append('<br><br>')
        ctoadd.append(endcol)
    if(j%2 !=0):#add void col if needed
        ctoadd.append(startcol)
        ctoadd.append(endcol)
    return ctoadd,varc,i



def fillListsfromComp(flatcomp):
    from app import app
    app.logger.debug('      inside fillListsfromComp')
    listcontext=[]
    listcontextvalues=[]
    listcontent=[]
    listcontentvalues=[]
    words1=['context','ctx','category','language','territory','composer']
    words2=['location','start_time','_end_time','setting','_health_care_facility','_participation','_uid']
    words3=['context','ctx']
    lastel=""
    for el in flatcomp:
        second=el.split('/')[1].split('|')[0]
        last=el.split('/')[-1]
        if(second in words1):
            #check if in already considered fields
            if(second in words3):
                third=el.split('/')[2].split('|')[0]
                if(third in words2):
                    app.logger.debug('not in context or content')
                    continue
                else:
                    #check if left part already found
                    if(el.split('|')[0]==lastel.split('|')[0]):
                        listcontext[-1].append([el])
                        listcontextvalues[-1].append(flatcomp[el])
                    else:
                        listcontext.append([el])
                        listcontextvalues.append([flatcomp[el]])
                    lastel=el
            else:
                pass
        else:
            #check if left part already found
            if(el.split('|')[0]==lastel.split('|')[0]):
                listcontent[-1].append(el)
                listcontentvalues[-1].append(flatcomp[el])
            else:
                listcontent.append([el])
                listcontentvalues.append([flatcomp[el]])
            lastel=el
    return listcontext,listcontent,listcontextvalues,listcontentvalues

def readform():
    from app import app
    app.logger.debug('inside readform')
    with open('./templates/form.html','r') as ff:
        allfile=ff.readlines()
    formstring=''.join(allfile)
    return formstring

def postform(client,auth,hostname,port,username,password,formname):
    from app import app
    app.logger.debug('inside postform')
    #retrieve var and path
    tid=formname
    formname=formname.lower()
    with open('./templates/form.html','r') as ff:
        allfile=ff.readlines()
    varinfo=allfile[-1].split('<!--')[1].split('-->')[0].strip()
    varinfolist=varinfo.split(',')
    #create flat composition
    composition={}
    #add context variables
    #category
    tcat=request.args.get("tcat","")
    if(tcat==""):
        tcat="openehr"
    ccat=request.args.get("ccat","")
    if(ccat==""):
        ccat="433"
    vcat=request.args.get("vcat","")
    if(vcat==""):
        vcat='event'
    composition[formname+'/category|terminology']=tcat
    composition[formname+'/category|code']=ccat
    composition[formname+'/category|value']=vcat
    #language
    tlan=request.args.get("tlan","")
    if(tlan==""):
        tlan="ISO_639-1"
    clan=request.args.get("clan","")
    if(clan==""):
        clan="en"
    composition[formname+'/language|terminology']=tlan
    composition[formname+'/language|code']=clan
    #territory
    tter=request.args.get("tter","")
    if(tter==""):
        tter="ISO_3166-1"
    cter=request.args.get("cter","")
    if(cter==""):
        cter="IT"
    composition[formname+'/territory|terminology']=tter
    composition[formname+'/territory|code']=cter
    #time
    stime=request.args.get("stime","")
    if(stime==""):
        stime="2022-03-15T12:04:38.49Z"
    etime=request.args.get("etime","")
    composition[formname+'/context/start_time']=stime
    if(etime != ""):
        composition[formname+'/context/_end_time']=etime
    #health_care_facility
    idhcf=request.args.get("idhcf","")
    idshcf=request.args.get("idshcf","")
    idnhcf=request.args.get("idnhcf","")
    nhcf=request.args.get("nhcf","")
    if(idhcf != ""):
        composition[formname+'/context/_health_care_facility|id']=idhcf
    if(idshcf != ""):
        composition[formname+'/context/_health_care_facility|id_scheme']=idshcf
    if(idnhcf != ""):    
        composition[formname+'/context/_health_care_facility|id_namespace']=idnhcf
    if(nhcf != ""):    
        composition[formname+'/context/_health_care_facility|name']=nhcf
    #participation1-2-3
    fpart1=request.args.get("fpart1","")
    mpart1=request.args.get("mpart1","")
    npart1=request.args.get("npart1","")
    ipart1=request.args.get("ipart1","")
    ispart1=request.args.get("ispart1","")
    inpart1=request.args.get("inpart1","")
    if(fpart1 !=""):
        composition[formname+'/context/_participation:0|function']=fpart1
    if(mpart1 !=""):
        composition[formname+'/context/_participation:0|mode']=mpart1
    if(npart1 !=""):
        composition[formname+'/context/_participation:0|name']=npart1
    if(ipart1 !=""):
        composition[formname+'/context/_participation:0|id']=ipart1
    if(ispart1 !=""):
        composition[formname+'/context/_participation:0|id_scheme']=ispart1
    if(inpart1 != ""):
        composition[formname+'/context/_participation:0|id_namespace']=inpart1
    if(fpart1 !=""):
        fpart2=request.args.get("fpart2","")
        mpart2=request.args.get("mpart2","")
        npart2=request.args.get("npart2","")
        ipart2=request.args.get("ipart2","")
        ispart2=request.args.get("ispart2","")  
        inpart2=request.args.get("inpart2","")    
        if(fpart2 !=""):
            composition[formname+'/context/_participation:1|function']=fpart2
        if(mpart2 !=""):
            composition[formname+'/context/_participation:1|mode']=mpart2
        if(npart2 !=""):
            composition[formname+'/context/_participation:1|name']=npart2
        if(ipart2 !=""):
            composition[formname+'/context/_participation:1|id']=ipart2
        if(ispart2 !=""):
            composition[formname+'/context/_participation:1|id_scheme']=ispart2
        if(inpart1 != ""):
            composition[formname+'/context/_participation:1|id_namespace']=inpart2
        if(fpart2!=""):
            fpart3=request.args.get("fpart3","")
            mpart3=request.args.get("mpart3","")
            npart3=request.args.get("npart3","")
            ipart3=request.args.get("ipart3","")
            ispart3=request.args.get("ispart3","")  
            inpart3=request.args.get("inpart3","") 
            if(fpart3 !=""):
                composition[formname+'/context/_participation:2|function']=fpart3
            if(mpart3 !=""):
                composition[formname+'/context/_participation:2|mode']=mpart3
            if(npart3 !=""):
                composition[formname+'/context/_participation:2|name']=npart3
            if(ipart3 !=""):
                composition[formname+'/context/_participation:2|id']=ipart3
            if(ispart3 !=""):
                composition[formname+'/context/_participation:2|id_scheme']=ispart3
            if(inpart3 != ""):
                composition[formname+'/context/_participation:2|id_namespace']=inpart3
    #composer PARTY_SELF or PARTY_IDENTIFIED
    cself=request.args.get("cself","")
    ciid=request.args.get("ciid","")
    if(cself != ""):#party self
        composition['ctx/composer_self']=True
        composition['ctx/composer_id']=cself
        sself=request.args.get("sself","")
        nself=request.args.get("nself","")
        if(sself != ""):
            composition['ctx/id_scheme']=sself
        if(nself != ""):
            composition['ctx/id_namespace']=nself
    elif(ciid != ""):#party identified
        composition['ctx/composer_id']=ciid
        ciname=request.args.get("ciname","")
        ciisc=request.args.get("ciisc","")
        cins=request.args.get("cins","")
        if(ciname != ""):
            composition['ctx//composer_name']=ciname
        if(ciisc != ""):
            composition['ctx//id_scheme']=ciisc
        if(cins != ""):
            composition['ctx/id_namespace']=cins      
    #setting
    setter=request.args.get("setter","")
    if(setter==""):
        setter="openehr"
    codeter=request.args.get("codeter","")
    if(codeter==""):
        codeter="238"
    valter=request.args.get("valter","")
    if(valter==""):
        valter="other care"
    composition[formname+'/context/setting|terminology']=setter
    composition[formname+'/context/setting|code']=codeter
    composition[formname+'/context/setting|value']=valter
    #location
    loc=request.args.get("loc","")
    if(loc != ""):
        composition[formname+'/context/_location']=loc
    #the remaining variables
    for var,path in two_at_a_time(varinfolist):
        value=request.args.get(var,"")
        if(value != ""):
            composition[path]=value
    #post the composition
    filetype='FLAT'
    eid=request.args.get("ename","")    
    check=request.args.get("check","")
    checkresults=""
    checkinfo=""
    comp=json.dumps(composition)
    myresp=postcomp(client,auth,hostname,port,username,password,comp,eid,tid,filetype,check)
    return myresp       
 
def two_at_a_time(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

def retrievetemplatefromform(formloaded):
    from app import app
    app.logger.debug('      inside retrievetemplatefromform')
    index=formloaded.rfind("<!-- ", 0, formloaded.rfind("<!-- "))
    index2=formloaded.find(" -->",index,len(formloaded))
    template_name=formloaded[index+4:index2].strip()
    return template_name

def fixformloaded(formloaded):
    from app import app
    app.logger.debug('      inside fixformloaded')
    #fix missing double braces 
    #<h1>Form for template form.html</h1>
    #{{forname}}
    fl=formloaded.replace("<h1>Form for template form.html</h1>",
                    "<h1>Form for template {{formname}}</h1>")
    fl2=fl.replace('<input class="form-control" type="text" id="ename" name="ename" value= >',
                    '<input class="form-control" type="text" id="ename" name="ename" value={{last}}>')

    index1=fl2.find("<h2>Results</h2>")+17
    index2=fl2.find("<br><br>",index1)
    index3=fl2.find("<br><br>",index2+8)
    linestoadd1='''
    {% macro linebreaks_for_string( the_string ) -%}
    {% if the_string %}
    {% for line in the_string.split('\n') %}
    <br />
    {{ line }}
    {% endfor %}
    {% else %}
    {{ the_string }}
    {% endif %}
    {%- endmacro %}
    {{ linebreaks_for_string( yourresults ) }}
    '''
    linestoadd2='{{checkresults}}'
    linestoadd3='{{checkinfo}}'  
    formfixed=fl2[:index1]+linestoadd1+fl2[index2:index2+9]+linestoadd2+fl2[index3:index3+9]+linestoadd3+fl2[index3+10:]
    return formfixed
