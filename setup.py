#!/usr/bin/env python

'''
This program sets up PYTHONPATH using the system-wide .bashrc 

You must run with sudo
'''

import os

try:
    f = open('/etc/bash.bashrc','r')
except IOError as e:
    print str(e)
    print 'Error reading from file... Are you running as root?'
    exit()
    
# Find the files we want to insert
setup_file_path = os.path.abspath(__file__)

# Drop the filename and the slash
install_dir,junk,filename = setup_file_path.rpartition('/')

# now add our part
install_dir = install_dir+'/python'

# now make our whole command

newPP = 'export PYTHONPATH=' + install_dir + ':$PYTHONPATH\n\n'

newPP = '# Added by RPi.lightController setup\n' + newPP

print 'I''m going to try to put\n\n' + newPP + 'In your system-wide bashrc.'

dont_install = False

for line in f:
    if 'PYTHONPATH' in line:
        if install_dir in line:
            dont_install=True
            
if dont_install == False:
    f.close()
    try:
        f = open('/etc/bash.bashrc','a')
        f.write(newPP)
        print 'Python path modified'
    except IOError as e:
        print str(e)
        print 'Error writing to file... Are you running as root?'    
else:
    print 'Python path unchanged'


    
