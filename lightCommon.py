l_pin=0
l_stat=1

# packet is network-endian, msg type, light number, on/off
packString = '!ii?'
# Packet info definitions
msg_info=0
msg_set=1
msg_dump=2
msg_done=3

msg_off=False
msg_on=True

socketPort = 54448

nodeList = [ '192.168.42.100' ]

HTMLBreak = '<br>'

def printHTMLHeader():
    print "Content-Type: text/html"     # HTML is following
    print                               # blank line, end of headers

def port():
    return socketPort

def queryStringParser(qString):
    queryArg=[]
    if qString is not None:
        while qString.find('&') is not -1:
            queryArg.append(qString[0:qString.find('&')])
            qString = qString[qString.find('&')+1:]
        if qString is not '':
            queryArg.append(qString)
        #else:
        #    print 'Empty query'
    #else:
    #    print 'No query'
    return queryArg

