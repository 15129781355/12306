
#python版本3.4

import hashlib
import http.client
import urllib.request
import urllib
import json
import base64
import user
import copy

def md5str(str): #md5加密字符串
		m=hashlib.md5(str.encode(encoding = "utf-8"))
		return m.hexdigest()
		
def md5(byte): #md5加密byte
		return hashlib.md5(byte).hexdigest()
		
class DamatuApi():
	
	ID = '55075'
	KEY = '0f9e3d2214493f09a5466e9ad367c61b'
	HOST = 'http://api.dama2.com:7766/app/'
	
	
	def __init__(self,username,password):
		self.username=username
		self.password=password
		
	def getSign(self,param=b''):
		return (md5(bytes(self.KEY, encoding = "utf8") + bytes(self.username, encoding = "utf8") + param))[:8]
		
	def getPwd(self):
		return md5str(self.KEY +md5str(md5str(self.username) + md5str(self.password)))
		
	def post(self,path,params={}):
		data = urllib.parse.urlencode(params).encode('utf-8')
		url = self.HOST + path
		response = urllib.request.Request(url,data)
		return urllib.request.urlopen(response).read()
	
	#查询余额 return 是正数为余额 如果为负数 则为错误码
	def getBalance(self):
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'sign':dmt.getSign()
		}
		res = self.post('d2Balance',data)
		res = str(res, encoding = "utf-8")
		jres = json.loads(res)
		if jres['ret'] == 0:
			return jres['balance']
		else:
			return jres['ret']
    
	#上传验证码 参数filePath 验证码图片路径 如d:/1.jpg type是类型，查看http://wiki.dama2.com/index.php?n=ApiDoc.Pricedesc  return 是答案为成功 如果为负数 则为错误码
	def decode(self,filePath,type):
		f=open(filePath,'rb')
		fdata=f.read()
		filedata=base64.b64encode(fdata)
		f.close()
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'type':type,
			'fileDataBase64':filedata,
			'sign':dmt.getSign(fdata)
		}		
		res = self.post('d2File',data)
		res = str(res, encoding = "utf-8")
		jres = json.loads(res)
		if jres['ret'] == 0:
			#注意这个json里面有ret，id，result，cookie，根据自己的需要获取
			return(jres['result'])
		else:
			return jres['ret']
		
	#url地址打码 参数 url地址  type是类型(类型查看http://wiki.dama2.com/index.php?n=ApiDoc.Pricedesc) return 是答案为成功 如果为负数 则为错误码
	def decodeUrl(self,url,type):
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'type':type,
			'url':urllib.parse.quote(url),
			'sign':dmt.getSign(url.encode(encoding = "utf-8"))
		}
		res = self.post('d2Url',data)
		res = str(res, encoding = "utf-8")
		jres = json.loads(res)
		if jres['ret'] == 0:
			#注意这个json里面有ret，id，result，cookie，根据自己的需要获取
			return(jres['result'])
		else:
			return jres['ret']
	
	#报错 参数id(string类型)由上传打码函数的结果获得 return 0为成功 其他见错误码
	def reportError(self,id):
		#f=open('0349.bmp','rb')
		#fdata=f.read()
		#print(md5(fdata))
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'id':id,
			'sign':dmt.getSign(id.encode(encoding = "utf-8"))
		}	
		res = self.post('d2ReportError',data)
		res = str(res, encoding = "utf-8")
		jres = json.loads(res)
		return jres['ret']


dmt=DamatuApi(user.use,user.password)

def get_code():
	list1 = dmt.decode('code.png',287).replace('|',',').split(',')
	'''第一种用pop insert的方法'''
	# tem_list = copy.deepcopy(list1)
	# num=1
	# for i in list1[1::2]:
	# 	i = str(int(i) - 30)
	# 	tem_list.pop(num)
	# 	tem_list.insert(num,i)
	# 	num+=2
	# print(list1)
	# print(tem_list)
	'''第二种用num索引返回值修改方法'''
	# num1 = 0
	# for i in list1[1::2]:
	# 	list1[num1 + 1] = str(int(i) - 30)
	# 	num1+=2
	# print(list1)
	'''第三种定义新列表append方法'''
	new_list=[]
	num=0
	for i in list1:
		if list1.index(i)%2==0:
			new_list.append(i)
		else:
			new_list.append(str(int(i)-30))
	return ','.join(new_list)

print(get_code())

