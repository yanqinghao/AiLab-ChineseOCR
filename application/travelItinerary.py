#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 01:01:37 2019
火车票识别
@author: chineseocr
"""
import datetime
from apphelper.image import union_rbox, adjust_box_to_origin
import re


class travelItinerary:
    """
    火车票结构化识别
    """

    def __init__(self, result, img, angle):
        self.result = union_rbox(result, 0.4)
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
        self.types = {"DiDi": False, "Shenzhou": False}
        self.company()
        if self.types["DiDi"]:
            self.didi()
        if self.types["Shenzhou"]:
            self.shenzhou()

    def company(self):
        """
        检查行程单类型
        """
        for i in range(self.N):
            txt = self.result[i]["text"].replace(" ", "")
            txt = txt.replace(" ", "")

            res = re.findall("滴滴出行|神州专车电子行程单", txt)
            if len(res) > 0:
                if res[0] == "滴滴出行":
                    self.types["DiDi"] = True
                    break
                elif res[0] == "神州专车电子行程单":
                    self.types["Shenzhou"] = True
                    break

    def didi(self):
        """
        滴滴出行行程单解析
        """
        station = {"车型": [], "时间": [], "城市": [], "起点": [], "终点": [], "里程": [], "金额": []}
        for i in range(self.N):
            txt = self.result[i]["text"]

            res = re.findall("快车|出租车|专车", txt)
            if len(res) > 0:

                state = {"金额": 0, "时间": 0, "起点": 0, "终点": 0, "城市": 0, "里程": 0, "车型": 0}
                if state["车型"] == 0:
                    station["车型"].append(res[0])
                    state["车型"] = 1
                res = re.findall(
                    "[0-9]{1,2}-[0-9]{2,4}[\.:-]{0,2}[0-9]{1,2}周[一二三四五六日曰]{0,1}", txt
                )
                if len(res) > 0 and state["时间"] == 0:
                    resDate = re.findall("[0-9]{1,2}-[0-9]{2}", txt)
                    resTime = re.findall("[0-9]{1,2}[\.:-]{0,2}[0-9]{2}周", txt)
                    current_year = datetime.datetime.now().year
                    time_concat = (
                        str(current_year)
                        + "-"
                        + resDate[0]
                        + " "
                        + resTime[0].replace("周", "")[:2]
                        + ":"
                        + resTime[0].replace("周", "")[-2:]
                        + ":00"
                    )
                    if (
                        datetime.datetime.strptime(time_concat, "%Y-%m-%d %H:%M:%S")
                        > datetime.datetime.now()
                    ):
                        time_concat = (
                            str(current_year - 1)
                            + "-"
                            + resDate[0]
                            + " "
                            + resTime[0].replace("周", "")[:2]
                            + ":"
                            + resTime[0].replace("周", "")[-2:]
                            + ":00"
                        )
                    station["时间"].append(time_concat)
                    state["时间"] = 1
                try:
                    txt = station["车型"][-1].join(txt.split(station["车型"][-1])[1:])
                    if state["城市"] == 0:
                        if len(txt.split(res[0])[1].split(" ")[0])>0:
                            station["城市"].append(txt.split(res[0])[1].split(" ")[0])
                        else:
                            station["城市"].append(txt.split(res[0])[1].split(" ")[1])
                        state["城市"] = 1
                    txt = station["城市"][-1].join(txt.split(station["城市"][-1])[1:])
                    if len(txt.split(" ")) <= 1:
                        if len(re.findall("快车|出租车", self.result[i - 1]["text"])) == 0:
                            txt = (
                                txt
                                + " "
                                + self.result[i - 1]["text"]
                            )
                        if len(re.findall("快车|出租车", self.result[i + 1]["text"])) == 0:
                            txt = txt + " " + self.result[i + 1]["text"]
                    rest = ["起点", "终点", "里程", "金额"]
                    rest_idx = 0
                    for n in txt.split(" "):
                        if len(n) > 0:
                            if len(n.split(".")) <= 2:
                                if rest_idx > 1:
                                    station[rest[rest_idx]].append(
                                        re.findall("[^一-龥]{3,8}", n)[0]
                                    )
                                else:
                                    station[rest[rest_idx]].append(n)
                                state[rest[rest_idx]] = 1
                            else:
                                if rest_idx > 1:
                                    station[rest[rest_idx]].append(
                                        re.findall(
                                            "[^一-龥]{3,8}",
                                            n.split(".")[0] + "." + n.split(".")[1][0],
                                        )[0]
                                    )
                                    station[rest[rest_idx + 1]].append(
                                        re.findall(
                                            "[^一-龥]{3,8}",
                                            n.split(".")[1][1:]
                                            + "."
                                            + n.split(".")[1][2],
                                        )[0]
                                    )
                                else:
                                    station[rest[rest_idx]].append(
                                        n.split(".")[0] + "." + n.split(".")[1][0]
                                    )
                                    station[rest[rest_idx + 1]].append(
                                        n.split(".")[1][1:] + "." + n.split(".")[1][2]
                                    )
                                state[rest[rest_idx]] = 1
                                state[rest[rest_idx + 1]] = 1
                            rest_idx += 1
                    station = self.check(state, station)
                except:
                    station = self.check(state, station)

        self.res.update(station)

    def shenzhou(self):
        """
        神州专车行程单解析
        """
        station = {"车型": [], "时间": [], "城市": [], "起点": [], "终点": [], "里程": [], "金额": []}
        points = []
        for i in range(self.N):
            txt = self.result[i]["text"]
            res = re.findall("金额:", txt)
            if len(res) > 0:
                points.append(i)

        for i in range(len(points)):
            if i == 0:
                start = 0
                end = points[i] + 1
            else:
                start = points[i - 1] + 1
                end = points[i] + 1
            state = {"金额": 0, "时间": 0, "起点": 0, "终点": 0, "城市": 0, "里程": 0, "车型": 0}
            station["车型"].append("神州专车")
            station["里程"].append("0")
            state["里程"] = 1
            state["车型"] = 1
            for j in range(start, end):

                txt = self.result[j]["text"]
                res = re.findall("[订单金额]{3,4}:￥", txt)
                if len(res) > 0 and state["金额"] == 0:
                    state["金额"] = 1
                    try:
                        resPrice = re.findall("[0-9]{1,4}.[0-9]{1,2}", txt)
                        station["金额"].append(resPrice[0])
                    except:
                        station["金额"].append("0")
                res = re.findall(
                    "[0-9]{1,4}-[0-9]{1,2}-[0-9]{2,4}:[0-9]{1,2}:[0-9]{1,2}", txt
                )
                if len(res) > 0 and state["时间"] == 0:
                    state["时间"] = 1
                    try:
                        resDate = re.findall("[0-9]{1,4}-[0-9]{1,2}-[0-9]{2}", txt)
                        resTime = re.findall("[0-9]{2}:[0-9]{1,2}:[0-9]{1,2}", txt)
                        station["时间"].append(resDate[0] + " " + resTime[0])
                    except:
                        station["时间"].append("无")
                res = re.findall("上车地点", txt)
                if len(res) > 0 and state["起点"] == 0:
                    state["起点"] = 1
                    try:
                        station["起点"].append(txt.split(" ")[1].split(":")[1])
                    except:
                        station["起点"].append("无")
                res = re.findall("下车地点", txt)
                if len(res) > 0 and state["终点"] == 0:
                    state["终点"] = 1
                    try:
                        station["终点"].append(txt.split(" ")[1].split(":")[1])
                    except:
                        station["终点"].append("无")
                res = re.findall("[用车城市]{3,4}", txt)
                if len(res) > 0 and state["城市"] == 0:
                    state["城市"] = 1
                    try:
                        station["城市"].append(txt.split(" ")[0].split(":")[1])
                    except:
                        station["城市"].append("无")
            station = self.check(state, station)
        self.res.update(station)

    def check(self, state, station):
        for i, j in state.items():
            if j == 0:
                if i in ["城市", "终点", "起点", "时间", "车型"]:
                    station[i].append("无")
                elif i in ["金额", "里程"]:
                    station[i].append("0")
        return station
