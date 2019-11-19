# coding=utf-8
from __future__ import absolute_import, print_function

import os
from PIL import Image
from suanpan.app.arguments import Bool, Int, Json, Float
from suanpan.app import app
from suanpan.storage import storage
from suanpan import path
from config import ocrModelTorchDense, ocrModelTorchLstm, ocrModelTorchEng
from crnn.keys import alphabetChinese, alphabetEnglish
from crnn.network_torch import CRNN
from utils.function import ocr_batch
from arguments import Images


@app.input(Images(key="inputImage"))
@app.input(Images(key="inputImageRaw"))
@app.input(Json(key="inputBoxes"))
@app.param(Bool(key="chineseModel", default=True))
@app.param(Bool(key="LSTMFLAG", default=True))
@app.param(Int(key="__gpu", default=0))
@app.param(Float(key="leftAdjustAlph", default=0.01))
@app.param(Float(key="rightAdjustAlph", default=0.01))
@app.output(Images(key="outputImageRaw"))
@app.output(Json(key="outputData"))
def SPCRNN(context):
    args = context.args
    images = args.inputImage
    imageRaw = args.inputImageRaw
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
        for i, img in enumerate(images):
            H, W = img.shape[:2]
            partImg = Image.fromarray(img[:, :, ::-1])
            text = crnn.predict(partImg.convert("L"))
            output["image"].append(
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
            )
            output["res"].append(
                {"text": text, "name": "0", "box": [0, 0, W, 0, W, H, 0, H]}
            )
    else:
        for i, img in enumerate(images):
            res = ocr_batch(
                img[:, :, ::-1],
                boxes["boxes"][
                    boxes["image"].index(
                        storage.delimiter.join(
                            images.images[i].split(storage.delimiter)[8:]
                        )
                    )
                ],
                crnn.predict_job,
                args.leftAdjustAlph,
                args.rightAdjustAlph,
            )
            for j, info in enumerate(res):
                del info["img"]

            output["image"].append(
                storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
            )
            output["res"].append(res)
    path.copy(imageRaw.folder, args.outputImageRaw)
    return args.outputImageRaw, output


if __name__ == "__main__":
    SPCRNN()

