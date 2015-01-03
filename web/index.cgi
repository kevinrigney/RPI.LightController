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

        recvMsg = s.recv(struct.calcsize(lc.packString))
        reqType,lightNum,lightStatus = struct.unpack(lc.packString,recvMsg)

        while reqType is not lc.msg_done:

            lights.append((node,lightNum))

            recvMsg = s.recv(struct.calcsize(lc.packString))
            reqType,lightNum,lightStatus = struct.unpack(lc.packString,recvMsg)
        
        s.close()

    except socket.error:
        badNode.append(node)

# Write HTML header

html.printl(html.textHeader())

# For each light make a checkbox to turn each on

lightOnCheckboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',1'
    text = str(light[0]) + ' Light ' + str(light[1])
    lightOnCheckboxes.append((name,value,text))


html.printl(html.submitCheckboxBuilder(lightOnCheckboxes,'onoff','statusframe','Turn On'))

# For each light make a checkbox to turn each off
lightOffCheckboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',0'
    text = str(light[0]) + ' Light ' + str(light[1])
    lightOffCheckboxes.append((name,value,text))

html.printl(html.submitCheckboxBuilder(lightOffCheckboxes,'onoff','statusframe','Turn Off'))


# Make all on
html.printl(html.singleButtonBuilder('Turn On All Lights','allon','statusframe'))


# Make all off
html.printl(html.singleButtonBuilder('Turn Off All Lights','alloff','statusframe'))

# Make status frame
html.printl(html.iframeBuilder('statusframe',100,300,'status'))


# Write HTML footer
html.printl(html.textFooter())

