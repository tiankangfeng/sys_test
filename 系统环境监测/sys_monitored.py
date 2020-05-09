#!/usr/bin python
# -*- coding:utf-8 -*-

import sys
import os
import atexit
import time
import psutil
import re
from email.mime.text import MIMEText
import smtplib


#time.sleep(3)
send_email_stat = 0
line_num = 1
global t
mail_content = "注意检查服务器配置，已经超负荷运行"


# function of Get CPU State;
def getCPUstate(interval=1):
    global send_email_stat
    global mail_content
    cpu_state_param = psutil.cpu_percent(interval)
    cpu_state_str = (" CPU: " + str(cpu_state_param) + "%")
    if float(cpu_state_param)>85 and send_email_stat==0:
        mail_content = '注意检查运行的程序，CPU使用率已经高达%d%%' % cpu_state_param
        send_email()
        send_email_stat = 1
    else:
        pass
    return cpu_state_str, cpu_state_param


# function of Get Memory
def getMemorystate():
    global send_email_stat
    global mail_content
    phymem = psutil.virtual_memory()
    memory_used = phymem.used / 1024 / 1024
    memory_total = phymem.total / 1024 / 1024
    line = "Memory: %5s%% %6s/%s" % (
        phymem.percent,
        str(int(memory_used)) + "M",
        str(int(memory_total)) + "M"
    )
    if float(phymem.percent)>85 and send_email_stat==0:
        mail_content = '注意检查运行的程序，内存使用率已经高达%s%%' % phymem.percent
        send_email()
        send_email_stat = 1
    else:
        pass
    return line, memory_used, memory_total


def getdisk():
    global send_email_stat
    global mail_content
    disk_data = []
    if os.name == 'nt':
        partition = psutil.disk_partitions()
        for i in partition[:-1]:
            disk_usage = psutil.disk_usage(i[0])
            disk_usage_dict = {}
            disk_usage_dict['filessystem'],disk_usage_dict['total'],disk_usage_dict['used'],disk_usage_dict['free'],disk_usage_dict['percent']= i[0],disk_usage[0],disk_usage[1],disk_usage[2],disk_usage[3]
            #print(disk_usage_dict['percent'])
            if float(disk_usage_dict['percent'])>85 and send_email_stat==0:
                #print(type(disk_usage_dict['filessystem']),type(disk_usage_dict['percent']))
                mail_content = '注意检查运行的程序，硬盘%s使用率已经高达%d%%' %(str(disk_usage_dict['filessystem']), int(disk_usage_dict['percent']))
                send_email()
                send_email_stat = 1
            else:
                pass
            disk_data.append(disk_usage_dict)

    else:
        disk_usage = os.popen('df').readlines()
        for i in disk_usage[1:]:
            disk_usage_list = re.sub(' +|\n',' ',i).split(' ')
            #print(disk_usage_list)
            disk_usage_dict = {}
            disk_usage_dict['filessystem'], disk_usage_dict['total'], disk_usage_dict['used'], disk_usage_dict['free'], disk_usage_dict['percent'] = disk_usage_list[5], disk_usage_list[1], disk_usage_list[2], disk_usage_list[3],disk_usage_list[4]
            if float(disk_usage_dict['percent'].replace('%',''))>85 and send_email_stat==0:
                mail_content = '注意检查运行的程序，硬盘%s使用率已经高达%s' % (disk_usage_dict['filessystem'], disk_usage_dict['percent'])
                send_email()
                send_email_stat = 1
            disk_data.append(disk_usage_dict)
    #print(disk_data)
    disk_data_str = "\nDisk_stat:\n%-10s\t%-15s\t%-15s\t%-15s\t%s\n"%('filessystem','total','used','free','percent')
    for j in disk_data:
        #print(type(j['filessystem']))
        disk_data_str += "%-10s\t%-15s\t%-15s\t%-15s\t%s\n" % (j['filessystem'], j['total'], j['used'], j['free'], j['percent'])
    #print(disk_data_str)
    return disk_data_str, disk_data


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
    cpu_state_1 = cpu_state1
    cpu_state_1 = cpu_state1
    cpu_state_2 = cpu_state2
    memory_state_1 = memory_state1
    memory_state_2 = memory_state2
    memory_state_3 = memory_state3

    t = time.time()
    print(time.asctime() + " | " + cpu_state_1 + " | " + memory_state_1)

    # totals
    print(disk_stat1)
    print("\nNetStates:")

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

def send_email():
    global mail_content
    try:
        content = MIMEText(mail_content, 'plain','utf-8')  # 第一个参数：邮件的内容；第二个参数：邮件内容的格式，普通的文本，可以使用:plain,如果想使内容美观，可以使用:html；第三个参数：设置内容的编码，这里设置为:utf-8
        reveivers = "lm0721126@aliyun.com,kangfeng.tian@gmail.com,348287224@qq.com,87389162@qq.com,2310969783@qq.com"
        content['To'] = reveivers  # 设置邮件的接收者，多个接收者之间用逗号隔开
        content['From'] = str("315552758@qq.com")  # 邮件的发送者,最好写成str("这里填发送者")，不然可能会出现乱码
        content['Subject'] = "47正式服务器系统环境超负荷_tian"  # 邮件的主题

        smtp_server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 第一个参数：smtp服务地址（你发送邮件所使用的邮箱的smtp地址，在网上可以查到，比如qq邮箱为smtp.qq.com） 第二个参数：对应smtp服务地址的端口号
        smtp_server.login("315552758@qq.com", "qyzaxfippgeubjjb")  # 第一个参数：发送者的邮箱账号 第二个参数：对应邮箱账号的密码

        smtp_server.sendmail("315552758@qq.com", ["lm0721126@aliyun.com", "kangfeng.tian@gmail.com","348287224@qq.com","87389162@qq.com","2310969783@qq.com"], content.as_string())  # 第一个参数：发送者的邮箱账号；第二个参数是个列表类型，每个元素为一个接收者；第三个参数：邮件内容
        smtp_server.quit()  # 发送完成后加上这个函数调用，类似于open文件后要跟一个close文件一样
        print('发送成功')
    except Exception as e:
        print(e)

try:
    interval = 0
    while 1:
        timestart = time.time()
        args = poll(interval)
        refresh_window(*args)
        interval = 1
        timeend = time.time()
        if send_email_stat ==1 and timeend-timestart>86400:
            send_email_stat = 0
except (KeyboardInterrupt, SystemExit):
    pass
