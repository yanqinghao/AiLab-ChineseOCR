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
        self.check()

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
        self.res.update(info)

    def price(self):
        """
        发票金额
        """
        price = {}
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")
            ##发票金额
            res = re.findall("\(小写\)[￥Y][0-9]{1,4}.[0-9]{1,2}", txt)
            if len(res) > 0:
                price["发票金额"] = re.findall("[0-9]{1,4}.[0-9]{1,2}", res[0])[0]
                self.res.update(price)
                break

    def full_name(self):
        """
        提取公司名称 纳税人识别号
        """
        name = {}
        for i in range(self.N):
            txt = self.result[i]["text"]
            txt = txt.replace(" ", "")
            ##公司名称
            res = re.findall("称:[一-龥()]{4,20}", txt)
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

    def check(self):
        if len(self.res) < 8 and len(self.res) > 0:
            updatekeys = set(
                ["货物或应税劳务、服务名称", "发票代码", "发票号码", "开票日期", "校验码", "名称", "纳税人识别号", "发票金额"]
            ) - set(self.res.keys())
            for i in updatekeys:
                name = {}
                name[i] = "无"
                self.res.update(name)
        if "货物或应税劳务、服务名称" in self.res.keys():
            if "机票" in self.res["货物或应税劳务、服务名称"]:
                remarks = {}
                for i in range(self.N):
                    txt = self.result[i]["text"]
                    ##订单号 姓名 行程
                    res = re.findall("订单号", txt)
                    if len(res) > 0:
                        try:
                            res = re.findall("订单号[0-9]{10}", txt)
                            remarks["订单号"] = res[0].replace("订单号", "")
                            remarks["姓名"] = txt.split(",")[1]
                            journey = txt.split(",")[3]
                            remarks["起点"] = journey.split("-")[0]
                            remarks["终点"] = journey.split("-")[1]
                        except:
                            for i in set(["订单号", "姓名", "起点", "终点"]) - set(
                                remarks.keys()
                            ):
                                remarks[i] = "无"
                        self.res.update(remarks)
            else:
                remarks = {}
                for i in ["订单号", "姓名", "起点", "终点"]:
                    remarks[i] = "无"
                self.res.update(remarks)
