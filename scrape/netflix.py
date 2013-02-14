#! /usr/bin python

import urllib
import httplib2

http = httplib2.Http()

url = 'https://signup.netflix.com/Login'
body = {'email': 'rpelton8@hotmail.com', 'password': 'cheese'}
headers = {'Content-type': 'application/x-www-form-urlencoded'}
response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))
print response, content

headers = {'Cookie': response['set-cookie']}

url = 'https://account.netflix.com/WiViewingActivity?all=true'
response, newcontent = http.request(url, 'GET', headers=headers)

