# coding=utf-8
from __future__ import absolute_import, print_function

import os
import pandas as pd
from suanpan.app.arguments import Csv
from suanpan.app import app
from suanpan.storage import storage
from suanpan.utils import image
from suanpan import path
from text.opencv_dnn_detect import angle_detect
from utils.function import detect_angle
from arguments import Images


@app.input(Images(key="inputImage"))
@app.output(Images(key="outputImage"))
@app.output(Images(key="outputImageRaw"))
@app.output(Csv(key="outputData"))
def SPAngleModel(context):
    args = context.args
    images = args.inputImage
    outputData = {"image": [], "angle": []}
    for i, img in enumerate(images):
        img, angle = detect_angle(img[:, :, ::-1], angle_detect)
        image.save(
            os.path.join(
                args.outputImage,
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]),
            ),
            img[:, :, ::-1],
        )
        outputData["image"].append(
            storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
        )
        outputData["angle"].append(angle)
    outputData = pd.DataFrame(outputData)
    path.copy(images.folder, args.outputImageRaw)
    return args.outputImage, args.outputImageRaw, outputData


if __name__ == "__main__":
    SPAngleModel()

