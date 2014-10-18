
""" 
  Exosite HTTPS POST API and CoAP Write examples using socket level calls to 
  show the difference in sizes of the total request/response.
"""


import socket
import sys
import ssl
import urllib
import time

cik = 'PUT_YOUR_DEVICE_CIK_HERE'

print '========================================================================'
print 'MAKE THE REQUESTS, Using CIK ', cik
print '========================================================================'
print '\r\n'

print '=================='
print 'POST - HTTPS'
print '=================='

content = 'input=1'

# Note: This example is building a large string to send over the socket, this could be done
# instead line by line.  For purposes of printing out the request, it is done this way.

request_packet = ''
request_packet += 'POST /api:v1/stack/alias HTTP/1.1\r\n'
request_packet += 'Host: m2.exosite.com\r\n'
request_packet += 'X-Exosite-CIK: '+cik+'\r\n'
request_packet += 'Connection: Close \r\n'
request_packet += 'Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n'
request_packet += 'Content-Length: '+ str(len(content)) +'\r\n'
request_packet += '\r\n' # Must have blank line here
request_packet += content # Must be same size as Content-Length specified

print '--REQUEST:-----------------------'
print str(request_packet)
print '---------------------------------'

# OPEN SOCKET
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_s = ssl.wrap_socket(s)
ssl_s.connect(('m2.exosite.com', 443))
# SEND REQUEST
ssl_s.send(request_packet)
# RECEIVE RESPONSE
response = ssl_s.recv(2048)
# CLOSE SOCKET
ssl_s.close()

# URL DECODE - If required
data = urllib.unquote_plus(response) # library specific to python
print '--RESPONSE:----------------------'
print str(data),
print '---------------------------------'
print '(Note: You should see a response of "HTTP/1.1 204 No Content" if this works correctly)'
print '\r\n\r\n'

print '--REQUEST / RESPONSE SIZE:----------------------'
print 'Request:'+ str(len(request_packet) )+ ' Bytes'
print 'Response:'+ str(len(response))+ ' Bytes'
print 'Total:' + str(len(request_packet)+len(response)) + ' Bytes'
print '---------------------------------'
print '\r\n\r\n'


time.sleep(2)

print '=================='
print 'COAP Write'
print '=================='
import binascii
import coap
import sys


ALIAS = "output"
SERVER = "coap.exosite.com"
PORT = 5683

# Create a New Conformable GET CoAP Request with Message ID 0x37.
msg = coap.Message(mtype=coap.CON, mid=0x37, code=coap.POST)
# Set the path where the format is "/1a/<datasource alias>".
msg.opt.uri_path = ('1a', ALIAS,)
# Encode the CIK to binary to save data
msg.opt.uri_query = (binascii.a2b_hex(cik),)
msg.payload = "1"
start = time.time()
print("Sending Message: {}".format(binascii.b2a_hex(msg.encode())))
print(coap.humanFormatMessage(msg))

# Setup Socket as UDP
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

# Encode and Send Message
sock.sendto(msg.encode(), (SERVER, PORT))
# Wait for Response
data, addr = sock.recvfrom(2048) # maximum packet size is 1500 bytes
print('time',time.time()-start,'ms')
# Decode and Display Response
recv_msg = coap.Message.decode(data)
print("Received Message: {}".format(binascii.b2a_hex(data)))
print(coap.humanFormatMessage(recv_msg))

print '--REQUEST / RESPONSE SIZE:----------------------'
print 'Request:'+ str(len(binascii.b2a_hex(msg.encode()))/2)+ ' Bytes'
print 'Response:'+ str(len(binascii.b2a_hex(data))/2)+ ' Bytes'
print 'Total:' + str(len(binascii.b2a_hex(msg.encode()))/2+len(len(binascii.b2a_hex(data))/2)) + ' Bytes'
print '---------------------------------'
print '\r\n\r\n'


