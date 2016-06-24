#!/usr/bin python3
#coding:utf-8
###################################################
#
# encrypt or decrypt file with xor operator
#
# Created by Vincent on 16-4-29.
#
###################################################
import os
import sys
import struct
SIGN_KEY = "xors"
SIGN_LEN = len(SIGN_KEY)
KEY = "vincent"
KEY_LEN = len(KEY)

def isEncrypt(file_path):
	size = os.path.getsize(file_path)
	file = open(file_path, "rb")
	if size < SIGN_LEN:
		print("file size is too small")
		sys.exit()
	key = struct.unpack('c' * SIGN_LEN,file.read(SIGN_LEN))
	file.close()
	for i in range(0, SIGN_LEN):
		if ord(key[i]) != ord(SIGN_KEY[i]):
			return False
	return True

def xor_operator(file_path, isEncrypt):
	if isEncrypt :
		print("do encrypt " + file_path)
		offset = 0
	else:
		print("do decrypt " + file_path)
		offset = SIGN_LEN

	file = open(file_path, "rb")
	file.seek(offset, 0)
	file.tell()
	content = file.read()
	file.close()

	new_file = open(file_path, "wb")

	if isEncrypt :
		for i in range(0, SIGN_LEN):
			new_file.write(struct.pack('B',ord(SIGN_KEY[i])))

	index = 0
	for i in range(0, len(content)):
		doxor = content[i] ^ ord(KEY[index % KEY_LEN])
		new_file.write(struct.pack('B',doxor))
		index = index + 1

	new_file.close()

def main():
	file_path = input("please drag in a file: ")
	file_path = file_path.strip()	#remove the space

	if isEncrypt(file_path):
		xor_operator(file_path, False)
	else:
		xor_operator(file_path, True)

if __name__ == '__main__':
	main()