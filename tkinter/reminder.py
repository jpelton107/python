#!/usr/bin/python

from Tkinter import *

class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="Break is over", fg="red", bg="yellow", command=frame.quit)
        self.button.pack(side=RIGHT)

        self.msg = Label(frame, text="Take a quick break.")
        self.msg.pack(side=LEFT)
        
root = Tk()
app = App(root)
root.mainloop()

