import pandas as pd
import cv2
import numpy as np
import serial
import time
from PIL import Image
from pytesseract import pytesseract

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened
    
def name_plate(image):
    image_crop = image[150:300, 0:300]
    gray_img = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(gray_img, 115, 255, cv2.THRESH_BINARY)
    
    #image_rot = cv2.rotate(image_crop) 
    
    return blackAndWhiteImage
    
def onlyTitle(string):
    i = 0
    x=""
    flag = 0
    alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    wanted_char = []
    while i < len(string):
    #walks through string and appends the title
        if string[i] not in alphabet:
            betabet = string[i]
            if (betabet == (' '))and (flag == 0):
                flag = 1                
            elif betabet == (' ') and flag == 1:               
                string = x.join(wanted_char)
                return string
            elif betabet == '\n':                
                string = x.join(wanted_char)
                return string               
            else:
                flag = 0
        else:
            wanted_char.append (string[i])
 
       #ends loop if two or more consecutive spaces are detected
        
        i+=1
    string = x.join(wanted_char)
    return string    


og_image = cv2.imread("temp_image.jpg")
image_rot = cv2.rotate(og_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

image = image_rot
image_rot = unsharp_mask(image)
cv2.imwrite('sharpened.jpg', image_rot)


name_plate = name_plate(image_rot)

cv2.imshow("56",name_plate)



text = pytesseract.image_to_string(name_plate)

print(text)