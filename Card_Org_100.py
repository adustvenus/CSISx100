from __future__ import print_function
from google.cloud import vision
import pandas as pd
import cv2
import numpy as np
import serial
import time
from PIL import Image
from pytesseract import pytesseract
import enchant
import json
import io
import csv
import os

quit_var = False
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\Wiz\Downloads\csis-365706-3da34eace197.json"
#Define path to tessaract.exe
path_to_tesseract = r'C:\Users\Wiz\Documents\MTG\Tesseract\Tesseract-OCR\tesseract.exe'

#Define path to image
path_to_image = r'C:\Users\Wiz\Documents\MTG\tess.jpg'

#Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract

#Open image with PIL
#img = Image.open(path_to_image)

def insert_data(text):
    #print("Insert_data_trigger")
    j = str(text)
    f = open("TSR.json", encoding="UTF8")
    data = json.load(f)
    ticker = 0
    found_card = False
    for i in data['data']['cards']:
        ticker += 1
        name = i['name']
        if (name == j):
            found_card = True
            mana = i['manaValue']
            type_ = i['originalType']
            with open ('data_file.csv', 'a', newline='') as f:
                temp_list = [name, mana, type_]
                writer = csv.writer(f)
                writer.writerow(temp_list)
                print("Card Added!")
                break
    if found_card == False:
        print("This card did not properly scan, please enter\nmanually or try again after completion.")
       

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    #print("Image_Sharpened")
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
    

def inverted(image):
    #print("Inverted_Active")
    image_crop = image[400:500, 275:375]   #[400:500, 300:400]
    gray_img = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(gray_img, 125, 255, cv2.THRESH_BINARY)
    #invert_img = cv2.bitwise_not(blackAndWhiteImage)    
    return blackAndWhiteImage

def name_plate(image):
    #print("Name_Plate_active")
    #image = unsharp_mask(image)
    image_crop = image[100:200, 0:300]
    gray_img = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(gray_img, 115, 255, cv2.THRESH_BINARY)
    #image_rot = cv2.rotate(image_crop) 
    
    return blackAndWhiteImage
    
ser = serial.Serial('COM6')
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
time.sleep(3)

print("Welcome to the Card Reader 100!\nWhat would you like to do?\n===================\n")
print("1 - Scan Deck of Magic the Gathering Cards")
print("2 - Manual Input for Magic the Gathering Cards")
selection = input(">> ")
while quit_var == False:
    if selection == "1":
        scan_num = input("How many cards would you like scan?\n>>")
        cards_left = int(scan_num)
        est_time = int(scan_num) * 15
        if est_time > 60:
            est_time = round(est_time/60, 1)
            print("Estimated time to print is ", est_time, "Minutes!")
        else:
            print("Estimated time to print is ", est_time, "Seconds!")
            
        ser.write(b'o')
        cam = cv2.VideoCapture(1)
        time.sleep(19)
        if not cam.isOpened():
            raise IOError("Cannot open webcam :(")
            print("Please turn on camera and try again!")
            exit()
        while (cards_left > 0):
            result, og_image = cam.read()
            
            cv2.imwrite("temp_image.jpg", og_image)
            og_image = cv2.imread("temp_image.jpg")
            image_rot = cv2.rotate(og_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            converted_image = inverted(image_rot)
            print("trigger")
            name = name_plate(image_rot)
            cv2.imwrite("google.jpg", name)
            ####################################GOOGLE###########
            
            try:
                #print("looked for text")
                client = vision.ImageAnnotatorClient()
                
                with io.open(r'C:\Users\Wiz\Documents\MTG\google.jpg', 'rb') as image_file:
                    content = image_file.read()
                   
                image_google = vision.Image(content=content)
                
                response = client.text_detection(image = image_google)
                texts = response.text_annotations[0].description
                insert_data(texts)
            except:
                print("Card Title Search Failed, Please try card again or enter manually :)")
                
            #print('#########')
            #print(texts[])
                          
            
            cv2.imwrite(str(cards_left)+".jpg", converted_image)
            
            TSR = cv2.imread("TSR.jpg")
           
            #logo = cv2.resize(logo, (20,20))
            logo = cv2.cvtColor(TSR, cv2.COLOR_BGR2GRAY)
            #logo = cv2.GaussianBlur(logo, (1,1), 3)
            #logo = cv2.bitwise_not(logo)
            cv2.imwrite("TSR2.jpg", logo)
            
            set_check = cv2.matchTemplate(converted_image, logo, cv2.TM_SQDIFF_NORMED)
            minval, maxval, minloc, maxloc = cv2.minMaxLoc(set_check)

            if minval < .2:
                print("Set Detected")
            else:
                print("Did Not Read Set")


            cards_left -= 1
            print(cards_left, " Cards left.")
            if cards_left != 1:
                time.sleep(15)
            
        cam.release()
        ser.write(b'q')
        
        quit_var = True


    elif selection == '2':
        print("======================")
        print("Manual Selection Mode:")
        print("Please input Name of card and set the card is from:")
        name = input("Name>> ")
        printing = input("Set>> ")
        
        insert_data(name)
        
        print("Would you like to add another?")
        quit_check = input('y/n >> ')
        if quit_check == ('n' or 'N'):
            quit_var = True
        