# -*- coding:utf-8 -*-
import sys
import os
import re
import time
import pymysql
from math import sin, asin, cos, radians, fabs, sqrt
import tkinter as tk

class hav:
    # def __init__(self, theta):
    #     self.theta = theta
    def hav(theta):
        s = sin(theta / 2)
        return s * s


class Latlng_test:
    def __init__(self,lat0, lng0, lat1, lng1):
        self.lat0 = lat0
        self.lng0 = lng0
        self.lat1 = lat1
        self.lng1 = lng1

    def get_distance_hav(self):
        EARTH_RADIUS = 6371  # 地球平均半径，6371km
        lat0 = radians(self.lat0)
        lat1 = radians(self.lat1)
        lng0 = radians(self.lng0)
        lng1 = radians(self.lng1)

        dlng = fabs(lng0 - lng1)
        dlat = fabs(lat0 - lat1)
        h = hav.hav(dlat) + cos(lat0) * cos(lat1) * hav.hav(dlng)
        distance = 2 * EARTH_RADIUS * asin(sqrt(h))

        return distance

time1 = time.time()
aaa = Latlng_test(39.9792305,116.2999529,39.9792534167321,116.29986841612538)
print(aaa.get_distance_hav())

aaa = Latlng_test(39.9792305,116.2999529,39.9792534167321,116.29986841612538)
print(aaa.get_distance_hav())

aaa = Latlng_test(39.9792305,116.2999529,39.9792534167321,116.29986841612538)
print(aaa.get_distance_hav())

aaa = Latlng_test(39.9792305,116.2999529,39.9792534167321,116.29986841612538)
print(aaa.get_distance_hav())

aaa = Latlng_test(39.9792305,116.2999529,39.9792534167321,116.29986841612538)
print(aaa.get_distance_hav())
time2 = time.time()
print(time2-time1)
