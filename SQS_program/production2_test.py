# -*- coding:utf-8 -*-
import sys
import os
import re
import time
import pymysql
from math import sin, asin, cos, radians, fabs, sqrt
import tkinter as tk

#import pymysql.cursors  # 好像import这个模块就可以了
#positionmode 1GPS 2wifi 3LBS 4phone 5室内转GPS -1无效定位


config = {
    'host': '',
    'port': ,
    'user': '',
    'password': '',
    'database': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.Cursor,
}
connection = pymysql.connect(**config)  # 连接数据库


EARTH_RADIUS = 6371  # 地球平均半径，6371km


def hav(theta):
    s = sin(theta / 2)
    return s * s


def get_distance_hav(lat0, lng0, lat1, lng1):
    #"用haversine公式计算球面两点间的距离。"
    # 经纬度转换成弧度
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)

    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))

    return distance



def sel_dev_GPS_his_num(did, date_time_start, date_time_end,real_lat,real_lng):
    sql_selc_data = "SELECT lat_gps,lng_gps FROM position_history_202004 WHERE did = '"+did+"' AND '"+date_time_start+"'<FROM_UNIXTIME(utc_create/1000,'%Y-%m-%d %H:%i:%s') AND '"+date_time_end+"'>FROM_UNIXTIME(utc_create/1000,'%Y-%m-%d %H:%i:%s')"
    #print(sql_selc_data)
    d_value_str = ''
    try:
        with connection.cursor() as cursor:
            GPS_num = 0
            WIFI_num = 0
            LBS_num = 0
            sql = sql_selc_data
            count = cursor.execute(sql_selc_data)  # 影响的行数
            if count>0:
                print('设备did：\t',did,"\t起止时间:\t",date_time_start,'\t',date_time_end)
                d_value_str += '设备did：\t'+did+"\t起止时间:\t"+date_time_start+'\t'+date_time_end+'\n'
                result = cursor.fetchall()  # 取出所有行
                for i in result:  # 打印结果
                    #print(type(i[5]))
                    #print(real_lat,real_lng, i[0],i[1])
                    d_value = get_distance_hav(real_lat,real_lng,i[0],i[1])
                    #print('原始坐标：',real_lat, real_lng,'\t设备定位坐标：',i[0],i[1],'\t两点的距离为：',d_value,'米')
                    d_value2 = ('原始坐标：\t' + str(real_lat) + '\t' + str(real_lng) + '\t设备定位坐标：\t' + str(i[0]) + '\t' + str(i[
                        1]) + '\t两点的距离为：\t' + str(d_value) + '\t米\n')
                    print(d_value2)
                    d_value_str += d_value2
                    #location_data.append([i[0],i[1]])
                connection.commit()  # 提交事务
            else:
                print(sql_selc_data)
                print('无数据')
    except:
        connection.rollback()  # 若出错了，则回滚

    #finally:
        #connection.close()
    return d_value_str




def run(did_list,date_time_list,real_location_list):
    data_d_value_str = ''
    for did_id in did_list:
        real_location_num = 0
        for date_times in date_time_list:
            date_time_start, date_time_end = date_times[0], date_times[1]
            real_lat, real_lng = real_location_list[real_location_num][0],real_location_list[real_location_num][1]
            #print(did_id, date_time_start, date_time_end)
            data_d_value = sel_dev_GPS_his_num(did_id, date_time_start, date_time_end,real_lat,real_lng)
            data_d_value_str += data_d_value

    print("*"*50)
    print(data_d_value_str)


did_list = ['88010E200100005F','88010E2001000067']
date_time_list = [['2020-04-15 00:00:00','2020-04-15 07:00:00'],['2020-04-15 07:00:00','2020-04-15 09:00:00'],['2020-04-15 09:00:00','2020-04-15 11:00:00']]
real_location_list = [[39.9805792,116.3029475],[39.9805792,116.3029475],[39.9805792,116.3029475]]

run(did_list,date_time_list,real_location_list)
connection.close()

