# coding=utf-8
from __future__ import absolute_import, print_function

import cv2
import numpy as np
from suanpan.app.arguments import Csv, Json
from suanpan.app import app
from suanpan.storage import storage
from arguments import Images
from apphelper.image import union_rbox, adjust_box_to_origin


@app.input(Images(key="inputImage"))
@app.input(Json(key="detectedText"))
@app.input(Csv(key="angles"))
@app.output(Json(key="outputData"))
@app.output(Images(key="outputImage"))
def SPUniversal(context):
    args = context.args
    images = args.inputImage
    detectedText = args.detectedText
    angles = args.angles
    output = {"image": [], "res": []}
    for i, img in enumerate(images):
        result = union_rbox(
            detectedText["res"][
                detectedText["image"].index(
                    storage.delimiter.join(
                        images.images[i].split(storage.delimiter)[8:]
                    )
                )
            ],
            0.2,
        )
        res = [
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
            for i, x in enumerate(result)
        ]
        res = (
            adjust_box_to_origin(
                img,
                angles.loc[
                    angles["image"]
                    == storage.delimiter.join(
                        images.images[i].split(storage.delimiter)[8:]
                    ),
                    "angle",
                ].values[0],
                res,
            )
            if angles is not None
            else adjust_box_to_origin(img, 0, res)
        )
        output["image"].append(
            storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
        )
        output["res"].append(res)

    outputImages = []
    for i, img in enumerate(images):
        boxArr = output["res"][
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

    return output, outputImages


if __name__ == "__main__":
    SPUniversal()

