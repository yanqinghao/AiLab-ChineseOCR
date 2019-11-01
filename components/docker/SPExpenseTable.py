# coding=utf-8
from __future__ import absolute_import, print_function

import datetime
import pandas as pd
from suanpan.app import app
from suanpan.log import logger
from suanpan.app.arguments import Csv


def list_operation(output, method, values, position=None):
    if method == "append":
        for i, j in enumerate(output.items()):
            output[j[0]].append(values[i])
    elif method == "insert":
        for i, j in enumerate(output.items()):
            output[j[0]].insert(position, values[i])
    else:
        pass
    return output


@app.input(Csv(key="inputTrainData"))
@app.input(Csv(key="inputInvoiceData"))
@app.input(Csv(key="inputItineraryData"))
@app.output(Csv(key="outputData"))
def SPExpenseTable(context):
    args = context.args
    trainDF = args.inputTrainData
    invoiceDF = args.inputInvoiceData
    itineraryDF = args.inputItineraryData

    outputDF = {
        "开始时间": [],
        "结束时间": [],
        "项目编码": [],
        "出差事由": [],
        "起始地点": [],
        "抵达地点": [],
        "宾馆住宿费": [],
        "城市间交通费": [],
        "市内交通费": [],
        "出差天数": [],
        "出差餐补": [],
        "总计": [],
    }

    if invoiceDF is not None:
        trainDF["列车时刻"] = trainDF["日期"].str.cat(trainDF["时间"], sep=" ")
        trainDF["列车时刻"] = pd.to_datetime(trainDF["列车时刻"], format="%Y-%m-%d %H:%M")
        trainDF = trainDF.sort_values("列车时刻").reset_index()
        for i in range(len(trainDF)):
            outputDF = list_operation(
                outputDF,
                "append",
                [
                    datetime.datetime.strftime(trainDF["列车时刻"][i], "%Y/%m/%d"),
                    "",
                    "",
                    "",
                    trainDF["出发"][i],
                    trainDF["到达"][i],
                    0,
                    trainDF["车票价格"][i],
                    0,
                    0,
                    0,
                    0,
                ],
            )

    if invoiceDF is not None:
        invoiceDF["发票日期"] = pd.to_datetime(invoiceDF["开票日期"], format="%Y-%m-%d")
        invoiceDF = invoiceDF.sort_values("发票日期").reset_index()
        for i in range(len(invoiceDF)):
            if "客运服务费" in invoiceDF["货物或应税劳务、服务名称"][i]:
                if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                    outputDF["开始时间"][-1], "%Y/%m/%d"
                ):
                    for j in range(len(outputDF["开始时间"]) - 1):
                        if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                            outputDF["开始时间"][j], "%Y/%m/%d"
                        ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                            outputDF["开始时间"][j + 1], "%Y/%m/%d"
                        ):
                            outputDF["市内交通费"][j + 1] += invoiceDF["发票金额"][i]
                            break
                elif invoiceDF["发票日期"][i] < datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ):
                    outputDF["市内交通费"][0] += invoiceDF["发票金额"][i]
                else:
                    outputDF["市内交通费"][-1] += invoiceDF["发票金额"][i]
            elif "住宿费" in invoiceDF["货物或应税劳务、服务名称"][i]:
                if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                    outputDF["开始时间"][-1], "%Y/%m/%d"
                ):
                    for j in range(len(outputDF["开始时间"]) - 1):
                        if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                            outputDF["开始时间"][j], "%Y/%m/%d"
                        ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                            outputDF["开始时间"][j + 1], "%Y/%m/%d"
                        ):
                            outputDF["宾馆住宿费"][j + 1] += invoiceDF["发票金额"][i]
                            break
                elif invoiceDF["发票日期"][i] < datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ):
                    outputDF["宾馆住宿费"][0] += invoiceDF["发票金额"][i]
                else:
                    outputDF["宾馆住宿费"][-1] += invoiceDF["发票金额"][i]
            elif "机票" in invoiceDF["货物或应税劳务、服务名称"][i]:
                if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                    outputDF["开始时间"][-1], "%Y/%m/%d"
                ):
                    for j in range(len(outputDF["开始时间"]) - 1):
                        if invoiceDF["发票日期"][i] >= datetime.datetime.strptime(
                            outputDF["开始时间"][j], "%Y/%m/%d"
                        ) and invoiceDF["发票日期"][i] <= datetime.datetime.strptime(
                            outputDF["开始时间"][j + 1], "%Y/%m/%d"
                        ):
                            outputDF = list_operation(
                                outputDF,
                                "insert",
                                [
                                    datetime.datetime.strftime(
                                        invoiceDF["发票日期"][i], "%Y/%m/%d"
                                    ),
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    0,
                                    invoiceDF["发票金额"][i],
                                    0,
                                    0,
                                    0,
                                    0,
                                ],
                                position=j + 1,
                            )
                            break
                elif invoiceDF["发票日期"][i] < datetime.datetime.strptime(
                    outputDF["开始时间"][0], "%Y/%m/%d"
                ):
                    outputDF = list_operation(
                        outputDF,
                        "insert",
                        [
                            datetime.datetime.strftime(
                                invoiceDF["发票日期"][i], "%Y/%m/%d"
                            ),
                            "",
                            "",
                            "",
                            "",
                            "",
                            0,
                            invoiceDF["发票金额"][i],
                            0,
                            0,
                            0,
                            0,
                        ],
                        position=0,
                    )
                else:
                    outputDF = list_operation(
                        outputDF,
                        "insert",
                        [
                            datetime.datetime.strftime(
                                invoiceDF["发票日期"][i], "%Y/%m/%d"
                            ),
                            "",
                            "",
                            "",
                            "",
                            "",
                            0,
                            invoiceDF["发票金额"][i],
                            0,
                            0,
                            0,
                            0,
                        ],
                        position=-1,
                    )

            else:
                logger.info("未识别的发票种类")

    if itineraryDF is not None:
        itineraryDF["打车时刻"] = pd.to_datetime(itineraryDF["时间"], format="%Y-%m-%d %H:%M")
        itineraryDF = itineraryDF.sort_values("打车时刻").reset_index()
        for i in range(len(itineraryDF)):
            if itineraryDF["打车时刻"][i] >= datetime.datetime.strptime(
                outputDF["开始时间"][0], "%Y/%m/%d"
            ) and itineraryDF["打车时刻"][i] <= datetime.datetime.strptime(
                outputDF["开始时间"][-1], "%Y/%m/%d"
            ):
                for j in range(len(outputDF["开始时间"]) - 1):
                    if itineraryDF["打车时刻"][i] >= datetime.datetime.strptime(
                        outputDF["开始时间"][j], "%Y/%m/%d"
                    ) and itineraryDF["打车时刻"][i] <= datetime.datetime.strptime(
                        outputDF["开始时间"][j + 1], "%Y/%m/%d"
                    ):
                        outputDF["市内交通费"][j + 1] += itineraryDF["金额"][i]
                        break
            elif itineraryDF["打车时刻"][i] < datetime.datetime.strptime(
                outputDF["开始时间"][0], "%Y/%m/%d"
            ):
                outputDF["市内交通费"][0] += itineraryDF["金额"][i]
            else:
                outputDF["市内交通费"][-1] += itineraryDF["金额"][i]

    outputDF = pd.DataFrame(outputDF)
    return outputDF


if __name__ == "__main__":
    SPExpenseTable()

