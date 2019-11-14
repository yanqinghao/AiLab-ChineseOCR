# coding=utf-8
from __future__ import absolute_import, print_function

import os
import numpy as np
from suanpan.app import app
from suanpan.storage import storage
from suanpan.utils import image
from arguments import Images


@app.input(Images(key="inputImage"))
@app.output(Images(key="outputImage"))
def SPRemoveWatermark(context):
    args = context.args
    images = args.inputImage
    alpha = 2.0
    beta = -160

    for i, img in enumerate(images):
        new = alpha * img + beta
        new = np.clip(new, 0, 255).astype(np.uint8)
        image.save(
            os.path.join(
                args.outputImage,
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:]),
            ),
            new,
        )

    return args.outputImage


if __name__ == "__main__":
    SPRemoveWatermark()

