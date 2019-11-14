# coding=utf-8
from __future__ import absolute_import, print_function

import os
import cv2
import pandas as pd
import numpy as np
from suanpan.app.arguments import Csv, Json
from suanpan.app import app
from suanpan.storage import storage
from suanpan.utils import image
from arguments import Images
from application import travelItinerary


@app.input(Images(key="inputImage"))
@app.input(Json(key="detectedText"))
@app.input(Csv(key="angles"))
@app.output(Json(key="outputData1"))
@app.output(Csv(key="outputData2"))
@app.output(Images(key="outputImage"))
def SPTravelItinerary(context):
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
        res = travelItinerary.travelItinerary(
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
            l = 0
            for m in output["res"][i]:
                l = len(m["text"])
                if m["name"] not in outputCsv.keys():
                    outputCsv[m["name"]] = m["text"]
                else:
                    outputCsv[m["name"]] += m["text"]
            if l:
                outputCsv["image"] += [j] * l
    length = min([len(j) for i, j in outputCsv.items()])
    for key, value in outputCsv.items():
        outputCsv[key] = value[:length]
    outputCsv = pd.DataFrame(outputCsv)

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
        image.save(
            os.path.join(
                args.outputImage,
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]),
            ),
            img,
        )

    return output, outputCsv, args.outputImage


if __name__ == "__main__":
    SPTravelItinerary()

