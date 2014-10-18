
""" 
  Exosite HTTPS POST/GET REST API example using socket level calls
"""


import socket
import sys
import ssl
import urllib
import time

cik = 'PUT_YOUR_DEVICE_CIK_HERE'


print '=================='
print 'GET - HTTPS'
print '=================='

# Note: This example is building a large string to send over the socket, this could be done
# instead line by line.  For purposes of printing out the request, it is done this way.
request_packet = ''
request_packet += 'GET /api:v1/stack/alias?output HTTP/1.1\r\n'
request_packet += 'Host: m2.exosite.com\r\n'
request_packet += 'X-Exosite-CIK: '+cik+'\r\n'
request_packet += 'Connection: Close\r\n'
request_packet += 'Accept: application/x-www-form-urlencoded; charset=utf-8\r\n'
request_packet += '\r\n' # Must have blank line

print '--REQUEST:-----------------------'
print str(request_packet),
print '---------------------------------'

# OPEN SOCKET
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_s = ssl.wrap_socket(s)
ssl_s.connect(('m2.exosite.com', 443))
# SEND REQUEST
ssl_s.send(request_packet)
# RECEIVE RESPONSE
data = ssl_s.recv(1024)
# CLOSE SOCKET
ssl_s.close()

# URL DECODE - If required
data = urllib.unquote_plus(data) # library specific to python
print '--RESPONSE:----------------------'
print str(data)
print '---------------------------------'
print '(Note: You should see a response of "HTTP/1.1 200 OK" if this works correctly)'
print '(Note: Some string data in the response may need formating, it is urlencoded)'
print '\r\n\r\n'

