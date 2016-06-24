#!/bin/python2
#coding:utf-8
###################################################
#
# Provide your mobileprovision file, resign the ipa
#
# Created by Vincent on 16-1-11.
#
###################################################
import sys,os
import string
import commands
import shutil
########################################################
#
#	get the string value in plist
#
########################################################
def getValueWithKeyInPlist(key,plist_str):
	p1 = plist_str.find(key)
	if p1 == -1 :
		print "Error : " + key + " not found"
		sys.exit();
	p1 = plist_str.find("<string>",p1) + len("<string>")
	p2 = plist_str.find("</string>",p1)
	return plist_str[p1:p2]

########################################################
#
#	get getAppID in .mobileprovision file
#
########################################################
def getAppID(mobileprovision):
	status, output = commands.getstatusoutput("security cms -D -i " + mobileprovision)
	appID = getValueWithKeyInPlist("application-identifier",output)
	#Prefix = AppID[:AppID.find(".")]
	#BundleID = AppID[AppID.find(".") + 1:]
	return appID

########################################################
#
#	get cer list in toolchain
#
########################################################
def getAndShowCerList():
	status, output = commands.getstatusoutput("security find-identity -v -p codesigning")
	arr = output.split('\"')
	if len(arr) == 1 :
		print "Error : .cer not found in toolchain"
		sys.exit()
	cers = []
	for i in range(1, len(arr), 2):
		cers.append(arr[i])
		print str(len(cers)) + ": " + arr[i]
	return cers

########################################################
#
#	create entitlements file
#
########################################################
def createEntitlementsFile(basepath, appID):
	prefix = appID[:appID.find(".")]
	filePath = os.path.join(basepath,"Entitlements.plist")
	content = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
	"<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">"
	"<plist version=\"1.0\">"
	"<dict>"
		"<key>application-identifier</key>"
		"<string>" + appID + "</string>"
		"<key>com.apple.developer.team-identifier</key>"
		"<string>" + prefix + "</string>"
		"<key>get-task-allow</key>"
		"<false/>"
		"<key>keychain-access-groups</key>"
		"<array>"
			"<string>" + appID + "</string>"
		"</array>"
	"</dict>"
	"</plist>"
	)
	file_object = open(filePath, 'w')
	file_object.write(content)
	file_object.close()
	return filePath

def main():
	#get the necessary file
	ipa = raw_input("please drag in .ipa : ")
	mobileprovision = raw_input("please drag in .mobileprovision : ")

	ipa = ipa.strip() #remove space
	mobileprovision = mobileprovision.strip() #remove space
	
	#get BundleID in .mobileprovision file
	appID = getAppID(mobileprovision)
	print "the appID in mobileprovision is " + appID

	#select a cer
	cers = getAndShowCerList()
	selectCer = ""
	while True:
		inputstr = raw_input("please enter the cer number : ")
		number = 0;
		try:
			number = int(inputstr)
		except:
			print "input error"

		if number > 0 and number <= len(cers):
			selectCer = cers[number - 1]
			break;
		else:
			print "Error : no this number"

	print "you select " + selectCer

	#unzip ipa
	print "step1 : unzip .ipa"
	basePath = os.path.dirname(ipa)
	unzipPath = os.path.join(basePath, ".ipa_resign_temp")
	if os.path.exists(unzipPath) :
		shutil.rmtree(unzipPath,True)
	status, output = commands.getstatusoutput("unzip " + ipa + " -d " + unzipPath)
	print "unzip successfully"

	#get .app in ipa
	payloadPath = os.path.join(unzipPath, "Payload")
	for li in os.listdir(payloadPath):
		if not li == ".DS_Store":
			appDir = os.path.join(payloadPath,li)
			break

	#delete sign file
	print "step2 : delete _CodeSignature"
	signDir = os.path.join(appDir,"_CodeSignature")
	if os.path.exists(signDir) :
		shutil.rmtree(signDir,True)

	#copy .mobileprovision into package
	print "step3 : copy .mobileprovision"
	shutil.copyfile(mobileprovision, os.path.join(appDir, "embedded.mobileprovision"))

	#create entitlements file
	print "step4 : create entitlements file"
	entitlements = createEntitlementsFile(unzipPath, appID)

	#modify bundleID in info.plist
	print "step5 : modify bundleID in info.plist"
	bundleID = appID[appID.find(".") + 1:]
	infoPlist = os.path.join(appDir, "Info.plist")
	infoPlist = infoPlist.replace(" ","\ ")
	os.system("echo " + bundleID + " | pbcopy")
	os.system("open -a xcode " + infoPlist)
	print "plist file has been opened"
	print "please overwrite '" + bundleID + "' for key 'Bundle identifier'"
	print "'" + bundleID +"' has copied into you clipboard"
	raw_input("if you finish, any key to continue...")

	#do resign
	appDir = appDir.replace(" ","\ ")
	print "step6 : resign"
	my_commands = "/usr/bin/codesign -f -s \"" + selectCer +"\" --entitlements " + entitlements + " " + appDir
	os.system(my_commands)
	#os.system("/usr/bin/codesign --verify " + appDir)
	#os.system("codesign -vv -d " + appDir)
	print 'signature replace successfully!'

	#rezip .ipa
	print "step7 : zip .ipa"
	resignIpa = ipa[:-4] + "-resign.ipa"
	my_commands = "cd " + unzipPath
	my_commands = my_commands + ";chmod -R +x Payload"
	my_commands = my_commands + ";zip -qr " + resignIpa + " Payload"
	status, output = commands.getstatusoutput(my_commands)

	#clean
	shutil.rmtree(unzipPath,True)

	print "all done!"

if __name__ == '__main__':
	main()

