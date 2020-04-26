# coding=utf-8
from __future__ import absolute_import, print_function

import os
import base64
import pytesseract
from io import BytesIO
from PIL import Image
import suanpan
from suanpan.app import app
from suanpan.utils import image
from suanpan.log import logger
from suanpan.app.arguments import Bool, Int, Json, Float
from utils.function import box_cluster, detect_box, detect_angle, ocr_batch
from text.keras_detect import text_detect
from text.opencv_dnn_detect import angle_detect
from text.detector.detectors import TextDetector
from config import ocrModelTorchDense, ocrModelTorchLstm
from crnn.keys import alphabetChinese
from crnn.network_torch import CRNN
from apphelper.image import union_rbox, adjust_box_to_origin, sort_box


PARAMETER = {}


@app.afterInit
def afterInit(context):
    args = context.args
    PARAMETER.update(
        {
            "chineseModel": args.chineseModel,
            "LSTMFLAG": args.LSTMFLAG,
            "leftAdjustAlph": args.leftAdjustAlph,
            "rightAdjustAlph": args.rightAdjustAlph,
            "scale": args.scale,
            "maxScale": args.maxScale,
            "maxHorizontalGap": args.maxHorizontalGap,
            "minVOverlaps": args.minVOverlaps,
            "minSizeSim": args.minSizeSim,
            "textProposalsMinScore": args.textProposalsMinScore,
            "textProposalsNmsThresh": args.textProposalsNmsThresh,
            "textLineNmsThresh": args.textLineNmsThresh,
            "lineMinScore": args.lineMinScore,
            "GPU": args.__gpu,
        }
    )


@app.input(Json(key="inputData1"))
@app.param(Int(key="chineseModel", default=1))
@app.param(Bool(key="LSTMFLAG", default=True))
@app.param(Float(key="leftAdjustAlph", default=0.01))
@app.param(Float(key="rightAdjustAlph", default=0.01))
@app.param(Int(key="scale", default=608))
@app.param(Int(key="maxScale", default=608))
@app.param(Int(key="maxHorizontalGap", default=100))
@app.param(Float(key="minVOverlaps", default=0.6))
@app.param(Float(key="minSizeSim", default=0.6))
@app.param(Float(key="textProposalsMinScore", default=0.1))
@app.param(Float(key="textProposalsNmsThresh", default=0.3))
@app.param(Float(key="textLineNmsThresh", default=0.99))
@app.param(Float(key="lineMinScore", default=0.1))
@app.param(Int(key="__gpu", default=0))
@app.output(Json(key="outputData1"))
def SPOCRComac(context):
    global PARAMETER

    args = context.args
    inputImage = args.inputData1

    try:
        if inputImage.get("parameter"):
            PARAMETER.update(inputImage["parameter"])
        textLine = True
        LSTMFLAG = PARAMETER["LSTMFLAG"]
        if PARAMETER["chineseModel"] == 1:
            alphabet = alphabetChinese
            if LSTMFLAG:
                logger.info("Use chinese lstm model")
                ocrModel = ocrModelTorchLstm
            else:
                logger.info("Use chinese dense model")
                ocrModel = ocrModelTorchDense
        elif PARAMETER["chineseModel"] == 0:
            logger.info("Use english model")
            img = Image.open(BytesIO(base64.b64decode(inputImage["data"])))
            res = pytesseract.image_to_data(img, lang="eng", output_type="dict")
            output = []
            for i, text in enumerate(res["text"]):
                if len(text) > 0:
                    output.append(
                        {
                            "name": str(i),
                            "text": text,
                            "box": [
                                res["left"][i],
                                res["top"][i],
                                res["left"][i] + res["width"][i],
                                res["top"][i],
                                res["left"][i] + res["width"][i],
                                res["top"][i] + res["height"][i],
                                res["left"][i],
                                res["top"][i] + res["height"][i],
                            ],
                        }
                    )
            return {"data": output, "status": "success", "reason": None, "log": None}
        elif PARAMETER["chineseModel"] == 2:
            logger.info("Use english model")
            img = Image.open(BytesIO(base64.b64decode(inputImage["data"])))
            res = pytesseract.image_to_data(img, lang="chi_sim+eng", output_type="dict")
            output = []
            for i, text in enumerate(res["text"]):
                if len(text) > 0:
                    output.append(
                        {
                            "name": str(i),
                            "text": text,
                            "box": [
                                res["left"][i],
                                res["top"][i],
                                res["left"][i] + res["width"][i],
                                res["top"][i],
                                res["left"][i] + res["width"][i],
                                res["top"][i] + res["height"][i],
                                res["left"][i],
                                res["top"][i] + res["height"][i],
                            ],
                        }
                    )
            return {"data": output, "status": "success", "reason": None, "log": None}
        else:
            return {
                "data": None,
                "status": "fail",
                "reason": "PLS SET chineseModel in (0,1,2)",
                "log": "Unknown chineseModel Type",
            }

        nclass = len(alphabet) + 1
        GPU = True if PARAMETER["GPU"] > 0 else False
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
            return {
                "data": None,
                "status": "fail",
                "reason": "请使用其他模型",
                "log": "wrong model",
            }
        filePath = "image.png"
        with open(filePath, "wb") as f:
            f.write(base64.b64decode(inputImage["data"]))
        img = image.read(filePath)[:, :, ::-1]
        img, angle = detect_angle(img, angle_detect)
        boxes, scores = detect_box(
            img, text_detect, scale=PARAMETER["scale"], maxScale=PARAMETER["maxScale"]
        )
        boxes, scores = box_cluster(
            img,
            boxes,
            scores,
            TextDetector,
            MAX_HORIZONTAL_GAP=PARAMETER["maxHorizontalGap"],  ##字符之间的最大间隔，用于文本行的合并
            MIN_V_OVERLAPS=PARAMETER["minVOverlaps"],
            MIN_SIZE_SIM=PARAMETER["minSizeSim"],
            TEXT_PROPOSALS_MIN_SCORE=PARAMETER["textProposalsMinScore"],
            TEXT_PROPOSALS_NMS_THRESH=PARAMETER["textProposalsNmsThresh"],
            TEXT_LINE_NMS_THRESH=PARAMETER["textLineNmsThresh"],  ##文本行之间测iou值
            LINE_MIN_SCORE=PARAMETER["lineMinScore"],
        )
        boxes = sort_box(boxes)
        if boxes:
            textLine = False
        if textLine:
            H, W = img.shape[:2]
            partImg = Image.fromarray(img)
            text = crnn.predict(partImg.convert("L"))
            output = {"text": text, "name": "0", "box": [0, 0, W, 0, W, H, 0, H]}
        else:
            res = ocr_batch(
                img,
                boxes,
                crnn.predict_job,
                PARAMETER["leftAdjustAlph"],
                PARAMETER["rightAdjustAlph"],
            )
            for j, info in enumerate(res):
                del info["img"]
            output = res
        result = union_rbox(output, 0.2)
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
            adjust_box_to_origin(img, angle, res)
            if angle is not None
            else adjust_box_to_origin(img, 0, res)
        )
        output = res
        return {"data": output, "status": "success", "reason": None, "log": None}
    except Exception as e:
        return {
            "data": None,
            "status": "fail",
            "reason": "请上传大于600*600的图片",
            "log": str(e),
        }


if __name__ == "__main__":
    suanpan.run(app)
