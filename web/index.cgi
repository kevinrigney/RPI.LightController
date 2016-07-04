#!/usr/bin/env python
'''

This python program is designed to be called from a web-server's CGI module.
It generates simple HTML to allow web-based control of the light nodes connected
to the network (and listed in lightCommon)

It first checks every light node and gets the available lights from it. It then
builds checkboxes for the user to turn on or off specific lights. It also adds
a 'turn all on' and 'turn all off' button. Finally, it makes a small frame to 
put updates into (so you can see the results of your request)

'''
import lightCommon as lc
import HTMLHelper as html

import socket, struct

# Enumerate all lights
lights=[]
bad_node=[]

node_list = lc.enumerateAll()
for node,props in node_list:
    lights.append((node,props[lc.l_num],props[lc.l_name]))

# Sort the lights by name
# See http://stackoverflow.com/a/10695161
lights = sorted(lights, key=lambda x: x[2])

# Write HTML header
print(html.textHeader())
# Write viewport
print(html.viewport)
# For each light make a checkbox to turn each on

# light 'on' checkboxes to build
l_on_checkboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.on))
    text = str(light[2])
    l_on_checkboxes.append((name,value,text))


html.printl(html.submitCheckboxBuilder(l_on_checkboxes,'cgi/onoff','statusframe','Turn On'))

# For each light make a checkbox to turn each off
l_off_checkboxes = []

for light in lights:
    name = light[0]
    value = str(light[1]) + ',' + str(int(lc.off))
    text = str(light[2])
    l_off_checkboxes.append((name,value,text))

html.printl(html.submitCheckboxBuilder(l_off_checkboxes,'cgi/onoff','statusframe','Turn Off'))

# Make all on
html.printl(html.singleButtonBuilder('Turn On All Lights','cgi/allon','statusframe'))

# Make all off
html.printl(html.singleButtonBuilder('Turn Off All Lights','cgi/alloff','statusframe'))

# Make status frame
html.printl(html.iframeBuilder('statusframe',100,300,'cgi/status'))

# Timed
html.printl(html.singleButtonBuilder('Set Timer','./timed.cgi'))

# Write HTML footer
print(html.textFooter())


