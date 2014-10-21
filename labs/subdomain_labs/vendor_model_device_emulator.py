import time
import random
from pprint import pprint
import json


import socket
import sys
import ssl

import urllib 
try:
	import httplib
except:
    # python 3
    from http import client as httplib

from httplib import HTTPResponse
from StringIO import StringIO


SHOW_HTTP_REQUESTS = False

# -----------------------------------------------------------------
# EXOSITE VENDOR / MODEL / SERIAL NUMBER INFORMATION
# -----------------------------------------------------------------
vendor = '<YOUR_VENDOR_ID_HERE>' 
model = 'product1'
serial_number = '000001'
host_address = vendor+'.m2.exosite.com'
https_port = 443
firmware_prefix = 'firmware'
firmware_divider = '_'

last_firmware_version = 0


class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file



#
# LOCAL DATA VARIABLES
#
FLAG_CHECK_ACTIVATION = False


command = ''
val_to_write = 50
second_val_to_write = 100

REQUEST_LOOP_INTERVAL = 5 #in seconds
FIRMWARE_CHECK_INTERVAL = 60 #seconds
connected = True

last_request = 0
last_firmware_check = 0
app_config = None

#
# FUNCTIONS
#

def SOCKET_SEND(http_packet):
		# SEND REQUEST
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssl_s = ssl.wrap_socket(s)
		ssl_s.connect((host_address, https_port))
		if SHOW_HTTP_REQUESTS: print ('--- Sending ---\r\n' + http_packet + '\r\n----')
		ssl_s.send(http_packet)

		# GET RESPONSE
		response = ssl_s.recv(1024)
		ssl_s.close()
		if SHOW_HTTP_REQUESTS: print ('--- Response --- \r\n' + str(response) + '\r\n---')

		#PARSE REPONSE
		fake_socket_response = FakeSocket(response)
		parsed_response = HTTPResponse(fake_socket_response)
		parsed_response.begin()
		return parsed_response


def ACTIVATE():
		try:
			print 'attempt to activate on Exosite OnePlatform'

			http_body = 'vendor='+vendor+'&model='+model+'&sn='+serial_number
			# BUILD HTTP PACKET 
			http_packet = ""
			http_packet = http_packet + 'POST /provision/activate HTTP/1.1\r\n'
			http_packet = http_packet + 'Host: '+host_address+'\r\n'
			http_packet = http_packet + 'Connection: Close \r\n'
			http_packet = http_packet + 'Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n'
			http_packet = http_packet + 'content-length:'+ str(len(http_body)) +'\r\n'
			http_packet = http_packet + '\r\n'
			http_packet = http_packet + http_body

			response = SOCKET_SEND(http_packet)

			# HANDLE POSSIBLE RESPONSES
			if response.status == 200:
				new_cik = response.read()
				print 'Activation Response: New CIK:' + new_cik
				return new_cik
			elif response.status == 409:
				print 'Activation Response: Device Aleady Activated / No New CIK'
			elif response.status == 404:
				print 'Activation Response: Bad Activation Request: check vendor, model, serial number'
			else:
				print 'Activation Response: failed: ', str(response.status), response.reason
				return None

		except Exception,err:
			#pass
			print 'exeception: ' + str(err)
		return None

def GET_STORED_CIK():
		print 'get stored CIK from non-volatile memory'
		try:
			f = open(model+"_"+vendor+"_"+serial_number+"_cik","r+") #opens file to store CIK
			local_cik = f.read()
			f.close()
			print 'stored cik: ' + str(local_cik)
			return local_cik
		except:
			print 'problem getting stored CIK'
			return None

def STORE_CIK(cik_to_store):
		print 'storing new CIK to non-volatile memory'
		f = open(model+"_"+vendor+"_"+serial_number+"_cik","w") #opens file that stores CIK
		f.write(cik_to_store)
		f.close()
		return True


def DECIDE_TO_DOWNLOAD_NEW(vendor_id, model_id,cik,content_list):
		try:
			# Get Exosite Provision API Instance
			current_version = GET_STORED_FIRMWARE_VERSION()
			print 'current firmware: ', current_version
			download = None
			download_version = 0
			content_ids = content_list.split('\r\n')
			#print content_ids
			for content in content_ids:
				#print content
				prefix = content.split(firmware_divider)
				if prefix[0] == firmware_prefix:
					if int(prefix[1]) > int(current_version) and int(prefix[1]) > download_version:
						print 'found new firmware to download: ' + content
						download = content
						download_version = prefix[1]
			if download:
				print 'EXO: attempt to download content ' + firmware_prefix + ' from Exosite OnePlatform'
				http_port = 80
				url = '/provision/download?vendor='+vendor_id+'&model='+model_id+'&id='+download
				headers = {'X-Exosite-CIK':cik}
				conn = httplib.HTTPConnection(vendor+'.m2.exosite.com',http_port)
				#conn.set_debuglevel(1)
				conn.request("GET",url,"",headers)
				response = conn.getresponse();
				data = response.read()
				conn.close()
				#print 'response: ',response.status,response.reason
				#print 'response data:', urllib.unquote(data)
				if response.status == 200:
					print 'Got New Download'
					print 'UPDATING....'
					STORE_FIRMWARE(download_version)
				else:
					print 'This device does not have correct authentication, server response:',response.status,response.reason
					return False
				return True
			else:
				print 'No New Firmware To Download'
				return True

		except Exception,err:
			pass
			print 'exeception: ' + str(err)
		return None


def CHECK_FIRMWARE(vendor_id, model_id,cik):
		try:
			# Get Exosite Provision API Instance
			print 'EXO: attempt get content list on Exosite OnePlatform'
			http_port = 80
			url = '/provision/download?vendor='+vendor_id+'&model='+model_id
			headers = {'X-Exosite-CIK':cik}
			conn = httplib.HTTPConnection(vendor+'.m2.exosite.com',http_port)
			#conn.set_debuglevel(1)
			conn.request("GET",url,"",headers)
			response = conn.getresponse();
			data = response.read()
			conn.close()
			#print 'response: ',response.status,response.reason
			#print 'response data:', urllib.unquote(data)
			if response.status == 204:
				print 'This device has no content to access'
				return None
			elif response.status == 200:
				print '--Content List:--\r\n' + str(data) + '\r\n-----------'
			else:
				print 'This device does not have correct authentication, server response:',response.status,response.reason
				return None
			return data
		except Exception,err:
			pass
			print 'exeception: ' + str(err)
		return None

def GET_STORED_FIRMWARE_VERSION():
		print 'get stored firmware version from non-volatile memory'
		try:
			f = open(model+"_"+vendor+"_"+serial_number+"_firmware","r+") #opens file to store CIK
			ver = f.read()
			f.close()
			print 'current version: ' + str(ver)
			return ver
		except:
			print 'problem getting stored firmware version'
			STORE_FIRMWARE('100') #default
			return '100'

def STORE_FIRMWARE(version):
		print 'storing firmware version to non-volatile memory'
		f = open(model+"_"+vendor+"_"+serial_number+"_firmware","w") #opens file that stores CIK
		f.write(version)
		f.close()
		return True

def WRITE(WRITE_PARAMS):
		try:
			print 'write data to Exosite OnePlatform'

			http_body = WRITE_PARAMS
			# BUILD HTTP PACKET 
			http_packet = ""
			http_packet = http_packet + 'POST /onep:v1/stack/alias HTTP/1.1\r\n'
			http_packet = http_packet + 'Host: '+host_address+'\r\n'
			http_packet = http_packet + 'X-EXOSITE-CIK: '+cik+'\r\n'
			http_packet = http_packet + 'Connection: Close \r\n'
			http_packet = http_packet + 'Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n'
			http_packet = http_packet + 'content-length:'+ str(len(http_body)) +'\r\n'
			http_packet = http_packet + '\r\n'
			http_packet = http_packet + http_body

			response = SOCKET_SEND(http_packet)

			# HANDLE POSSIBLE RESPONSES
			if response.status == 204:
				#print 'write success'
				return True,204
			elif response.status == 401:
				print '401: Bad Auth, CIK may be bad'
				return False,401
			elif response.status == 400:
				print '400: Bad Request: check syntax'
				return False,400
			elif response.status == 405:
				print '405: Bad Method'
				return False,405		
			else:
				print str(response.status), response.reason, 'failed:'
				return False,response.status

		except Exception,err:
			#pass
			print 'exeception: ' + str(err)
		return None

def READ(READ_PARAMS):
		try:
			print 'read data from Exosite OnePlatform'

			# BUILD HTTP PACKET 
			http_packet = ""
			http_packet = http_packet + 'GET /onep:v1/stack/alias?'+READ_PARAMS+' HTTP/1.1\r\n'
			http_packet = http_packet + 'Host: '+host_address+'\r\n'
			http_packet = http_packet + 'X-EXOSITE-CIK: '+cik+'\r\n'
			#http_packet = http_packet + 'Connection: Close \r\n'
			http_packet = http_packet + 'Accept: application/x-www-form-urlencoded; charset=utf-8\r\n'
			http_packet = http_packet + '\r\n'

			response = SOCKET_SEND(http_packet)

			# HANDLE POSSIBLE RESPONSES
			if response.status == 200:
				#print 'read success'
				return True,response.read()
			elif response.status == 401:
				print '401: Bad Auth, CIK may be bad'
				return False,401
			elif response.status == 400:
				print '400: Bad Request: check syntax'
				return False,400
			elif response.status == 405:
				print '405: Bad Method'
				return False,405		
			else:
				print str(response.status), response.reason, 'failed:'
				return False,response.status

		except Exception,err:
			#pass
			print 'exeception: ' + str(err)
		return None


# --------------------------
# APPLICATION STARTS RUNNING HERE 
# --------------------------


# --------------------------
# BOOT
# --------------------------

#Check if CIK locally stored already
cik = GET_STORED_CIK()
if cik == None:
	print 'try to activate'
	act_response = ACTIVATE()
	if act_response != None:
		cik = act_response
		STORE_CIK(cik)
		FLAG_CHECK_ACTIVATION = False
	else:
		FLAG_CHECK_ACTIVATION = True

# --------------------------
# MAIN LOOP
# --------------------------
print 'starting main looop'

counter = 100 #for debug purposes so you don't have issues killing this process
LOOP = True

while LOOP:
		if time.time() - last_request > REQUEST_LOOP_INTERVAL:
			last_request = time.time()
			if cik != None and FLAG_CHECK_ACTIVATION != True:
				val_to_write = random.randint(val_to_write-1,val_to_write+1)
				if val_to_write > 100: val_to_write = 100
				if val_to_write < 1: val_to_write = 1

				second_val_to_write = random.randint(second_val_to_write-20,second_val_to_write+20)
				if second_val_to_write > 1000: second_val_to_write = 1000
				if second_val_to_write < 1: second_val_to_write = 1
				
				status,resp = WRITE('data1='+str(val_to_write)+'&data2='+str(second_val_to_write))
				if status == False and resp == 401:
					FLAG_CHECK_ACTIVATION = True
				
				status,resp = READ('command')
				if status == False and resp == 401:
					FLAG_CHECK_ACTIVATION = True
				if status == True:
					print('Command Value:' + str(resp))
				
				status,resp = READ('config')
				if status == False and resp == 401:
					FLAG_CHECK_ACTIVATION = True
				if status == True:
					print('Command Value:' + str(resp))

				if FLAG_CHECK_ACTIVATION == True:
					print('ACTIVATION STATE: NOT ACTIVATED')
				#else:
				#	print('ACTIVATION STATE: ACTIVATED')

		if FLAG_CHECK_ACTIVATION == True:
			print ('Device CIK may be bad, expired, or not available (not owned) - try to activate')
			act_response = ACTIVATE()
			if act_response != None:
				cik = act_response
				STORE_CIK(cik)
				FLAG_CHECK_ACTIVATION = False
			else:
				print ('Wait 10 seconds and attempt to activate again')
				time.sleep(10)

		if time.time() - last_firmware_check > FIRMWARE_CHECK_INTERVAL:
			last_firmware_check = int(time.time())
			print('Checking for new firmware')
			content_list = CHECK_FIRMWARE(vendor, model, cik)
			if content_list:
				if len(content_list) > 0:
					update = DECIDE_TO_DOWNLOAD_NEW(vendor,model,cik,content_list)
					if update:
						print('updated firmware')
					else:
						print('no update required')
			cur_version = GET_STORED_FIRMWARE_VERSION()
			#if connected:
			#	WRITE('devreport={"lastupdate":"unknown","lastcheck":"'+str(last_firmware_check)+'","cur_fm":"' +cur_version +'"}')		
		time.sleep(1)
		if counter > 0:
			if (counter%10) == 0:
				print('stopping app loop in ~' +str(counter)+ ' seconds')
			counter = counter - 1

		if counter <= 0:
			print('killing the auto loop for this emulator app')
			LOOP=False
			break

