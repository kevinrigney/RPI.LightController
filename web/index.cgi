#!/usr/bin/env python

import lightCommon as lc
import HTMLHelper as html

import socket, struct

# Enumerate all lights
lights=[]
badNode=[]

nodeList = lc.enumerateAll()
for node,props in nodeList:
    lights.append((node,props[lc.l_num],props[lc.l_name]))

# Write HTML header
print(html.textHeader())
# Write viewport
print(html.viewport)
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
print(html.textFooter())


