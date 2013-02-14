#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk

class View:
	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_size_request(400, 300)
		self.window.set_title("Blog")
		
		# close
		self.window.connect("delete_event", self.delete_event)

		# destroy
		self.window.connect("destroy", self.destroy)

		vbox = gtk.VBox(False, 5)
		hbox = gtk.HBox(False, 5)
		self.window.add(hbox)
		hbox.pack_start(vbox, False, False, 0)
		self.window.set_border_width(5)
		
		frame = gtk.Frame("Normal Label")
		label = gtk.Label("This is a Normal label")
		frame.add(label)
		vbox.pack_start(frame, False, False, 0)

		self.window.show_all()


		

#	def addItem(self, item):
		
	def main(self):
		gtk.main()
