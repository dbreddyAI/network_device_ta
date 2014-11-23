""" 
http://docs.python.org/2/library/difflib.html

Above is a link to the original script, which was transformed
into a Splunk search command.  

James Donn and Chhean Saur
jdonn@splunk.com
"""

import re
import csv
import sys
import splunk.Intersplunk
import string
import sys, os, time, difflib, optparse

### open logfile
#f = open('/tmp/workfile', 'a')
#f.write('\nStarting\n')
#f.write('argv length ' + str(len(sys.argv)) + '\n')
#for arg in sys.argv:
#    f.write('we have argv of %r.\n' % arg)
#f.write('argv 0 - \"' + sys.argv[0] + '\"\n')

### Set the html dir
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../appserver/static/html/sdiff.html')
output = open(filename, 'w+')

### Uncomment this and another isgetinfo statement below to debug ARGV
# (isgetinfo, sys.argv) = splunk.Intersplunk.isGetInfo(sys.argv)

### Declare optional args
u    = ''
xpo  = ''
n    = 3
c    = False
w    = None
last = ''

### Expect arguments in any order, ignoring anything that doesn't belong, but in this format: 
### <search> | sdiff pos1=n* pos2=n* u=t(rue) or 1 xpo=(line number to ignore) n=# c=True|False
### * Are the only required fields
if len(sys.argv) < 2:
    splunk.Intersplunk.parseError("Invalid argument '%s'" % arg)
for arg in sys.argv:
    if re.search('^pos1\s?=\s?', arg, re.IGNORECASE):
        position1 = arg
        if position1:
            pos1 = re.sub(r'^pos1\s?=\s?', "", position1)
            #f.write('position1 = "' + position1 + '\"\n')
            #f.write('pos1 = \"' + pos1 + '\"\n')
    if re.search('^pos2\s?=\s?', arg, re.IGNORECASE):
        position2 = arg
        if position2:
            pos2 = re.sub(r'^pos2\s?=\s?', "", position2)
            #f.write('position2 = "' + position2 + '\"\n')
            #f.write('pos2 = \"' + pos2 + '\"\n')
    if re.search('^u\s?=\s?(t[rue]?|1)', arg, re.IGNORECASE):
        position3 = arg
        if position3:
            u = re.sub(r'^u\s?=\s?', "", position3)
            #f.write('position3 = "' + position3 + '\"\n')
            #f.write('u = \"' + u + '\"\n')
    if re.search('^xpo=.*', arg, re.IGNORECASE):
        position5 = arg
        if position5:
            xpo = re.sub(r'^xpo=', "", position5)
            #f.write('position5 = "' + position5 + '\"\n')
            #f.write('xpo = \"' + xpo + '\"\n')
    if re.search('^n=', arg, re.IGNORECASE):
        position6 = arg
        if position6:
            n = re.sub(r'^n=', "", position6)
            n = int(n)
            #f.write('position6 = "' + position6 + '\"\n')
            #f.write('n = \"' + n + '\"\n')
    if re.search('^c=', arg, re.IGNORECASE):
        position7 = arg
        if position7:
            c = re.sub(r'^c=', "", position7)
            ### Boolean False is an empty string
            if c == "False":
                c = ''
            #f.write('position7 = "' + position7 + '\"\n')
            #f.write('c = \"' + c + '\"\n')
    if re.search('^w=', arg, re.IGNORECASE):
        position8 = arg
        if position8:
            w = re.sub(r'^w=', "", position8)
            if re.search(r'\d+', position8):
                w = int(w)
            #f.write('position8 = "' + position8 + '\"\n')
            #f.write('w = \"' + w + '\"\n')
    if re.search('^last=', arg, re.IGNORECASE):
        position9 = arg
        if position9:
            last = re.sub(r'^last=', "", position9)
            ### Boolean False is an empty string
            if last == "False":
                last = ''
            #f.write('position9 = "' + position9 + '\"\n')
            #f.write('l = \"' + l + '\"\n')
    # if re.search('^l=', arg, re.IGNORECASE):
    #     l = re.sub(r'^l=', "", arg)

    #f.write('arg = \"' + arg + '\"\n')
#f.write('n = \"' + str(n) + '\"\n')
#f.write('c = \"' + str(c) + '\"\n')

### Validate required fields
if len(pos1) == 0 or len(pos2) == 0:
    splunk.Intersplunk.parseError("Invalid or empty field '%s'" % field)

### If a field exists, make sure it is the proper type.



### Now that you have stated all of argv for testing above, outputInfo
### outputInfo automatically calls sys.exit()
#if isgetinfo:
#    splunk.Intersplunk.outputInfo(False, False, True, False, None, True)

try:
    #f.write('Getting results from Splunk\n')
    results = splunk.Intersplunk.readResults(None, None, True)

    #f.write('Success\n')
    #f.write('Size of resultset' + str(len(results)) + '\n')
    #for res in results:
    #    if res['_raw']:
    #        f.write('RAW = \"' + res['_raw']  + '\"\n')

    ### We only care about _raw, lets remove everything else
    raw = []
    for res in results:
        if res['_raw']:
            raw.append(res['_raw'])
            #f.write('We have %r \n' % res['_raw'])

    #for line in raw:
    #    f.write('RAW list is %r \n' % line)
        
    ### Prepare pos1 and pos2
    pos1=int(pos1)
    pos1 -= 1
    pos2=int(pos2)
    pos2 -= 1

    #f.write("The pos1 element is {0}.\n".format(raw[pos1]))
    #f.write("The pos2 element is {0}.\n".format(raw[pos2]))

    ### Extract the file names (command names) and time from the first line
    m1 = re.search(r'^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', raw[pos1])
    fromdate = m1.group(0)
    m2 = re.search(r'^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', raw[pos2])
    todate   = m2.group(0)
    m3 = re.search(r'command.*', raw[pos1])
    fromfile = m3.group(0)
    m4 = re.search(r'command.*', raw[pos2])
    tofile   = m4.group(0)

    #f.write('fromdate=' + fromdate + '\n')
    #f.write('todate=' + todate + '\n')
    #f.write('fromfile=' + fromfile + '\n')
    #f.write('tofile=' + tofile + '\n')

    ### Remove the first line of each command, since they have a timestamp in them
    fromlines = []
    tolines = []
    fromlines = raw[pos1].split('\n')
    tolines = raw[pos2].split('\n')
    del fromlines[0]
    del tolines[0]
    
    ### Remove the xpo line
    if xpo:
        xpo=int(xpo)
        xpo -=1
        del fromlines[int(xpo)]
        del tolines[int(xpo)]

        #f.write('we have XPO of %r.\n' % xpo)
        #for line in fromlines:
        #    f.write('fromlines list is %r \n' % line)
        #for line in tolines:
        #    f.write('tolines list is %r \n' % line)

    ### Pass doctored up pos1 and pos2 to the diff command and create the html
    diff = difflib.HtmlDiff(wrapcolumn=w).make_file(fromlines, tolines, fromfile, tofile, context=c, numlines=n)

    ### Change the auto refresh so we see updates right away! 
    diff = re.sub(r'<head>', '<head>\n<meta http-equiv=\"refresh\" content=\"4\"/> ', diff)

    #f.write('diff='+diff)
    #f.close()

    output.write(diff)
    output.close()

    if last:
        for res in results:
            if res['_raw']:
                res['_raw'] = re.sub(r'^.*\n','',res['_raw'])
        splunk.Intersplunk.outputResults(results)
    else:
        splunk.Intersplunk.outputResults(results)

    # splunk.Intersplunk.outputResults(results)

except Exception, e:
    splunk.Intersplunk.generateErrorResults("Unhandled exception:  %s" % (e,))
