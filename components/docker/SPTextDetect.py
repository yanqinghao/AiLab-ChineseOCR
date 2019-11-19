# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app.arguments import Json, Int, Float
from suanpan.app import app
from suanpan.storage import storage
from arguments import Images
from utils.function import box_cluster, detect_box
from apphelper.image import sort_box
from text.keras_detect import text_detect
from text.detector.detectors import TextDetector


@app.input(Images(key="inputImage"))
@app.param(Int(key="scale", default=608))
@app.param(Int(key="maxScale", default=608))
@app.param(Float(key="maxHorizontalGap", default=100))
@app.param(Float(key="minVOverlaps", default=0.6))
@app.param(Float(key="minSizeSim", default=0.6))
@app.param(Float(key="textProposalsMinScore", default=0.1))
@app.param(Float(key="textProposalsNmsThresh", default=0.3))
@app.param(Float(key="textLineNmsThresh", default=0.99))
@app.param(Float(key="lineMinScore", default=0.1))
@app.output(Json(key="outputData"))
def SPTextDetect(context):
    args = context.args
    images = args.inputImage
    scale = args.scale
    maxScale = args.maxScale
    res = {"image": [], "boxes": []}
    for i, img in enumerate(images):
        boxes, scores = detect_box(
            img[:, :, ::-1], text_detect, scale=scale, maxScale=maxScale
        )  ##文字检测
        boxes, scores = box_cluster(
            img[:, :, ::-1],
            boxes,
            scores,
            TextDetector,
            MAX_HORIZONTAL_GAP=args.maxHorizontalGap,  ##字符之间的最大间隔，用于文本行的合并
            MIN_V_OVERLAPS=args.minVOverlaps,
            MIN_SIZE_SIM=args.minSizeSim,
            TEXT_PROPOSALS_MIN_SCORE=args.textProposalsMinScore,
            TEXT_PROPOSALS_NMS_THRESH=args.textProposalsNmsThresh,
            TEXT_LINE_NMS_THRESH=args.textLineNmsThresh,  ##文本行之间测iou值
            LINE_MIN_SCORE=args.lineMinScore,
        )
        boxes = sort_box(boxes)
        res["boxes"].append(boxes)
        res["image"].append(
            storage.delimiter.join(images.images[i].split(storage.delimiter)[8:])
        )
    return res


if __name__ == "__main__":
    SPTextDetect()

