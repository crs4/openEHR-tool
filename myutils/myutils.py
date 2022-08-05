import base64
import json
from lxml import etree
from xmldiff import main as diffmain
from xdiff import xdiff
from json_tools import diff
import collections
from typing import Any,Callable
import re

def getauth(username,password):
    message=username+":"+password
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    auth="Basic "+base64_message
    return auth

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

def reorderbytime(fvalues_noorder,posfilled,sessiontotalevents,currentposition,reventsrecorded):
    #reorder log lines with first line created first
    if(sessiontotalevents<=reventsrecorded):
        return fvalues_noorder
    #currentposition-posfilled the first to be displayed
    fvalues=fvalues_noorder[currentposition:posfilled]
    #0-currentposition are the last to be displayed
    fvalues.extend(fvalues_noorder[0:currentposition])
    return fvalues

def findvaluesfromsearch(fv,logsearch,andornot):
    #custom search of multiple keys in and/or or both not
    #fv lines of log
    #logsearch keywords
    #andornot "and" or "or" or "not"
    if(logsearch==""):
        print('no keys')
    else:
        logsplit=logsearch.split()
        keywords=[k.lower() for k in logsplit]
        old=""
        for k in keywords:
            index=[]
            indexnot=[]
            for w in fv:
                if(k in w.lower()):
                    index.append('1')
                    indexnot.append('0')
                else:
                    index.append('0')
                    indexnot.append('1')
            sfinal=''.join(index)
            sfinalnot=''.join(indexnot)
            new=int(sfinal,2)
            newnot=int(sfinalnot,2)
            if(old!=""):
                if(andornot=='and'):
                    newvalue=bin(old & new)
                elif(andornot=='or'):
                    newvalue=bin(old | new)
                elif(andornot=='not'):
                    newvalue=bin(old & newnot)
                old=int(newvalue,2)
            else:
                if(andornot=='not'):
                    old=newnot
                else:
                    old=new
        newfinal=bin(old)
        l=len(fv)
        newfinalnob=newfinal.split('0b')[1]
        ln=len(newfinalnob)
        newvaluepadded='0'*(l-ln)+newfinalnob
        fv3=[]
        for i,n in enumerate(newvaluepadded):
            if(n=='1'):
                fv3.append(fv[i])
        return fv3
    