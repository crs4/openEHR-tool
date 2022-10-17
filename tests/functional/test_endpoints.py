from flask import url_for,request
import app
import shutil,os,json
import requests,requests_mock
from lxml import etree
from pytest_mock import mocker

def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"This is a tool" in response.data
    assert b"interact with a EHRBase server" in response.data


def test_home_page_post(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = test_client.post('/')
    assert response.status_code == 200
    assert b"405" in response.data

def test_gtemp_page_redirect(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/gtemp' page is requested (GET) a redirect is 
    followed to the settings page if several global variables
    are not set.
    THEN check that the redirection is to settings page
    """
    #print(f'values {app.hostname} {app.port} {app.username} {app.password} {app.nodename}')
    response = test_client.get('/gtemp.html', follow_redirects=True)
    assert response.status_code == 200
    assert request.path == '/settings.html'
    assert b'admin_password=' in response.data


def test_gtemp_page(test_client_with_globalvars,mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/gtemp' page is requested (GET) and the 
    relevant global variables are set 
    THEN check that the gtemp page is returned with valid response
    """
    mydir=os.path.dirname(os.path.realpath(__file__))
    myfile=mydir+'/../../templates/gtemp.html'
    ## If file exists, delete it ##
    if os.path.isfile(myfile):
        #print('it exists')
        os.remove(myfile)
    else:    ## Show an error ##
        #print(f'{myfile} not found')
        pass
    mycode=200
    mytextjson=json.loads('[{"concept":"Interhealth_cancer_registry","template_id":"Interhealth_cancer_registry","archetype_id":"openEHR-EHR-COMPOSITION.report.v1","created_timestamp":"2022-10-03T15:26:28.293Z"},{"concept":"Pluto concept","template_id":"Pluto","archetype_id":"openEHR-EHR-COMPOSITION.event_summary.v0","created_timestamp":"2022-09-01T10:23:51.292Z"}]')
    mytext=json.dumps(mytextjson)
    myheaders=json.loads('{"Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers", "X-Content-Type-Options": "nosniff", "X-XSS-Protection": "1; mode=block", "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate", "Pragma": "no-cache", "Expires": "0", "X-Frame-Options": "DENY", "Content-Type": "application/json", "Transfer-Encoding": "chunked", "Date": "Tue, 27 Sep 2022 10:29:43 GMT", "Keep-Alive": "timeout=60", "Connection": "keep-alive"}')
    myurl='http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4?format=JSON'
    with requests_mock.Mocker() as mock:
        mocker.patch('app.insertlogline', return_value='')
        mock.get(myurl, status_code=mycode,text=mytext,headers=myheaders)
        response = test_client_with_globalvars.get('/gtemp.html')
        assert response.status_code == 200
        assert request.path == '/gtemp.html'
        #print(response.data)
        assert b'Get Templates list' in response.data

        #Now move to user choice
        #check get list templates
        response = test_client_with_globalvars.get('/gtemp.html',query_string={'pippo2':'Get List'})
        idx = response.text.find('success 200')
        assert idx != -1
        idx2= response.text.find('<br>',idx)
        text2= response.text[idx+12:idx2].strip().replace('&#34;','"')
        text2json=json.loads(text2)
        assert mytextjson==text2json
        #
        #check get template Interhealth_cancer_registry.xml format OPT
        templatelist=[]
        filename=mydir+'/../Interhealth_cancer_registry.opt'
        with open(filename) as f:
            templatelist=f.readlines()
        templatelist=templatelist[1:]
        tlist=[]
        for t in templatelist:
            tlist.append(t.strip())
        templatestring=''.join(tlist)
        mycodepippo=200
        mytextpippo=templatestring
        myheaderspippo=json.loads('{"Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers", "Last-Modified": "Fri, 02 Jan 1970 10:12:04 GMT", "ETag": "Interhealth_cancer_registry", "Location": "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/Interhealth_cancer_registry%3Fformat=JSON/rest/openehr/v1/definition/template/adl1.4/Interhealth_cancer_registry", "X-Content-Type-Options": "nosniff", "X-XSS-Protection": "1; mode=block", "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate", "Pragma": "no-cache", "Expires": "0", "X-Frame-Options": "DENY", "Content-Type": "application/xml", "Content-Length": "64299", "Date": "Wed, 28 Sep 2022 07:49:24 GMT", "Keep-Alive": "timeout=60", "Connection": "keep-alive"}')
        myurlpippo='http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/Interhealth_cancer_registry'
        mock.get(myurlpippo, status_code=mycodepippo,text=mytextpippo,headers=myheaderspippo)
        response = test_client_with_globalvars.get('/gtemp.html',query_string={'pippo':'Get Template','tname':'Interhealth_cancer_registry','format':'OPT'})
        assert response.status_code == 200
        print(response.text)
        assert "&lt;value&gt;Interhealth_cancer_registry&lt;/value&gt;" in response.text
        #
        #check get template Interhealth_cancer_registry.xml format WebTemplate
        filename=mydir+'/../Interhealth_cancer_registry.json'
        with open(filename, encoding='utf-8') as f:
            templatejson=json.load(f)
        mycodepippo=200
        mytextpippo=json.dumps(templatejson)
        myheaderspippo=json.loads('{"Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers", "Last-Modified": "Fri, 02 Jan 1970 10:12:04 GMT", "ETag": "Interhealth_cancer_registry", "Location": "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/Interhealth_cancer_registry%3Fformat=JSON/rest/openehr/v1/definition/template/adl1.4/Interhealth_cancer_registry", "X-Content-Type-Options": "nosniff", "X-XSS-Protection": "1; mode=block", "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate", "Pragma": "no-cache", "Expires": "0", "X-Frame-Options": "DENY", "Content-Type": "application/xml", "Content-Length": "64299", "Date": "Wed, 28 Sep 2022 07:49:24 GMT", "Keep-Alive": "timeout=60", "Connection": "keep-alive"}')
        myurlpippo='http://localhost:8080/ehrbase/rest/ecis/v1/template/Interhealth_cancer_registry?format=JSON'
        mock.get(myurlpippo, status_code=mycodepippo,text=mytextpippo,headers=myheaderspippo)
        response = test_client_with_globalvars.get('/gtemp.html',query_string={'pippo':'Get Template','tname':'Interhealth_cancer_registry','format':'WT'})
        assert response.status_code == 200
        assert "&#34;templateId&#34;: &#34;Interhealth_cancer_registry&#34;" in response.text



