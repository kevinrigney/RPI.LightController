#!/usr/bin/env python
'''


'''
import lightCommon as lc
import HTMLHelper as html

import socket, struct

# Enumerate all lights
lights=[]

node_list = lc.enumerateAll()
for node,props in node_list:
    lights.append((node,props[lc.l_num],props[lc.l_name]))

# Write HTML header
print(html.textHeader())
# Write viewport
print(html.viewport)
# For each light make a checkbox

# light 'on' checkboxes to build
l_on_checkboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.on)) + ','
    text = str(light[2])
    l_on_checkboxes.append((name,value,text))

html.printl(html.submitTextboxBuilder(l_on_checkboxes,'lights/tonoff','statusframe','Turn On'))

# For each light make a checkbox to turn each off
l_off_checkboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.off)) + ','
    text = str(light[2])
    l_off_checkboxes.append((name,value,text))

html.printl(html.submitTextboxBuilder(l_off_checkboxes,'lights/tonoff','statusframe','Turn Off'))

# Make status frame
html.printl(html.iframeBuilder('statusframe',100,300,'lights/status'))

# Write HTML footer
print(html.textFooter())


