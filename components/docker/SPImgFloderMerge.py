# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app import app
from suanpan.storage import storage
from arguments import Images


@app.input(Images(key="inputImage1"))
@app.input(Images(key="inputImage2"))
@app.input(Images(key="inputImage3"))
@app.input(Images(key="inputImage4"))
@app.input(Images(key="inputImage5"))
@app.output(Images(key="outputImage"))
def SPImgFloderMerge(context):
    args = context.args
    images1 = args.inputImage1
    images2 = args.inputImage2
    images3 = args.inputImage3
    images4 = args.inputImage4
    images5 = args.inputImage5
    inputImages = [images1, images2, images3, images4, images5]
    outputImages = []
    for images in inputImages:
        if images:
            for i, img in enumerate(images):
                outputImages.append(
                    (
                        storage.delimiter.join(
                            images.images[i].split(storage.delimiter)[8:]
                        ),
                        img,
                    )
                )
    return outputImages


if __name__ == "__main__":
    SPImgFloderMerge()

