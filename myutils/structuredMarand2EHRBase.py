import json
import re
from flatten_json import flatten
from flask import current_app
import re
from terminology import openterm
import random


def get_composition_name(cM):
    '''retrieve the name of the composition (template)'''
    for child in cM:
        if child != 'ctx':
            cname=child
            return cname


def convert_ctx(cM,cE):
    '''convert the ctx from a Marand composition to the equivalent in EHRBase'''
    if 'ctx' not in cM:
        current_app.logger.warning('ctx not in Marand Composition')
        return
    cctx=cM['ctx']
    if 'language' in cctx:
        cE['language']=[{
            '|code':cctx['language'],
            '|terminology':'ISO_639-1'}]
    else:#defaults to english
        cE['language']=[{
            '|code':'en',
            '|terminology':'ISO_639-1'}]
                
    if 'territory' in cctx:
        if cctx['territory']=='en':
            cctx['territory']='GB'
        cE['territory']=[{
            '|code':cctx['territory'],
            '|terminology':'ISO_3166-1'}]    
    else:#defaults to IT
        cE['territory']=[{
            '|code':'IT',
            '|terminology':'ISO_3166-1'}] 
    cE['composer']=[{
        '|name':cctx['composer_name']
    }]

def convert_context(cM,cname):
    '''convert the context from a Marand composition to the equivalent in EHRBase'''
    cctx=cM[cname][0]['context'][0]
    cont={}
    if 'setting' in cctx:
        if cctx['setting'][0]['|code']=='setting code':#defaults to other care if not set
            cctx['setting'][0]['|code']='238'
            cctx['setting'][0]['|value']='other care'

    for k in cctx:
        if k=='setting':
           cont['setting']=[{ 
               '|code':cctx['setting'][0]['|code'],
               '|value':cctx['setting'][0]['|value'],
               '|terminology':'openehr'
           }] 
        else:
            cont[k]=cctx[k]
    return cont

def convert_category(cM,cE,cname):
    '''convert the category entry from a Marand composition to the equivalent in EHRBase'''
    cctx=cM[cname][0]['category'][0]
    if cctx['|code']=='433':
        cE['category']=[{
            '|code':cctx['|code'],
            '|terminology':'openehr',
            '|value':'event'
        }]
    else:
        current_app.logger.warning(f"category not event category_code={cctx['|code']}\nPlease add category manually")
    
def convert_content(cM,cE,cname):
    '''convert the rest of the content from Marand to EHRBase'''
    cctx=cM[cname][0]
    for k in cctx:
        if k not in cE:
            cE[k]=cctx[k]

def wtinfoaddtoList(mylist,elements,rmtypeobj,compulsory=False):
    for el in elements:
        eid=el['id']
        aqlpath=el['aqlPath']
        rmtype=el['rmType']
        dvintervalcondition= rmtypeobj=='DV_INTERVAL' and rmtype.startswith(rmtypeobj)
        if 'content' in aqlpath and (rmtype==rmtypeobj or dvintervalcondition):
            if 'inputs' in el:
                inputs=el['inputs']
            else:
                inputs=[]
            if compulsory:
                if el['min']>0:
                    mylist.append([eid,aqlpath,rmtype,inputs])
            else:
                mylist.append([eid,aqlpath,rmtype,inputs])
        if 'children' in el:
            wtinfoaddtoList(mylist,el['children'],rmtypeobj,compulsory)
    return mylist


def etinfoaddtoListDVCODEDTEXT(extemp):
    mylist2=[]
    for k in extemp:
        if k.endswith('|code') and not k.endswith('math_function|code') and \
        not k.endswith('/category|code') and not k.endswith('context/setting|code') and \
        not ':1' in k and not ':2' in k and not ':3' in k:
            if k[:-4]+'value' in extemp and k[:-4]+'terminology' in extemp:
                path=k[:-5]
                el={}
                lastslash=path.rfind('/')
                id=path[lastslash+1:]
                if id[-2]==':':
                    id=id[:-2]
                el['id']=id
                el['code']=extemp[k]
                el['value']=extemp[k[:-4]+'value']
                el['terminology']=extemp[k[:-4]+'terminology']
                sel={}
                sel[path]=el
                mylist2.append(sel)
    return mylist2

def lookforlist(w):
    '''create the list of admissable code/value for a given element whose list is not defined in the webtemplate'''
    if 'ism_transition' in w[1]:
        if w[0]=='transition':
            advalues=[]
            for it in openterm['instruction_transitions']:
                value=it['id']
                label=it['rubric']
                advalues.append({'label': label, 'localizedLabels': {'en': label}, 'value': value})
            w[3]=[{'list': advalues, 'suffix': 'code', 'terminology': 'openehr', 'type': 'CODED_TEXT'}]
            return True
    return False

def comparelists_WT_ET_DVCODEDTEXT(mylistW,mylistE):
    '''compare and merge the lists of dv_coded_text elements made from webtemplate and example composition from template
    output: list with id,possiblevalues,[match_indicator,pathfromExample]'''
    newlist=[]
    for w in mylistW:
        idw=w[0]
        pw=w[1]
        # current_app.logger.debug(f'w={w}')
        # current_app.logger.debug(w[3])
        if not 'list' in w[3][0]:
            #current_app.logger.debug(f'Creating a list for {w[0]} if possible')
            outcome=lookforlist(w)
            # current_app.logger.debug(f'list transition added w={w}')
            if not outcome:
                current_app.logger.error(f"Couldn't find any list of allowed codes/values for w={w}")
        nvalues=len(w[3][0]['list'])
        values=[{'code':w[3][0]['list'][i]['value'],'value':w[3][0]['list'][i]['label'],
                 'terminology':w[3][0]['terminology']} for i in range(nvalues)]
        if len(w[3])>1:
            if 'suffix' in w[3][1]:
                values.append({w[3][1]['suffix']:'othertext'})
        pathelements=[]
        if 'name/value' in pw:
            ifind=0
            while ifind != -1:
                ifindold=ifind
                ifind=pw.find('name/value=',ifindold+1)
                if ifind != -1:
                    jfind=pw.find("'",ifind+12)
                    pathelements.append(pw[ifind+12:jfind].lower().replace(' ','_'))
        liste=[]
        for e in mylistE:
            for k in e:
                pe=k
                ide=e[k]['id']
                g=0
                if idw==ide:
                    # current_app.logger.debug('--------')
                    # current_app.logger.debug(f'id={ide}')
                    # current_app.logger.debug(f'pathW={pw}')
                    # current_app.logger.debug(f'pathE={pe}')
                    if len(pathelements)>0:
                        for p in pathelements:
                            if p in pe:
                                g+=1
                    liste.append([g,pe])
        newlist.append([idw,values,liste])
    final_list=[]
    for n in newlist:
        if len(n[2])>1:
            wl=max(n[2], key = lambda i : i[0])
            final_list.append([n[0],n[1],[wl]])
        else:
            final_list.append(n)
    return final_list

def flattenpath(cM):
    cMstring=json.dumps(cM)
    cM22string=cMstring.replace("_","@")
    cM2=json.loads(cM22string)
    return flatten(cM2)

    
def createpathstructured(pathflat):
    '''convert a flat path to a structured one and return it along with a list of elements to be checked for occurrences in composition
    Return strings so it needs eval on the calling subroutine'''
    pathsplit=pathflat.split('/')
    newpathsplit=[]
    lenocc=[]
    for i,p in enumerate(pathsplit):
        if p.endswith(':0'):
            p2=p[:-2]
            newpathsplit.append("['"+p2+"']")             
            if i != len(pathsplit)-1:
                pstruct='[0]'.join(newpathsplit)
                # current_app.logger.debug(f'pstruct={pstruct}')
                lenocc.append(pstruct)    
        else:
            newpathsplit.append("['"+p+"']")
    pathstruct='[0]'.join(newpathsplit)
    
    return (pathstruct,lenocc)

def flatlike(l):
    l2=l.replace('_','@')
    l3=re.sub(r"\[\'(\D+\d*)\'\]",r"\g<1>",l2,re.MULTILINE)
    l4=re.sub(r"\[(\d)\]",r"_\g<1>_",l3,re.MULTILINE)
    return l4

def structlikefromflat(l):
    l2=re.sub(r"\_(\d)\_","'][\g<1>]['",l)
    l3=re.sub(r"\_(\d)$","'][\g<1>]",l2)
    l4=l3.replace('@','_')
    l5="['"+l4
    return l5

def createnewpaths(path,lenocc,flattenedcm,cname):

    if len(lenocc)==0:
        lcname2=len(cname)+7#len=2{['}+len(cname)+2{']}+3{[0]}'
        newpaths=[path[lcname2:]]
    else:
        newpaths_partials=[]
        for l in lenocc:
            # current_app.logger.debug(f'lenocc={l}')
            newpaths_partials_lenocc=[]
            pathtocheck=flatlike(l)
            occurrence_exists=True
            i=-1
            while occurrence_exists:
                i=i+1
                p=pathtocheck+'_'+str(i)
                # current_app.logger.debug(f'looking for {p}')
                found=False
                for f in flattenedcm:
                    if f.startswith(p):
                        # current_app.logger.debug(f'{p} found in {f}')
                        newpaths_partials_lenocc.append(p)
                        found=True
                        break
                occurrence_exists=found
            newpaths_partials.append(newpaths_partials_lenocc)
        
        # current_app.logger.debug('NPP')
        # current_app.logger.debug(newpaths_partials)

        newpathtotgarbled=getpaths(newpaths_partials)
        # current_app.logger.debug('NPG')
        # current_app.logger.debug(newpathtotgarbled)

        newpaths=[]
        lcname2=len(cname)+7#len=2{['}+len(cname)+2{']}+3{[0]}'
        # current_app.logger.debug('PIECE')
        lastnpg=structlikefromflat(newpathtotgarbled[-1])
        lastpiecepath=path[len(lastnpg):]
        # current_app.logger.debug(f'path={path}')
        # current_app.logger.debug(f'lastnpg={lastnpg}')
        for npg in newpathtotgarbled:
            # current_app.logger.debug(f'npg={npg}')
            npgn=structlikefromflat(npg)
            # current_app.logger.debug(f'npgn={npgn}')
            newpaths.append(npgn[lcname2:]+lastpiecepath)
        #     current_app.logger.debug(f'npfinal={npgn[lcname2:]+lastpiecepath}')

        # current_app.logger.debug('CREATENEWPATHS')
        # current_app.logger.debug(f'path={path}')
        # current_app.logger.debug(f'newpaths={newpaths}')

    return newpaths

def getpaths(newpaths_partials):
    oldfirst=newpaths_partials[0][0]
    for i in range(1,len(newpaths_partials)):
        first=newpaths_partials[i][0]
        if not first.startswith(oldfirst):
            print(f'Error: inner path {oldfirst} not included in outer one {first}')
            break
        oldfirst=first

    newpath=[]
    if len(newpaths_partials)==1:
        i=0
        for j,n in enumerate(newpaths_partials[i]):
            newpath.append(n)

    else:
        i=0
        for j,n in enumerate(newpaths_partials[i]):
            # current_app.logger.debug(f'j={j}')
            piece=[n]
            for m in range(i+1,len(newpaths_partials)):
                # current_app.logger.debug(f'm={m}')
                for k,nn in enumerate(newpaths_partials[m]):
                    if k==0:
                        newpiece=[]
                    # current_app.logger.debug(f'nn={nn}')
                    for p in piece:
                        newpiece.append(p+nn[len(p):])

                    # current_app.logger.debug(f'newpieces {newpiece}')
                    
                    if k==len(newpaths_partials[m])-1:
                        piece=newpiece
                    if m==len(newpaths_partials)-1 and k==len(newpaths_partials[m])-1:
                        # current_app.logger.debug(f'NP: newpiece={newpiece}')
                        newpath.extend(newpiece)
    
    # current_app.logger.debug(f'len(newpath)={len(newpath)}')

    return newpath



def findpathtocoded(cE,listofcoded,cname,flattenedcm):
    ''' find path in Marand for dv_coded_text elements in list of paths and return it together with allowed values'''
    pathtocoded=[]
    for lc in listofcoded:
        # current_app.logger.debug(f'id={lc[0]}')
        (path,lenocc)=createpathstructured(lc[2][0][1])
        # current_app.logger.debug('FINDPATHTOCODED')
        # for l in lenocc:
        #     current_app.logger.debug(f'original l={l}')
        #     current_app.logger.debug(flatlike(l))
        
        # current_app.logger.debug(f'path={path} lenocc={lenocc}')
        newpaths=createnewpaths(path,lenocc,flattenedcm,cname)
        # current_app.logger.debug(f'newpaths={newpaths}')

        if len(newpaths)!=0:
            for p in newpaths:
                pathtocoded.append(["cE"+p,lc[1]])
                # current_app.logger.debug(f'appended [{"cE"+p} , {lc[1]}]')
        
    return pathtocoded



def fixes_dv_coded_text(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_coded_text in webtemplate content
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_CODED_TEXT')
    #current_app.logger.debug(len(mylistW))
    #current_app.logger.debug(mylist)
    #create same list but from example composition
    mylistE=etinfoaddtoListDVCODEDTEXT(extemp)
    #current_app.logger.debug('------')
    # current_app.logger.debug(f'len listE={len(mylistE)}')
    # current_app.logger.debug(f'listE={mylistE}')

    #compare and merge the two lists to find the right paths and allowed values
    listofcoded=comparelists_WT_ET_DVCODEDTEXT(mylistW,mylistE)
    # current_app.logger.debug(f'listofcoded={listofcoded}')

    #find path in Marand for the dv coded values
    pathtocoded=findpathtocoded(cE,listofcoded,cname,flattenedcm)
    # current_app.logger.debug(json.dumps(pathtocoded,indent=2))

    # current_app.logger.debug('------')
    #fix all the coded_text in the list
    #code is right, the rest must be corrected
    for p in pathtocoded:
        # current_app.logger.debug('&&&&&&&&&&&&loop in pathtocoded&&&&&&&&&&&&&&&&&')
        # current_app.logger.debug(p[0])
        # current_app.logger.debug(p[1])
        # current_app.logger.debug(eval(p[0]))
        cpresent=eval(p[0])[0]
        if '|code' in cpresent:
            otherpresent=cpresent.pop('|other', None)
            if otherpresent != None:
                current_app.logger.debug('removed other')
            codepresent=cpresent['|code']
            valuepresent='Not found'
            # current_app.logger.debug(f'code={codepresent}')
            cc=False
            for cv in p[1]:
                if 'code' in cv:
                    cc=True
                    ff=False
                    if cv['code']==codepresent:
                        valuepresent=cv['value']
                        # current_app.logger.debug(f'=>value={valuepresent}')
                        cpresent['|value']=valuepresent
                        # current_app.logger.debug(eval(p[0])[0]['|value'])
                        if 'terminology' in cv:
                            cpresent['|terminology']=cv['terminology']
                            # current_app.logger.debug(f"=>{eval(p[0])[0]['|terminology']}")
                        ff=True
                        break
            if cc:
                if not ff: #code present in webtemplate but coded element not among allowed ones
                    maxl=len(p[1])
                    chosen=random.randint(0,maxl-1)
                    if "['ism_transition'][0]['transition']" in p[0]:
                        chosen=14
                    cpresent['|code']=p[1][chosen]['code']
                    cpresent['|value']=p[1][chosen]['value']
                    if 'terminology' in p[1][chosen]:
                            cpresent['|terminology']=p[1][chosen]['terminology']
                    current_app.logger.debug(f"code present in webtemplate but coded element not among allowed ones {p[0]}\n added {cpresent}")

        elif '|other' in cpresent:
            current_app.logger.debug('other present')
            if 'other' in p[1][-1]:
                current_app.logger.debug('other admissible')
                pass#do nothing
            else:
                current_app.logger.warning(f'other not allowed for {p[0]}')

def etinfoaddtoListDVQUANTITY(extemp):
    mylist2=[]
    for k in extemp:
        if k.endswith('|unit'):
            if k[:-4]+'magnitude' in extemp and \
                not ':1' in k and not ':2' in k and not ':3' in k:
                path=k[:-5]
                el={}
                lastslash=path.rfind('/')
                id=path[lastslash+1:]
                if id[-2]==':':
                    id=id[:-2]
                el['id']=id
                el['magnitude']=extemp[k[:-4]+'magnitude']
                sel={}
                sel[path]=el
                mylist2.append(sel)
    return mylist2

def findpathtoquantity(cE,listofq,cname,flattenedcm):
    ''' find path in Marand for quantity elements in list of paths and return it'''
    # with open('pippo','w') as p:
    #     json.dump(cE,p)
    #current_app.logger.debug(json_list_traverse(cE))
    pathtoq=[]
    for lc in listofq:
        pathq=list(lc.keys())
        # current_app.logger.debug(f"id={lc[pathq[0]]['id']}")
        (path,lenocc)=createpathstructured(pathq[0])
        # current_app.logger.debug('FPQ')
        # current_app.logger.debug(path)
        # current_app.logger.debug(lenocc)
        #path=path[lcname:]#remove template name
        #current_app.logger.debug(path)
        #current_app.logger.debug(eval("cE"+path))
        newpaths=createnewpaths(path,lenocc,flattenedcm,cname)
        if len(newpaths)!=0:
            for p in newpaths:
                pathtoq.append(["cE"+p])
                # current_app.logger.debug(f'appended [{"cE"+p}]')

    return pathtoq

def fixes_dv_quantity(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_quantity in webtemplate content
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_QUANTITY')
    mylistE=etinfoaddtoListDVQUANTITY(extemp)
    if len(mylistW) != len(mylistE):
        current_app.logger.debug(f'warning DV_QUANTITY: from template #entity={len(mylistW)} from composition #entity={len(mylistE)}')
    # current_app.logger.debug(json.dumps(mylistE,indent=2))

    #find path in Marand for the dv coded values
    pathtoq=findpathtoquantity(cE,mylistE,cname,flattenedcm)
    # current_app.logger.debug(json.dumps(pathtoq,indent=2))

    # current_app.logger.debug('------')
    #fix all the dv_quantity in the list
    #unit is right, missing magnitude
    for p in pathtoq:
        # current_app.logger.debug('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # current_app.logger.debug(p[0])
        # current_app.logger.debug(eval(p[0]))
        cpresent=eval(p[0])[0]
        if '|unit' in cpresent:
            if '|magnitude' not in cpresent:
                cpresent['|magnitude']=0
                # current_app.logger.debug(cpresent)

def etinfoaddtoListDVPROPORTION(extemp):
    mylist2=[]
    for k in extemp:
        if k.endswith('|denominator'):
            # current_app.logger.debug(f'k={k}**************')
            if k[:-11]+'numerator' in extemp and \
                not ':1' in k and not ':2' in k and not ':3' in k:
                path=k[:-12]
                el={}
                lastslash=path.rfind('/')
                id=path[lastslash+1:]
                if id[-2]==':':
                    id=id[:-2]
                el['id']=id
                el['numerator']=extemp[k[:-11]+'numerator']
                el['denominator']=extemp[k[:-11]+'denominator']
                sel={}
                sel[path]=el
                mylist2.append(sel)
    return mylist2

def findpathtoproportion(cE,listofp,cname,flattenedcm):
    ''' find path in Marand for proportion elements in list of paths and return it'''
    return findpathtoquantity(cE,listofp,cname,flattenedcm)


def fixes_dv_proportion(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_proportion in webtemplate content
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_PROPORTION')
    #current_app.logger.debug(len(mylistW))
    #current_app.logger.debug(mylist)
    #create same list but from example composition
    mylistE=etinfoaddtoListDVPROPORTION(extemp)
    if len(mylistW) != len(mylistE):
        current_app.logger.debug(f'warning DV_PROPORTION: from template #entity={len(mylistW)} from composition #entity={len(mylistE)}')
    # current_app.logger.debug(json.dumps(mylistE,indent=2))
    #current_app.logger.debug(len(mylistE))

    #compare and merge the two lists to find the right paths and allowed values
    #listofcoded=comparelists_WT_ET(mylistW,mylistE)

    #find path in Marand for the dv coded values
    pathtop=findpathtoproportion(cE,mylistE,cname,flattenedcm)
    # current_app.logger.debug(json.dumps(pathtop,indent=2))

    # current_app.logger.debug('------')
    #fix all the dv_proportion in the list
    #unit is right, missing magnitude
    for p in pathtop:
        # current_app.logger.debug('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # current_app.logger.debug(p[0])
        # current_app.logger.debug(eval(p[0]))
        cpresent=eval(p[0])[0]
        if '|denominator' in cpresent:
            if '|type' not in cpresent:
                cpresent['|type']=3
                if cpresent['|denominator'] != 0:
                    cpresent['']=cpresent['|numerator']/cpresent['|denominator']
                # current_app.logger.debug(cpresent)


def findentriesinex(extemp,entries):
    mylist2=[]
    for e in entries:
        found=False
        for k in extemp:
            if  not found:
                ksplit=k.split('/')
                if e in ksplit and not ':1' in k and not ':2' in k and not ':3' in k:
                    # current_app.logger.debug(f'k={k}**************')
                    kindex=ksplit.index(e)
                    kpath='/'.join(ksplit[:kindex+1])
                    # current_app.logger.debug(kpath)
                    path=kpath
                    el={}
                    lastslash=path.rfind('/')
                    id=path[lastslash+1:]
                    if id[-2]==':':
                        id=id[:-2]
                    el['id']=id
                    sel={}
                    sel[path]=el
                    mylist2.append(sel)
                    found=True
    return mylist2    

def addentriesfromex(extemp,mypathE):
    mylist=[]

    for m in mypathE:
        # current_app.logger.debug(f'mypathE first {m}')
        break

    for k in extemp:
        if k.endswith('/language|code') and len(k.split('/'))>2:
            # current_app.logger.debug(f'kkkkkkkkkkk={k}')
            lastslash=k.rfind('/')
            path=k[:lastslash]
            llast=k.rfind('/',1,lastslash)
            id=k[llast+1:lastslash]
            if id[-2]==':':
                id=id[:-2]
            el={}
            sel={}
            el['id']=id
            sel[path]=el
            mylist.append(sel)
    return mylist  


def add_language_encoding(cE,extemp,cname,flattenedcm):
    mypathE=[]

    #add language and encoding in example not considered yet
    addede=addentriesfromex(extemp,mypathE)
    # current_app.logger.debug(f'mylist={addede}')

    mypathE.extend(addede)

    pathtoe=findpathtoproportion(cE,mypathE,cname,flattenedcm)
    # current_app.logger.debug(f'pathtoe={pathtoe}')
    #current_app.logger.debug(json.dumps(pathtoe,indent=2))
    for p in pathtoe:
            # current_app.logger.debug('&&&&&&&&&add language encoding&&&&&&&&&&&&&&&&&&&&')
            # current_app.logger.debug(f'p[0]={p[0]}')
            #current_app.logger.debug(eval(p[0]))
            cpresent=eval(p[0])
            for c in cpresent:
                if 'language' not in c:
                    c['language']= [
                                {
                                    "|code": "en",
                                    "|terminology": "ISO_639-1"
                                }
                            ]
                if 'encoding' not in c:
                    c['encoding']= [
                        {
                            "|code": "UTF-8",
                            "|terminology": "IANA_character-sets"
                        }
                    ]

def etinfoaddtoListcustom(extemp,customend):
    mylist2=[]
    for k in extemp:
        for c in customend:
            if k.endswith(c):
                if not ':1' in k and not ':2' in k and not ':3' in k:
                    path=k
                    el={}
                    lastslash=path.rfind('/')
                    id=path[lastslash+1:]
                    if id[-2]==':':
                        id=id[:-2]
                    el['id']=id
                    sel={}
                    sel[path]=el
                    mylist2.append(sel)
    return mylist2

def fix_position_substituted(cE,extemp,cname,flattenedcm):
    mypathps=etinfoaddtoListcustom(extemp,['position_substituted'])
    # current_app.logger.debug(mypathps)
    pathtos=findpathtoproportion(cE,mypathps,cname,flattenedcm)

    for p in pathtos:
        # current_app.logger.debug('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # current_app.logger.debug(p[0])
        # current_app.logger.debug(p[0][:-24])
        # current_app.logger.debug(eval("len('+p[0][:-24]+')"))
        cpresent=eval(p[0][:-24])
        cpresent['position_substituted']=[0]
        # current_app.logger.debug(cpresent)
        #current_app.logger.debug(eval(p[0]))   
  
def fixes_dv_count(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_count in webtemplate content with min>0
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_COUNT',True)
    #current_app.logger.debug(len(mylistW))
    # current_app.logger.debug('555555555555555')
    # current_app.logger.debug(mylistW)
    mylistfirsts=[m[0] for m in mylistW]
    mypathps=etinfoaddtoListcustom(extemp,mylistfirsts)
    # current_app.logger.debug(mypathps)
    pathtos=findpathtoproportion(cE,mypathps,cname,flattenedcm)
    # current_app.logger.debug(pathtos)
    # current_app.logger.debug(type(pathtos))
    
    #fix all the min>1 dv_count  in the list
    for p in pathtos:
        # current_app.logger.debug(p[0])
        i=p[0].rfind('[0]')+3
        # current_app.logger.debug('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # current_app.logger.debug(p[0][:i])
        # current_app.logger.debug(eval("len('+p[0][:i]+')"))
        cpresent=eval(p[0][:i])
        #current_app.logger.debug(cpresent)
        id=p[0][i+2:-2]
        # current_app.logger.debug(id)
        cpresent[id]=[0]
        # current_app.logger.debug(cpresent)
        #current_app.logger.debug(eval(p[0]))   

def convertintervalname(name):
    return name.replace("<dv","_of").replace(">","")

def fixes_dv_interval(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_interval in webtemplate content with min>0
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_INTERVAL',True)
    #current_app.logger.debug(len(mylistW))
    # current_app.logger.debug('7777777')
    # current_app.logger.debug(mylistW)

    conversions=[]
    for m in mylistW:
        converted=convertintervalname(m[0])
        conversions.append([converted,m[0]])

    for c in conversions:
        fc0=flatlike(c[0])
        for f in flattenedcm:
            if fc0 in f:
                myindex=f.find(fc0)
                l=len(fc0)
                # current_app.logger.debug(f'f={f}')
                pathbefore=structlikefromflat(f[len(cname)+3:myindex-1])
                cpresent=eval("cE"+pathbefore)
                if c[0] in cpresent: #not yet corrected
                    value=eval("cE"+pathbefore+"['"+c[0]+"']")
                    # current_app.logger.debug(f'8888 pathbefore={pathbefore} value={value} c[1]={c[1]}')
                    cpresent[c[1]]=value
                    # current_app.logger.debug(f' cpresent={cpresent}')
                    cpresent.pop(c[0])
                    # current_app.logger.debug(f'final cpresent={cpresent}')

def fixes_dv_boolean(cE,webtemp,extemp,cname,flattenedcm):
    #find all dv_boolean in webtemplate content with min>0 and add them to the composition
    wt=webtemp['webTemplate']['tree']['children']
    mylistW=[]
    mylistW=wtinfoaddtoList(mylistW,wt,'DV_BOOLEAN',True)
    #current_app.logger.debug(len(mylistW))
    # current_app.logger.debug('999')
    # current_app.logger.debug(mylistW)

    mybooleans=[]
    for m in mylistW:
        for e in extemp:
            if m[0] in e and ':1' not in e and ':2' not in e and ':3' not in e:
                mybooleans.append(e)
    
    # current_app.logger.debug(f'mybooleans={mybooleans}')
    pathstob=[]
    for mb in mybooleans:
        (path,lenocc)=createpathstructured(mb)
        # current_app.logger.debug('FINDPATHTOBOOLEANS')
        # for l in lenocc:
            # current_app.logger.debug(f'original l={l}')
            # current_app.logger.debug(f'flatlike l={flatlike(l)}')
        #path=path[lcname:]#remove template name
        # current_app.logger.debug(f'path={path} lenocc={lenocc}')
        #current_app.logger.debug(f'path[lcname:]={path[lcname:]}')
        newpaths=createnewpaths(path,lenocc,flattenedcm,cname)
        # current_app.logger.debug(f'newpaths={newpaths}')
        if len(newpaths)!=0:
            for p in newpaths:
                pathstob.append(["cE"+p])
                # current_app.logger.debug(f'appended [{"cE"+p}]')
    
    for ptb in pathstob:
        # current_app.logger.debug(f'ptb={ptb}')
        for p in ptb:
            commitptb(cE,p,False)
        #false

def commitptb(cE,pathtobecommitted,value):
    #recreate all the path when needed till the last element where the value is inserted
# ["cE['histopathology'][0]['result_group'][0]['laboratory_test_result'][0]['any_event'][0]['recurrence'][0]['anatomical_pathology_finding'][0]['biological_material_from_recurrence_available']"]   
    ptbs=pathtobecommitted.split('[')
    position=len(ptbs)-1
    for i in range(3,len(ptbs)-1,2):
        element=ptbs[i].split(']')[0].replace("'","")
        path='['.join(ptbs[:i])
        elbefore=eval(path)
        # current_app.logger.debug(f'i={i} element={element} path={path} elbefore={elbefore}')
        # current_app.logger.debug(type(element),type(elbefore))
        # current_app.logger.debug(f'element in elbefore={element in elbefore}')
        # current_app.logger.debug(f'element in keys={element in elbefore.keys()}')
        # current_app.logger.debug(f'elbeforekeys={elbefore.keys()}')
        # for ek in list(elbefore.keys()):
        #     current_app.logger.debug(f'ek={ek} element={element}')
        if not (element in elbefore):
            # current_app.logger.debug(f'element not in elbefore position={i}')
            # current_app.logger.debug(f'element={element} elbefore={elbefore}')
            # current_app.logger.debug(elbefore.keys())
            position=i
            # current_app.logger.debug(f'position={position}')
            break
    #return position
    #cE['histopathology'][0]['result_group'][0]['laboratory_test_result'][0]['any_event'][0]['recurrence'][0]['anatomical_pathology_finding'][0]['biological_material_from_recurrence_available']
    #'cE', "'histopathology']", '0]', 
    # "'result_group']", '0]', 
    # "'laboratory_test_result']", '0]', 
    # "'any_event']", '0]', 
    # "'recurrence']", '0]', 
    # "'anatomical_pathology_finding']", '0]', 
    # "'biological_material_from_recurrence_available']"]
    #ce={'histopathology':[{'result_group':[{'laboratory_test_result':[{'any_event':[{'recurrence':[{'anatomical_pathology_finding':[{biological_material_from_recurrence_available':'pippo'}]}]}]}]}]}]}
    #cp=[{'laboratory_test_result': [{'any_event': [{'recurrence': [{'anatomical_pathology_finding': [{'biological_material_from_recurrence_available': 'pippo'}]}]}]}]}]

    if position != len(ptbs)-1:
        for i in range(len(ptbs)-1,position+2,-1):      
                element=ptbs[i].split(']')[0]
                # current_app.logger.debug(f'i={i} element={element}')
                if "'" in element:
                    element=element.replace("'","")
                    if i==len(ptbs)-1:
                        cp={}
                        cp[element]=value
                        # current_app.logger.DEBUG(f'cp={cp}')
                    else:
                        newcp={}
                        newcp[element]=cp
                        cp=newcp
                        # current_app.logger.debug(f'cp={cp}')
                else:
                    newcp=[]
                    newcp.append(cp)
                    cp=newcp
                    # current_app.logger.debug(f'cp={cp}')
        pathbef="[".join(ptbs[:position])
        ep=eval(pathbef)
        mykey=ptbs[position].split(']')[0].replace("'","")
        ep[mykey]=cp
        # current_app.logger.debug(f'ep={ep} mykey={mykey} ep[mykey]={ep[mykey]}')
    else:
        pathbef="[".join(ptbs[:position])
        ep=eval(pathbef)
        mykey=ptbs[position].split(']')[0].replace("'","")
        ep[mykey]=value
        # current_app.logger.debug(f'ep={ep} mykey={mykey} ep[mykey]={ep[mykey]}')
        # current_app.logger.debug(cE)


def structuredMarand2EHRBase(compMARAND,client,auth,hostname,port,username,password,composition,eid,tid):
    '''convert a structured Marand composition to a EHRBase one
    input: composition returned from Marand Designer, template in webtemplate format
    output: composition in EHRBase structured format'''
    current_app.logger.debug('inside structuredMarand2EHRBase')
    # import sys
    # sys.path.append('..')
    from ehrbase_routines import gettemp,examplecomp

    

    cname=tid
    # current_app.logger.debug(f'CNAME={cname}')

    #create flattened version of structured composition
    flattenedcm=flattenpath(compMARAND)
    # current_app.logger.debug('FLATTENED')
    # for fl in flattenedcm:
    #     current_app.logger.debug(fl)

    #get webtemplate
    myresptemp=gettemp(client,auth,hostname,port,username,password,'wt',tid)
    if 'template' in myresptemp:
        mwtstring=myresptemp['template']
        webtemp=json.loads(mwtstring)
    else:
        myresptemp['status']='failure'
        current_app.logger.debug('Problem in getting webtemplate')
        return myresptemp

    #get example from template
    myrespex=examplecomp(client,auth,hostname,port,username,password,tid,'FLAT')
    if 'flat' in myrespex:
        mexstring=myrespex['flat']
        extemp=json.loads(mexstring)
    else:
        myrespex['status']='failure'
        current_app.logger.debug('Problem in getting excample from template')        
        return myrespex


    compEHRBase={}
    comp={}

    current_app.logger.info('Converting ctx')
    convert_ctx(compMARAND,comp)

    current_app.logger.info('Converting context')
    compcontext=convert_context(compMARAND,cname)

    comp['context']=[]
    comp['context'].append(compcontext)

    current_app.logger.info('converting category')
    convert_category(compMARAND,comp,cname)


    current_app.logger.info('converting content')
    convert_content(compMARAND,comp,cname)


    current_app.logger.info('Fixing DV_CODED_TEXT leafs')
    fixes_dv_coded_text(comp,webtemp,extemp,cname,flattenedcm)

    
    current_app.logger.info('Fixing DV_QUANTITY leafs')
    print('Fixing DV_QUANTITY leafs')
    fixes_dv_quantity(comp,webtemp,extemp,cname,flattenedcm)
  

    current_app.logger.info('Fixing DV_PROPORTION leafs')
    fixes_dv_proportion(comp,webtemp,extemp,cname,flattenedcm)

    current_app.logger.info('Fixing DV_COUNT leafs')
    fixes_dv_count(comp,webtemp,extemp,cname,flattenedcm)


    current_app.logger.info('Fixing DV_INTERVAL leafs')
    fixes_dv_interval(comp,webtemp,extemp,cname,flattenedcm)

    current_app.logger.info('Fixing DV_BOOLEAN leafs. Boolean are lost during export of forms!!!!')
    fixes_dv_boolean(comp,webtemp,extemp,cname,flattenedcm)

    current_app.logger.info('Adding Language and encoding to all entries (i.e. OBSERVATION, ACTION, EVALUATION, ADMIN_ENTRY)')
    add_language_encoding(comp,extemp,cname,flattenedcm)

    #assign temp composition to EHRBase composition
    compEHRBase[cname]=comp

    current_app.logger.debug(f'done converting Archetype Designer Structured Composition to EHRBase Structured format')

    myresp={}
    myresp['status']='success'
    myresp['composition']=compEHRBase
    
    return myresp
