#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2019/11/05
用户自定义识别
@author: yanqing
"""
from apphelper.image import union_rbox, adjust_box_to_origin
import re


class userDefine:
    """
    用户自定义识别
    """

    def __init__(self, result, img, angle, field, keyword, regex):
        self.field = field
        self.keyword = keyword
        self.regex = regex
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
        self.match()

    def match(self):
        station = {self.field: ""}
        for i in range(self.N):
            txt = self.result[i]["text"]

            res = re.findall(self.keyword, txt)
            values = ""
            if len(res) > 0:
                if self.regex:
                    res = re.findall(self.regex, txt)
                    if len(res) > 0:
                        values = ",".join(res)
                else:
                    values = txt
            if len(values) > 0:
                if len(station[self.field]) > 0:
                    station[self.field] += ";" + values
                else:
                    station[self.field] += values

        self.res.update(station)
