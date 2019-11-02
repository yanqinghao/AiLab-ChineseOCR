# coding=utf-8
from __future__ import absolute_import, print_function

import os
import json
from suanpan.app import app
from suanpan.app.arguments import Folder
from suanpan.utils import image
from suanpan.storage import storage
from arguments import Images


@app.input(Images(key="inputImage"))
@app.input(Folder(key="inputData"))
@app.output(Images(key="outputImage"))
def SPViaSegment(context):
    args = context.args
    images = args.inputImage

    jsonFile = os.path.join(args.inputData, "project.json")
    with open(jsonFile, "rb") as load_f:
        fileInfo = json.load(load_f)

    outputData = []
    files = []
    for i, j in fileInfo["metadata"].items():
        files.append(os.path.join(images.folder, j["vid"]))
        filename = j["vid"].splitext()[0] + "_" + j["av"]["1"] + ".png"
        xy = j["xy"][1:]
        img = image.read(os.path.join(images.folder, j["vid"]))
        outputData.append((filename, img[xy[0] : xy[2], xy[1] : xy[3]]))

    for idx, img in enumerate(images):
        if images.images[idx] not in files:
            outputData.append(
                (
                    storage.delimiter.join(
                        images.images[idx].split(storage.delimiter)[8:]
                    ),
                    img,
                )
            )

    return outputData


if __name__ == "__main__":
    SPViaSegment()
