#!/usr/bin/python

from Tkinter import *

class App:
    def __init__(self, master):
        self.master = master

        self.setFrame1()
       
    def setFrame1(self):
        self.openFrame = Frame(self.master, name="frame")
        self.openFrame.pack()

        lbl = Label(self.openFrame, text="Welcome. Would you like to continue?")
        lbl.pack(side=LEFT)
        
        btn = Button(self.openFrame, text="Continue", bg="green", command=self.setFrame2)
        btn.pack(side=RIGHT)

        
    def setFrame2(self):
       self.openFrame.pack_forget()
       closeFrame = Frame(self.master)
       closeFrame.pack()

       lbl = Label(closeFrame, text="You have completed the app. Please come again soon.")
       lbl.pack(side=LEFT)

       btn = Button(closeFrame, text="Exit", bg="red", command=closeFrame.quit)
       btn.pack(side=RIGHT)

root = Tk()
app = App(root)
root.mainloop()
        
