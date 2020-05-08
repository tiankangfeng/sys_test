#!/usr/bin python
# -*- coding:utf-8 -*-

import sys
import os
import atexit
import time
import psutil
# import MySQLdb as mysql
#
# db = mysql.connect(user="root", passwd="root", db="sys_state", host="localhost")
# # db.autocommit(True)
# cur = db.cursor()

# print "Welcome,current system is",os.name," 3 seconds late start to get data..."
time.sleep(3)

line_num = 1
global t


# function of Get CPU State;
def getCPUstate(interval=1):
    cpu_state_param = psutil.cpu_percent(interval)
    cpu_state_str = (" CPU: " + str(cpu_state_param) + "%")
    return cpu_state_str, cpu_state_param


# function of Get Memory
def getMemorystate():
    phymem = psutil.virtual_memory()
    memory_used = phymem.used / 1024 / 1024
    memory_total = phymem.total / 1024 / 1024
    line = "Memory: %5s%% %6s/%s" % (
        phymem.percent,
        str(int(memory_used)) + "M",
        str(int(memory_total)) + "M"
    )
    return line, memory_used, memory_total


def getdisk():
    disk_data = []
    if os.name == 'nt':
        partition = psutil.disk_partitions()
        for i in partition[:-1]:
            disk_usage = psutil.disk_usage(i[0])
            disk_usage_dict = {}
            disk_usage_dict['filessystem'],disk_usage_dict['total'],disk_usage_dict['used'],disk_usage_dict['free'],disk_usage_dict['percent']= i[0],disk_usage[0],disk_usage[1],disk_usage[2],disk_usage[3]
            disk_data.append(disk_usage_dict)

    else:
        disk_usage = os.popen('df').readlines()
        for i in disk_usage[1:]:
            disk_usage_dict = {}
            disk_usage_dict['filessystem'], disk_usage_dict['total'], disk_usage_dict['used'], disk_usage_dict['free'], disk_usage_dict['percent'] = i[5], i[1], i[2], i[3],i[4]
            disk_data.append(disk_usage_dict)
    #print(disk_data)
    disk_data_str = "Disk_stat:\n%-10s\t%-15s\t%-15s\t%-15s\t%s\n"%('filessystem','total','used','free','percent')
    for j in disk_data:
        #print(type(j['filessystem']))
        disk_data_str += "%-10s\t%-15d\t%-15d\t%-15d\t%.2f\n" % (j['filessystem'], j['total'], j['used'], j['free'], j['percent'])
    #print(disk_data_str)
    return disk_data_str,disk_data


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K'
    >>> bytes2human(100001221)
    '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


def poll(interval):
    """Retrieve raw stats within an interval window."""
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    # get cpu state
    cpu_state1, cpu_state2 = getCPUstate(interval)
    # get memory
    memory_state1, memory_state2, memory_state3 = getMemorystate()

    return (
    tot_before, tot_after, pnic_before, pnic_after, cpu_state1, cpu_state2, memory_state1, memory_state2, memory_state3)


def refresh_window(tot_before, tot_after, pnic_before, pnic_after, cpu_state1, cpu_state2, memory_state1, memory_state2,
                   memory_state3):
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")
    """Print stats on screen."""
    disk_stat1, disk_stat2 = getdisk()
    # print current time #cpu state #memory
    cpu_state_1 = cpu_state1
    cpu_state_2 = cpu_state2
    memory_state_1 = memory_state1
    memory_state_2 = memory_state2
    memory_state_3 = memory_state3

    t = time.time()
    print(time.asctime() + " | " + cpu_state_1 + " | " + memory_state_1)

    # totals
    print(disk_stat1)
    print("NetStates:")

    net_totalbytes_sent = bytes2human(tot_after.bytes_sent)
    net_totalbytes_received = bytes2human(tot_after.bytes_recv)
    net_totalpackets_sent = tot_after.packets_sent
    net_totalpackets_received = tot_after.packets_recv

    print("total bytes:                     sent: %-10s     received: %s" % (
    net_totalbytes_sent, net_totalbytes_received))
    print("total packets:                 sent: %-10s     received: %s" % (
    net_totalpackets_sent, net_totalpackets_received))

    #        print (type(cpu_state_1),type(memory_state_1),type(net_totalpackets_sent),type(net_totalbytes_received),type(net_totalpackets_sent),type(net_totalpackets_received),type(t))

    # param1 = (
    # cpu_state_2, memory_state_2, memory_state_3, net_totalbytes_sent, net_totalbytes_received, net_totalpackets_sent,
    # net_totalpackets_received, t)
    # sql1 = "insert into `sys_state`(`cpu_state`,`memory_state_used`,`memory_state_total`,`net_total_bytes_sent`,`net_total_bytes_recv`,`net_total_packets_sent`,`net_total_packets_recv`,`collect_time`) value (%s,%s,%s,%s,%s,%s,%s,%s)"
    # cur.execute(sql1, param1)
    # db.commit()
    # db.rollback()

    # per-network interface details: let's sort network interfaces so
    # that the ones which generated more traffic are shown first
    print("")
    nic_names = pnic_after.keys()
    # nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
    '''
    for name in nic_names:
        stats_before = pnic_before[name]
        stats_after = pnic_after[name]

        net_name = name
        total_netstats_bytes_sent = stats_after.bytes_sent
        per_sec_netstats_bytes_sent = stats_after.bytes_sent - stats_before.bytes_sent
        total_netstats_bytes_recv = stats_after.bytes_recv
        per_sec_netstats_bytes_recv = stats_after.bytes_recv - stats_before.bytes_recv
        total_netstats_pkts_sent = stats_after.packets_sent
        per_sec_netstats_pkts_sent = stats_after.packets_sent - stats_before.packets_sent
        total_netstats_pkts_recv = stats_after.packets_recv
        per_sec_netstats_pkts_recv = stats_after.packets_recv - stats_before.packets_recv

        # param2 = (net_name, total_netstats_bytes_sent, per_sec_netstats_bytes_sent, total_netstats_bytes_recv,
        #           per_sec_netstats_bytes_recv, total_netstats_pkts_sent, per_sec_netstats_pkts_sent,
        #           total_netstats_pkts_recv, per_sec_netstats_pkts_recv, t)
        # sql2 = "insert into `net_state`(`net_name`,`total_netstate_bytes_sent`,`per_sec_netstate_bytes_sent`,`total_netstate_bytes_recv`,`per_sec_netstate_bytes_recv`,`total_netstate_packets_sent`,`per_sec_netstate_packets_sent`,`total_netstate_packets_recv`,`per_sec_netstate_packets_recv`,`collect_time`) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # cur.execute(sql2, param2)
        # db.commit()
        # db.rollback()

        templ = "%-15s %15s %15s"
        print(templ % (net_name, "TOTAL", "PER-SEC"))
        print(templ % (
        "bytes-sent", bytes2human(total_netstats_bytes_sent), bytes2human(per_sec_netstats_bytes_sent) + '/s',))
        print(templ % (
        "bytes-recv", bytes2human(total_netstats_bytes_recv), bytes2human(per_sec_netstats_bytes_recv) + '/s',))
        print(templ % ("pkts-sent", total_netstats_pkts_sent, per_sec_netstats_pkts_sent,))
        print(templ % ("pkts-recv", total_netstats_pkts_recv, per_sec_netstats_pkts_recv,))
        print("")
    '''


try:
    interval = 0
    while 1:
        args = poll(interval)
        refresh_window(*args)
        interval = 1
except (KeyboardInterrupt, SystemExit):
    pass