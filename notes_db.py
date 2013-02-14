#!/usr/bin/env python

from pymongo import Connection
from Tkinter import *
import datetime, re

class DB:
	def __init__(self):
		# connect
		c = Connection('localhost', 27017)
		# declare DB name
		db = c.info
		# declare 'table' name
		posts = db.posts
		self.posts = posts

	def createPost(self, text, tag, duedate):
		post = {"text"	: text,
			"tag"	: tag,
			"duedate": duedate,
			"date"	: datetime.datetime.now()
			}
		self.posts.insert(post)
		print "Post successfully made..."
		print 

	def showTasks(self):
		posts = self.posts
		i = 1
		self.number_posts = {}
		for post in posts.find().sort("duedate"):
			self.number_posts[i] = post
			print "#" * 30
			print "# " + str(i) + ") " + post['text']
			print "# Tag:",post['tag']
			print "# Due Date: ",post['duedate']
			print "#" * 30
			print 
			i += 1
	
	def postCount(self):
		print "Number of posts:",self.posts.count()

	def deletePost(self, number):
		# get post number
		targetPost = self.number_posts[number]
		
		print targetPost

def mainMenu():
	print "#" * 30
	print "a) view posts"
	print "b) create post"
	print "d) delete post"
	print
	print "q) Quit"

	response = raw_input("What would you like to do? ")

	db = DB()
	if response == "a":
		db.showTasks()
	elif response == "b":
		text = raw_input("Message: ")
		tag = raw_input("Tag: ")
		duedate = raw_input("Due Date: ")
		db.createPost(text, tag, duedate)
	elif re.search("^d\s\d$",response):
		number = re.search("^d\s(\d)$", response)
		print number
		db.deletePost(number)
	elif response == "q":
		quit()
	


if __name__ == "__main__":
	while 1:
		mainMenu()



