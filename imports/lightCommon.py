l_pin=0
l_stat=1

# packet is network-endian, msg type, light number, on/off
packString = '!ii?'
# Packet info definitions
msg_info=0
msg_set=1
msg_dump=2
msg_done=3

msg_off=False
msg_on=True

socketPort = 54448

nodeList = [ '192.168.42.100' ]

def port():
    return socketPort



