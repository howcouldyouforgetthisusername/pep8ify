# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 14:49:00 2016

@author: giraffe
"""

import re
from pprint import pprint

def getContentOfAnnualReports(fi):
    """
    Takes in an official statement text file and returns the text of the
    section entitled "(?i)Content of Annual Reports" as a big ol' string.
    """
    contentSection = []
    
    inContentOfAnnualReports = False
    # We iterate over the lines in the official statement, including every
    # line between the section entitled "content of annual reports" and
    # the next section.
    for line in fi:
        #print(line)
        # If we pass the end of the Content of Annual Reports section, return.
        if inContentOfAnnualReports and\
            re.match("(?i)Section\d{1,2}\.",
                     re.sub('\s+', '',  line)):
            return ''.join(contentSection).strip() 
        
        # Check if we just entered the content of annual reports section.
        if not inContentOfAnnualReports and\
            re.match("(?i)Section\d{1,2}\.ContentOfAnnualReports\.",
                    re.sub('\s+', '', line)):
            inContentOfAnnualReports = True
        
        if inContentOfAnnualReports:
            contentSection.append(line)

def isStopGroup(group):
    """
    Takes in the text of a group from the Content of Annual Reports section of
    an official statement, and returns whether or not this is a 'stop group',
    i.e. a group that doesn't actually list a requirement.
    """
    if re.search("(?i)in addition to any of the information expressly required", group):
        return True
    if re.search("(?i)any or all of the items listed above", group):
        return True
    if re.search("(?i)to the extent not .{2,10} in the audited financial statements", group):
        return True
    
    return False

def getAnnualReportRequirements(contentOfAnnualReportsSection):
    """
    Takes in a big ol' string representing the section of an official statement
    entitled "Content of Annual Reports" and returns a plaintext list of
    requirements for that annual report. If possible, will return a canonical
    version of the requirement; if not, will just return it as-is.
    """
    """
    The rough plan here:
    Look through each 'grouping' of the text; i.e. starting with (???) on a
    new line and ending with the next such grouping. For each grouping,
    try to look through it for various terms and canonicalize if possible.
    If not, just append the entire text of that grouping to the return list.
    """
    annualReportRequirements = []
    groups = re.split("(?i)\n\s*\([^()]*\) |\n\d\. ", '\n' + contentOfAnnualReportsSection)[1:]
    for group in groups:
        group = re.sub("\n", ' ', group)
        group = re.sub("  ", " ", group)
        group = re.sub("[^a-zA-Z0-9 ]", '', group).strip()
        # First, we filter out some laaaame groups that don't do anything.
        if not isStopGroup(group):
            annualReportRequirements.append(group)
    
    return annualReportRequirements
    

def classifyRequirements(plaintextRequirements):
    """
    Takes a list of strings, each representing a requirement for annual reports.
    Returns a dictionary containing 5 k/v pairs:
    "budget" : T/F
    "attendance" : T/F
    "audited financial statements" : T/F
    "assessed valuation" : T/F
    "top taxpayers" : T/F
    """
    requirements = {"budget" : False,
                       "attendance" : False,
                       "audited financial statements" : False,
                       "assessed valuation" : False,
                       "top taxpayers" : False}
    for req in plaintextRequirements:
        # First, we check if it's a budget requirement.
        if re.search("(?i)budget", req):
            requirements["budget"] = True
        # Check if it's an attendance requirement
        if re.search("(?i)attendance|enrollment", req):
            requirements["attendance"] = True
        # Check if it's an audited financials requirement.
        if re.search("(?i)audited financial statements", req):
            requirements["audited financial statements"] = True
        # Check if it's an assessed valuation requirement.
        if re.search("(?i)assessed valuation", req):
            requirements["assessed valuation"] = True
        # Check if it's a top taxpayers requirement.
        if re.search("(?i)tax payers|taxpayers", req):
            requirements["top taxpayers"] = True
    return requirements


filenames = ['OS1.txt', 'OS2.txt', 'OS3.txt']
for fn in filenames:
    with open(fn, 'r') as fi:
        requirementsPlaintext = getAnnualReportRequirements(getContentOfAnnualReports(fi))
        docReqs = classifyRequirements(requirementsPlaintext)
        pprint(docReqs)