#!/usr/bin/env python

# Custom module
import lightCommon as lc

import RPi.GPIO as gpio

import sys,signal,os
import socket,struct

# Global
lights = []

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    s.close()

def turnOn():
    pass

def turnOff():
    pass

def serverLoop(s):
    # Never end... This is a server after all
    while s:
        # Accept a connection
        conn, addr = s.accept()
        print 'Connection accepted from: ', addr
        # Connections to the server immediately send a message
        recvMsg = conn.recv(struct.calcsize(lc.packString))
        try:
            # Unpack the message
            reqType, lightNum, lightStatus = struct.unpack(lc.packString,recvMsg)

            # For debugging
            print reqType, lightNum, lightStatus

            # Query that state of one light
            if ( reqType == lc.msg_info ):
                lightStatus = lights[str(lightNum)][lc.l_stat]
                lightName = lights[str(lightNum)][lc.l_name]
                sendMsg = struct.pack(lc.queryPackString,reqType,lightNum,lightStatus,lightName)
                conn.send(sendMsg)

            # Set the state of one light
            elif ( reqType == lc.msg_set ):
                gpio.output(lights[str(lightNum)][lc.l_pin],lightStatus)   
                lights[str(lightNum)][lc.l_stat] = lightStatus

            # Query all the lights available
            elif ( reqType == lc.msg_dump ):
                for light in lights:
                    lightStatus = lights[light][lc.l_stat]
                    lightName = lights[light][lc.l_name]
                    
                    sendMsg = struct.pack(lc.queryPackString,reqType,int(light),lightStatus,lightName)
                    conn.send(sendMsg)

        # If a light is requested that doesn't exist
        except KeyError:
            print "Error: Light number", lightNum, "does not exist."

        # If an error happens in packing / unpacking
        except struct.error as e:
            print "Error:",e

        # Only one message processed at a time. Dump the client
        conn.send(struct.pack(lc.queryPackString,lc.msg_done,0,0,''))
        conn.close()

if __name__ == '__main__':


    # Set the signal handler
    signal.signal(signal.SIGINT, handler)

    print('Process ID is: ' + str(os.getpid()))

    myIp = sys.argv[1]
    print('My IP is: ' + myIp)

    # Set up GPIO on the raspberry pi
    gpio.setmode(gpio.BCM)

    # A dictionary containing info about every light connected to the RPi
    # In the form of: 'lightNum':[pinNum,onOrOffBool,name]
    try:
        lights = lc.lightList[myIp]
    except IndexError:
        print('No IP address specified')
    except KeyError:
        print('No lights found for node ' + myIp)

    # Set up every light in the dictionary
    for light in lights:
        gpio.setup(lights[light][lc.l_pin],gpio.OUT,initial=lights[light][lc.l_stat])
        statMsg = 'LightNum: ' + str(light) + ' Pin: '
        statMsg = statMsg + str(lights[light][lc.l_pin]) + ' State: '
        statMsg = statMsg + str(lights[light][lc.l_stat]) + ' Name: '
        statMsg = statMsg + str(lights[light][lc.l_name])

        print(statMsg)

    print 'GPIO set up'

    try:
        # Socket listening on any interface, socket port set in lightCommon
        listenIp = '0.0.0.0'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((listenIp, lc.socketPort))
        s.listen(1)

        serverLoop(s)

    except socket.error as e:
        print 'Error:',e

    gpio.cleanup()
    s.close()

    print('Exiting server')
