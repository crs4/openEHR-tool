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

client=requests.Session()

def init_session(username,password):
    message=username+":"+password
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    auth="Basic "+base64_message
    return auth

def gettemp(auth,hostname,port,username,password,template=""):
    EHR_SERVER_BASE_URL = "http://"+hostname+":"+port+"/ehrbase/rest/openehr/v1/"
    client.auth = (username,password)
    if(template==""):#get all templates
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4')
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    else:
        myurl=url_normalize(EHR_SERVER_BASE_URL  + 'definition/template/adl1.4/'+template)
        response=client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
    if(response.status_code==200):
        if(template!=""):
 #           responsexml = minidom.parseString(response.text).toprettyxml(indent="   ")
            root = etree.fromstring(response.text)
 #           root.indent(tree, space="\t", level=0)
            responsexml = etree.tostring(root,  encoding='unicode', method='xml', pretty_print=True)
            return responsexml
        else:
            return response.text
    else:
        return 'Error: '+str(response.status_code)

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
    myresp="{\n"
    for k,v in response.headers.items():
        myresp+=k+" : "+v+",\n"
    myresp+="}"
    if(response.status_code<210 and response.status_code>199):
        return f"successfully inserted \ncode={response.status_code} \ntext={myresp}"
    else:
        return f"unsuccesfully inserted \ncode {response.status_code} \ntext={myresp}"


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
    print(myresp)
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
    else:
        myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
    return myresp  

#def runaql(auth,hostname,port,username,password,aqltext,qmethod,offset,fetch,eid,qparam,qname,version):
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


