#from sre_constants import SUCCESS
import requests
import base64
from url_normalize import url_normalize
from lxml import etree
from io import StringIO, BytesIO
import json
from typing import Any,Callable
from json_tools import diff
import collections
import re
from xmldiff import main as diffmain
#from xml.dom import minidom
from xdiff import xdiff
import string,random
import sys

client=requests.Session()

def getauth(username,password):
    message=username+":"+password
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    auth="Basic "+base64_message
    return auth

def gettemp(auth,hostname,port,username,password,template=""):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    myresp={}
    if(template==""):#get all templates
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4')
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4/'+template)
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    print(response.status_code)
    print(response.text)
    print(response.headers)
    if(response.status_code<210 and response.status_code>199):
        if(template!=""):
 #           responsexml = minidom.parseString(response.text).toprettyxml(indent="   ")
            root = etree.fromstring(response.text)
 #           root.indent(tree, space="\t", level=0)
            responsexml = etree.tostring(root,  encoding='unicode', method='xml', pretty_print=True)
            #responsexml=responsexml.replace("&#13","").replace("#","%23")
            responsexml=responsexml.replace("#","%23")
            myresp['template']=responsexml
        myresp['text']=response.text
        myresp['status']='success'
        myresp['headers']=response.headers
        myresp['status_code']=  response.status_code  
        return myresp
    else:
        myresp['text']=response.text
        myresp['status']='failure'
        myresp['headers']=response.headers  
        myresp['status_code']=  response.status_code   
        return myresp

def posttemp(auth,hostname,port,username,password,uploaded_template):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    root=etree.fromstring(uploaded_template)
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4/')
    response=client.post(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/XML'},
        data=etree.tostring(root))
    print(response.text)
    print(response.status_code)
    print(response.headers)
    print(type(response.status_code))
    myresp={}
    myresp['headers']=response.headers
    myresp['status_code']=response.status_code
    myresp['text']=response.text
    if(response.status_code<210 and response.status_code>199):
        myresp['status']='success'
    else:
        myresp['status']='failure'
    return myresp

def updatetemp(adauth,hostname,port,adusername,adpassword,uploaded_template,templateid):
    EHR_SERVER_URL = "http://"+hostname+":"+port+"/ehrbase/"
    client.auth = (adusername,adpassword)
    root=etree.fromstring(uploaded_template)
    myurl=url_normalize(EHR_SERVER_URL  + 'rest/admin/template/'+templateid)
    response=client.put(myurl,params={'format': 'XML'},headers={'Authorization':adauth,'Content-Type':'application/xml',
                 'prefer':'return=minimal','accept':'application/xml' },
                 data=etree.tostring(root))
    print(response.text)
    print(response.status_code)
    print(response.headers)
    print(type(response.status_code))
    myresp="{\n"
    for k,v in response.headers.items():
        myresp+=k+" : "+v+",\n"
    myresp+="}"
    if(response.status_code<210 and response.status_code>199):
        return f"successfully updated \ncode={response.status_code} \ntext={myresp}"
    else:
        return f"unsuccesfully updated \ncode {response.status_code} \ntext={myresp}"


def createehrid(auth,hostname,port,username,password,eid):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    print("launched createehrid")
    withehrid=True
    if(eid==""):
        withehrid=False    
    if(not withehrid):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
        response=client.post(myurl, params={},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid)
        response=client.put(myurl, params={},headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        if(withehrid):
            ehrid=response.headers['Location'].split("ehr/")[4]
            if(eid != ehrid):
                print('ehrid given and obtain do not match')
        else:
            ehrid=response.headers['Location'].split("ehr/")[4]
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers         
    myresp['status_code']=response.status_code 
    print(myresp)
    return myresp

def createehrsub(auth,hostname,port,username,password,sid,sna,eid):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    print("launched createehrsub")
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
    print(body)
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
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        if(withehrid):
            ehrid=response.headers['Location'].split("ehr/")[4]
            if(eid != ehrid):
                print('ehrid given and obtain do not match')
        else:
            ehrid=response.headers['Location'].split("ehr/")[4]
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['headers']=response.headers
        myresp['text']=response.text
    myresp['status_code']=response.status_code 
    return myresp

def getehrid(auth,hostname,port,username,password,ehrid):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    print("launched getehr")
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+ehrid)
    response=client.get(myurl, params={},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers         
    myresp['status_code']=response.status_code 
    #print(myresp)
    return myresp

def getehrsub(auth,hostname,port,username,password,sid,sna):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    print("launched getehrsub")
    print(f'sid={sid} sna={sna}')
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr')
    response=client.get(myurl, params={'subject_id':sid,'subject_namespace':sna},headers={'Authorization':auth, \
            'Content-Type':'application/JSON','Accept': 'application/json','Prefer': 'return={representation|minimal}'})
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    if(response.status_code<210 and response.status_code>199):
        myresp['status']="success"
        ehrid=response.headers['Location'].split("ehr/")[3]
        myresp["ehrid"]=ehrid
        myresp['text']=response.text
    else:
        myresp['status']="failure"
        myresp['text']=response.text   
        myresp['headers']=response.headers         
    myresp['status_code']=response.status_code 
    print(myresp)
    return myresp



def postcomp(auth,hostname,port,username,password,composition,eid,tid,filetype,check):
    client.auth = (username,password)
    print('inside post_composition')
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL + 'ehr/'+eid+'/composition')
        root=etree.fromstring(composition)
        response = client.post(myurl,
                       params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml', \
                           'accept':'application/xml'}, data=etree.tostring(root)) 
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            if(check=="Yes"):
                checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo          
        else:
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
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            if(check=="Yes"):
                checkinfo= compcheck(auth,hostname,port,username,password,compositionjson,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo
        else:
            myresp["status"]="failure"
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
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['compositionid']=response.headers['Location'].split("composition/")[1]
            if(check=="Yes"):
                checkinfo= compcheck(auth,hostname,port,username,password,compositionjson,eid,filetype,myresp['compositionid'])
                if(checkinfo==None):
                    myresp['check']='Retrieved and posted Compositions match'
                    myresp['checkinfo']=""
                else:
                    myresp['check']='WARNING: Retrieved different from posted Composition'
                    myresp['checkinfo']=checkinfo
        else:
            myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp

def getcomp(auth,hostname,port,username,password,compid,eid,filetype):
    client.auth = (username,password)
    print('inside get_composition')
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        #root=etree.fromstring(composition)
        response=client.get(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml','accept':'application/xml'})
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            root = etree.fromstring(response.text)
 #          root.indent(tree, space="\t", level=0)
            myresp['xml'] = etree.tostring(root,  encoding='unicode', method='xml', pretty_print=True)
            myresp["status"]="success"
            #myresp['xml']=response.text
        else:
            myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp
    elif(filetype=="JSON"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        response = client.get(myurl, params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/json'} )
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['json']=response.text
        else:
            myresp["status"]="failure"
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
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        myresp['compositionid']=compid
        myresp['ehrid']=eid
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['flat']=json.dumps(json.loads(response.text)['composition'],sort_keys=True, indent=4, separators=(',', ': '))
        else:
            myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp


def postaql(auth,hostname,port,username,password,aqltext,qname,version,qtype):
    print('inside post_aql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    if(qtype==""):
        qtype="AQL"
    if(version==""):
        version="1.0.0"
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname+"/"+version)
    response = client.put(myurl,params={'type':qtype,'format':'RAW'},headers={'Authorization':auth,'Content-Type':'text/plain'},data=aqltext)
    print(response.url)
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    myresp["status_code"]=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp["status"]="success"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        #myresp['compositionid']=response.headers['Location'].split("composition/")[1]
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
    return myresp

def getaql(auth,hostname,port,username,password,qname,version):
    client.auth = (username,password)
    print('inside get_aql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    if(version!=""):
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname+"/"+version)
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/'+qname)
    response = client.get(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'})
    print(response.url)
    print(response.text)
    print(response.status_code)
    print(response.headers)
    myresp={}
    myresp["status_code"]=response.status_code
    if(response.status_code<210 and response.status_code>199):
        myresp["status"]="success"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        if ('q' in myresp['text']):
            myresp['aql']=json.loads(myresp['text'])['q']
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
    return myresp  

def runaql(auth,hostname,port,username,password,aqltext,qmethod,limit,eid,qparam,qname,version):
    print('inside run_aql')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
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
            print(f"params={params}")
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
            print(f"data={data}")
            response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
        print(response.url)
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['text']=response.text
            myresp["headers"]=response.headers
        else:
            myresp["status"]="failure"
            myresp['text']=response.text
            myresp["headers"]=response.headers
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
            print(f"params={params}")
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
            print(f"data={data}")
            response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
        print(response.url)
        print(response.text)
        print(response.status_code)
        print(response.headers)
        myresp={}
        myresp["status_code"]=response.status_code
        if(response.status_code<210 and response.status_code>199):
            myresp["status"]="success"
            myresp['text']=response.text
            myresp["headers"]=response.headers
        else:
            myresp["status"]="failure"
            myresp['text']=response.text
            myresp["headers"]=response.headers
        return myresp  


def compcheck(auth,hostname,port,username,password,composition,eid,filetype,compid):
    if(filetype=="XML"):
        EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition/'+compid)
        response=client.get(myurl,params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml','accept':'application/xml'})
        origcompositiontree=etree.fromstring(composition)
        if(response.status_code<210 and response.status_code>199):
            retrievedcompositiontree= etree.fromstring(response.text)
            comparison_results=compare_xmls(origcompositiontree,retrievedcompositiontree)
            ndiff=analyze_comparison_xml(comparison_results)
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
            print(retrievedcomposition) 
            origchanged=change_naming(origcomposition)
            retrchanged=change_naming(retrievedcomposition)
            comparison_results=compare_jsons(origchanged,retrchanged)
            ndiff=analyze_comparison_json(comparison_results)
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
            print(retrievedcomposition)
            origchanged=change_naming(origcomposition)
            retrchanged=change_naming(retrievedcomposition)
            comparison_results=compare_jsons(origchanged,retrchanged)
            ndiff=analyze_comparison_json(comparison_results)
            if(ndiff>0):
                return comparison_results
            else:
                return None
            

def compare_xmls(firstxml,secondxml):
    xml_parser = etree.XMLParser(remove_blank_text=True,
                                     remove_comments=False,
                                     remove_pis=False)    
    firststring=etree.tostring(firstxml)
    secondstring=etree.tostring(secondxml)
    firstxml=etree.fromstring(firststring,xml_parser)
    secondxml=etree.fromstring(secondstring,xml_parser)    
    difference=xdiff(firstxml,secondxml)
    return difference

def convert_duration_to_days(duration_string):
    argument=duration_string[-1]
    duration=int(duration_string[1:-1])
    if(argument=="D"):
        return duration
    elif(argument=="W"):
        return 7*duration
    elif(argument== "Y"):
        return 365*duration
    else:
        return -1


def analyze_comparison_xml(comparison_results):
    ndifferences=0
    for l in comparison_results:
        if("hunk" not in l[0]):
            continue
        else:
            if("<uid" in l[1]):#uid 
                continue
            elif("<value>" in l[1]):
                text1=l[1].split("<value>")[1].split("</value>")[0]
                if(text1.startswith("P")):
                    text2=l[2].split("<value>")[1].split("</value>")[0]
                    if(convert_duration_to_days(text1)==convert_duration_to_days(text2)):
                        continue
                ndifferences+=1
    return ndifferences


def compare_jsons(firstjson:json,secondjson:json)->None:
    '''
    compare the given jsons
    '''
    one=flatten(firstjson)
    two=flatten(secondjson)
    return json.dumps((diff(one,two)),indent=4)


def change_naming(myjson:json)->json:
    '''change naming convention on the json'''
    return change_dict_naming_convention(myjson,convertcase)

def flatten(d:dict, parent_key:str='', sep:str='_')->dict:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
                items.extend(flatten(v, new_key, sep=sep).items())
        else:
                items.append((new_key, v))
    return dict(items)

def change_dict_naming_convention(d:Any, convert_function:Callable[[str],str])->dict:
    """
    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        convert_function (func): function that takes the string in one convention and returns it in the other one.
    Returns:
            Dictionary with the new keys.
    """
    if not isinstance(d,dict):
            return d
    new = {}
    for k, v in d.items():
        new_v = v
        if isinstance(v, dict):
                new_v = change_dict_naming_convention(v, convert_function)
        elif isinstance(v, list):
                new_v = list()
                for x in v:
                        new_v.append(change_dict_naming_convention(x, convert_function))
        new[convert_function(k)] = new_v
    return new


def convertcase(name:str)->str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def analyze_comparison_json(comparison_results:list)->int:
    ndifferences=0
    for l in comparison_results:
        if "add" in l:
            if("_uid" in l['add']): #ignore if it is _uid 
                continue
            else:
                ndifferences+=1
                print(f"difference add:{l['add']} value={l['value']}")
        elif "remove" in l:
            ndifferences+=1
            print(f"difference remove:{l['remove']} value={l['value']}")
        elif "replace" in l:
            if(l['value'].endswith("Z") and l['value'][:3].isnumeric()):
                if(l['value'][:18]==l['prev'][:18]):
                    continue
                ndifferences+=1
                print(f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}")				
            elif(l['value'].startswith("P") and l['value'].endswith('D') and l['prev'].endswith('W')):
                daysvalue=int(l['value'][1:-1])
                daysprev=int(l['prev'][1:-1])
                if(daysvalue == daysprev):
                    continue
                ndifferences+=1
                print(f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}")				
            else:
                ndifferences+=1
                print(f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}")		
    return ndifferences    
    
    
def get_dashboard_info(auth,hostname,port,username,password,adauth,adusername,adpassword):
    print('inside dashboard info')
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)            
    #get aql stored
    myresp={}
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/query/')
    responseaql = client.get(myurl, headers={'Authorization':auth,'Content-Type': 'application/json'})                     
    print (responseaql.url)
    print (responseaql.status_code)
    print (responseaql.text)
    print (responseaql.headers)
    print(type(responseaql.text))
    if(responseaql.status_code<210 and responseaql.status_code>199):
        resultsaql=json.loads(responseaql.text)['versions']
        myresp['aql']=len(resultsaql) 
    # get total ehrs  
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')
    data={}
    aqltext="select e/ehr_id/value FROM EHR e"
    data['q']=aqltext
    response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
    print(response.url)
    print(response.text)
    print(response.status_code)
    print(response.headers)
  
    if(response.status_code<210 and response.status_code>199):
        results=json.loads(response.text)['rows']
        myresp['ehr']=len(results) 

    #get ehrid,compid, templateid list
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'query/aql')
    data={}
    aqltext="select e/ehr_id/value,c/uid/value,c/archetype_details/template_id/value from EHR e contains COMPOSITION c"
    data['q']=aqltext
    response = client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, \
                data=json.dumps(data) )
    print(response.url)
    print(response.text)
    print(response.status_code)
    print(response.headers)
  
    if(response.status_code<210 and response.status_code>199):
        results=json.loads(response.text)['rows']
        myresp['composition']=len(results)
    #get templates
    myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4')
    response2=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    if(response2.status_code<210 and response2.status_code>199):
        resultstemp=json.loads(response2.text)
        myresp['template']=len(resultstemp)
        templates=[rt['template_id'] for rt in resultstemp]
        #calculate total ehr in use
        ehr=set(r[0] for r in results)
        myresp['uehr']=len(ehr)
        #total templates in use
        templates_in_use=set(r[2] for r in results)
        myresp['utemplate']=len(templates_in_use)
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
        myresp['bar_max']=max(myresp['bar_value'])      
        myresp['pie_label']=list(d.keys())
        myresp['pie_value']=list(d.values())
        myresp['status']='partial_success'

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
            if(resp.status_code<210 and resp.status_code>199):
                info=json.loads(resp.text)['build']
                myinfo={}
                myinfo['openehr_sdk']=info['openEHR_SDK']['version']
                myinfo['ehrbase_version']=info['version']
                myinfo['archie']=info['archie']['version']
                myresp['info']=myinfo
                myurl=url_normalize(EHR_SERVER  + 'management/env')
                resp2 = client.get(myurl,headers={'Authorization':adauth,'Content-Type':'application/JSON'})
                if(resp2.status_code<210 and resp2.status_code>199):
                    env=json.loads(resp2.text)
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
                    aql["ENV_AQL_ARRAY_DEPTH"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_DEPTH"]["value"]
                    aql["ENV_AQL_ARRAY_IGNORE_NODE"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_IGNORE_NODE"]["value"]
                    aql["ENV_AQL_ARRAY_DEPTH"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_DEPTH"]["value"]
                    aql["ENV_AQL_ARRAY_IGNORE_NODE"]=env["propertySources"][3]["properties"]["ENV_AQL_ARRAY_IGNORE_NODE"]["value"]
                    aql["server.aqlConfig.useJsQuery"]=env["propertySources"][4]["properties"]["server.aqlConfig.useJsQuery"]["value"]
                    aql["server.aqlConfig.ignoreIterativeNodeList"]=env["propertySources"][4]['properties']["server.aqlConfig.ignoreIterativeNodeList"]["value"]
                    aql["server.aqlConfig.iterationScanDepth"]=env["propertySources"][4]['properties']["server.aqlConfig.iterationScanDepth"]["value"]
                    myresp["aqlinfo"]=aql
                    gen_properties["SERVER_NODENAME"]=env["propertySources"][3]['properties']["SERVER_NODENAME"]["value"]
                    gen_properties["HOSTNAME"]=env["propertySources"][3]['properties']["HOSTNAME"]["value"]
                    gen_properties["LANG"]=env["propertySources"][3]['properties']["LANG"]["value"]
                    gen_properties["SECURITY_AUTHTYPE"]=env["propertySources"][3]['properties']["SECURITY_AUTHTYPE"]["value"]
                    gen_properties["SYSTEM_ALLOW_TEMPLATE_OVERWRITE"]=env["propertySources"][3]['properties']["SYSTEM_ALLOW_TEMPLATE_OVERWRITE"]["value"]
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
                    myurl=url_normalize(EHR_SERVER  + 'management/health')
                    resp3 = client.get(myurl,headers={'Authorization':adauth,'Content-Type':'application/JSON'})
                    if(resp3.status_code<210 and resp3.status_code>199):
                        health=json.loads(resp3.text)
                        myresp["db"]["db"]=health["components"]["db"]["details"]["database"]
                        disk={}
                        disk["total_space"]=health["components"]["diskSpace"]["details"]["total"]
                        disk["free_space"]=health["components"]["diskSpace"]["details"]["free"]
                        myresp["disk"]=disk
                        myresp['status']='success'
        return myresp
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp


def postbatch1(auth,hostname,port,username,password,uploaded_files,tid,check,sidpath,snamespace,filetype,random,comps):
    client.auth = (username,password)
    print('inside post_batch composition1')
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
#            uf.stream.seek(0)
#            composition=uf.read()
            root=etree.fromstring(composition)
            #create EHRID
            if(random):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,composition)
                print(f'sid found={sid}')
                if(sid==-1):
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                     #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    eids.append(eid)
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
                eids.append(eid)
            myurl=url_normalize(EHR_SERVER_BASE_URL + 'ehr/'+eid+'/composition')
            response = client.post(myurl,
                       params={'format': 'XML'},headers={'Authorization':auth,'Content-Type':'application/xml', \
                           'accept':'application/xml'}, data=etree.tostring(root)) 
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
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
            if(random):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,comp)
                print(f'sid found={sid}')
                if(sid==-1):
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    eids.append(eid)
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
                eids.append(eid)
            myurl=url_normalize(EHR_SERVER_BASE_URL  + 'ehr/'+eid+'/composition')
            response = client.post(myurl,params={'format': 'RAW'},headers={'Authorization':auth,'Content-Type':'application/json', \
             'accept':'application/json'}, data=compositionjson)   
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
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
        print(type(uploaded_files))
        for uf,composition in zip(uploaded_files,comps):
#            print(type(uf))
#            uf.stream.seek(0)
#            composition=uf.read()
            comp = json.loads(composition)
            compositionjson=json.dumps(comp) 
            #create EHRID
            if(random):
                sid=randomstring()
                sna='fakenamespace'
            else:
                sna=snamespace
                sid=findpath(filetype,sidpath,comp)
                print(f'sid found={sid}')
                if(sid==-1):
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                     #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    eids.append(eid)
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
                eids.append(eid)
            EHR_SERVER_BASE_URL_FLAT = "http://"+hostname+":"+port+"/ehrbase/rest/ecis/v1/"    
            myurl=url_normalize(EHR_SERVER_BASE_URL_FLAT  + 'composition')
            response = client.post(myurl,
                       params={'ehrId':eid,'templateId':tid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=minimal'},
                       data=compositionjson
                      )
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
            if(csucc!=0):
                myresp['status']='success'
            else:
                myresp['status']='failure'
        else:
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
        # print("before findjson")
        # print(composition)
        print(elements[-1])
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
        #print(composition)
        for c in composition:
            #print(c.lower().replace("_"," "),elements[-1])
            if(elements[-1] in c.lower().replace("_"," ")):
                    # print("found")
                    # print(composition[c])
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
    # print("------------------------------------------") 
    # print("findjson called")
    # print(JSON)
    # if(type(JSON)==dict):
        # print(keytofind,JSON.keys())
        # print(JSON.values())
        # print(keytofind in JSON)
        # if(keytofind in JSON):
        #     print(valuetofind in JSON[keytofind])
        #     print(type(JSON[keytofind]))
        #     if(type(JSON[keytofind])==str):
        #         print(JSON[keytofind].lower())
    if keytofind in JSON and type(JSON[keytofind])==str and valuetofind in JSON[keytofind].lower():
        path = path + keytofind 
        all_paths.append(path)
        print('FOUND')
        print(JSON)
        #print(keytofind,JSON[keytofind],path)
    # print("JSON PRIMA")
    # print(type(JSON))
    #print(JSON)
    for i,key in enumerate(JSON):
        # print("key")
        # print(key)
        if(type(JSON) is list):
            # print("JSON is list")
            findjson(keytofind, valuetofind, key, path + '['+str(i)+']/',all_paths)
        else:
            if isinstance(JSON[key], dict):
                # print("json[key] is dict")
                # print(JSON[key])
                findjson(keytofind, valuetofind, JSON[key], path + key + '/',all_paths)
            elif(type(JSON[key]) is list):
                # print("json[key] is list")
                findjson(keytofind, valuetofind, JSON[key], path + key,all_paths)



def randomstring(N=10,chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(N))


def postbatch2(auth,hostname,port,username,password,uploaded_files,tid,check,eid,filetype,random,comps):
    client.auth = (username,password)
    print('inside post_batch composition1')
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                myerror="couldn't create ehrid="+eid+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                print(myerror)
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
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                myerror=f"couldn't create ehrid={eid}"+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                print(myerror)
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
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
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
            resp10=createehrsub(auth,hostname,port,username,password,sid,sna,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'Specified party has already an EHR set' in json.loads(resp10['text'])['message']):
                    #get ehr summary by subject_id , subject_namespace
                    payload = {'subject_id':sid,'subject_namespace':sna}
                    ehrs = client.get(EHR_SERVER_BASE_URL + 'ehr',  params=payload,headers={'Authorization':auth,'Content-Type':'application/JSON','Accept': 'application/json'})
                    print('ehr already existent')
                    eid=json.loads(ehrs.text)["ehr_id"]["value"]
                    print(f'Patient {sid}: retrieved ehrid={eid}')
            else:
                eid=resp10['ehrid']
        else:
            resp10=createehrid(auth,hostname,port,username,password,eid)
            if(resp10['status']!='success'):
                if(resp10['status_code']==409 and 'EHR with this ID already exists' in json.loads(resp10['text'])['message']):
                    pass
                else:
                    myerror=f"couldn't create ehrid={eid}"+" "+resp10['status_code']+"\n"+ resp10['headers']+"\n"+resp10['text']
                    print(myerror)
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
#            print(type(uf))
#            uf.stream.seek(0)
#            composition=uf.read()
            comp = json.loads(composition)
            compositionjson=json.dumps(comp) 
            myurl=url_normalize(EHR_SERVER_BASE_URL_FLAT  + 'composition')
            response = client.post(myurl,
                       params={'ehrId':eid,'templateId':tid,'format':'FLAT'},
                       headers={'Authorization':auth,'Content-Type':'application/json','Prefer':'return=minimal'},
                       data=compositionjson
                      )
            print(response.text)
            print(response.status_code)
            print(response.headers)
            if(response.status_code<210 and response.status_code>199):
                succ+=1
                cid=response.headers['Location'].split("composition/")[1]
                compids.append(cid)
                if(check=="Yes"):
                    checkinfo= compcheck(auth,hostname,port,username,password,composition,eid,filetype,cid)
                    if(checkinfo==None):
                        csucc+=1
                    else:
                        filenamecheckfailed.append(uf.filename)
            else:
                filenamefailed.append(uf.filename)
        if(check=='Yes'):
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
        myresp['error']=""
        return myresp
