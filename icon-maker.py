#!/bin/python2
#coding:utf-8
###################################################
#
# provide one image, generation all sizes of icons for iOS and Android
#
# Created by Vincent on 16-1-10.
#
###################################################
import os,sys
from PIL import Image

def make_ios_icons(imagePath):
	iosSavePath = os.path.join(os.path.dirname(imagePath),"iOS_Icons")
	if not os.path.exists(iosSavePath):
		os.makedirs(iosSavePath)
	image = Image.open(imagePath)
	iosIconDic = {
		"Icon-57.png" : 57,			#iPhone App Icon for iOS 5,6
		"Icon-57@2x.png" : 114,		#iPhone App Icon for iOS 5,6
		"Icon-60@2x.png" : 120,		#iPhone App Icon for iOS 7+
		"Icon-60@3x.png" : 180,		#iPhone App Icon for iPhone6/6s Plus
		"Icon-72.png" : 72,			#iPad App Icon for iOS 5,6
		"Icon-72@2x.png" : 144,		#iPad App Icon for iOS 5,6
		"Icon-76.png" : 76,			#iPad App Icon for 7+
		"Icon-76@2x.png" : 152,		#iPad App Icon for 7+
		"Icon-83.5@2x.png" : 167,	#iPad App Icon for iPad Pro
	}
	for key in iosIconDic:
		size = iosIconDic[key]
		newImage = image.resize((size,size), Image.ANTIALIAS)
		newImage.save(os.path.join(iosSavePath,key))

def make_android_icons(imagePath):
	androidSavePath = os.path.join(os.path.dirname(imagePath),"android_Icons")
	if not os.path.exists(androidSavePath):
		os.makedirs(androidSavePath)
	image = Image.open(imagePath)
	androidIconDic = {
		"drawable-mdpi" : 48,
		"drawable-hdpi" : 72,
		"drawable-xhdpi" : 96,
		"drawable-xxhdpi" : 144,
		"drawable-xxxhdpi" : 192,
	}
	for key in androidIconDic:
		size = androidIconDic[key]
		path = os.path.join(androidSavePath,key)
		if not os.path.exists(path) :
			os.makedirs(path)
		newImage = image.resize((size,size), Image.ANTIALIAS)
		newImage.save(os.path.join(path,"icon.png"))

def main():
	imagePath = raw_input("please drag in a image:")
	imagePath = imagePath.strip()	#remove the space
	mode = raw_input("target platform (iOS/android) : ")
	mode = mode.lower()
	if mode == "ios":
		make_ios_icons(imagePath)
	elif mode == "android":
		make_android_icons(imagePath)
	else:
		print "target platform input error"
		os.exit()

if __name__ == '__main__':
	main()