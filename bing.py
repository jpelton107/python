#!/usr/bin/python 

import webbrowser 
import time

i = 0
# create 45 tabs.. (max of 45 bing rewards visits per day)
while i < 45:
	i += 1
	url = 'http://www.bing.com/search?q=%d' % (i,)
	#webbrowser.open_new_tab(url)
	print url


# then close the browser after they have had time to load
end = time.time() + 10
while 1:
	if time.time() > end:
		print "End"
		break

