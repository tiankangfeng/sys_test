# -*- coding:utf-8 -*-
import sys
import os
import re
import time
import pymysql
from math import sin, asin, cos, radians, fabs, sqrt
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext        # 导入滚动文本框的模块



config_test = {
    'host': '',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.Cursor,
}


config_dev = {
    'host': '',
    'port': 3306,
    'user': 'blvhop',
    'password': '',
    'database': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.Cursor,
}

config = config_dev
#file_name = 'E:\手牵手测试\GPS经纬度采集apk\gpslog.txt'
open_type = 'r'


def open_file(file_name, open_type):
    file =open(file_name,open_type)
    context = file.readlines()
    file.close()
    return context

def data_list_to_dict(file_date):
    phone_GPS_list = []
    for i in file_date:
        re_data = re.findall(r"------", i)
        if re_data:
            pass
        else:
            position_time = i.split('>>>')
            phone_GPS_list.append(position_time)
    phone_GPS_dict = dict(phone_GPS_list)
    return phone_GPS_dict #, date_time_start_utc, date_time_end_utc


EARTH_RADIUS = 6371  # 地球平均半径，6371km

def hav(theta):
    s = sin(theta / 2)
    return s * s

def get_distance_hav(lat0, lng0, lat1, lng1):
    #"用haversine公式计算球面两点间的距离。"
    # 经纬度转换成弧度
    lat0 = radians(float(lat0))
    lat1 = radians(float(lat1))
    lng0 = radians(float(lng0))
    lng1 = radians(float(lng1))

    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))

    return distance

def sel_dev_GPS_his_num(did, date_time_start, date_time_end,phone_GPS_dict,time_number):
    time_numbers = time_number*60
    #print(time_numbers)
    if date_time_start[0:7] == date_time_end[0:7]:
        M = date_time_start[0:7].replace('-', '')
        data_tab = "position_history_" + M
        sql_selc_data = "SELECT lat_gps,lng_gps,FROM_UNIXTIME(utc_upload/1000,'%Y-%m-%d %H:%i:%s'), utc_upload FROM " + data_tab + " WHERE did = '" + did + "' AND '" + date_time_start + "'<FROM_UNIXTIME(utc_upload/1000,'%Y-%m-%d %H:%i:%s') AND '" + date_time_end + "'>FROM_UNIXTIME(utc_upload/1000,'%Y-%m-%d %H:%i:%s')"
    else:
        print('开始时间与结束时间相差较大')
    d_value_str = ''
    try:
        with connection.cursor() as cursor:
            count = cursor.execute(sql_selc_data)  # 影响的行数
            if count>0:
                result = cursor.fetchall()  # 取出所有行
                device_position_num = 1
                for i in result:  # 打印结果
                    upload_time = i[3]/1000
                    print("\n设备ID：\t" + did + "\t计算第" + str(device_position_num) + "个点的坐标偏移值")
                    d_value_str += "\n设备ID：\t" + did + "\t计算第" + str(device_position_num) + "个点的坐标偏移值\n"
                    d_value_str += "参考点时间" + " "*10 + "参考点坐标" + " "*13 + "设备坐标" + " "*29+"误差\n"
                    reference_posint_num = 1
                    value_dict = {}
                    for phone_GPS_key, phone_GPS_value in phone_GPS_dict.items():
                        int_key = int(phone_GPS_key) / 1000
                        if upload_time+time_numbers > int_key > upload_time-time_numbers:
                            phone_GPS_values = phone_GPS_value.replace('\n','')
                            reference_posint_latlng = phone_GPS_values.split(':')
                            real_lat,real_lng = reference_posint_latlng[0],reference_posint_latlng[1]
                            d_value = get_distance_hav(real_lat,real_lng,i[0],i[1])
                            value_dict[phone_GPS_key] = d_value*1000
                            reference_posint_num += 1
                    value_sort_list = sorted(value_dict.values())
                    for ss in value_sort_list[0:10]:
                        key11 = [k for k, v in value_dict.items() if v == ss]

                        phone_GPS_values = phone_GPS_dict[key11[0]].replace('\n', '').replace(':',',')
                        d_value2 = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(key11[0])/1000))+'\t'+phone_GPS_values.replace(':',',')+'\t'+str(i[0])+','+str(i[1])+'\t'+str(round(ss,3))+'\n'
                        print(d_value2)
                        d_value_str += d_value2
                    device_position_num += 1
                d_value_str += '\n'
                connection.commit()  # 提交事务
            else:
                d_value_str += '设备did：\t' + did + "\t起止时间:\t" + date_time_start + '\t' + date_time_end + '\n无数据\n\n'
                print(sql_selc_data)
                print('无数据')
    except Exception as e:
        print(e)
        connection.rollback()  # 若出错了，则回滚

    return d_value_str


def run(did_list,date_times,file_name,time_number):
    data_d_value_str = ''
    file_date = open_file(file_name, open_type)
    phone_GPS_dict = data_list_to_dict(file_date)
    for did_id in did_list:
        if did_id:
            re_data = re.findall(r",|\t|--|，", date_times)
            date_time = date_times.split(re_data[0])
            date_time_start, date_time_end = date_time[0], date_time[1]
            data_d_value = sel_dev_GPS_his_num(did_id, date_time_start, date_time_end,phone_GPS_dict,time_number)
            data_d_value_str += data_d_value
        else:
            pass

    return data_d_value_str


def minus(var1, var2,var3,var4):
    print("查询计算中.....")
    file_name = var1.replace('\n','')
    did_list = var2.split('\n')
    date_times = var3.replace('\n','')
    time_number = eval(var4)
    #print(time_number,type(time_number))
    Value = run(did_list, date_times, file_name,time_number)
    print("*" * 50, "完成", "*" * 50)
    return Value


window = tk.Tk()
window.title('手牵手室外静态定位点精度计算')
window.geometry('900x900')

Label5 = tk.Label(window, text="选择查询服务器")
Label5.pack()
server_str = tk.StringVar()
e5 = ttk.Combobox(window, width=12, textvariable=server_str, state='readonly')
e5['values'] = ('正式服务器', '测试服务器')
e5.pack()
e5.current(0)


Label1 = tk.Label(window, text="参考数据文件路径及名称 格式：\nE:\手牵手测试\GPS经纬度采集apk\gpslog.txt")
Label1.pack()
e1 = tk.Text(window, width=120, height=3)
e1.pack()

Label2 = tk.Label(window, text="设备did 格式：\n88010E200100005F\n88010E2001000067")
Label2.pack()
e2 = tk.Text(window, width=120, height=6)
e2.pack()

Label3 = tk.Label(window, text="时间段 格式：\n2020-04-15 10:00:00--2020-04-15 10:10:00")
Label3.pack()
e3 = tk.Text(window, width=120, height=2)
e3.pack()

Label4 = tk.Label(window, text="取值范围（输入一个取值范围--分钟）")
Label4.pack()
number = tk.StringVar()
e4 = ttk.Combobox(window, width=12, textvariable=number, state='readonly')
e4['values'] = (0.05, 0.1, 0.5, 1, 2, 3, 5, 10, 15, 20)
e4.pack()
e4.current(0)


def insert_point():
    global config, config_dev, config_test, connection
    t1.delete('1.0', 'end')
    var1 = e1.get("0.0", "end")
    var2 = e2.get("0.0", "end")
    var3 = e3.get("0.0", "end")
    var4 = e4.get()
    var5 = e5.get()
    print(var5)
    if var5 == '正式服务器':
        config = config_dev
    else:
        config = config_test
    #print(config)
    print("连接数据库中....")
    connection = pymysql.connect(**config)  # 连接数据库
    print("连接成功....")
    t1.insert('insert', minus(var1, var2, var3, var4))
    connection.close()
    print("关闭数据库连接")

b1 = tk.Button(window, text='计算', width=15, height=2, command=insert_point)
b1.pack()

Label13 = tk.Label(window, text="设备定位偏差 (米/公里)")
Label13.pack()

#t1 = tk.Text(window, width=120, height=30)
t1 = scrolledtext.ScrolledText(window, width=120, height=30)
t1.pack()

window.mainloop()
