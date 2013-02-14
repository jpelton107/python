#!/usr/bin/python

from Tkinter import *

class App(Frame):
	def __init__(self, master=None):
		Frame.__init__(self,master)
		self.grid(sticky=N+S+E+W)
		self.create_widgets()

	def create_widgets(self):
		top = self.winfo_toplevel()
		top.rowconfigure(0, weight=1)
		top.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.quit_button = Button(self, text='Quit', command=self.quit)
		self.quit_button.grid(row=0, column=0, sticky=N+S+E+W)
		
app = App()
app.master.title("Sample App")
app.mainloop()
