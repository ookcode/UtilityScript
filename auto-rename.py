import os,sys
import re
root_path = os.path.dirname(os.path.realpath(sys.argv[0]))
param_path = sys.argv[1]
input_re = input("请输入截取正则：")
src_list = []
print("匹配到以下文件：")
for file in os.listdir(param_path):
	result = re.search(input_re, file)
	if not result:
		continue
	key = result.group()
	src_list.append([key, file])
	print(key, file)

input_format = input("请输入输出格式({}代表截取字符)：")
print("自动重命名预览：")
rename_dic = {}
for index in src_list:
	key = index[0]
	file = index[1]
	new_file = input_format.format(key)
	src = os.path.join(param_path, file)
	dest = os.path.join(param_path, new_file)
	rename_dic[src] = dest
	print(new_file)

confirm = input("是否确认重命名(y/n)：")
if confirm == "y":
	for key in rename_dic.keys():
		os.rename(key, rename_dic[key])
	print("操作完成！")
else:
	print("操作取消！")