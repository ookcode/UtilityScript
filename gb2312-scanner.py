#!/bin/python3
#coding:utf-8
###################################################
#
# scan a directory, find gb2312 file and convert to utf-8 file
#
# Created by Vincent on 16-08-08
#
###################################################

import os,sys
import codecs

def get_content(file_path, encoding):
	try:
		file = codecs.open(file_path, 'r', encoding)
		content = file.read()
		success = True
	except Exception as e:
		content = ""
		success = False
	finally:
		file.close()
	return success, content

def convert_file(file_path):
	#try utf-8 and gb2312
	success, content = get_content(file_path, 'utf-8')
	if success:
		#print(file_path, "utf-8", "skip")
		return
	success, content = get_content(file_path, 'gb2312')
	if success:
		print(file_path, "gb2312", "converted")
	else:
		print(file_path, "unknow", "skip")
		return

	# do convert
	try:
		file = codecs.open(file_path, 'w', 'utf-8')
		file.write(content)
	except Exception as e:
		print('error', e)
	finally:
		file.close()
	
def main():
	script_lua = input("please input scriptlua dir path:")
	script_lua = script_lua.strip()
	#scan files
	for root, dirs, files in os.walk(script_lua):
		for file in files:
			extend = os.path.splitext(file)[1]
			#only .lua file
			if extend == ".lua":
				file_path = os.path.join(root, file)
				convert_file(file_path)

if __name__ == '__main__':
	main()