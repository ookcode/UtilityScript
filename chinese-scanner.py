#!/bin/python3
#coding:utf-8
###################################################
#
# 扫描一个目录下的所有文件，找到其中的非注释中文
#
# Created by Vincent on 17-06-17
#
###################################################

import os,sys
if not sys.version_info[0] == 3:
	raise("当前脚本只能在python3.x下运行，请更换您的python版本！")

FILTER_EXTEND = [".lua"] # 过滤后缀名
MULTI_SIGN_BEGIN = ['-', '-', '[', '['] # 多行注释开始符号
MULTI_SIGN_END = [']', ']'] # 多行注释结束符号
SINGLE_SIGN = ['-', '-'] # 单行注释符号

# FILTER_EXTEND = [".c", ".cpp"] # 过滤后缀名
# MULTI_SIGN_BEGIN = ['/', '*'] # 多行注释开始符号
# MULTI_SIGN_END = ['*', '/'] # 多行注释结束符号
# SINGLE_SIGN = ['/', '/'] # 单行注释符号

class Scanner():
	def __init__(self):
		self._clear()

	def _clear(self):
		self.beginSign = MULTI_SIGN_BEGIN[:]
		self.endSign = MULTI_SIGN_END[:]
		self.singleSign = SINGLE_SIGN[:]

	def _checkBeginSign(self, word):
		if word == self.beginSign[0]:
			self.beginSign.pop(0)
		else:
			self.beginSign = MULTI_SIGN_BEGIN[:]

	def _checkEndSign(self, word):
		if word == self.endSign[0]:
			self.endSign.pop(0)
		else:
			self.endSign = MULTI_SIGN_END[:]

	def _checkSingleSign(self, word):
		if word == self.singleSign[0]:
			self.singleSign.pop(0)
		else:
			self.singleSign = SINGLE_SIGN[:]

	def _readFile(self, file_path):
		if not os.path.isfile(file_path):
			raise("_ERROR:", file_path, "NOT EXISTS")
			return
		try:
			f = open(file_path, 'r', encoding='utf-8')
			content = f.readlines()
			f.close()
		except Exception as e:
			print("\n_WARNING:", file_path, "NOT UTF-8")
			try:
				f = open(file_path, 'r', encoding='gb2312')
				content = f.readlines()
				f.close()
			except Exception as e:
				raise("_ERROR:", file_path, "UNKNOW ENCODE")
		return content

	def scan(self, file_path):
		content = self._readFile(file_path)
		isPrintName = False
		diffLen = len(MULTI_SIGN_BEGIN) - len(SINGLE_SIGN)

		for index, line in enumerate(content):
			for word in line:
				# 匹配到多行注释符
				if len(self.beginSign) == 0:
					# 匹配结束符
					if len(self.endSign) == 0:
						self._clear()
					else:
						self._checkEndSign(word)

				# 匹配到单行注释符
				elif len(self.singleSign) == 0:
					# 判断多行注释符是否匹配中
					if len(self.beginSign) <= diffLen:
						# 继续匹配多行注释符号
						self._checkBeginSign(word)
					else:
						# 不是多行注释，跳过该行
						self._clear()
						break
				else:
					self._checkSingleSign(word)
					self._checkBeginSign(word)

					# 中文字符判断
					if '\u4e00' <= word <= '\u9fa5':
						if isPrintName == False:
							isPrintName = True
							print("\n" + file_path)
						print("line {} {}".format(index + 1, line.strip()))
						self._clear()
						break

def main():
	scanner = Scanner()
	script_lua = input("请拖入一个目录：")
	script_lua = script_lua.strip()
	for root, dirs, files in os.walk(os.path.expanduser(script_lua)):
		for file in files:
			extend = os.path.splitext(file)[1]
			if extend in FILTER_EXTEND:
				file_path = os.path.join(root, file)
				scanner.scan(file_path)

if __name__ == '__main__':
	main()