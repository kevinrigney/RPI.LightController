#!/usr/bin/env python

import lightCommon as lc
import HTMLHelper as html

import socket, struct

# Enumerate all lights
lights=[]
badNode=[]
htmlOut = ''

# Get lights from every node
for node in lc.nodeList:

    reqType = lc.msg_dump
    lightNum = 0
    lightStatus = 0

    try:        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((node, lc.port()))
        s.sendall(struct.pack(lc.packString,reqType,lightNum,lightStatus))

        recvMsg = s.recv(struct.calcsize(lc.queryPackString))
        #print recvMsg
        reqType,lightNum,lightStatus,lightName = struct.unpack(lc.queryPackString,recvMsg)

        while reqType is not lc.msg_done:

            lights.append((node,lightNum,lightName))

            recvMsg = s.recv(struct.calcsize(lc.queryPackString))
            reqType,lightNum,lightStatus,lightName = struct.unpack(lc.queryPackString,recvMsg)
        
        s.close()

    except socket.error:
        badNode.append(node)

# Write HTML header

html.printl(html.textHeader())

# For each light make a checkbox to turn each on

lightOnCheckboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.on))
    text = str(light[2])
    lightOnCheckboxes.append((name,value,text))


html.printl(html.submitCheckboxBuilder(lightOnCheckboxes,'lights/onoff','statusframe','Turn On'))

# For each light make a checkbox to turn each off
lightOffCheckboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.off))
    text = str(light[2])
    lightOffCheckboxes.append((name,value,text))

html.printl(html.submitCheckboxBuilder(lightOffCheckboxes,'lights/onoff','statusframe','Turn Off'))


# Make all on
html.printl(html.singleButtonBuilder('Turn On All Lights','lights/allon','statusframe'))


# Make all off
html.printl(html.singleButtonBuilder('Turn Off All Lights','lights/alloff','statusframe'))

# Make status frame
html.printl(html.iframeBuilder('statusframe',100,300,'lights/status'))


# Write HTML footer
html.printl(html.textFooter())

