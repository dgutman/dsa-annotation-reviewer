import numpy as np
import os
import skimage.io
from histomicstk.cli.utils import CLIArgumentParser
from math import sqrt
from skimage import data
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.color import rgb2gray
import json
import cv2

import logging

logging.basicConfig(level=logging.CRITICAL)


def convert_to_DSA_annotations(shapeParamArray, shapeType):
    # This will convert an array of shapes into the proper format for the DSA annotation endpoint
    # This currently only supports circles formatted as ( centerX, centerY, radius) in absolute image coordinates
    # Will add more shapes as needed

    fillColor = "rgba(41,78,201,1)"  ## Make a param and define format
    lineColor = "rgb(213, 0, 213)"  ## TO DO
    lineWidth = 2  ## TODO
    group = "neuron"
    annotationElements = []

    if shapeType != "circle":
        print("Did not receive circle as a shape type... and that's all I can process so far!")
        return None

    ## Note: X,Y seem to be inverted so had to do s[1],s[0] instead of s[0],s[1]
    for s in shapeParamArray:
        annotationElements.append(
            {
                "fillColor": fillColor,
                "lineColor": lineColor,
                "lineWidth": lineWidth,
                "center": [s[1], s[0], 0],
                "radius": s[2],
                "group": "neuron",
                "type": shapeType,
            }
        )
    print(annotationElements)
    return annotationElements


def SimpleBlobDetector(in_file, threshold, max_sigma, outputBlobAnnotationFile):
    ## Fow now only implementing the hessian a that seemed to produce the best results, will eventually add functino to do all three
    #    inpImage = skimage.io.imread(in_file)
    inpImage = cv2.imread(in_file)  ## Super hacky.. need to figure out the weird color conversion issues
    image_gray = rgb2gray(inpImage)
    blob_color = "red"  ## TBD MAke it a parameter

    # blobs_log = blob_log(image_g  ray, max_sigma=30, num_sigma=10, threshold=.1)
    # # Compute radii in the 3rd column.
    # blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)

    # blobs_dog = blob_dog(image_gray, max_sigma=30, threshold=.1)
    # blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
    blobs_doh = blob_doh(image_gray, max_sigma=max_sigma, threshold=threshold)
    # print(blobs_doh)
    # im_input = skimage.io.imread(in_file)
    annotation_elements = convert_to_DSA_annotations(blobs_doh, "circle")
    print(annotation_elements)
    annotDoc = {
        "description": "Determinant of Hessian output from algorithm",
        "elements": annotation_elements,
        "name": "Hessian Results",
    }  ## TO DO add time stampt

    with open(outputBlobAnnotationFile, "w") as fp:
        json.dump(annotDoc, fp)


def main(args):
    SimpleBlobDetector(args.in_file, args.threshold, args.max_sigma, args.outputBlobAnnotationFile)


if __name__ == "__main__":
    main(CLIArgumentParser().parse_args())
