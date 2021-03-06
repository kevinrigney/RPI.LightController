#!/usr/bin/env python

# Custom module
import lightCommon as lc

# Raspberry Pi GPIO
import RPi.GPIO as gpio


import sys,os, socket, struct
from time import sleep

    
class momentaryHandler():    
    def callback(self,pin):

        print('Callback called for pin '+str(pin))
        
        # This next piece of logic could be better written as a do...while
        # Oh well. There isn't much of a performance hit because of it. 
        # This is a simple application after all
    
        # Debounce JUST a little more
        if self.debounce:
            sleep(0.2)
    
        # This is another "debounce" of sorts. Because we are using the raspberry pi
        # as a VERY SMALL current source it may fluctuate at times. This makes sure 
        # that if there is a dip in the supply but the switch hasn't changed that the 
        # light doesn't toggle
        
        #self.status = gpio.input(self.switch_pin)

        if self.read() == gpio.LOW:

            try:
                self.status = not self.status
                print('Actually triggering pin '+ str(self.light) + ' status ' + str(self.status))
                light_num = self.light
                light_status = self.status
                req_type = lc.msg_set
            
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.node, lc.port()))
                s.sendall(struct.pack(lc.packString,req_type,light_num,light_status,0))
                s.close()

            except socket.error as e:
                print 'Socket error: ',e

    
    def read(self):        
        return gpio.input(self.switch_pin)
    
    def __init__(self,switch_pin,switch_type,node,light_num,debounce=False):
        self.switch_pin = switch_pin
        self.switch_type = switch_type  
        self.status = not self.read()
        self.node = lc.getIpFromName(node)
        self.light = light_num
        self.first_run = True
        self.debounce = debounce
        self.callback(self.switch_pin)
        
        
class toggleHandler():    
    def callback(self,pin):

        print('Callback called for pin '+str(pin))
        
        # Because this is a toggle just take the value of the switch and
        # apply it to the light
        # Debounce JUST a little more
        if self.debounce:
            sleep(0.2)

        if self.read() == True:
            self.status = lc.on
        else:        
            self.status = lc.off

        try:            
            print('Actually triggering pin '+ str(self.light) + ' status ' + str(self.status))
            light_num = self.light
            light_status = self.status
            req_type = lc.msg_set
        
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.node, lc.port()))
            s.sendall(struct.pack(lc.packString,req_type,light_num,light_status,0))
            s.close()

        except socket.error as e:
            print 'Socket error: ',e           

    
    def read(self):
        if gpio.input(self.switch_pin) == self.switch_active:        
            return True
        else:
            return False
    
    def __init__(self,switch_dict,debounce=False):
        self.switch_pin = switch_dict['switch_pin']
        self.switch_type = switch_dict['switch_type']
        self.switch_active = switch_dict['switch_active']
        self.status = self.read()
        self.node = lc.getIpFromName(switch_dict['node_name'])
        self.light = switch_dict['node_light']
        self.debounce=debounce
        # Now that the class is set up act on the status of the switch
        self.callback(self.switch_pin)        


# First figure out what node this is so we can make sure this program actually
# has to run. We'll check for switches
node_props = lc.getNodeProps()
if 'switches' in node_props:
    switches = node_props['switches']
else:
    print('No switches attached to this node')
    exit()
    
# The node we are connecting to ( localhost? )
node = lc.getIpFromName(node_props['node'])

# Set up GPIO on the raspberry pi
gpio.setmode(gpio.BCM)

# Now for every switch set up the GPIO
for switch in switches:    
    gpio.setup(switch['switch_pin'], gpio.IN, pull_up_down=gpio.PUD_UP)
    
    if switch['switch_type'] == 'momentary':
        new_handler = momentaryHandler(switch['switch_pin'],switch['switch_type'],switch['node_name'],switch['node_light'])
        gpio.add_event_detect(switch['switch_pin'], gpio.FALLING, callback=new_handler.callback, bouncetime=500)
    
    elif switch['switch_type'] == 'toggle':
        new_handler = toggleHandler(switch)
        gpio.add_event_detect(switch['switch_pin'], gpio.BOTH, callback=new_handler.callback, bouncetime=500)
        
print 'GPIO set up'

try:
    input() # blocks forever
except KeyboardInterrupt:
    print('Exiting..')
    


'''
# Enumerate lights on the local device
local_lights=[]

req_type = lc.msg_dump
light_num = 0
light_status = 0

try:        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node, lc.port()))
    s.sendall(struct.pack(lc.packString,req_type,light_num,light_status))

    recv_msg = s.recv(struct.calcsize(lc.queryPackString))
    req_type,light_num,light_status,light_name = struct.unpack(lc.queryPackString,recv_msg)

    while req_type is not lc.msg_done:

        local_lights.append(light_num)

        recv_msg = s.recv(struct.calcsize(lc.queryPackString))
        req_type,light_num,light_status,light_name = struct.unpack(lc.queryPackString,recv_msg)
            
    s.close()

except socket.error as e:
    print 'Error:',e

# Now that lights are enumerated wait for button to be pressed

# Set up for main loop
on_or_off = lc.off
first_run = True
switch_pin=26

gpio.setup(switch_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

if True:

    while end_it == False:
    
        # This next piece of logic could be better written as a do...while
        # Oh well. There isn't much of a performance hit because of it. 
        # This is a simple application after all
    
        # Wait for button press
        if first_run == False:
            gpio.wait_for_edge(switch_pin, gpio.BOTH)
            # Debounce
            sleep(0.2)
        else:
            first_run = False
            # set to "not" to force the next piece of logic
            switch_status = not gpio.input(switch_pin)
    
    
        # This is another "debounce" of sorts. Because we are using the raspberry pi
        # as a VERY SMALL current source it may fluctuate at times. This makes sure 
        # that if there is a dip in the supply but the switch hasn't changed that the 
        # light doesn't toggle
    
        # Not equal means it really changed.
        if gpio.input(switch_pin) != switch_status:
    
            # lc.switch_off is defined in light common. 
            if gpio.input(switch_pin) == lc.switch_off:
                on_or_off = lc.off
            else:
                on_or_off = lc.on
    
            switch_status = gpio.input(switch_pin)
    
            for light in local_lights:
                try:
    
                    req_type = lc.msg_set
                    light_num = light
                    light_status = on_or_off
    
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((node, lc.port()))
                    s.sendall(struct.pack(lc.packString,req_type,light_num,light_status))
                    s.close()
    
                except socket.error as e:
                    print 'Error:',e
                    
else:
    pass

'''
    
gpio.cleanup()

print('Exiting localToggle')
