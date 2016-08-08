#!/usr/bin/python3
#coding=utf-8
############################################################
#
# 提供搜索和下载功能的轻小说下载器，资源来自http://xs.dmzj.com/
# 需要安装bs4库：sudo pip3 install bs4
# 本脚本仅在*nix系统上验证通过，并未测试windows的兼容性
#
# Created by Vincent on 16-7-3.
#
############################################################
import sys
if not sys.version_info[0] == 3:
	print("当前脚本只能在python3.x下运行，请更换您的python版本！")
	sys.exit()
	
import os
import urllib.request
import threading
import re
import json
import platform
from bs4 import BeautifulSoup

ROOT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

class DMZJ:
	def __init__(self):
		self.downloadThreads = []
		self.baseUrl = "http://xs.dmzj.com"
		self.html = ""
		self.novelName = ""
		self.novelId = None

	#请求HTML页面
	def _getHtml(self):
		url = self.baseUrl + "/" + str(self.novelId) + "/index.shtml"
		request = urllib.request.Request(url)
		response = urllib.request.build_opener().open(request)
		return response.read().decode('utf-8')

	#分析标题和下载链接
	def _analysis(self):
		soup = BeautifulSoup(self.html)
		for chapter in soup.find_all(class_="download_rtx"):
			title = list(chapter.find('li').strings)[1]
			#不下载短篇和特典等分卷
			if not re.match("第\w*卷", title):
				print(title,"pass")
				continue
			#替换不符合目录命名规范的特殊字符
			if 'Windows' in platform.system():
				title = re.sub('[\/:*?"<>|]', ' ', title)
			else:
				title = title.replace('/','\\')
			url = chapter.find(class_="download_boxbg").find('a')["href"]
			print(title)
			t = threading.Thread(target=self._download,args=(title,self.baseUrl + url))
			self.downloadThreads.append(t)

	#执行下载
	def _download(self, title, url):
		'''
		a:已经下载的数据块
		b:数据块的大小
		c:远程文件的大小
		'''
		def schedule(a, b, c):
			per = a * b / c
			if per > 1 :
				print(title,"下载完成")

		save_path = os.path.join(ROOT_PATH, self.novelName, title + ".txt")
		urllib.request.urlretrieve(url, save_path, schedule)

	#执行搜索
	def _searchBook(self, searchName):
		'''
		"author":
	    "image_url":
	    "lnovel_name":
	    "last_chapter_name":
	    "lnovel_url":
	    "last_chapter_url":
	    "full_name":
	    "fullc_name":
	    "types":
	    "status":
	    "description":
	    '''
		url = "http://s.acg.178.com/lnovelsum/search.php?s=" + urllib.request.quote(searchName)
		request = urllib.request.Request(url)
		response = urllib.request.build_opener().open(request).read().decode('utf-8')
		prefix = "var g_search_data = "
		data = json.loads(response[len(prefix):-1])			
		for index, book in enumerate(data):
			print(index, "《" + book['full_name'] + "》")
			print("类型:", book['types'])
			print("作者:", book['author'])
		return data

	def clean(self):
		self.downloadThreads = []
		self.html = ""
		self.novelName = ""
		self.novelId = None

	def start(self):
		self.clean()
		searchName = input("请输入轻小说名称(输入n退出):")
		if searchName == "n":
			print("谢谢使用！")
			sys.exit()
		print("正在搜索...\n" + "-" * 40)
		data = self._searchBook(searchName)
		if len(data) == 0 :
			print("呜呜，没有搜索到相关轻小说，建议缩短关键词进行搜索，记得考虑译名方式和繁简体哦！\n" + "-" * 40)
			self.start()
			return
		print("-" * 40)
		while(True):
			if len(data) == 1:
				number = 0
			else:
				number = int(input("请输入序号:"))
			if 0 <= number < len(data):
				self.novelName = data[number]['lnovel_name']
				print("您选择了","《" + data[number]['full_name'] + "》")
				mixUrl = data[number]['lnovel_url']
				beginPos = mixUrl.find('../') + 3
				endPos = mixUrl.find('/',beginPos)
				self.novelId = int(mixUrl[beginPos : endPos])
				break
			else:
				print("输入有误！")

		while(True):
			select = input("是否开始下载(y/n):")
			if select == "y":
				print("-" * 40,"\n正在获取分卷列表...")
				self.html = self._getHtml()
				self._analysis()
				if len(self.downloadThreads) == 0:
					print("呜呜，这本小说被魔女干掉了。\n" + "-" * 40)
					self.start()
					return
				print("-" * 40,"\n开始下载...")
				dirPath = os.path.join(ROOT_PATH, self.novelName)
				if not os.path.exists(dirPath):
					os.mkdir(dirPath)
				for t in self.downloadThreads:
					t.start()
				break
			elif select == "n":
				print("您取消了下载！\n" + "-" * 40)
				self.start()
				return
			else:
				print("输入有误！")

def main():
	downloader = DMZJ()
	downloader.start()

if __name__ == '__main__':
	main()
