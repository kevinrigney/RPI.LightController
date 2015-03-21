import socket
import struct
import RPi.GPIO as gpio


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

# Globallly accepted values... ALWAYS use these to avoid confusion
off = False
on = True


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


# A list of device serial numbers with properties... This is slowly replacing everything else
nodeProps = {
    '00000000ee52a78b' : {'node':'b',
                        'switches':
                            [{'switch_pin':19,'switch_type':'momentary','switch_active':gpio.LOW,'node_name':'b','node_light':1},
                             {'switch_pin':26,'switch_type':'momentary','switch_active':gpio.LOW,'node_name':'b','node_light':0}],
                        'relays':
                            [{'relay_pin':3,'relay_active':gpio.LOW},{'relay_pin':2,'relay_active':gpio.LOW}],
                        'lights':
                            [ [3,off,'LR Door',[] ], [2,off,'LR All', [ ['b',0],['c',0],['c',1] ] ] ]
                        },
    '0000000039ee3670' : {'node':'c',
                        'relays':
                            [{'relay_pin':3,'relay_active':gpio.LOW},{'relay_pin':2,'relay_active':gpio.LOW}],
                        'lights':
                            [ [3,off,'LR Couch', [] ], [2,off,'LR TV', [] ] ]
                        },    
    '00000000f5d02a25' : {'node':'a',
                        'switches':
                            [{'switch_pin':26,'switch_type':'toggle','switch_active':gpio.HIGH,'node_name':'a','node_light':0}],
                        'relays':
                            [{'relay_pin':4,'relay_active':gpio.HIGH}],
                        'lights':
                            [ [4,off,'Bedroom',[] ] ]
                        },
             }

# This list contains all of the lights, pin definitions, initial state, and links

# List of lists. the list contains each light. Each light is defined as:
# [pin,initial_state,name,links]
# where pin is actual raspberry pi pin
# initial_state is on or off
# name is what gets used in the webpage
# and links are lights that are toggled when this light is toggles
# The layout of links is [node_name,lightNum]

lightList = { 
    'b':
        nodeProps['00000000ee52a78b']['lights'] ,
    'a':
        nodeProps['0000000039ee3670']['lights'],
    'c':
        nodeProps['00000000f5d02a25']['lights'] 
    }

def getNodeProps():
    '''
    This function looks up the node properties based on the CPU serial number
    and the information contained in the switchList
    '''        
    try:
        cpuInfoFile = open('/proc/cpuinfo','r')
        for line in cpuInfoFile:
            if line.startswith('Serial'):
                # The serial is the last item in the line
                serial = line.rsplit(' ')[-1]
                # Dump the line break
                serial = serial.rstrip()
        cpuInfoFile.close()
    except:
        print('Error retrieving serial number')
    
    if serial in nodeProps:
        return nodeProps[serial]
    else:
        return {}    


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
