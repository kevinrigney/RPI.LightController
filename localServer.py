#!/usr/bin/env python

# Custom module
import lightCommon as lc

# For communicating with GPIO on Raspberry Pi
import RPi.GPIO as gpio

import socket

import sys,signal,os,time
import struct

# Global
lights = []

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    s.close()
    
def findRelayActive(pin):
    # All we get here is a pin. This function is called by turnOn or turnOff
    
    # No error handling yet.
    relays = lc.getNodeProps()['relays']
    for relay in relays:
        if relay['relay_pin'] == pin:
            return relay['relay_active']
        
      

def turnOn(num):
    '''
    This function turns on a locally-connected light based
    on the light number. This SHOULD BE the only place where
    lc.on/off gets mapped to a T/F write to GPIO
    '''
    # First look up the relay_active property
    relay_on = findRelayActive(lights[num][lc.l_pin])
    
    try:
        gpio.output(lights[num][lc.l_pin],relay_on)   
        lights[num][lc.l_stat] = lc.on

    except KeyError as e:
        print 'KeyError in turnOn: ' + str(e)

def turnOff(num):
    '''
    This function turns off a locally-connected light based
    on the light number. This SHOULD BE the only place where
    lc.on/off gets mapped to a T/F write to GPIO
    '''
    # First look up the relay_active property
    relay_off = not findRelayActive(lights[num][lc.l_pin])
        
    try:
        gpio.output(lights[num][lc.l_pin],relay_off)   
        lights[num][lc.l_stat] = lc.off

    except KeyError as e:
        print 'KeyError in turnOff: ' + str(e)

def setLight(num, status):
    '''
    This either calls turnOn or turnOff based on the status requested
    It also sends messages to all linked lights
    '''
    if status == lc.on:
        turnOn(num)
    else:
        turnOff(num)

    for link in lights[num][lc.l_links]:
        lc.sendSetMsg(link[lc.link_node],link[lc.link_num],status)


def getStatus(num):
    '''
    Returns a light number's name and status (on, off)
    '''
    try:
        status = lights[num][lc.l_stat]
        name = lights[num][lc.l_name]
        return status, name
    except IndexError as e:
        print 'IndexError in getStatus: ' + str(e)

def serverLoop(s):
    # Never end... This is a server after all
    while s:
        # Accept a connection from any client
        conn, addr = s.accept()
        print str(time.time()) + ' Connection accepted from: ', addr
        # Clients to the server immediately send a message
        recv_msg = conn.recv(struct.calcsize(lc.packString))
        try:
            # Unpack the message
            req_type, light_num, light_status = struct.unpack(lc.packString,recv_msg)

            # For debugging
            print('req_type: %d light_num: %d light_status: %d' % (req_type, light_num, light_status) )

            # Query that state of one light
            if ( req_type == lc.msg_info ):
                print 'msg_info'
                light_status, light_name = getStatus(light_num)
                print light_num,light_status,light_name
                send_msg = struct.pack(lc.queryPackString,req_type,light_num,light_status,light_name)
                conn.send(send_msg)

            # Set the state of one light
            elif ( req_type == lc.msg_set ):
                print 'msg_set'
                print light_num, light_status
                setLight(light_num, light_status)
                
            # Query all the lights available
            elif ( req_type == lc.msg_dump ):
                print 'msg_dump'
                for light in lights:
                    light_num = lights.index(light)
                    light_status, light_name = getStatus(light_num)                    
                    print req_type,light_num, light_status, light_name
                    send_msg = struct.pack(lc.queryPackString,req_type,light_num,light_status,light_name)
                    conn.send(send_msg)

            else:
                print('Incorrect request type: %d' % (req_type) )

        # If a light is requested that doesn't exist
        except KeyError:
            print "Error: Light number", light_num, "does not exist."

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

    nodeInfo = lc.getNodeProps()
    try:
        nodeName = nodeInfo['node']
    except KeyError:
        print('This node not found')

    # Set up GPIO on the raspberry pi
    gpio.setmode(gpio.BCM)

    # A dictionary containing info about every light connected to the RPi
    # In the form of: 'lightNum':[pinNum,onOrOffBool,name]
    try:
        lights = lc.lightList[nodeName]
    except KeyError:
        print('No lights found for node ' + myIp)

    # Set up every light in the dictionary
    for light in lights:
        initial_state = findRelayActive(light[lc.l_pin])
        if light[lc.l_stat] == lc.off:
            initial_state = not initial_state    
            
        gpio.setup(light[lc.l_pin],gpio.OUT,initial=initial_state)
        stat_msg = 'LightNum: ' + str(light) + ' Pin: '
        stat_msg = stat_msg + str(light[lc.l_pin]) + ' State: '
        stat_msg = stat_msg + str(light[lc.l_stat]) + ' Name: '
        stat_msg = stat_msg + str(light[lc.l_name])

        print(stat_msg)

    print 'GPIO set up'

    try:
        # Socket listening on any interface, socket port set in lightCommon
        listen_ip = '0.0.0.0'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((listen_ip, lc.socketPort))
        s.listen(5)

        serverLoop(s)

    except socket.error as e:
        print 'Socket error: ',e

    gpio.cleanup()
    s.close()

    print('Exiting server')
