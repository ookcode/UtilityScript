#!/bin/python3
#coding:utf-8
import os
import sys
import subprocess
import re
import biplist
import shutil
###################################################
#
#	ipa重签名工具
#	Created by Vincent Yao on 17-07-10.
#
###################################################
def getWrapped(text, beginKey, endKey):
	match = re.findall('{}.*{}'.format(beginKey, endKey), text)
	wraplist = []
	for value in match:
		wraplist.append(value[len(beginKey) : -len(endKey)])
	return wraplist

def getCerContentByName(name):
	output = subprocess.getoutput("security find-certificate -c '{}' -p".format(name))
	content = "".join(output.split("\n")[1:-1])
	return content

def createEntitlementsFile(path, team_id, bundle_id):
	file_path = os.path.join(path, "Entitlements.plist")
	content = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
	"<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">"
	"<plist version=\"1.0\">"
	"<dict>"
		"<key>application-identifier</key>"
		"<string>" + team_id + "." + bundle_id + "</string>"
		"<key>com.apple.developer.team-identifier</key>"
		"<string>" + team_id + "</string>"
		"<key>get-task-allow</key>"
		"<false/>"
		"<key>keychain-access-groups</key>"
		"<array>"
			"<string>" + team_id + "." + bundle_id + "</string>"
		"</array>"
	"</dict>"
	"</plist>"
	)
	f = open(file_path, 'w')
	f.write(content)
	f.close()
	return file_path

def log(*params):
	print(*params)

def error(*params):
	log(*params)
	sys.exit()

def main():
	ipa = input("请拖入要重签名的.ipa：").strip()
	provision = input("请拖入对应的签名文件.mobileprovision：").strip()

	log("● 正在获取本地证书列表")
	output = subprocess.getoutput("security find-identity -v -p codesigning")
	wraplist = getWrapped(output, "\"", "\"")

	log("● 正在解析签名文件")
	output = subprocess.getoutput("security cms -D -i " + provision)
	output = output[output.find("<?xml"):]
	cer_content = getWrapped(output, "<data>", "</data>")[0]
	match_cer = None
	for name in wraplist:
		content = getCerContentByName(name)
		if cer_content == content:
			match_cer = name
			break

	if match_cer == None:
		error("× 没有安装该证书对应的签名文件")

	try:
		plist = biplist.readPlistFromString(bytes(output, "utf-8"))
		identify = plist['Entitlements']['application-identifier']
		pos = identify.find('.')
		provision_uuid = plist['UUID']
		provision_name = plist['Name']
		provision_team = identify[:pos]
		provision_id = identify[pos + 1:]
	except Exception as e:
		error("× 签名文件解析失败")


	log("● 正在解压.ipa")
	base_path = os.path.dirname(ipa)
	unzip_path = os.path.join(base_path, ".ipa_resign_temp")
	if os.path.exists(unzip_path) :
		shutil.rmtree(unzip_path, True)
	os.system("unzip -q " + ipa + " -d " + unzip_path)
	log("● 解压完成")
	# input("● ipa已经解压到.ipa_resign_temp目录，现在你可以随意修改包内的内容，修改完成后任意键继续")

	payload = os.path.join(unzip_path, "Payload")
	app_path = None
	for file in os.listdir(payload):
		if re.match(".*\.app", file):
			app_path = os.path.join(payload, file)
			break

	log("● 正在删除原始签名文件")
	sign_path = os.path.join(app_path, "_CodeSignature")
	if os.path.exists(sign_path) :
		shutil.rmtree(sign_path, True)

	log("● 正在复制新的签名文件")
	shutil.copyfile(provision, os.path.join(app_path, "embedded.mobileprovision"))

	log("● 正在修改包名")
	info_plist = os.path.join(app_path, "Info.plist")
	try:
		plist = biplist.readPlist(info_plist)
		plist["CFBundleIdentifier"] = provision_id
		biplist.writePlist(plist, info_plist)
	except Exception as e:
		error("× Info.plist解析失败", e)

	log("● 正在重签名")
	entitlements = createEntitlementsFile(unzip_path, provision_team, provision_id)
	os.system("/usr/bin/codesign -f -s \"{}\" --entitlements {} {}".format(match_cer, entitlements, app_path))
	# os.system("/usr/bin/codesign --verify " + app_path)
	# os.system("codesign -vv -d " + app_path)
	log("● 重签名成功")

	log("● 正在生成新的.ipa")
	resign_ipa = ipa[:-4] + "-resign.ipa"
	my_commands = "cd " + unzip_path
	my_commands = my_commands + ";chmod -R +x Payload"
	my_commands = my_commands + ";zip -qr " + resign_ipa + " Payload"
	os.system(my_commands)

	shutil.rmtree(unzip_path, True)
	os.system("open " + base_path)
	log("● 任务已完成")

if __name__ == '__main__':
	main()