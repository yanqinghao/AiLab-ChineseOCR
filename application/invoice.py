#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2019-10-31
发票识别
@author: yanqing
"""
from apphelper.image import union_rbox, adjust_box_to_origin
import re


class invoice:
    """
    发票结构化识别
    """

    def __init__(self, result, img, angle):
        self.result = union_rbox(result, 0.2)
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
        self.types()
        self.basic_info()
        self.price()
        self.full_name()

    def types(self):
        """
        提取服务名称
        """
        types = {}
        for i in range(self.N):
            txt = self.result[i]["text"]

            res = re.findall("客运服务费 |机票 |住宿费", txt)
            if len(res) > 0:
                types["货物或应税劳务、服务名称"] = txt.split(" ")[0]

            if len(types) > 0:
                self.res.update(types)
                break

    def basic_info(self):
        """
        提取开票日期 发票代码 校验码 发票号码 
        """
        info = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##匹配开票日期
            res = re.findall("开票日期:[0-9]{1,4}年[0-9]{1,2}月[0-9]{1,2}日", txt)
            if len(res) > 0:
                info["开票日期"] = (
                    res[0]
                    .replace("开票日期:", "")
                    .replace("年", "-")
                    .replace("月", "-")
                    .replace("日", "")
                )
            ##匹配发票代码
            res = re.findall("发票代码:[0-9]{1,20}", txt)
            if len(res) > 0:
                info["发票代码"] = res[0].replace("发票代码:", "")
            ##匹配发票号码
            res = re.findall("发票号码:[0-9]{1,20}", txt)
            if len(res) > 0:
                info["发票号码"] = res[0].replace("发票号码:", "")
            ##匹配校验码
            res = re.findall("校验码:[0-9]{1,20}", txt)
            if len(res) > 0:
                info["校验码"] = res[0].replace("校验码:", "")
            if len(info) == 4:
                self.res.update(info)
                break

    def price(self):
        """
        发票金额
        """
        price = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##发票金额
            res = re.findall("(小写)￥[0-9]{1,4}.[0-9]{1,2}", txt)
            if len(res) > 0:
                price["发票金额"] = res[0].replace("(小写)￥", "")
                self.res.update(price)
                break

    def full_name(self):
        """
        提取公司名称 纳税人识别号
        """
        name = {}
        for i in range(self.N):
            txt = self.result[i]["text"]
            txt = txt.split(" ")[0]
            ##公司名称
            res = re.findall("称:[一-龥]{4,20}", txt)
            if len(res) > 0:
                if res[0].replace("称:", "") != "无锡雪浪数制科技有限公司":
                    name["名称"] = res[0].replace("称:", "")
            ##纳税人识别号
            res = re.findall("纳税人识别号:[a-zA-Z0-9]{10,20}", txt)
            if len(res) > 0:
                if res[0].replace("纳税人识别号:", "") != "91320211MA1WJC2585":
                    name["纳税人识别号"] = res[0].replace("纳税人识别号:", "")
            if len(name) == 2:
                self.res.update(name)
