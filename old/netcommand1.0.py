#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhujunhui'

import sys
import time

def dotelnet(host, usr, passwd, ensu, vendor='cisco'):
    import telnetlib
    devname = 'devname'
    datetime = str(time.strftime("%Y-%m-%d", time.localtime()))
    # Test only. For simulation login
    '''tn = telnetlib.Telnet('127.0.0.1', port=2001, timeout=10)
    tn.set_debuglevel(2)
    tn.write('\n')'''

    # Begin here!!!
    # lower string vendor
    vendor = vendor.lower()
    # Telnet connect to host
    tn = telnetlib.Telnet(host, timeout=10)
    tn.set_debuglevel(2)
    time.sleep(2)
    #tn.write('\r\n')
    #tn.write('telnet %s' % host + '\n')

    # Discriminate device need username. if need, enter username.
    # if not, directly enter password
    login = ['login:', 'Login:', 'Username:', 'Password:']
    receiveword = tn.expect(login, timeout=10)
    if receiveword[0] != 3:
        tn.write(usr + '\n')
        tn.read_until('Password:')
        tn.write(passwd + '\n')
    else:
        tn.write(passwd + '\n')
    time.sleep(5)

    # according to vendor elevation of privilege
    if vendor == 'huawei':
        # get device name
        tn.write('\r\n')
        devname = tn.read_until('>', timeout=5)
        devname = devname[devname.rfind('\n'):]
        devname = devname.strip()
        devname = devname.replace('<', '')
        devname = devname.replace('>', '')
        devname = devname.replace('#', '')
        # print devname

        # discriminate has manage privilege.
        # if not,enter super password.
        tn.write('super' + '\n')
        superpassword = ['Password:']
        receiveword = tn.expect(superpassword, timeout=5)
        if receiveword[0] == 0:
            tn.write(ensu + '\n')
        else:
            pass

        # command in telnet session
        command = []
        with open('huawei_command.txt', 'rt') as CommandFile:
            for line in CommandFile:
                command.append(line)
        # execute command
        for execommand in command:
            tn.write(execommand)
            time.sleep(1)
        time.sleep(2)
        tn.write('\n' + '***the_end***' + '\n')
        tn.write('quit' + '\n')

    elif vendor == 'cisco':
        # discriminate command line mode
        tn.write('\r\n')
        prompt = ['#', '>']
        receiveword1 = tn.expect(prompt, timeout=5)
        if receiveword1[0] != 0:
            tn.write('enable' + '\r\n')
            tn.read_until('Password:')
            tn.write(ensu + '\r\n')
        else:
            pass

        devname = tn.read_until('#', timeout=5)
        devname = devname[devname.rfind('\n'):]
        devname = devname.strip()
        devname = devname.replace('<', '')
        devname = devname.replace('>', '')
        devname = devname.replace('#', '')

        # command in telnet session
        command = []
        with open('cisco_command.txt', 'rt') as CommandFile:
            for line in CommandFile:
                command.append(line)
        # execute command
        for execommand in command:
            tn.write(execommand)
            time.sleep(1)
        time.sleep(2)
        tn.write('\n' + '***the_end***' + '\n')
        tn.write('exit' + '\r\n')

    else:
        print 'Sorry! Do not support this vendor device.'

    # write to file,filename ip and device name
    outmsg = tn.read_until('***the_end***', timeout=10)
    outfile = open('%s_%s_%s.txt' % (host, devname, datetime), 'wt')
    outfile.write(outmsg)
    outfile.close()

    # close telnet connect
    print devname + ' ' + host + " finish."
    tn.close()


def devicelist(devicefilename='deviceinfo.csv'):
    import csv
    from collections import namedtuple
    import threading

    threads = []

    # Open device list file, get device info.
    with open(devicefilename) as f:
        f_csv = csv.reader(f)
        headings = next(f_csv)
        Row = namedtuple('Row', headings)
        for r in f_csv:
            row = Row(*r)
            print 'Host:', row.host
            print 'Username:', row.usename
            print 'Password:', row.password
            print 'Enable or Super:', row.enable
            print 'Vendor:', row.vendor

            if row.password != '' and row.vendor != '':
                t = threading.Thread(target=dotelnet, args=(row.host, row.usename, \
                                                            row.password, row.enable, row.vendor,))
                threads.append(t)
            else:
                print 'Host in device info file ' \
                        'missing necessary parameters!!!'
                print 'Password and Vendor should not empty!!!'
                print 'Break Out!!!'
                break

        nloops = xrange(len(threads))
        for n in nloops:
            threads[n].start()
        for n in nloops:
            threads[n].join()


if __name__ == '__main__':
    devicelist()

