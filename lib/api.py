import sys
import json
import uuid
import http.client
import time
import os.path
import datetime
import gzip

class API(object):
	def __init__(self,api="ghr.wotvffbe.com",print_req=False, debug=False):
		object.__init__(self)
		self.api=api
		self.print_req=print_req
		self.debug=debug
		if debug:
			os.makedirs('debug',exist_ok=True)

	def get(self,string):
		return getattr(self, string,False)

	def pass_enviroment(self, version):
		return self.api_request("pass/environment", {"ver":version})["environments"]["wotvffbe"]

	####	CONNECTION ###########################################################
	def api_request(self,url,body={},request='POST',raw=False,retry=False):
		if url[0]!= '/':
			url='/%s'%url

		res_body=self.api_connect(url,body,request)
		
		try:
			ret = res_body['body']
		except Exception as e:
			print('error: failed to retrieve %s'%url)
			print(e)
			print(res_body)
			if retry:
				ret=self.api_request(url,body,request,raw,retry=False)
			else:
				raw=True
		return res_body if raw else ret

	def generate_headers(self, body = {}):
		RID=str(uuid.uuid4()).replace('-','')
		return {
			"Expect": "100-continue",
			"X-GUMI-APP-VERSION": "default",
			"X-Unity-Version": "2018.4.0f1",
			"X-Gumi-Game-Environment": "production",
			"X-GUMI-STORE-PLATFORM": "googleplay",
			"Content-Type": "application/json; charset=utf-8",
			"X-GUMI-REQUEST-ID": RID,
			"X-GUMI-TRANSACTION": RID,
			"X-GUMI-DEVICE-OS": "android",
			"X-Gumi-User-Agent": '{"device_model":"oppo oppo r9tm","device_vendor":"<unknown>","os_info":"Android OS 5.1.1 / API-22 (LYZ28N/V9.5.2.0.LACCNFA)","cpu_info":"ARMv7 VFPv3 NEON VMH","memory_size":"2.02GB","graphics_device_name":"Adreno (TM) 540","graphics_device_type":"OpenGLES3","graphics_device_vendor":"Qualcomm","graphics_device_version":"OpenGL ES 3.1","graphics_memory_size":512,"graphics_multi_threaded":true,"graphics_shader_level":45}',
			"X-SIG-AUTH": "Ev4dnE4mBmYZ",
			"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; oppo r9tm Build/LYZ28N)",
			"Host": self.api,
			"Connection": "Keep-Alive",
			"Accept-Encoding": "gzip",
			"Content-Length": len(json.dumps(body)) if body else 0
		}

	def api_connect(self,url, body={},request="POST",api=False, ignoreStat=False, no_access_token=False):
		#print(self.access_token)
		if not api:
			api=self.api
		headers = self.generate_headers(body)
		if self.print_req:
			print(api+url)
		try:
			con = http.client.HTTPSConnection(api)
			con.connect()
			con.request(request, url, json.dumps(body), headers)
			res_body = con.getresponse().read()
			#print(res_body)
			con.close()
		except http.client.RemoteDisconnected:
			return self.api_connect(url, body)
		try:
			try:
				res_body = gzip.decompress(res_body)
			except OSError:
				pass
			json_res= json.loads(res_body)

			if self.debug:
				with open(os.path.join('debug','{:%y%m%d-%H-%M-%S}{}.json'.format(datetime.datetime.utcnow(),url.replace('/','_'))),'wb') as f:
					f.write(json.dumps(json_res, indent=4, ensure_ascii=False).encode('utf8'))
			return(json_res)
		except Exception as e:
			print(e)
			"""
			print(e)
			print(url)
			print(res_body)

			if self.debug:
				with open(os.path.join('debug','{:%y%m%d-%H-%M-%S}{}.json'.format(datetime.datetime.utcnow(),url.replace('/','_'))),'wb') as f:
					f.write(res_body.encode('utf8'))

			if '504 Gateway Time-out' in str(res_body) or '502 Bad Gateway' in str(res_body):
				print('Waiting 5s, then trying it again')
				time.sleep(5)
				return self.api_connect(url, body)
			elif str(e)=='maximum recursion depth exceeded while calling a Python object':
				raise ValueError('max recursion')
			else:
				input('Unknown Error')
			#return self.api_connect(url, body)
			raise RecursionError('-')
			"""
