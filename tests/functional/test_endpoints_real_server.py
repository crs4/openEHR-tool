import pytest
import requests
import requests_mock
import ehrbase_routines
from myutils import myutils
import app
import os
import json
from lxml import etree
# from flask import current_app
# from unittest.mock import patch


url_base="http://localhost:8080/ehrbase/rest/openehr/v1/"
url_base_ecis="http://localhost:8080/ehrbase/rest/ecis/v1/"
url_base_admin="http://localhost:8080/ehrbase/rest/admin/"
url_base_management="http://localhost:8080/ehrbase/management/"
client=requests.Session()
username=app.default_username
password=app.default_password
auth=myutils.getauth(username,password)
adusername=app.default_adusername
adpassword=app.default_adpassword
adauth=myutils.getauth(adusername,adpassword)
ehrbase_version=app.default_ehrbase_version
nodename=app.default_nodename
ehrid1='1b924490-5e72-49e3-847a-4347af2fa456'
ehrid2='2c924690-5e72-49e3-847a-4347af2fa456'

class upfile():
    def __init__(self,filename):
        self.filename=filename

@pytest.fixture(scope="module")
def gapp():
    lapp = app.create_app()  # Assuming your app is created by this function
    lapp.config['TESTING'] = True  # Enable Flask's testing mode
    yield lapp

def index_in_list(data,target_key,target_value):
    return next((i for i, d in enumerate(data) if d.get(target_key) == target_value), None)

#old stuff
#def test_post_template_opt(gapp,caplog):
#   with gapp.app_context():
#       with caplog.at_level("CRITICAL"):
# #def test_list_templates(requests_mock,gapp,caplog):
#             # mock_response={}
#             # requests_mock.get(url_base+'definition/template/adl1.4', json=mock_response) 


##TEMPLATE
# #create a template
def test_create_templates(gapp):
    with gapp.app_context():
        with open('./tests/data_for_tests/test_simple_template.opt', 'rb') as f:
            template = f.read()
        result = ehrbase_routines.posttemp(client,auth,url_base,template)
        assert result['status_code'] == 201


# # 62
def test_del_temp(gapp):
    with gapp.app_context():
        templateid='test_simple_template'
        result=ehrbase_routines.deltemp(client,adauth,url_base_admin,templateid)
        assert result['status']=='success'

# #create 2 templates
def test_create_templates(gapp):
    with gapp.app_context():
        with open('./tests/data_for_tests/test_simple_template.opt', 'rb') as f:
            template = f.read()
        result = ehrbase_routines.posttemp(client,auth,url_base,template)
        assert result['status_code'] == 201
        with open('./tests/data_for_tests/test_simple_template2.opt', 'rb') as f:
                template = f.read()
        result = ehrbase_routines.posttemp(client,auth,url_base,template)
        assert result['status_code'] == 201

# # 63
def test_del_alltemp(gapp):
    with gapp.app_context():
        result=ehrbase_routines.delalltemp(client,adauth,url_base_admin)
        assert result['status']=='success'

        
#1)
def test_post_template_opt(gapp):
    with gapp.app_context():
        # Call the function to test
        with open('./tests/data_for_tests/Interhealth_cancer_registry.opt', 'rb') as f:
            template = f.read()
        result = ehrbase_routines.posttemp(client,auth,url_base,template)
        # print(f'result={result}')
        assert result['status_code'] == 201

def test_post_template_opt2(gapp):
    with gapp.app_context():
        # Call the function to test
        with open('./tests/data_for_tests/test_simple_template.opt', 'rb') as f:
            template = f.read()
        result = ehrbase_routines.posttemp(client,auth,url_base,template)
        # print(f'result={result}')
        assert result['status_code'] == 201

#2)
def test_list_templates(gapp):
    with gapp.app_context():
            result = ehrbase_routines.listtemp(client,auth,url_base)
            assert result['status_code'] == 200
            assert len[result['json']]>0
            assert index_in_list(result['json'],'template_id','Interhealth_cancer_registry')!= None
         
#3)
def test_get_template_opt(gapp):
    with gapp.app_context():
        tformat='OPT'
        template_name='Interhealth_cancer_registry'
        result = ehrbase_routines.gettemp(client,auth,url_base,url_base_ecis,tformat,template_name,ehrbase_version)
        assert result['status_code'] == 200
        namespaces = {'ns': 'http://schemas.openehr.org/v1'}
        print(f"result_template={result['template']}")
        root = etree.fromstring(result['template'].replace("&",""))
        template_name_returned=root.xpath('//ns:template_id/ns:value/text()', namespaces=namespaces)[0]
        assert template_name_returned==template_name

#4)
def test_get_template_webtemplate(gapp):
    with gapp.app_context():
        tformat='webtemplate'
        template_name='Interhealth_cancer_registry'
        result = ehrbase_routines.gettemp(client,auth,url_base,url_base_ecis,tformat,template_name,ehrbase_version)
        assert result['status_code'] == 200
        template_name_returned=json.loads(result['template'])['templateId']
        assert template_name_returned==template_name

#5)
def test_update_template_opt(gapp):
    with gapp.app_context():
        # Call the function to test
        with open('./tests/data_for_tests/test_simple_template_mod.opt', 'rb') as f:
            template = f.read()
        templateid='Interhealth_cancer_registry'
        result = ehrbase_routines.updatetemp(client,adauth,url_base_admin,template,templateid)
        assert result['status_code'] == 200

#EHR
#6)
@pytest.fixture(scope="module")
def test_post_ehr_ehrid_withoutehrid(gapp):
    with gapp.app_context():
        # Call the function to test
        eid=''
        result=ehrbase_routines.createehrid(client,auth,url_base,eid)
        assert result['status_code'] == 201
        return result['ehrid']
def test_post_ehr_ehrid_withoutehrid_run(gapp,test_post_ehr_ehrid_withoutehrid):
    assert test_post_ehr_ehrid_withoutehrid != ''

#7)
def test_post_ehr_ehrid_withehrid(gapp):
    with gapp.app_context():
        eid=ehrid1
        result=ehrbase_routines.createehrid(client,auth,url_base,eid)
        assert result['status_code'] == 201
        assert result['ehrid']==ehrid1

#8)
def test_get_ehr_from_ehrid(gapp):
    with gapp.app_context():
        # Call the function to test
        ehrid=ehrid1
        result=ehrbase_routines.getehrid(client,auth,url_base,ehrid)
        assert result['status_code'] == 200
        assert result['ehrid']==ehrid

#9)
def test_post_ehr_with_id_namespace_withoutehrid(gapp):
    with gapp.app_context():
        # Call the function to test
        eid=''
        sid='I12' #subject_id
        sna='CRS4' #subject_namespace
        result=ehrbase_routines.createehrsub(client,auth,url_base,sid,sna,eid)
        assert result['status_code'] == 201

#10)
def test_post_ehr_with_id_namespace_withehrid(gapp):
    with gapp.app_context():
        # Call the function to test
        eid=ehrid2
        sid='I13' #subject_id
        sna='CRS4' #subject_namespace
        result=ehrbase_routines.createehrsub(client,auth,url_base,sid,sna,eid)
        assert result['status_code'] == 201
        assert result['ehrid']==ehrid2

#11)
def test_get_ehr_from_id_namespace(gapp):
    with gapp.app_context():
        # Call the function to test
        sid='I13' #subject_id
        sna='CRS4' #subject_namespace
        result=ehrbase_routines.getehrsub(client,auth,url_base,sid,sna)
        assert result['status_code'] == 200
        assert result['ehrid']==ehrid2

#DIR------------------
#12)
def test_post_dir_json(gapp):
    with gapp.app_context():
        with open('./tests/data_for_tests/DirectoryExample1.json','r') as f:
            dir=json.load(f)
        # Call the function to test
        eid=ehrid1
        filetype='JSON'
        result=ehrbase_routines.postdir(client,auth,url_base,eid,json.dumps(dir),filetype)
        assert result['status_code'] == 201

#13) CURRENTLY NOT WORKING. I CANNOT CREATE A VALID DIRECTORY FOLDER IN XML YET
# def test_post_dir_xml(gapp):
#     with gapp.app_context():
#         with open('./tests/data_for_tests/DirectoryExample2.xml','rb') as f:
#             dir=f.read()
#         # Call the function to test
#         eid=ehrid2
#         filetype='XML'
#         result=ehrbase_routines.postdir(client,auth,url_base,eid,dir,filetype)
#         assert result['status_code'] == 201

#14)
def test_get_dir_json_vat(gapp):
    with gapp.app_context():
        # Call the function to test
        eid=ehrid1
        outtype="VAT" #version_at_time
        vat='2050-01-20T16:40:07.227+01:00'
        filetype='JSON'
        vid=''
        path=''
        result=ehrbase_routines.getdir(client,auth,url_base,eid,outtype,vat,vid,path,filetype)
        assert result['status_code'] == 200

#15
def test_get_dir_json_vid(gapp):
    with gapp.app_context():
        # Call the function to test
        eid=ehrid1
        outtype="VID" #by version
        vat=''
        filetype='JSON'
        vid='6e13bbdb-893c-4260-b47d-f3585d178667::local.ehrbase.org::1'
        path=''
        result=ehrbase_routines.getdir(client,auth,url_base,eid,outtype,vat,vid,path,filetype)
        assert result['status_code'] == 200

#16
def test_update_dir_json(gapp):
    with gapp.app_context():
        with open('./tests/data_for_tests/DirectoryExample1mod.json','r') as f:
            dir=json.load(f)
        # Call the function to test
        eid=ehrid1
        filetype='JSON'
        vid='6e13bbdb-893c-4260-b47d-f3585d178667::local.ehrbase.org::1'
        result=ehrbase_routines.updatedir(client,auth,url_base,eid,vid,json.dumps(dir),filetype)
        assert result['status_code'] == 200

# #16 DEPENDS ON 13 THAT IS CURRENTLY NOT WORKING
# def test_update_dir_xml(gapp):
#     with gapp.app_context():
#         with open('./tests/data_for_tests/DirectoryExample2mod.xml','rb') as f:
#             dir=f.read()
#         # Call the function to test
#         eid=ehrid2
#         filetype='XML'
#         vid='7f13bbdb-893c-4260-b47d-f3585d178667::local.ehrbase.org::1'
#         result=ehrbase_routines.updatedir(client,auth,url_base,eid,vid,dir,filetype)
#         assert result['status_code'] == 200

EHRSTATUS
#17 
@pytest.fixture(scope="module")
def test_post_ehrstatus(gapp):
    with gapp.app_context():
        with open('./tests/data_for_tests/EHRStatus1.json','r') as f:
            ehrstatus1=json.load(f)            
        result=ehrbase_routines.postehrstatus(client,auth,url_base,json.dumps(ehrstatus1))
        assert result['status_code'] == 201
        ehrid3=json.loads(result['text'])['ehr_id']['value']
        ehrstatus_vid=json.loads(result['text'])['ehr_status']['uid']['value']
        # print(f'ehrid3={ehrid3} ehrstatus_vid={ehrstatus_vid}')
        return ehrstatus_vid,ehrid3
def test_post_ehrstatus_run(test_post_ehrstatus):
    assert test_post_ehrstatus[1] != ''

# #18
def test_get_ehrstatus_vat(gapp,test_post_ehrstatus):
    with gapp.app_context():
        ehrstatus_vid=test_post_ehrstatus[0]
        ehrid3=test_post_ehrstatus[1]
        outtype='VAT'
        eid=ehrid3
        vat='2050-01-20T16:40:07.227+01:00' 
        vid=''         
        result=ehrbase_routines.getehrstatus(client,auth,url_base,eid,outtype,vat,vid)
        assert result['status_code'] == 200
        ehrstatus_vid_retrieved=json.loads(result['text'])['uid']['value']
        assert ehrstatus_vid==ehrstatus_vid_retrieved

#19
def test_get_ehrstatus_vbv(gapp,test_post_ehrstatus):
    with gapp.app_context():
        ehrstatus_vid=test_post_ehrstatus[0]
        ehrid3=test_post_ehrstatus[1]
        outtype='VBV'
        eid=ehrid3
        vat=''
        vid=ehrstatus_vid        
        result=ehrbase_routines.getehrstatus(client,auth,url_base,eid,outtype,vat,vid)
        assert result['status_code'] == 200
        ehrstatus_vid_retrieved=json.loads(result['text'])['uid']['value']
        assert ehrstatus_vid==ehrstatus_vid_retrieved

#20
def test_update_ehrstatus(gapp,test_post_ehrstatus):
    with gapp.app_context():   
        with open('./tests/data_for_tests/EHRStatus1mod.json','r') as f:
            ehrstatus1=json.load(f) 
        ehrstatus_vid=test_post_ehrstatus[0]
        ehrid3=test_post_ehrstatus[1]
        eid=ehrid3
        vid=ehrstatus_vid  
        result=ehrbase_routines.updateehrstatus(client,auth,url_base,json.dumps(ehrstatus1),eid,vid)
        assert result['status_code'] == 200
        ehrstatus_vid_retrieved=json.loads(result['text'])['uid']['value']
        ehrstatus_vid_next=ehrstatus_vid[:-1]+str(int(ehrstatus_vid[-1])+1)
        assert ehrstatus_vid_next==ehrstatus_vid_retrieved
            

#21
def test_get_ehrstatusversioned_vat(gapp,test_post_ehrstatus):
    with gapp.app_context():
        ehrstatus_vid=test_post_ehrstatus[0]
        ehrid3=test_post_ehrstatus[1]
        outtype='VAT'
        eid=ehrid3
        vat='2050-01-20T16:40:07.227+01:00' 
        vid=''         
        result=ehrbase_routines.getehrstatusversioned(client,auth,url_base,eid,outtype,vat,vid)
        assert result['status_code'] == 200
        ehrstatus_vid_retrieved=json.loads(result['text'])['data']['uid']['value']
        ehrstatus_vid_next=ehrstatus_vid[:-1]+str(int(ehrstatus_vid[-1])+1)
        assert ehrstatus_vid_next==ehrstatus_vid_retrieved

#22
def test_get_ehrstatusversioned_vbv(gapp,test_post_ehrstatus):
    with gapp.app_context():
        ehrstatus_vid=test_post_ehrstatus[0]
        ehrid3=test_post_ehrstatus[1]
        outtype='VBV'
        eid=ehrid3
        vat=''
        vid=ehrstatus_vid        
        result=ehrbase_routines.getehrstatusversioned(client,auth,url_base,eid,outtype,vat,vid)
        assert result['status_code'] == 200
        ehrstatus_vid_retrieved=json.loads(result['text'])['uid']['value']
        assert ehrstatus_vid==ehrstatus_vid_retrieved
            

#COMPOSITION
#23
def test_examplecomp_xml(gapp):
    with gapp.app_context():
        template_name='Interhealth_cancer_registry'
        filetype='XML'
        result = ehrbase_routines.examplecomp(client,auth,url_base,url_base_ecis,template_name,filetype,ehrbase_version)
        assert result['status_code']==200
        assert 'xml' in result

#24
def test_examplecomp_json(gapp):
    with gapp.app_context():
        template_name='Interhealth_cancer_registry'
        filetype='JSON'
        result = ehrbase_routines.examplecomp(client,auth,url_base,url_base_ecis,template_name,filetype,ehrbase_version)
        assert result['status_code']==200
        assert 'json' in result     

#25
def test_examplecomp_structured(gapp):
    with gapp.app_context():
        template_name='Interhealth_cancer_registry'
        filetype='STRUCTURED'
        result = ehrbase_routines.examplecomp(client,auth,url_base,url_base_ecis,template_name,filetype,ehrbase_version)
        assert result['status_code']==200
        assert 'structured' in result 

#26
def test_examplecomp_flat(gapp):
    with gapp.app_context():
            template_name='Interhealth_cancer_registry'
            filetype='FLAT'
            result = ehrbase_routines.examplecomp(client,auth,url_base,url_base_ecis,template_name,filetype,ehrbase_version)
            assert result['status_code']==200
            assert 'flat' in result                                 

#27
@pytest.fixture(scope="module")
def test_postcomp_xml(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample1.xml','rb') as f:
            comp=f.read()
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="XML"
        check="NO"
        result = ehrbase_routines.postcomp(client,auth,url_base,url_base_ecis,comp,eid,tid,filetype,check,ehrbase_version)
        assert result['status_code']==204
        composition1_id=result['compositionid']
        return composition1_id
def test_postcomp_xml_run(test_postcomp_xml):
    assert test_postcomp_xml != ''

#28
@pytest.fixture(scope="module")
def test_postcomp_json(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample2.json','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="JSON"
        check="NO"
        result = ehrbase_routines.postcomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,filetype,check,ehrbase_version)
        assert result['status_code']==204
        composition2_id=result['compositionid']
        return composition2_id
def test_postcomp_json_run(test_postcomp_json):
    assert test_postcomp_json != ''

29
@pytest.fixture(scope="module")
def test_postcomp_structured(gapp):
    with gapp.app_context():       
        with open('./tests/data_for_tests/CompositionExample3.structured','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="STRUCTURED"
        check="NO"
        result = ehrbase_routines.postcomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,filetype,check,ehrbase_version)
        assert result['status_code']==201
        composition3_id=result['compositionid']
        return composition3_id
def test_postcomp_structured_run(test_postcomp_structured):
    assert test_postcomp_structured != ''

30
@pytest.fixture(scope="module")
def test_postcomp_flat(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample4.flat','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="FLAT"
        check="NO"
        result = ehrbase_routines.postcomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,filetype,check,ehrbase_version)
        assert result['status_code']==201
        composition4_id=result['compositionid']
        return composition4_id
def test_postcomp_flat_run(test_postcomp_flat):
    assert test_postcomp_flat != ''

#31 fails
def test_postcomp_structmarand(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample5.structmarand','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="STRUCTMARAND"
        check="NO"
        ehrbase_version='2.0.0'
        result = ehrbase_routines.postcomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,filetype,check,ehrbase_version)
        assert result['status_code']==201

#32
def test_getcomp_json(gapp,test_postcomp_xml):
    with gapp.app_context():     
            composition1_id=test_postcomp_xml      
            compid=composition1_id
        eid=ehrid1
        filetype="JSON"
        result = ehrbase_routines.getcomp(client,auth,url_base,url_base_ecis,compid,eid,filetype,ehrbase_version)
        assert result['status_code']==200
        composition_vid_returned=json.loads(result['json'])['uid']['value']
        composition_vid=compid+'::'+nodename+"::1"
        assert composition_vid_returned==composition_vid

# 33
def test_getcomp_xml(gapp,test_postcomp_xml):
    with gapp.app_context():       
        composition1_id=test_postcomp_xml      
        compid=composition1_id
        eid=ehrid1
        filetype="XML"
        result = ehrbase_routines.getcomp(client,auth,url_base,url_base_ecis,compid,eid,filetype,ehrbase_version)
        assert result['status_code']==200
        namespaces = {'ns': 'http://schemas.openehr.org/v1'}
        print(f"result_xml={result['xml']}")
        root = etree.fromstring(result['xml'].replace("&",""))
        composition_vid_returned=root.xpath('//uid/value', namespaces=namespaces)[0].text
        composition_vid=compid+'::'+nodename+"::1"
        assert composition_vid_returned==composition_vid
    
#34
def test_getcomp_structured(gapp,test_postcomp_xml):
    with gapp.app_context():      
        composition1_id=test_postcomp_xml      
        compid=composition1_id
        eid=ehrid1
        filetype="STRUCTURED"
        result = ehrbase_routines.getcomp(client,auth,url_base,url_base_ecis,compid,eid,filetype,ehrbase_version)
        assert result['status_code']==200
        template_name='Interhealth_cancer_registry'.lower()
        composition_vid_returned=json.loads(result['structured'])[template_name]['_uid'][0]
        composition_vid=compid+'::'+nodename+"::1"
        assert composition_vid_returned==composition_vid

#35
def test_getcomp_flat(gapp,test_postcomp_xml):
    with gapp.app_context():
        composition1_id=test_postcomp_xml      
        compid=composition1_id
        eid=ehrid1
        filetype="FLAT"
        result = ehrbase_routines.getcomp(client,auth,url_base,url_base_ecis,compid,eid,filetype,ehrbase_version)
        assert result['status_code']==200
        template_name='Interhealth_cancer_registry'.lower()
        composition_vid_returned=json.loads(result['flat'])[template_name+"/_uid"]
        composition_vid=compid+'::'+nodename+"::1"
        assert composition_vid_returned==composition_vid

#36
def test_updatecomp_xml(gapp,test_postcomp_xml):
    with gapp.app_context():     
        with open('./tests/data_for_tests/CompositionExample1updated.xml','rb') as f:
            comp=f.read()
        composition1_id=test_postcomp_xml
        versionid=composition1_id+"::"+nodename+"::1"
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        filetype="XML"
        check="NO"
        result = ehrbase_routines.updatecomp(client,auth,url_base,url_base_ecis,comp,eid,tid,versionid,filetype,check,ehrbase_version)
        assert result['status_code']==200
            
#37
def test_updatecomp_json(gapp,test_postcomp_json):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample2updated.json','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        composition2_id=test_postcomp_json
        versionid=composition2_id+"::"+nodename+"::1"
        filetype="JSON"
        check="NO"
        result = ehrbase_routines.updatecomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,versionid,filetype,check,ehrbase_version)
        assert result['status_code']==200

#38
def test_updatecomp_structured(gapp,test_postcomp_structured):
    with gapp.app_context():     
        with open('./tests/data_for_tests/CompositionExample3updated.structured','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        composition3_id=test_postcomp_structured
        versionid=composition3_id+"::"+nodename+"::1"
        filetype="STRUCTURED"
        check="NO"
        result = ehrbase_routines.updatecomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,versionid,filetype,check,ehrbase_version)
        assert result['status_code']==200

#39
def test_updatecomp_flat(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/CompositionExample4updated.flat','r') as f:
            comp=json.load(f)
        eid=ehrid1
        tid='Interhealth_cancer_registry'
        composition4_id=test_postcomp_flat
        versionid=composition4_id+"::"+nodename+"::1"
        filetype="FLAT"
        check="NO"
        result = ehrbase_routines.updatecomp(client,auth,url_base,url_base_ecis,json.dumps(comp),eid,tid,versionid,filetype,check,ehrbase_version)
        assert result['status_code']==200      

#40
def test_getcompversioned_info(gapp,test_postcomp_xml):
    with gapp.app_context():  
        composition1_id=test_postcomp_xml     
        compid=composition1_id
        eid=ehrid1
        outtype="INFO"
        vat=""
        vid=""
        result = ehrbase_routines.getcompversioned(client,auth,url_base,compid,eid,outtype,vat,vid)
        assert result['status_code']==200

#41
def test_getcompversioned_revhist(gapp,test_postcomp_xml):
    with gapp.app_context(): 
        composition1_id=test_postcomp_xml          
        compid=composition1_id
        eid=ehrid1
        outtype="REVHIST"
        vat=""
        vid=""
        result = ehrbase_routines.getcompversioned(client,auth,url_base,compid,eid,outtype,vat,vid)
        assert result['status_code']==200

#42
def test_getcompversioned_vat(gapp,test_postcomp_xml):
    with gapp.app_context():
        composition1_id=test_postcomp_xml           
        compid=composition1_id
        eid=ehrid1
        outtype="VAT"
        vat="2050-01-20T16:40:07.227+01:00"
        vid=""
        result = ehrbase_routines.getcompversioned(client,auth,url_base,compid,eid,outtype,vat,vid)
        assert result['status_code']==200

#43
def test_getcompversioned_vid(gapp,test_postcomp_xml):
    with gapp.app_context():
        composition1_id=test_postcomp_xml            
        compid=composition1_id
        eid=ehrid1
        outtype="VBV"
        vat=""
        vid=compid+"::"+nodename+"::2"
        result = ehrbase_routines.getcompversioned(client,auth,url_base,compid,eid,outtype,vat,vid)
        assert result['status_code']==200

# 44
@pytest.fixture(scope="module")
def test_postbatch1_xml(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.xml"),upfile("BatchComposition2.xml")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        myrandom=True
        inlist=True
        tid='Interhealth_cancer_registry'
        filetype="XML"
        check="NO"
        sidpath=""
        snamespace=""
        result = ehrbase_routines.postbatch1(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,sidpath,snamespace,filetype,myrandom,comps,inlist,ehrbase_version)
        assert result['status']=="success"
        compids1=result['compositionid']
        return compids1
def test_postbatch1_xml_run(test_postbatch1_xml):
    assert test_postbatch1_xml != []

# 45
@pytest.fixture(scope="module")
def test_postbatch1_json(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.json"),upfile("BatchComposition2.json")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        myrandom=True
        inlist=True
        tid='Interhealth_cancer_registry'
        filetype="JSON"
        check="NO"
        sidpath=""
        snamespace=""
        result = ehrbase_routines.postbatch1(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,sidpath,snamespace,filetype,myrandom,comps,inlist,ehrbase_version)
        assert result['status']=="success"
        compids2=result['compositionid']
        return compids2
def test_postbatch1_json_run(test_postbatch1_json):
    assert test_postbatch1_json != []

#46
@pytest.fixture(scope="module")
def test_postbatch1_flat(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.flat"),upfile("BatchComposition2.flat")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        myrandom=True
        inlist=True
        tid='Interhealth_cancer_registry'
        filetype="FLAT"
        check="NO"
        sidpath=""
        snamespace=""
        result = ehrbase_routines.postbatch1(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,sidpath,snamespace,filetype,myrandom,comps,inlist,ehrbase_version)
        assert result['status']=="success"
        compids3=result['compositionid']
        return compids3
def test_postbatch1_flat_run(test_postbatch1_flat):
    return test_postbatch1_flat != []

# 47
@pytest.fixture(scope="module")
def test_postbatch2_xml(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.xml"),upfile("BatchComposition2.xml")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        random=True
        tid='Interhealth_cancer_registry'
        filetype="XML"
        check="NO"
        eid=ehrid2
        result = ehrbase_routines.postbatch2(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,eid,filetype,random,comps)
        assert result['status']=="success"
        compids2=result['compositionid']
        return compids2
def test_postbatch2_xml_run(test_postbatch2_xml):
    assert test_postbatch2_xml != []

# 48
@pytest.fixture(scope="module")
def test_postbatch2_json(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.json"),upfile("BatchComposition2.json")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        random=True
        tid='Interhealth_cancer_registry'
        filetype="JSON"
        check="NO"
        eid=ehrid2
        result = ehrbase_routines.postbatch2(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,eid,filetype,random,comps,ehrbase_version)
        assert result['status']=="success"
        compids2=result['compositionid']
        return compids2
def test_postbatch2_json_run(test_postbatch2_json):
    assert test_postbatch2_json != []

# # 49
@pytest.fixture(scope="module")
def test_postbatch2_flat(gapp):
    with gapp.app_context():
        uploaded_files=[upfile("BatchComposition1.flat"),upfile("BatchComposition2.flat")]
        comps=[]
        for uf in uploaded_files:
            with open('./tests/data_for_tests/'+uf.filename,'rb') as f:
                comps.append(f.read())
        random=True
        tid='Interhealth_cancer_registry'
        filetype="FLAT"
        check="NO"
        eid=ehrid2
        result = ehrbase_routines.postbatch2(client,auth,url_base,url_base_ecis,uploaded_files,tid,check,eid,filetype,random,comps,ehrbase_version)
        assert result['status']=="success"
        compids2=result['compositionid']
        return compids2
def test_postbatch2_flat_run(test_postbatch2_flat):
    assert test_postbatch2_flat != []

#50
@pytest.fixture(scope="module")
def test_postcontrib(gapp):
    with gapp.app_context():      
        with open('./tests/data_for_tests/ContributionExample1.json','r') as f:
            uploaded_contrib=json.load(f)
        eid=ehrid1
        result = ehrbase_routines.postcontrib(client,auth,url_base,eid,json.dumps(uploaded_contrib))
        assert result['status_code']==201
        contributionid=json.loads(result['text'])
        return contributionid
def test_postcontrib_run(test_postcontrib):
    assert test_postcontrib != ''

#51
def test_getcontrib(gapp,test_postcontrib):
    with gapp.app_context():      
        vid=test_postcontrib['uid']['value']
        eid=ehrid1
        result = ehrbase_routines.getcontrib(client,auth,url_base,eid,vid)
        assert result['status_code']==200

#52)
reversed_nodename=".".join(reversed(nodename.split(".")))
qname='tquery'
qname=reversed_nodename+"::"+qname
def test_post_aql(gapp):
    with gapp.app_context():
        aqltext='SELECT e/ehr_id/value FROM EHR e'
        version='1.0.0'
        qtype='AQL'
        result = ehrbase_routines.postaql(client,auth,url_base,aqltext,qname,version,qtype)
        assert result['status_code'] == 200

#53)
def test_get_aql(gapp):
    with gapp.app_context():
        aqltextobj='SELECT e/ehr_id/value FROM EHR e'
        version='1.0.0'
        result = ehrbase_routines.getaql(client,auth,url_base,qname,version)
        assert result['status_code'] == 200
        answer=json.loads(result['text'])
        assert answer['q']==aqltextobj
        assert answer['name']==qname
        assert answer['version']==version

#54)
def test_run_aql_get(gapp):
    with gapp.app_context():
        aqltext='SELECT e/ehr_id/value FROM EHR e'
        version2=''
        qname2=''
        qmethod='GET'
        qparam=''
        eid=''
        offset=''
        limit=''
        result = ehrbase_routines.runaql(client,auth,url_base,aqltext,qmethod,limit,offset,eid,qparam,qname2,version2)
        assert result['status_code'] == 200
        answer=json.loads(result['text'])
        assert answer['q']==aqltext      
        assert len(answer['rows'])>0

#54)
def test_run_aql_post(gapp):
    with gapp.app_context():
        aqltext='SELECT e/ehr_id/value FROM EHR e'
        version2=''
        qname2=''
        qmethod='POST'
        qparam=''
        eid=''
        offset=''
        limit=''
        result = ehrbase_routines.runaql(client,auth,url_base,aqltext,qmethod,limit,offset,eid,qparam,qname2,version2)
        assert result['status_code'] == 200
        answer=json.loads(result['text'])
        assert answer['q']==aqltext      
        assert len(answer['rows'])>0

#55
def test_create_form(gapp):
    with gapp.app_context():
        template_name='Interhealth_cancer_registry'
        result = ehrbase_routines.createform(client,auth,url_base,url_base_ecis,template_name,ehrbase_version)
        assert result['status']=='success'

#56
def test_del_aql(gapp):
    with gapp.app_context():
        version='1.0.0'
        result = ehrbase_routines.delaql(client,adauth,url_base_admin,qname,version)
        assert result['status']=='success'


# 57
def test_del_comp_user(gapp,test_postcomp_xml):
    with gapp.app_context():    
        composition1_id=test_postcomp_xml      
        compid=composition1_id+'::'+nodename+"::1"
        eid=ehrid1
        result = ehrbase_routines.delcompuser(client,auth,url_base,compid,eid)
        assert result['status']=='success'

# 58
def test_del_comp_admin(gapp,test_postcomp_json):
    with gapp.app_context():    
        composition2_id=test_postcomp_json      
        compid=composition2_id
        ehrid=ehrid1
        result = ehrbase_routines.delcomp(client,adauth,url_base_admin,compid,ehrid)
        assert result['status']=='success'

# 59
def test_del_dir_user(gapp):
    with gapp.app_context():    
        vid="6e13bbdb-893c-4260-b47d-f3585d178667::local.ehrbase.org::2"
        eid=ehrid1
        result = ehrbase_routines.deldir(client,auth,url_base,eid,vid)
        assert result['status']=='success'

# 60
def test_del_dir_admin(gapp):
    with gapp.app_context():    
        did="6e13bbdb-893c-4260-b47d-f3585d178667"
        eid=ehrid1
        result = ehrbase_routines.deldiradmin(client,adauth,url_base_admin,eid,did)
        assert result['status']=='success'

# 61
def test_del_ehr(gapp,test_post_ehr_ehrid_withoutehrid):
    with gapp.app_context():
        ehrid=test_post_ehr_ehrid_withoutehrid
        result=ehrbase_routines.delehrid(client,adauth,url_base_admin,ehrid)
        assert result['status']=='success'

