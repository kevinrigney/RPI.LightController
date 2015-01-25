import socket
import struct

# Definitions

# list locations
l_num=0
l_pin=0
l_stat=1
l_name=2
l_links=3
link_node=0
link_num=1

# packet is network-endian, msg type, light number, on/off
packString = '!ii?'
queryPackString = packString+'30s'
# Packet info definitions
msg_info=0
msg_set=1
msg_dump=2
msg_done=3

# GPIO output values
off = True
on = False

msg_off=off
msg_on=on

# All sockets use this port
socketPort = 54448

# This is the list of lights that will show up on the web page.
# If it's not on this list it can be controlled locally or
# by linking
nodeList = [ 'b','a','c' ]

# Every node should be in this list
nameList = {
        'a':'192.168.42.101',
        'b':'192.168.42.100',
        'c':'192.168.42.102'
        }

# This list contains all of the lights, pin definitions, initial state, and links
lightList = { 
    'b':
        [ [3,off,'LR Door',[] ], [2,off,'LR All', [ ['b',0],['c',0],['c',1] ] ] , 
    'a':
        [ [3,off,'Bedroom',[] ] ],
    'c':
        [ [3,off,'LR Couch', [] ], [2,off,'LR TV', [] ] ] 
    }

def port():
    return socketPort

def getIpFromName(name):

    # TODO Add try/except key error

    return nameList[str(name)]

def getNameFromIp(ip):

    name = ''

    for item in nameList:
        if nameList[item] == ip:
            name = item
            break

    return name
        

def sendSetMsg(node,lNum,lStat):

    success = False

    try:
        node = getIpFromName(node)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((node, port()))
        s.sendall(struct.pack(packString,msg_set,lNum,lStat))
        s.close()
        success = True
    except socket.error:
        pass

    return success

def enumerateAll():

    nodes = []

    for node in nodeList:

        reqType = msg_dump
        lightNum = 0
        lightStatus = 0

        try:        
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((getIpFromName(node), port()))
            s.sendall(struct.pack(packString,reqType,lightNum,lightStatus))

            recvMsg = s.recv(struct.calcsize(queryPackString))
            reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)
            
            # Strip trailing '\x00' from socket packing
            trail_point = lightName.find('\x00')
            if trail_point >= 1:
                lightName = lightName[:trail_point]

            while reqType is not msg_done:
                nodes.append((node,[lightNum,lightStatus,lightName])) 

                recvMsg = s.recv(struct.calcsize(queryPackString))
                reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)
            
            s.close()

        except socket.error:
            #print "error connecting to " + str(node)
            pass

    return nodes
