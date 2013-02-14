#!/usr/bin/env python

from Tkinter import *
import tkFont

class App:

    def __init__(self, root):
        self.y = 0
        root.bind('<Return>', self.enter)
        root.bind_all('<Key>', self.checkKey)

        # create button map
        self.symbols = ['-', '+', '*', '/', '.']
        self.buttons = [['7', '8', '9', '-'],
                    ['4', '5', '6', '+'],
                    ['1', '2', '3', '*'],
                    ['0', '.', '/', '=']]

        # spawn items to frames
        self.entryFont = tkFont.Font(size=18)
        self.btnFont = tkFont.Font(size=14)
        self.spawnInput(root)
        self.spawnBackspace(root)
        self.spawnButtons(root)

    def updateEntry(self, inp):
        if inp is '=':
            self.calculate()
        else:
            self.textEntry.insert("end", inp)

    def spawnInput(self, root):
        self.textEntry = Entry(root, width=17, font=self.entryFont)
        self.textEntry.grid(row=self.y,column=0, columnspan=4)
        self.y += 1

    def spawnBackspace(self, root):
        bksp = Button(root, width=9, height=2, text="BKSPCE", font=self.btnFont, command=self.backspace);
        clr = Button(root, width=9, height=2, text="CLR", font=self.btnFont, command=self.clear);
        
        clr.grid(row=self.y, column=2, columnspan=2)
        bksp.grid(row=self.y, column=0, columnspan=2)
        self.y += 1
 
    def spawnButtons(self, root):
        #self.btn_frame = Frame(root, width=800, height=800)
        k = 0
        button = {}
        for i in self.buttons:
            x = 0
            for j in i:
                button[k] = Button(root, width=3,height=2, text=j, font=self.btnFont, command=lambda item=j: self.updateEntry(item))
                button[k].grid(row=self.y, column=x)
                k += 1
                x += 1
            self.y += 1

    def calculate(self):
        string = self.textEntry.get()
        self.clear()
        self.textEntry.insert("end", eval(string))

    def backspace(self):
        
        txt = self.textEntry.get()
        length = len(txt)
        self.textEntry.delete(length-1, END)

    def clear(self):
        self.textEntry.delete(0, END)

    def enter(self, event):
        self.calculate()

    def checkKey(self, event):
        if event.char == event.keysym:
            self.textEntry.insert("end", event.char)
        else:
            if event.char in self.symbols:
                self.textEntry.insert("end" , event.char)
            elif event.keysym == 'BackSpace':
                self.backspace()


root = Tk()
app = App(root)
root.mainloop()
