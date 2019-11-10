# coding=utf-8
from __future__ import absolute_import, print_function

import cv2
import pandas as pd
import numpy as np
from suanpan.app.arguments import Csv, Json, String, Float
from suanpan.app import app
from suanpan.storage import storage
from arguments import Images
from application import invoice


@app.input(Images(key="inputImage"))
@app.input(Json(key="detectedText"))
@app.input(Csv(key="angles"))
@app.param(Float(key="alpha", default=0.2))
@app.param(String(key="services", default=r"客运服务费 |机票 |住宿费|技术服务|餐费"))
@app.param(String(key="money", default=r"\(小写\)[￥Y一-龥][0-9]{1,5}.[0-9]{1,2}"))
@app.param(String(key="date", default=r"开票日期:[0-9]{1,4}年[0-9]{1,2}月[0-9]{1,2}"))
@app.output(Json(key="outputData1"))
@app.output(Csv(key="outputData2"))
@app.output(Images(key="outputImage"))
def SPInvoice(context):
    args = context.args
    images = args.inputImage
    detectedText = args.detectedText
    angles = args.angles
    params = {
        "services": args.services,
        "money": args.money,
        "date": args.date,
        "alpha": args.alpha,
    }
    output = {"image": [], "res": [], "box": []}
    for i, img in enumerate(images):
        angle = (
            angles.loc[
                angles["image"]
                == storage.delimiter.join(
                    images.images[i].split(storage.delimiter)[8:]
                ),
                "angle",
            ].values[0]
            if angles is not None
            else 0
        )
        res = invoice.invoice(
            detectedText["res"][
                detectedText["image"].index(
                    storage.delimiter.join(
                        images.images[i].split(storage.delimiter)[8:]
                    )
                )
            ],
            img,
            angle,
            **params
        )
        result = [{"text": res.res[key], "name": key, "box": {}} for key in res.res]

        output["image"].append(
            storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
        )
        output["res"].append(result)
        output["box"].append(res.box)

    outputCsv = {"image": []}
    for i, j in enumerate(output["image"]):
        if output["res"][i]:
            outputCsv["image"].append(j)
            for m in output["res"][i]:
                if m["name"] not in outputCsv.keys():
                    outputCsv[m["name"]] = [m["text"]]
                else:
                    outputCsv[m["name"]].append(m["text"])
    length = min([len(j) for i, j in outputCsv.items()])
    for key, value in outputCsv.items():
        outputCsv[key] = value[:length]
    outputCsv = pd.DataFrame(outputCsv)

    outputImages = []
    for i, img in enumerate(images):
        boxArr = output["box"][
            output["image"].index(
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
            )
        ]
        for j in boxArr:
            x1, y1, x2, y2, x3, y3, x4, y4 = j["box"]
            cv2.polylines(
                img,
                [np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)],
                True,
                (0, 0, 255),
            )
        outputImages.append(
            (storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]), img)
        )

    return output, outputCsv, outputImages


if __name__ == "__main__":
    SPInvoice()

