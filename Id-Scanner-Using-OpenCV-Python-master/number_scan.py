# USAGE
#  python number_scan.py --image images/morphi.jpg

# import the necessary packages
from typing import Optional, Match

from fpt import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils

from PIL import Image
import PIL.Image

from pytesseract import image_to_string
import pytesseract
import re

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument( "-i", "--image", required=True,
                 help="Path to the image to be scanned" )
args = vars( ap.parse_args() )

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
image = cv2.imread( args["image"] )
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize( image, height=500 )

# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
gray = cv2.GaussianBlur( gray, (5, 5), 0 )
edged = cv2.Canny( gray, 75, 200 )

# show the original image and the edge detected image
print( "STEP 1: Edge Detection" )
cv2.imshow("Original Image", image)
cv2.imshow("Edged", edged)
cv2.waitKey( 0 )
cv2.destroyAllWindows()

# find the contours in the edged image, keeping only the
# largest ones, and initialize the screen contour
cnts = cv2.findContours( edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE )
cnts = imutils.grab_contours( cnts )
cnts = sorted( cnts, key=cv2.contourArea, reverse=True )[:5]

# loop over the contours
for c in cnts:
    # approximate the contour
    peri = cv2.arcLength( c, True )
    approx = cv2.approxPolyDP( c, 0.02 * peri, True )

    # if our approximated contour has four points, then we
    # can assume that we have found our screen
    if len( approx ) == 4:
        screenCnt = approx
        break

# show the contour (outline) of the piece of paper
print( "STEP 2: Find contours of paper" )
cv2.drawContours( image, [screenCnt], -1, (0, 255, 0), 2 )
cv2.imshow("Outline", image)
cv2.waitKey( 0 )
cv2.destroyAllWindows()

# apply the four point transform to obtain a top-down
# view of the original image
warped = four_point_transform( orig, screenCnt.reshape( 4, 2 ) * ratio )

# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
warped = cv2.cvtColor( warped, cv2.COLOR_BGR2GRAY )
T = threshold_local( warped, 11, offset=10, method="gaussian" )
warped = (warped > T).astype( "uint8" ) * 255

# show the original and scanned images
print( "STEP 3: Apply perspective transform" )
# cv2.imshow("Original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned", imutils.resize(warped, height = 650))
# size(warped, height = 650))
cv2.waitKey( 0 )

imS = cv2.resize( warped, (720, 520) )
cv2.imshow( "output", imS )
cv2.imwrite( 'out/' + 'Output_Image.PNG', imS )
cv2.waitKey( 0 )

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PREFIX = 'C:/Program Files /Tesseract-OCR'
output = pytesseract.image_to_string( PIL.Image.open( 'out/' + 'Output_Image.PNG' ).convert( "RGB" ), lang='eng' )

# print( output )

f = open( 'nums.json', 'w' )
f.write( output )
f.close()

import re

#find the line with "Name:"
searchStr = re.search( r'Name: ((.*)*)', output, re.M | re.I )

#store the name in names
if searchStr:
    names : str = searchStr.group(1)
    # print ("searchObj.group() : ", searchObj.group())
    # print ("searchObj.group(1) : ", names )
else:
    print( "Can't detect!!" )

#find the id number
# nums = re.findall( r'[\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', output)
nums = re.findall(r'[0-9][0-9]{8,15}[0-9]', output)


# print(names)
# print(nums)

#open ids.json
F = open( 'ids.json', 'a+' )

#write Name to ids.json
F.write( '\nNAME :-> ' + names + '\t' )
print('\nInformations saved in ids.json-')
print( 'NAME :-> ' + names )

#write Id number to ids.json
for num in nums:
    F.write( '\nId No. :-> ' + num + '\n')
    print('ID No. :-> ' + num)
