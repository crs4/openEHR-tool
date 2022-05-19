import requests
import base64
from url_normalize import url_normalize
from lxml import etree
from io import StringIO, BytesIO
import json
#from xml.dom import minidom

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



def postcomp(auth,hostname,port,username,password,composition,eid,tid,filetype):
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
            myresp['flat']=response.text
        else:
            myresp["status"]="failure"
        myresp['text']=response.text
        myresp["headers"]=response.headers
        return myresp