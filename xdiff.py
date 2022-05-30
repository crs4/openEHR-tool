#!/usr/bin/python3
# xdiff.py -- compare XML files
# Andreas Nolda 2022-05-11
# modified to be used as a routine by surfer@crs4.it
# from blessings import Terminal
# import sys

import re
from lxml import etree
from difflib import unified_diff
# term = Terminal(force_styling=True)

# def parse_file(file):
#     try:
#         xml_parser = etree.XMLParser(remove_blank_text=True,
#                                      remove_comments=False,
#                                      remove_pis=False)
#         tree = etree.parse(file, xml_parser)
#         return tree
#     except IOError:
#         print(term.bold_red(file) + ": No such file", file=sys.stderr)
#         sys.exit(2)
#     except etree.XMLSyntaxError:
#         print(term.bold_red(file) + ": File cannot be parsed", file=sys.stderr)
#         sys.exit(2)



def canonicalize_tree(tree):
    # canonicalize attributes
    string = etree.tostring(tree, method="c14n").decode()
    # canonicalize whitespace
    string = re.sub("\s+", " ", string)
    # indent elements linewise
    string = etree.tostring(etree.XML(string),
                            encoding="utf-8",
                            pretty_print=True).decode()

    string = re.sub("\n\s+", "\n", string)
    return string

def escape_spaces_in_string(string):
    return string.replace(" ", "\x00")

def unescape_spaces_in_string(string):
    return string.replace("\x00", " ")

def escape_spaces_in_match(match):
    match_string = match.group(0)
    string = escape_spaces_in_string(match_string)
    return string

def split_string_into_words(string):
    prefix = re.match("\s*", string).group(0)
    # escape whitespace in elements
    escaped_string = re.sub("<[^>]+>", escape_spaces_in_match, string)
    # unescape whitespace in elements after splitting string into words
    list = [unescape_spaces_in_string(item)
            for item in escaped_string.split()]
    
    list = [prefix + item
            for item in list]
    return list

def split_string_into_lines(string):
    # split string into lines
    list = string.splitlines(keepends=True)
    return list

def diff_strings(string1, string2):
    list1 = split_string_into_lines(string1)
    list2 = split_string_into_lines(string2)
    context = 0
    diff = unified_diff(list1,
                        list2,
                        fromfile='xml1',
                        tofile='xml2',
                        n=context)
    return diff

def xdiff(tree1,tree2):
    n = 0
    # tree1 = parse_file("../myoutput7DB10_1000_id_59499_retrieved_and_changed.xml")
    # tree2 = parse_file("../myoutput7DB10_1000_id_59499_retrieved.xml")
    string1 = canonicalize_tree(tree1)
    string2 = canonicalize_tree(tree2)
    diff = diff_strings(string1, string2)
    output=[]
    temp=[]
    for line in diff:
        if line.startswith("@@"):
            if(len(temp)):
                output.append(temp)
                temp=[]
            n += 1
            temp.append("@@ hunk #{0}:".format(n))
            # print(term.bold("@@ hunk #{0}:".format(n)))
        elif line.startswith("+++"):
            temp.append(line.rstrip())
            # print(term.bold(line), end="")
        elif line.startswith("---"):
            temp.append(line.rstrip())
            # print(term.bold(line), end="")
        elif line.startswith("+"):
            temp.append(line.rstrip())
            #  print(term.green(line), end="")
        elif line.startswith("-"):
            temp.append(line.rstrip())
            # print(term.red(line), end="")
        else:
            temp.append(line)            
            # print(line, end="")
    output.append(temp)    

    return output

