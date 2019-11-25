#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 01:01:37 2019
火车票识别
@author: chineseocr
"""
from apphelper.image import union_rbox, adjust_box_to_origin
import re


class trainTicket:
    """
    火车票结构化识别
    """

    def __init__(self, result, img, angle, **kw):
        for name, value in kw.items():
            setattr(self, name, value)
        self.result = union_rbox(result, getattr(self, "alpha", 0.4))
        self.box = [
            {
                "text": x["text"],
                "name": str(i),
                "box": {
                    "cx": x["cx"],
                    "cy": x["cy"],
                    "w": x["w"],
                    "h": x["h"],
                    "angle": x["degree"],
                },
            }
            for i, x in enumerate(self.result)
        ]
        self.box = adjust_box_to_origin(img, angle, self.box)
        self.N = len(self.result)
        self.res = {}
        self.station()
        self.time()
        self.price()
        self.full_name()

    def station(self):
        """
        安顺站K492贵阳站
        re.findall('[一-龥]+站','安顺站K492贵阳站'),re.findall('[一-龥]+站(.+?)[][一-龥]+站','安顺站K492贵阳站')
        
        """
        station = {}
        for i in range(self.N):
            txt = self.result[i]["text"]

            res = re.findall("[一-龥]+站", txt)
            if len(res) > 0:
                for value in res:
                    if "出发" not in station.keys():
                        station["出发"] = value
                    else:
                        station["到达"] = value
            res = re.findall("([KGZTC]{1}[0-9]{1,4}) ", txt)
            if len(res) > 0:
                if "车次" not in station.keys():
                    station["车次"] = res[0]

        if len(station) > 0:
            self.res.update(station)

    def time(self):
        """
        提取日期 时间 
        """
        time = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##匹配日期
            res = re.findall("[0-9]{1,4}年[0-9]{1,2}月[0-9]{1,2}", txt)
            if len(res) > 0:
                time["日期"] = res[0].replace("年", "-").replace("月", "-")
                ##匹配时间
                res = re.findall("[0-9]{1,2}:[0-9]{1,2}", txt)
                if len(res) > 0:
                    time["时间"] = res[0]
                    self.res.update(time)
                    break

    def price(self):
        """
        车票价格
        """
        price = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##车票价格
            res = re.findall("￥[0-9]{1,4}.[0-9]{1,2}元", txt)
            res += re.findall("[0-9]{1,4}.[0-9]{1,2}元", txt)
            res += re.findall("[0-9]{1,6}元", txt)
            res += re.findall("￥[0-9]{1,4}.[0-9]{1,2}", txt)
            if len(res) > 0:
                price["车票价格"] = res[0].replace("￥", "").replace("元", "")
                self.res.update(price)
                break

    def full_name(self):
        """
        姓名
        """
        name = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##车票价格
            res = re.findall("\d*\*\d*([一-龥]{1,4})", txt)
            if len(res) > 0:
                name["姓名"] = res[0]
                self.res.update(name)

