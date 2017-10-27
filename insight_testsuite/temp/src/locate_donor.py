#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 21:49:36 2017

@author: Nan
"""

from __future__ import division

__author__ = "Nan Shen"
__copyright__ = "Copyright 2017, Nan-Shen"
__credits__ = ["Nan Shen"]
__license__ = "GPL"
__version__ = "0.1-dev"
__maintainer__ = "Nan Shen"
__email__ = "nan.shen@icahn.mssm.edu"


"""This script can take in pipe-delimited txt file contains information about 
a campaign contribution that was made on a particular date from a donor to 
a recipient. It will generate two output files:
    
    1. Pipe-delimited "medianvals_by_zip.txt": for each input file line, 
    calculate the running median of contributions, total number of transactions 
    and total amount of contributions streaming in so far for that recipient 
    and zip code.
    
    2. Pipe-delimited "medianvals_by_date.txt": for each combination of date 
    and recipient, median contribution, total number of transactions, 
    and total amount of contributions, sorted alphabetical by recipient 
    and then chronologically by date.
"""

import sys
from os.path import isfile
from datetime import datetime

def locate_donor():
    """main function: parse arguments, check if output files exist and finally 
    read in input, process and write output files
    """
    infp, out1, out2 = parse_arg()
    check_fp(out1)
    check_fp(out2)
    parse_input(infp, out1, out2)

#########################################
## parse input file and check fields ##
#########################################
def parse_input(infp, out1, out2):
    """Parse input file, check format and field values and write to output file
    infp: input file path
    out1: "medianvals_by_zip.txt" output file path
    out2: "medianvals_by_date.txt" output file path
    """
    zipDic = {}
    dtDic = {}
    with open(infp) as f:
        for line in f:
            cmteID, zipCode, date, amt, otherID = parse_line(line)
            if check_line(cmteID, amt, otherID):
                if check_line_zip(zipCode):
                    zipline = update_zipDic(cmteID, zipCode, amt, zipDic)
                    #write medianvals_by_zip.txt as reading input line by line.
                    write_zipDic(zipline, out1)
                if check_line_dt(date):
                    update_dtDic(cmteID, date, amt, dtDic)
    #write medianvals_by_date.txt when the full Dic is complete.
    write_dtDic(dtDic, out2)                
                    
def parse_arg():
    """Parse arguments.
    infp: input file path
    out1: "medianvals_by_zip.txt" output file path
    out2: "medianvals_by_date.txt" output file path
    """
    scrp, infp, out1, out2 = sys.argv
    return (infp, out1, out2)

def parse_line(line, delimiter='|', cmteIDidx=0, dateidx=13, 
               zipCodeidx=10, amtidx=14, otherIDidx=15):
    """Parse one line of input. Check each fields. 
    line: current line of input file
    delimiter: demiliter in FEC database file, default="|"
    cmteIDidx: CMTE_ID index in line as described by the FEC, default=0
    zipCodeidx: ZIP_CODE index in line as described by the FEC, default=10
    dateidx: TRANSACTION_DT in line as described by the FEC, default=13
    amtidx: TRANSACTION_AMT in line as described by the FEC, default=14
    otherIDidx: OTHER_ID in line as described by the FEC, default=15
    cmteId: the recipient of this contribution
    otherId: a field that denotes whether contribution came from a person or 
                an entity
    zipCode: first five digits/characters of zip code of the contributor
    date: date of the transaction
    amt: amount of the transaction
    """
    fields = line.split(delimiter)
    check_format(fields)
    cmteID, zipCode, date, amt, otherID = fields[cmteIDidx], fields[zipCodeidx], \
                                            fields[dateidx], fields[amtidx], \
                                            fields[otherIDidx]
    return (cmteID, zipCode, date, amt, otherID)
    
def check_format(fields, num=21):
    """Check the format of every input line. If the number of fields is 
    not 21, this input file is not a standard FEC file. 
    The index of each fields we assumed may be wrong.
    fields: all fields in current line of input file
    num: number of fields in standard FEC file, default is 21
    If number of fields is invalid, exit and send warning.
    """
    try:
        if len(fields) != num:
            raise ValueError('Wrong input format')
    except ValueError:
        sys.stderr.write('This is not a standard FEC database file. Please check!')
        exit


def check_line(cmteID, amt, otherID):
    """Check three fields to determine if to skip this line.
    1. if amount of the transaction or recipient of this contribution is 
    invalid, skip line.
    2. if contribution came from an entity or OTHER_ID is not empty, skip line.
    cmteID: the recipient of this contribution
    otherID: a field that denotes whether contribution came from a person or 
                an entity
    amt: amount of the transaction in current line
    Return false to skip line when at least one of cmteID, otherID and amt is
    invalid.
    """
    if not cmteID or not amt.isdigit() or otherID != '':
        return False
    return True
        

def check_line_zip(zipCode):
    """Check zip code field, if there is fewer than five digits, don't add 
    current line to zip code output or out1.
    zipCode: full zip code field value of the contributor
    Return false to skip adding current line to zip code output or out1 when 
    zip code is invalid.
    """
    if len(zipCode) < 5:
        return False
    return True
    
def check_line_dt(date):
    """Check date field(MMDDYYYY), if date is invalid (e.g., empty, malformed), 
    don't add current line to date output or out2.
    date: date of the transaction in current line
    Return false to skip adding current line to date output or out2 when date
    is invalid.
    """
    try:
        valid_date = datetime.strptime(date, '%m%d%Y')
        if not valid_date:
            raise ValueError('Wrong date format')
    except ValueError:
        return False
    return True
    
#########################################
## organize and process input data     ##
#########################################
def update_zipDic(cmteID, zipCode, amt, zipDic):
    """Add new donation amount to recipient from corresponding zip code in 
    previous zip code dictionary. If recipient and zip combination did not exist,
    create new item.
    cmteID: the recipient ID of this contribution
    zipCode: full zip code field value of the contributor
    amt: amount of the transaction in current line
    zipDic: previous zip code dictionary, a dictionary with recipient and 
    zip code as keys and a list contain contribution median, number and 
    total amount as value.
    """
    zipcode = zipCode[:5]
    amt = float(amt)
    if zipDic.get((cmteID, zipcode)):
        Median, num, total = zipDic[(cmteID, zipcode)]
        num +=1
        total += amt
        Median = round(total / num, 0)
        zipDic[(cmteID, zipcode)] = [Median, num, total]
    else:
        zipDic[(cmteID, zipcode)] = [amt, 1, amt]
    zipline = '%s|%s|%d|%d|%d\n' % (cmteID, zipcode, 
                                    zipDic[(cmteID, zipcode)][0], 
                                    zipDic[(cmteID, zipcode)][1], 
                                    zipDic[(cmteID, zipcode)][2])
    return zipline

def write_zipDic(zipline, out1):
    """When reading in a new line from input file, update zipDic and 
    write updated donations from current zip code area to current recipient  
    into output file, "medianvals_by_zip.txt".
    zipline: updating line, e.g. "recipient|zip code|median|number|total\n" 
    out1: "medianvals_by_zip.txt" output file path
    """ 
    f = open(out1, 'a')
    f.write(zipline)
    f.close()

def update_dtDic(cmteID, date, amt, dtDic):
    """Add new donation amount to exisitng recipient and date combination or 
    create new recipient and date combination to store current data.
    cmteID: the recipient ID of this contribution
    date: data field value (MMDDYYYY)
    amt: amount of the transaction in current line
    dtDic: previous date dictionary, a dictionary with recipient and date as keys
    and a list contain contribution median, number and total amount as value.
    """
    dt = datetime.strptime(date, '%m%d%Y')
    amt = float(amt)
    if dtDic.get((cmteID, dt)):
        Median, num, total = dtDic[(cmteID, dt)]
        num +=1
        total += amt
        Median = round(total / num, 0)
        dtDic[(cmteID, dt)] = [Median, num, total]
    else:
        dtDic[(cmteID, dt)] = [amt, 1, amt]

def write_dtDic(dtDic, out2):
    """When read in input file is finished, sort date Dic by recipient ID and
    date, and then write it into output file, "medianvals_by_date.txt".
    dtDic: complete date Dic, a dictionary with recipient and date as keys
    and a list contain contribution median, number and total amount as value.
    out2: "medianvals_by_date.txt" output file path
    """ 
    f = open(out2, 'w')
    for key in sorted(dtDic.iterkeys()):
        f.write('%s|%s|%d|%d|%d\n' % (key[0], 
                                       datetime.strftime(key[1],'%m%d%Y'), 
                                       dtDic[key][0], 
                                       dtDic[key][1], 
                                       dtDic[key][2]))
    f.close()
    
def check_fp(out_fp):
    """Check if output file path exist. If exist, send a warning and exit.
    out_fp: output file path to write on.
    """
    try:
        if isfile(out_fp):
            raise OSError('Output file exists')
    except OSError:
        sys.stderr.write('Output file \"%s\" already exists.' % (out_fp))
        exit
    
if __name__ == "__main__":
     locate_donor() 
     