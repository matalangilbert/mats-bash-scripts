#!/usr/bin/python

# TODO 
# Make regex more robust
# Only match complete hostname in hosts. If supplied hostname is a substring of
# a complete hostname, it currently matches.

import imaplib, email, re
import argparse
from tempfile import mkstemp
from os import remove, close, rename
from shutil import move, copystat

def parse_args():
    parser = argparse.ArgumentParser(description='A small script to login into\
            Gmail, and parse an IP address from the latest specifically labelled\
            message.')
    parser.add_argument('email_details_file',\
            help='file containing a single line "<email>,<password>"',\
            )
    parser.add_argument('email_label',\
            help='Gmail label to parse emails from',\
            )
    parser.add_argument('hostname',\
            help='Hostname to update in hosts file'
            )

    args = parser.parse_args()

    return args

def parse_details_file(filename):
    email_details = []
    try:
        with open(filename) as f:
            for line in f:
                for n in line.strip().split(','):
                    email_details.append(n)
    except FileNotFoundError:
        print('%s not found' % filename)
        exit(1)

    return (email_details[0], email_details[1])


def check_email(user, password, label):

    print("Checking email..")
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)

    try:
        (resp, capabilities) = conn.login(user, password)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)

    (resp, data) = conn.select(label) 

    if resp == 'NO':
        print('Label not found in mailbox')
        exit(1)

    (resp, items) = conn.search(None, 'ALL')

    if len(items[0].split()) == 0:
        print('No emails found for label')
        exit(1)

    if resp == 'OK':
        items = items[0].split()

        resp, data = conn.fetch(items[-1], '(RFC822)') # get the last email

        msg = str(email.message_from_bytes(data[0][1]))

        ipPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}') # regex for ip

        ip = re.findall(ipPattern, msg)[0]  # pull ip from msg (not perfect regex so
                                            # use first index of results)
        conn.close()   # close mailbox
        conn.logout()  # log out of email

        return ip


def rewrite_hosts(hostname, ip):
    fh, abspath = mkstemp()     # create temp file
    fo = open(abspath, 'w')     # open temp file for writing
    fi = open('/etc/hosts')     # open hosts file for reading

    # copy original hosts line for line, inserting new ip + hostname instead of 
    # the old one
    hostname_found = False
    for line in fi:
        if hostname in line:
            fo.write(''.join(ip) + '\t%s\n' % hostname)
            hostname_found = True
        else:
            fo.write(line)

    fi.close()
    close(fh)
    fo.close()

    if hostname_found != True:
        print('Hostname not found in /etc/hosts.')
        exit(1)

    print("Rewriting /etc/hosts. Old hosts at /etc/hosts.bak")
    copystat('/etc/hosts', abspath)         # copy old hosts permissions
    try:
        # keep a backup copy of the old hosts..
        rename('/etc/hosts', '/etc/hosts.bak')  
        move(abspath, '/etc/hosts')      # move the new file into place
    except PermissionError:
        print('Writing failed. You must be root to update /etc/hosts')

if __name__ == '__main__':
    args = parse_args()
    username, password = parse_details_file(args.email_details_file)
    ip = check_email(username, password, args.email_label)
    if ip is not None:
        rewrite_hosts(args.hostname, ip)

