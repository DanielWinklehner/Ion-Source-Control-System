#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import math
import time
import sys
import requests
import json
import re
import subprocess

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0



# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)


# Initialize library.
disp.begin()

# Get display width and height.
width = disp.width
height = disp.height

# Clear display.
disp.clear()
disp.display()

# Create image buffer.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (width, height))

# Load default font.
font = ImageFont.load_default()
#font = ImageFont.truetype("/var/www/html/Ion-Source-Control-System/Python/server/Consolas.ttf", 16, encoding="unic")

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as this python script!
# Some nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('OpenSans-Bold.ttf', 16, encoding="utf-32")

# Create drawing object.
draw = ImageDraw.Draw(image)



url = "http://127.0.0.1/"
def get_server_status():
	try:
		r = requests.get(url)
		return r.status_code == 200
	except requests.exceptions.ConnectionError:
		return False
	except Exception:
		return False

def get_number_of_arduinos():
	r = requests.get(url + "arduino/all")
	response = r.text

	if r.status_code == 200:
		return len(json.loads(response))
	
	return 0

def get_pi_ip():
	proc = subprocess.Popen('ifconfig | grep inet', stdout=subprocess.PIPE, shell=True)
	output = proc.stdout.read().strip()
	match_object = re.match("inet addr:([0-9]+.[0-9]+.[0-9]+.[0-9]+)", output)
	if match_object:
		return match_object.group(1) 
	
	return  "Off"


# Define text and get total width.

y_s = [0, 16, 32, 48]



'''
Server IP
"=> 127.0.0.1" OR "=> OFF"

"Initializing..." while server is starting.
'''

while True:

	texts = ["Server Status:", "", "Arduinos Found:", ""]
	
	if get_server_status():
		texts[1] = "=> {}".format(get_pi_ip())
	else:
		texts[1] = "=> Not Running"
	
	if get_server_status():
		texts[3] = "=> {}".format(get_number_of_arduinos())
	else:
		del texts[-1]
		del texts[-1]
	
	

	for text, y in zip(texts, y_s):
		maxwidth, unused = draw.textsize(text, font=font)

		x = 0

		# Draw text.
		draw.text((x, y), text, font=font, fill=255)

		# Draw the image buffer.
		disp.image(image)
		disp.display()
	
	# Clear image buffer by drawing a black filled box.
	draw.rectangle((0, 18, width, 36), outline=0, fill=0)
	draw.rectangle((0, 52, width, 65), outline=0, fill=0)
	
	
	time.sleep(1)

