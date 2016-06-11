import hashlib as hl
import base64, binascii
import cPickle
from random import randint
from string import printable
from os import urandom

saltlength=32 # in bytes
num_iterations=100000

# Make sure it's outside of the repo where the server
# can't access it
cred_db_filename='python/credentials.db'

try:
    with open(cred_db_filename,'rb') as fh:
        credentials = cPickle.load(fh)
except:
    if __name__ == '__main__':
        # TODO - check if there is already a credential file. Maybe we can't open
        # if for a reason
        print('Creating an empty credential file')
        credentials = {}
        #with open(cred_db_filename,'wb') as fh:
        #    cPickle.dump(credentials,fh)
    else:
        print('No credential file found. Run as main to create one.')
        exit(-1)
    

DB_NUMITS = 0
DB_HASH = 1
DB_SALT = 2
DB_SALTLEN = 3


def generate_salted_password(password,num_its=None,salt_len=None,salt=None):
    # The salting functions
    # Make some salt
    if num_its == None:
        num_its = num_iterations
    if salt == None:
        if salt_len == None:
            salt_len = saltlength
        salt=urandom(salt_len)

    # and generate a reasonably secure password.
    # See here https://docs.python.org/2.7/library/hashlib.html#key-derivation
    # And here https://nakedsecurity.sophos.com/2013/11/20/serious-security-how-to-store-your-users-passwords-safely/
    dk = hl.pbkdf2_hmac('sha256', password, salt, num_its)
    return (binascii.hexlify(dk),salt)

def generate_db_tuple(password,num_its=None,salt_len=None):
    '''
    Given the appropriate information about a password for a user
    make a tuple to insert into the database
    '''
    # Can be none. If so use our latest-and-greatest number of iterations
    if num_its == None:
        num_its = num_iterations
    # Can be none. If so use our latest-and-greates length
    if salt_len == None:
        salt_len = saltlength

    hash,salt = generate_salted_password(password,num_its,salt_len)
    return (num_its,hash,salt,salt_len)

def test_db_tuple(password,hash,num_its,salt,salt_len):
    '''
    Given the information in a database tuple, check if a password
    matches the hash
    '''
    (test_hash,salt) = generate_salted_password(password,num_its,salt_len,salt)
    return hash == test_hash

def try_adduser(username,password):
    # Try to add a user. Fail if a user exists or
    # we don't like their username or password

    # Check that the username only contains printable characters
    for c in username:
        if c not in printable:
            return False
    # and make sure it's an appropriate length
    if (len(username) < 4) or (len(username) > 64):
        return False

    # And printable characters in the password
    for c in password:
        if c not in printable:
            return False

    # and password length
    if (len(password) < 6) or (len(password) > 64):
        return False  

    # Make sure a user doesn't already exist
    if username in credentials:
        return False

    # If we made it here it's because there isn't another user
    # So add this one and write out the DB
    # Notice we're only giving gen_db_tup the password.
    # This means by default it will use the most secure hashing settings
    credentials[username] = generate_db_tuple(password)
    try:
        with open(cred_db_filename,'wb') as fh:
            cPickle.dump(credentials,fh)
        return True
    except:
        return False

def try_rmuser(username,password):
    # Given a username and password try to 
    # remove a user from the database. You should only
    # let authenticated users do this or it will
    # be vulnerable to bruteforce
    if username in credentials:
        creds = credentials[username]
        if(test_db_tuple(password,creds[DB_HASH],creds[DB_NUMITS],creds[DB_SALT],creds[DB_SALTLEN])):
            # The password is a match. Delete it.
            del credentials[username]
            try:
                with open(cred_db_filename,'wb') as fh:
                    cPickle.dump(credentials,fh)
                return True
            except IOError:
                # There was an error opening the database
                return False
        # The password didn't match
        else:
            return False
    # The username could not be found
    else:
        return False


def try_authenticate(authorization,authtype='basic'):
    # Given an authroization string check if the user exists
    # in the database

    if authtype=='basic':
        user=None

        if authorization:
            authorization = authorization.split()
            if len(authorization) == 2:
                type = authorization[0]
                if authorization[0].lower() == "basic":
                    try:
                        authorization = base64.decodestring(authorization[1])
                    except binascii.Error:
                        pass
                    else:
                        authorization = authorization.split(':')
                        if len(authorization) == 2:
                            user = authorization[0]
        if user:
            # We've parsed the auth string. Test the password
            password=authorization[1]
            # If the user exists
            if user in credentials:
                creds = credentials[user]
                if(test_db_tuple(password,creds[DB_HASH],creds[DB_NUMITS],creds[DB_SALT],creds[DB_SALTLEN])):
                    # TODO if the num_its or the salt length aren't the most up-to-date
                    # then replace the old hash with a new one
                    # Maybe by calling try_rmuser then try_adduser
                    return True,user
            # We get here if the password is bad or the user doesn't exist
            return False, user
    # We get here if the auth string was bad
    return False,None

if __name__ == "__main__":
    # Add a user
    import getpass
    user = raw_input('Username: ')
    password = getpass.getpass('Password: ')
    if(password == getpass.getpass('Password again: ')):
        if(not try_rmuser(user,password)):
            if try_adduser(user,password):
                print("User " + user + " successfully added.")
            else:
                print("User " + user + " could not be added.")
        else:
            print("User " + user + " successfully removed.")
    else:
        print("Passwords do not match")
