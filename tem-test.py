#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhujunhui'

import time
import csv
from collections import namedtuple
import threading

def dotelnet(host, usr, passwd, ensu, vendor='cisco'):
    print host, usr, passwd, ensu, vendor + '  threading'
    time.sleep(3)

def devicelist(devicefilename='deviceinfo.csv'):
    threads = []
    tcheck = []

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

            t = threading.Thread(target=dotelnet, args=(row.host, row.usename, \
                                                        row.password, row.enable, row.vendor,))
            threads.append(t)
            tc = [row.host,row.password,row.vendor]
            tcheck.append(tc)
    for i in tcheck:
        if i[1] == '' or i[2] == '':
            print "break out"
            return

    nloops = xrange(len(threads))
    for n in nloops:
        threads[n].start()
    for n in nloops:
        threads[n].join()



if __name__ == '__main__':
    devicelist()
