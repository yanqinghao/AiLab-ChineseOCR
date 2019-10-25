# coding=utf-8
from __future__ import absolute_import, print_function

import os
import numpy as np
from PIL import Image
from suanpan.app.arguments import Bool, Int, Json, Float
from suanpan.app import app
from config import ocrModelTorchDense, ocrModelTorchLstm, ocrModelTorchEng
from crnn.keys import alphabetChinese, alphabetEnglish
from crnn.network_torch import CRNN
from utils.function import ocr_batch
from arguments import Images


@app.input(Images(key="inputImage"))
@app.input(Json(key="inputBoxes"))
@app.param(Bool(key="chineseModel", default=True))
@app.param(Bool(key="LSTMFLAG", default=True))
@app.param(Int(key="__gpu", default=0))
@app.param(Float(key="leftAdjustAlph", default=0.01))
@app.param(Float(key="rightAdjustAlph", default=0.01))
@app.output(Json(key="outputData"))
@app.output(Images(key="outputImage"))
def SPCRNN(context):
    args = context.args
    images = args.inputImage
    boxes = args.inputBoxes
    textLine = True
    LSTMFLAG = args.LSTMFLAG
    if args.chineseModel:
        alphabet = alphabetChinese
        if args.LSTMFLAG:
            ocrModel = ocrModelTorchLstm
        else:
            ocrModel = ocrModelTorchDense
    else:
        ocrModel = ocrModelTorchEng
        alphabet = alphabetEnglish
        LSTMFLAG = True

    nclass = len(alphabet) + 1

    GPU = True if args.__gpu > 0 else False

    crnn = CRNN(
        32,
        1,
        nclass,
        256,
        leakyRelu=False,
        lstmFlag=LSTMFLAG,
        GPU=GPU,
        alphabet=alphabet,
    )

    if os.path.exists(ocrModel):
        crnn.load_weights(ocrModel)
    else:
        print("download model or tranform model with tools!")

    if boxes:
        textLine = False
    output = {"image": [], "res": []}
    if textLine:
        imgRes = images.folder
        for i, img in enumerate(images):
            H, W = img.shape[:2]
            partImg = Image.fromarray(img)
            text = crnn.predict(partImg.convert("L"))
            output["image"].append(images.images[i])
            output["res"].append(
                {"text": text, "name": "0", "box": [0, 0, W, 0, W, H, 0, H]}
            )
    else:
        imgRes = []
        for i, img in enumerate(images):
            res = ocr_batch(
                img,
                boxes["boxes"][i],
                crnn.predict_job,
                args.leftAdjustAlph,
                args.rightAdjustAlph,
            )
            for j, info in enumerate(res):
                imgRes.append(("image_{}_{}".format(i, j), np.asarray(info["img"])))
                del info["img"]

            output["image"].append(images.images[i])
            output["res"].append(res)

    return output, imgRes


if __name__ == "__main__":
    SPCRNN()

