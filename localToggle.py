#!/usr/bin/env python

# Custom module
import lightCommon as lc

import RPi.GPIO as gpio

import sys,signal,os
from time import sleep

import socket,struct

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    endIt = True

# Set the signal handler
signal.signal(signal.SIGINT, handler)
endIt = False

# The node we are connecting to ( localhost )
node = '127.0.0.1'

# Set up GPIO on the raspberry pi
gpio.setmode(gpio.BCM)
switchPin = 26
gpio.setup(switchPin, gpio.IN, pull_up_down=gpio.PUD_UP)

print 'GPIO set up'

# Enumerate lights on the local device
localLights=[]

reqType = lc.msg_dump
lightNum = 0
lightStatus = 0

try:        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node, lc.port()))
    s.sendall(struct.pack(lc.packString,reqType,lightNum,lightStatus))

    recvMsg = s.recv(struct.calcsize(lc.queryPackString))
    reqType,lightNum,lightStatus,lightName = struct.unpack(lc.queryPackString,recvMsg)

    while reqType is not lc.msg_done:

        localLights.append(lightNum)

        recvMsg = s.recv(struct.calcsize(lc.queryPackString))
        reqType,lightNum,lightStatus,lightName = struct.unpack(lc.queryPackString,recvMsg)
            
    s.close()

except socket.error as e:
    print 'Error:',e

# Now that lights are enumerated wait for button to be pressed

# We'll use this to set all the lights when the button is pressed
onOrOff = lc.off

while endIt == False:

    # Wait for button press
    gpio.wait_for_edge(switchPin, gpio.BOTH)

    # Because our input is a pullup tied to ground
    # a high pin means the switch is open
    if gpio.input(switchPin) == gpio.HIGH:
        onOrOff = lc.off
    else:
        onOrOff = lc.on

    for light in localLights:
        try:

            reqType = lc.msg_set
            lightNum = light
            lightStatus = onOrOff

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((node, lc.port()))
            s.sendall(struct.pack(lc.packString,reqType,lightNum,lightStatus))
            s.close

        except socket.error as e:
            print 'Error:',e


gpio.cleanup()
s.close()

print('Exiting localToggle')
