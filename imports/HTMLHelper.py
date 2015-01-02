
HTMLBreak = '<br>'

def textHeader():

    header = ''
    header = header + 'Content-Type: text/html\n\n'
    header = header + '<!DOCTYPE html>'
    header = header + '<html>'
    header = header + '<body>'
    
    return header

def textFooter():

    footer = '</body>'
    footer = footer + '</html>'
    
    return footer

def printl(text):
    print(text+HTMLBreak+'\n')
    
def queryStringParser(qString):
    queryArg=[]
    if qString is not None:
        while qString.find('&') is not -1:
            queryArg.append(qString[0:qString.find('&')])
            qString = qString[qString.find('&')+1:]
        if qString is not '':
            queryArg.append(qString)
    return queryArg
