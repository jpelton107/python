#!/usr/bin/env python

from Tkinter import *
import tkFont
from StringIO import StringIO
import pycurl

class App:
    
    def __init__(self, root):
        
        self.mainframe = Frame(root, width=300, height=200)
        self.mainframe.pack()
        self.createUI()

    def createUI(self):

        self.reference = Entry(self.mainframe, width=17)
        self.submit = Button(self.mainframe, text="Get", command=self.getVerse)
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
        self.passage = Message(self.mainframe, text=passage, anchor=CENTER)
        self.passage.grid(row=1, column=0, columnspan=2)
        

root = Tk()
root.title('Bible Passage Search')
root.minsize(300,200)
root.maxsize(1400, 800)

app = App(root)
root.mainloop()
