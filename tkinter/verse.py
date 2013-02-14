#!/usr/bin/env python

from Tkinter import *
import tkFont
from StringIO import StringIO
import pycurl

class App:
    
    def __init__(self, root):
        
        self.createUI(root)

    def createUI(self, root):

        self.reference = Entry(root, width=17)
        self.submit = Button(root, text="Get", command=self.getVerse)
        self.reference.grid(row=0, column=0)
        self.submit.grid(row=0, column=1)
        
    def getVerse(self):
        
        reference = self.reference.get()
        reference = reference.replace(" ", "%20")
        url = "http://labs.bible.org/api/?passage=" + reference
        print url
        s = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, s.write)
        c.perform()
        c.close()
        passage = s.getvalue()
        passage = passage.replace('<b>', '')
        passage = passage.replace('</b>', '')
        self.passage = Message(root, text=passage)
        self.passage.grid(row=1, column=0, columnspan=2)
        

root = Tk()
root.title('Bible Passage Search')
root.minsize(300,200)

app = App(root)
root.mainloop()
