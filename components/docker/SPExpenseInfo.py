# coding=utf-8
from __future__ import absolute_import, print_function

import pandas as pd
from suanpan.app import app
from suanpan.app.arguments import Csv
from suanpan import path
from arguments import Images


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
@app.input(Images(key="inputImage"))
@app.output(Csv(key="outputData"))
@app.output(Images(key="outputImage"))
def SPExpenseInfo(context):
    args = context.args
    trainDF = args.inputTrainData
    invoiceDF = args.inputInvoiceData
    itineraryDF = args.inputItineraryData
    images = args.inputImage

    path.copy(images.folder, args.outputImage)

    outputDF = {"图片": [], "时间": [], "起点": [], "终点": [], "费用": [], "费用种类": []}

    if invoiceDF is not None:
        for i in range(len(trainDF)):
            outputDF = list_operation(
                outputDF,
                "append",
                [
                    trainDF["image"][i],
                    trainDF["日期"][i],
                    trainDF["出发"][i],
                    trainDF["到达"][i],
                    trainDF["车票价格"][i],
                    "火车票",
                ],
            )

    if invoiceDF is not None:
        for i in range(len(invoiceDF)):
            outputDF = list_operation(
                outputDF,
                "append",
                [
                    invoiceDF["image"][i],
                    invoiceDF["开票日期"][i],
                    invoiceDF["起点"][i],
                    invoiceDF["终点"][i],
                    invoiceDF["发票金额"][i],
                    invoiceDF["货物或应税劳务、服务名称"][i],
                ],
            )

    if itineraryDF is not None:
        for i in range(len(itineraryDF)):
            outputDF = list_operation(
                outputDF,
                "append",
                [
                    itineraryDF["image"][i],
                    itineraryDF["时间"][i],
                    itineraryDF["起点"][i],
                    itineraryDF["终点"][i],
                    itineraryDF["金额"][i],
                    itineraryDF["车型"][i],
                ],
            )

    outputDF = pd.DataFrame(outputDF)
    outputDF.loc[outputDF["时间"] == "无", ["时间"]] = "1900-01-01"
    outputDF["日期"] = pd.to_datetime(outputDF["时间"], format="%Y-%m-%d")
    outputDF = outputDF.sort_values("日期").reset_index()
    outputDF = outputDF.drop(["日期", "index"], axis=1)
    outputDF.loc[outputDF["时间"] == "1900-01-01", ["时间"]] = "无"
    return outputDF, args.outputImage


if __name__ == "__main__":
    SPExpenseInfo()

