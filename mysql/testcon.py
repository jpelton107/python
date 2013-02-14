#!/usr/bin/python

import MySQLdb as mdb
import wx
import os

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500,300))
	self.printAgencies()
	self.CreateStatusBar()

        filemenu = wx.Menu()

        menuAbout = filemenu.Append(
            wx.ID_ABOUT, "&About", 
            "Information about this program")
	menuExit = filemenu.Append(
            wx.ID_EXIT, "E&xit", 
            "Terminate the program")

	menuBar = wx.MenuBar()
	menuBar.Append(filemenu, "&File")
	self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Show(True)

    def OnAbout(self, e):
        dlg = wx.MessageDialog(
            self, "A small text editor", 
            "Amout sample editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def printAgencies(self):
        con = None
 
        try:
            con = mdb.connect('tstmysql', 'lobbyist', 
		              'pw4lobby', 'Lobbyist')

            cursor = con.cursor(mdb.cursors.DictCursor)
            cursor.execute("select * from Agencies_Report order by id desc limit 10")

            rows = cursor.fetchall()
  
            posy = 0
            for row in rows:
	        result = "%s)  %s" % (row["id"], row["ReportOf"])
		self.display = wx.StaticText(self, label=result, pos=(5, posy))
                posy += 20

        finally:
            if con:
	        con.close()


app = wx.App(False)
frame = MyFrame(None, 'Small editor')
app.MainLoop()


