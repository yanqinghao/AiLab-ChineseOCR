# coding=utf-8
from __future__ import absolute_import, print_function

import numpy as np
from suanpan.app import app
from suanpan.storage import storage
from arguments import Images


@app.input(Images(key="inputImage"))
@app.output(Images(key="outputImage"))
def SPRemoveWatermark(context):
    args = context.args
    images = args.inputImage
    alpha = 2.0
    beta = -160

    outputImages = []
    for i, img in enumerate(images):
        new = alpha * img + beta
        new = np.clip(new, 0, 255).astype(np.uint8)
        outputImages.append(
            (storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]), new)
        )

    return outputImages


if __name__ == "__main__":
    SPRemoveWatermark()

