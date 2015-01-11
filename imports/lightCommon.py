import socket
import struct

# Definitions

l_pin=0
l_stat=1
l_name=2

# packet is network-endian, msg type, light number, on/off
packString = '!ii?'
queryPackString = packString+'30s'
# Packet info definitions
msg_info=0
msg_set=1
msg_dump=2
msg_done=3

off = True
on = False

msg_off=off
msg_on=on

socketPort = 54448

nodeList = [ '192.168.42.100','192.168.42.101','192.168.42.102' ]

nodeList2 = {
        'a':'192.168.42.101',
        'b':'192.168.42.100',
        'c':'192.168.42.102'
        }

lightList = { 
	'192.168.42.100':
                [ [3,off,'Living Room'], [2,off,'Living Room 2'] ] , 
	'192.168.42.101':
		[ [3,off,'Bedroom'] ],
	'192.168.42.102':
		[ [3,off,'Office'], [2,off,'Office 2'] ] 
	}

def port():
    return socketPort

def sendSetMsg(node,lNum,lStat):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node, port()))
    s.sendall(struct.pack(packString,msg_set,lNum,lStat))
    s.close()

    # TODO Add actual return code indicating status
    return True

def enumerateAll():

    nodes = []

    for node in nodeList:

        reqType = msg_dump
        lightNum = 0
        lightStatus = 0

        try:        
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((node, port()))
            s.sendall(struct.pack(packString,reqType,lightNum,lightStatus))

            recvMsg = s.recv(struct.calcsize(queryPackString))
            reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)

            while reqType is not msg_done:
                nodes.append((node,[lightNum,lightStatus,lightName])) 

                recvMsg = s.recv(struct.calcsize(queryPackString))
                reqType,lightNum,lightStatus,lightName = struct.unpack(queryPackString,recvMsg)
            
            s.close()

        except socket.error:
            html.printl('Error connecting to node ' + node)

    return nodes
