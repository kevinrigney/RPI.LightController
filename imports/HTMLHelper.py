
HTMLBreak = '<br>'

cb_name=0
cb_value=1
cb_text=2

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

def submitCheckboxBuilder(boxes,action,target):
    outstr = ''
    outstr = outstr + '<form action="'
    outstr = outstr + str(action) + '" target="'
    outstr = outstr + str(target) + '">'

    for box in boxes:
        outstr = outstr + '<input type="checkbox" name="'
        outstr = outstr + str(box[cb_name]) +'" value="'
        outstr = outstr + str(box[cb_value]) + '">'
        outstr = outstr + str(box[cb_text])

    outstr = outstr + '</form>'

    return outstr

def singleButtonBuilder(value,action,target):

    outstr = ''
    outstr = outstr + '<form action="' + str(action) + '" '
    outstr = outstr + 'target="' + str(target) +'">'
    outstr = outstr + '<input type="submit" value="'
    outstr = outstr + str(value) + '"></form>'

    return outstr

def iframeBuilder(name,height,width,source):

    outstr = ''
    outstr = outstr + '<iframe ' 
    outstr = outstr + 'name="' + str(name) + '" '
    outstr = outstr + 'height=' + str(height) + ' '
    outstr = outstr + 'width=' + str(width) + ' '
    outstr = outstr + 'src="' + str(source) + '"'
    outstr = outstr + '></iframe>'

    return outstr

