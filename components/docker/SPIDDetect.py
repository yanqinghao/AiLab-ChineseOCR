# coding=utf-8
from __future__ import absolute_import, print_function

import cv2
import pandas as pd
import numpy as np
from suanpan.app.arguments import Csv, Json
from suanpan.app import app
from suanpan.storage import storage
from arguments import Images
from application import idcard


@app.input(Images(key="inputImage"))
@app.input(Json(key="detectedText"))
@app.input(Csv(key="angles"))
@app.output(Json(key="outputData1"))
@app.output(Csv(key="outputData2"))
@app.output(Images(key="outputImage"))
def SPIDDetect(context):
    args = context.args
    images = args.inputImage
    detectedText = args.detectedText
    angles = args.angles
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
        res = idcard.idcard(
            detectedText["res"][
                detectedText["image"].index(
                    storage.delimiter.join(
                        images.images[i].split(storage.delimiter)[8:]
                    )
                )
            ],
            img,
            angle,
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
    SPIDDetect()

