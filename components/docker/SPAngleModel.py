# coding=utf-8
from __future__ import absolute_import, print_function

import pandas as pd
from suanpan.app.arguments import Csv
from suanpan.app import app
from suanpan.storage import storage
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
    outputImages = []
    outputImageRaw = []
    outputData = {"image": [], "angle": []}
    for i, img in enumerate(images):
        outputImageRaw.append(
            (storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]), img)
        )
        img, angle = detect_angle(img, angle_detect)
        outputImages.append(
            (storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]), img)
        )
        outputData["image"].append(
            storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
        )
        outputData["angle"].append(angle)
    outputData = pd.DataFrame(outputData)
    return outputImages, outputImageRaw, outputData


if __name__ == "__main__":
    SPAngleModel()

