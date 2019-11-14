# coding=utf-8
from __future__ import absolute_import, print_function

import os
import sys
import shutil
import numpy as np
from pdf2image import convert_from_path
from suanpan.app.arguments import Folder
from suanpan.app import app
from suanpan.storage import storage
from suanpan.utils import image
from arguments import Images


def find_all_images(folder):
    files_ = []
    list = [i for i in os.listdir(folder)]
    for i in range(0, len(list)):
        path = os.path.join(folder, list[i])
        if os.path.isdir(path):
            files_.extend(find_all_images(path))
        if not os.path.isdir(path):
            if path.lower().endswith("pdf"):
                files_.append(path)
    return files_


@app.input(Folder(key="inputPDF"))
@app.output(Images(key="outputImage"))
def SPPDF2Image(context):
    args = context.args
    pdfs = args.inputPDF

    if not os.path.exists("/usr/share/fonts/myfonts"):
        os.makedirs("/usr/share/fonts/myfonts")
    if not os.path.exists("/usr/share/fonts/myfonts/华文宋体.ttf"):
        shutil.copyfile(
            os.path.join(os.path.dirname(sys.argv[0]), "tools/华文宋体.ttf"),
            "/usr/share/fonts/myfonts/华文宋体.ttf",
        )

    pdfFiles = find_all_images(pdfs)
    for pdf in pdfFiles:
        pages = convert_from_path(pdf, 500)

        for i, page in enumerate(pages):
            image.save(
                os.path.join(
                    args.outputImage,
                    os.path.splitext(
                        storage.delimiter.join(pdf.split(storage.delimiter)[8:])
                    )[0]
                    + "_"
                    + str(i)
                    + ".png",
                ),
                np.asarray(page),
            )

    return args.outputImage


if __name__ == "__main__":
    SPPDF2Image()

