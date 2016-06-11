import socket
import struct
import warnings
from multiprocessing import Process,Manager
try:
    import RPi.GPIO as gpio
except ImportError as e:
    warnings.warn('Are you running on a rasbperry pi?')
    class gpio:
        LOW = 0
        HIGH = 1
        pass
# Definitions

# list locations
l_num=0
l_pin=0
l_stat=1
l_name=2
l_links=3
link_node=0
link_num=1

# packet is network-endian, msg type, light number, on/off, time in future
packString = '!ii?i'
queryPackString = '!ii?'+'30s'
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
nodeList = [ 'b','a','c','d' ]

# Every node should be in this list - it's used to map
# node names to IP addresses and vice versa
nameList = {
        'a':'192.168.42.101',
        'b':'192.168.42.100',
        'c':'192.168.42.102',
        'd':'192.168.42.103',
        }

'''
Here's the all-encompasing nodeProps dictionary. This dictionary lets the raspberry pi know what's actually 
connected to itself, and lets all other pi's know what is connected to each other.

The initial dictionary entry is the serial number of the raspberry pi. Here's the details of the contents
of the rest of the dictionary:
    Node - The common name for the node - used in the CGI, switches['node_name'], and the lights list
    switches - a list of dictionaries that describe the switches connected to the raspberry pi
        switch_pin - the GPIO pin the switch is connected to
        switch_type - 'momentary' or 'toggle', the localSwitch program handles the cases differently
        switch_active - the GPIO state the switch the pin has to be in for localSwitch to activate
        node_name - the node that the switch controls
        node_light - the light on the node that the switch controls
    relays - A list of dictionaries that describe all connected relays (that control an actual outlet)
        relay_pin - the GPIO pin the relay is connected to
        relay_active - the GPIO status that turns the relay on
    lights - A list of lists that describe the lights that this node controls
        [0] - the "light number" (see switches['node_light'])
        [1] - the default state - on or off
        [2] - a list of lists describing any linked lights - must be [] at minimum
            [0] - the node name of the node that controls the linked light
            [1] - the light number on the node of the light you want to change
'''
nodeProps = {
    '00000000ee52a78b' : {'node':'b',
                        'switches':
                            [{'switch_pin':19,'switch_type':'momentary','switch_active':gpio.LOW,'node_name':'b','node_light':1},
                             {'switch_pin':26,'switch_type':'momentary','switch_active':gpio.LOW,'node_name':'b','node_light':0}],
                        'relays':
                            [{'relay_pin':3,'relay_active':gpio.LOW},{'relay_pin':2,'relay_active':gpio.LOW}],
                        'lights':
                            # For Christmas Only
                            [ [3,off,'LR Door',[] ], [2,off,'LR All', [ ['b',0],['c',1] ] ] ]
                            #[ [3,off,'LR Door',[] ], [2,off,'LR All', [ ['b',0],['c',0],['c',1] ] ] ]
                        },
    '0000000039ee3670' : {'node':'c',
                        'relays':
                            [{'relay_pin':3,'relay_active':gpio.LOW},{'relay_pin':2,'relay_active':gpio.LOW}],
                        'lights':
                            # For Christmas Only
                            [ [3,off,'Christmas Lights', [] ], [2,off,'LR Wall', [] ] ]
                            #[ [3,off,'LR Couch', [] ], [2,off,'LR TV', [] ] ]
                        },    
    '00000000f5d02a25' : {'node':'a',
                        'switches':
                            [{'switch_pin':26,'switch_type':'toggle','switch_active':gpio.HIGH,'node_name':'localhost','node_light':0}],
                        'relays':
                            [{'relay_pin':4,'relay_active':gpio.HIGH}],
                        'lights':
                            [ [4,off,'Bedroom',[] ] ]
                        },
    '00000000fc2516db' : {'node':'d',
                        'relays':
                            [{'relay_pin':3,'relay_active':gpio.LOW},{'relay_pin':2,'relay_active':gpio.LOW}],
                        'lights':
                            [ [3,off,'D-Bottom', [] ], [2,off,'D-Top', [] ] ]
                        },    

             }



'''
THE LIGHTLIST HAS BEEN SUPERCEDED BY nodeProps.
THE LIGHTLIST IS DEPRECATED

List of lists. the list contains each light. Each light is defined as:
[pin,initial_state,name,links]
where pin is actual raspberry pi pin
initial_state is on or off
name is what gets used in the webpage
and links are lights that are toggled when this light is toggles
The layout of links is [node_name,lightNum]
'''
lightList = { 
    'b':
        nodeProps['00000000ee52a78b']['lights'] ,
    'a':
        nodeProps['00000000f5d02a25']['lights'],
    'c':
        nodeProps['0000000039ee3670']['lights'], 
    'd':
        nodeProps['00000000fc2516db']['lights'],
    }

def getNodeProps():
    '''
    This function looks up the node properties based on the CPU serial number
    and the information contained in the switchList
    '''        
    try:
        with open('/proc/cpuinfo','r') as cpuInfoFile:
            for line in cpuInfoFile:
                if line.startswith('Serial'):
                    # The serial is the last item in the line
                    serial = line.rsplit(' ')[-1]
                    # Dump the line break
                    serial = serial.rstrip()
    except:
        print('Error retrieving serial number')
    
    if serial in nodeProps:
        return nodeProps[serial]
    else:
        print('Could not look up node properties. Serial is: ' + serial)
        return {}    


def port():
    return socketPort

def getIpFromName(name):
    '''
    Look up the IP address of a common name (nameList)
    or maybe of a dns entry
    '''
    ip = ''
    
    try:
        ip = nameList[str(name)]
    except KeyError as e:
        pass
    
    if ip == '':
        ip = socket.gethostbyname(name)   
            
    return ip

def getNameFromIp(ip):
    '''
    use the nameList to turn a name
    into an IP address to open a socket to
    '''

    name = ''

    for item in nameList:
        if nameList[item] == ip:
            name = item
            break

    return name
        

def sendSetMsg(node,lNum,lStat,tif=0):
    '''
    Send a message to a listening localServer
    to set a light to a specific state at some
    time in the future
    '''

    success = False

    try:
        node = getIpFromName(node)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((node, port()))
        s.sendall(struct.pack(packString,msg_set,lNum,lStat,tif))
        s.close()
        success = True
    except socket.error:
        pass

    return success

def getNodeStatus(node,outList):
    '''
    Given a node in the nodeList gather the status about it.
    Primarily so we can thread out enumerateAll (it can get slow if 
    a node can't be contacted)
    '''
    reqType = msg_dump
    lightNum = 0
    lightStatus = 0
    tif = 0

    try:        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((getIpFromName(node), port()))
        s.sendall(struct.pack(packString,reqType,lightNum,lightStatus,tif))

        recvMsg = s.recv(struct.calcsize(queryPackString))
        reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)
            
        # Strip trailing '\x00' from socket packing
        trail_point = lightName.find('\x00')
        if trail_point >= 1:
            lightName = lightName[:trail_point]

        while reqType is not msg_done:
            outList.append((node,[lightNum,lightStatus,lightName])) 

            recvMsg = s.recv(struct.calcsize(queryPackString))
            reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)
            
        s.close()

    except socket.error:
        #print "error connecting to " + str(node)
        pass

def enumerateAll():
    '''
    This function asks every node for its connected lights
    and their respective status.
    '''
    # We're implementing some threading here
    # Testing showed about a 0.5s speedup
    manager = Manager()
    nodes = manager.list()
    processes=[]

    for node in nodeList:
        p = Process(target=getNodeStatus, args=(node,nodes))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return nodes
