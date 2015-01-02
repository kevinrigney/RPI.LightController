#!/usr/bin/env python

# Custom module
from lightCommon import *

import socket
import RPi.GPIO as gpio
from time import sleep
import struct

# Set up GPIO on the raspberry pi
gpio.setmode(gpio.BCM)


# A dictionary containing info about every light connected to the RPi
# In the form of: 'lightNum':[pinNum,onOrOffBool]
lights = {'1':[26,0]}

# Set up every light in the dictionary
for light in lights:
    gpio.setup(lights[light][l_pin],gpio.OUT,initial=lights[light][l_stat])

print 'GPIO set up'

try:
    # Socket listening on any interface, socket port set in lightCommon
    listenIp = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listenIp, socketPort))
    s.listen(1)

    # Never end... This is a daemon after all
    while 1:
        # Accept a connection
        conn, addr = s.accept()    
        print 'Connection accepted from: ', addr
        # Connections to the server immediately send a message
        recvMsg = conn.recv(struct.calcsize(packString))
        try:
            # Unpack the message
            reqType, lightNum, lightStatus = struct.unpack(packString,recvMsg)

            # For debugging
            print reqType, lightNum, lightStatus

            # Query that state of one light
            if ( reqType == msg_info ):
                lightStatus = lights[str(lightNum)][l_stat]
                sendMsg = struct.pack(packString,reqType,lightNum,lightStatus)
                conn.send(sendMsg)
            # Set the state of one light
            elif ( reqType == msg_set ):
                gpio.output(lights[str(lightNum)][l_pin],lightStatus)   
                lights[str(lightNum)][l_stat] = lightStatus
            # Query all the lights available
            elif ( reqType == msg_dump ):
                for light in lights:
                    lightStatus = lights[light][l_stat]
                    sendMsg = struct.pack(packString,reqType,int(light),lightStatus)
                    conn.send(sendMsg)

        # If a light is requested that doesn't exist
        except KeyError:
            print "Error: Light number", lightNum, "does not exist."

        # If an error happens in packing / unpacking
        except struct.error as e:
            print "Error:",e

        # Only one message processed at a time. Dump the client
        conn.send(struct.pack(packString,msg_done,0,0))
        conn.close()

except socket.error as e:
    print 'Error:',e

gpio.cleanup()
