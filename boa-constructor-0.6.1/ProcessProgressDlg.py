#-----------------------------------------------------------------------------
# Name:        ProcessProgressDlg.py
# Purpose:     Dialog that shows errors and output of a process executed with
#              wxProcess. Operation can be canceled.
#
# Author:      Riaan Booysen
#
# Created:     2001/02/04
# RCS-ID:      $Id: ProcessProgressDlg.py,v 1.19 2007/07/02 15:01:06 riaan Exp $
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ProcessProgressDlg

import wx
from wx.lib.anchors import LayoutAnchors

import os, time, sys, StringIO

# XXX Change to be non-modal, minimizable and run CVS operation in thread !!

import Preferences
from Utils import _

from wxPopen import ProcessRunnerMix

[wxID_PROCESSPROGRESSDLG, wxID_PROCESSPROGRESSDLGCANCELBTN, 
 wxID_PROCESSPROGRESSDLGCMDSTXT, wxID_PROCESSPROGRESSDLGERRORTCTRL, 
 wxID_PROCESSPROGRESSDLGKILLBTN, wxID_PROCESSPROGRESSDLGOUTPUTTCTRL, 
 wxID_PROCESSPROGRESSDLGSPLITTERWINDOW, wxID_PROCESSPROGRESSDLGSTATUSGGE, 
 wxID_PROCESSPROGRESSDLGSTATUSSTXT, 
] = [wx.NewId() for _init_ctrls in range(9)]

class ProcessProgressDlg(wx.Dialog, ProcessRunnerMix):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_PROCESSPROGRESSDLG,
              name='ProcessProgressDlg', parent=prnt, pos=wx.Point(313, 215),
              size=wx.Size(428, 363),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=self.dlg_caption)
        self.SetAutoLayout(True)
        self.SetClientSize(wx.Size(420, 336))
        self.Bind(wx.EVT_CLOSE, self.OnProcessprogressdlgClose)

        self.cancelBtn = wx.Button(id=wxID_PROCESSPROGRESSDLGCANCELBTN,
              label=_('Cancel'), name='cancelBtn', parent=self, pos=wx.Point(332,
              304), size=wx.Size(80, 24), style=0)
        self.cancelBtn.SetConstraints(LayoutAnchors(self.cancelBtn, False,
              False, True, True))
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelbtnButton,
              id=wxID_PROCESSPROGRESSDLGCANCELBTN)

        self.cmdStxt = wx.StaticText(id=wxID_PROCESSPROGRESSDLGCMDSTXT,
              label='staticText1', name='cmdStxt', parent=self, pos=wx.Point(8,
              8), size=wx.Size(404, 64), style=wx.ST_NO_AUTORESIZE)
        self.cmdStxt.SetConstraints(LayoutAnchors(self.cmdStxt, True, True,
              True, False))

        self.splitterWindow = wx.SplitterWindow(id=wxID_PROCESSPROGRESSDLGSPLITTERWINDOW,
              name='splitterWindow', parent=self, pos=wx.Point(8, 80),
              size=wx.Size(360, 192), style=self.splitterStyle)
        self.splitterWindow.SetConstraints(LayoutAnchors(self.splitterWindow,
              True, True, True, True))

        self.errorTctrl = wx.TextCtrl(id=wxID_PROCESSPROGRESSDLGERRORTCTRL,
              name='errorTctrl', parent=self.splitterWindow, pos=wx.Point(0, 0),
              size=wx.Size(360, 80), style=wx.TE_MULTILINE | wx.TE_RICH,
              value='')
        self.errorTctrl.SetForegroundColour(wx.Colour(128, 0, 0))

        self.outputTctrl = wx.TextCtrl(id=wxID_PROCESSPROGRESSDLGOUTPUTTCTRL,
              name='outputTctrl', parent=self.splitterWindow, pos=wx.Point(0,
              87), size=wx.Size(360, 105), style=wx.TE_MULTILINE | wx.TE_RICH,
              value='')
        self.splitterWindow.SplitHorizontally(self.errorTctrl, self.outputTctrl,
              80)

        self.statusStxt = wx.StaticText(id=wxID_PROCESSPROGRESSDLGSTATUSSTXT,
              label='staticText1', name='statusStxt', parent=self,
              pos=wx.Point(8, 288), size=wx.Size(292, 16), style=0)
        self.statusStxt.SetConstraints(LayoutAnchors(self.statusStxt, True,
              False, True, True))

        self.statusGge = wx.Gauge(id=wxID_PROCESSPROGRESSDLGSTATUSGGE,
              name='statusGge', parent=self, pos=wx.Point(8, 312), range=100,
              size=wx.Size(208, 16), style=wx.GA_HORIZONTAL)
        self.statusGge.SetConstraints(LayoutAnchors(self.statusGge, True, False,
              True, True))

        self.killBtn = wx.Button(id=wxID_PROCESSPROGRESSDLGKILLBTN,
              label=_('Kill'), name='killBtn', parent=self, pos=wx.Point(242, 304),
              size=wx.Size(81, 24), style=0)
        self.killBtn.SetConstraints(LayoutAnchors(self.killBtn, False, False,
              True, True))
        self.killBtn.Enable(False)
        self.killBtn.Bind(wx.EVT_BUTTON, self.OnKillbtnButton,
              id=wxID_PROCESSPROGRESSDLGKILLBTN)

    def __init__(self, parent, command, caption, modally=True,
          linesep=os.linesep, autoClose=True, overrideDisplay=''):

        self.dlg_caption = 'Progress'
        self.dlg_caption = caption
        self.splitterStyle = Preferences.splitterStyle
        self._init_ctrls(parent)

        self.splitterWindow.SetMinimumPaneSize(20)

        ProcessRunnerMix.__init__(self, [])

        self.Center(wx.BOTH)

        self.modally = True
        self.linesep = linesep
        self.autoClose = autoClose

        if overrideDisplay:
            self.cmdStxt.SetLabel(overrideDisplay)
        else:
            self.cmdStxt.SetLabel(command)

        self.execute(command, modally)

        if not modally:
            while not self.finished:
                wx.Yield()

    def execute(self, cmd, modally = True):
        self.killBtn.Enable(True)
        self.cancelBtn.SetLabel(_('Cancel'))
        self.statusStxt.SetLabel(_('Waiting for response...'))
        self.responded = False
        self.modally = modally

        ProcessRunnerMix.execute(self, cmd)

    def updateStream(self, stream, data):
        resp = self.responded
        try:
            return ProcessRunnerMix.updateStream(self, stream, data)
        finally:
            if self.responded == (not resp):
                self.statusStxt.SetLabel(_('Receiving response...'))

    def updateErrStream(self, stream, data):
        txt = ProcessRunnerMix.updateErrStream(self, stream, data)
        if txt is not None:
            self.errorTctrl.SetFocus()
            self.errorTctrl.AppendText(txt)

    def updateOutStream(self, stream, data):
        txt = ProcessRunnerMix.updateOutStream(self, stream, data)
        if txt is not None:
            self.outputTctrl.SetFocus()
            self.outputTctrl.AppendText(txt)

    def OnIdle(self, event=None):
        # step the gauge to indicate activity
        if not self.finished:
            v = self.statusGge.GetValue()
            if v >= 100:
                v = 0
            else:
                v = v + 1
            self.statusGge.SetValue(v)

        ProcessRunnerMix.OnIdle(self, event)

    def OnProcessEnded(self, event):
        ProcessRunnerMix.OnProcessEnded(self, event)

        self.statusStxt.SetLabel(_('Response received.'))

        self.prepareResult()
        self.statusGge.SetValue(0)

        self.killBtn.Enable(False)
        self.cancelBtn.SetLabel(_('OK'))

        if self.modally and self.autoClose:
            self.EndModal(wx.OK)

    def OnProcessprogressdlgClose(self, event):
        try:
            self.detach()
        finally:
            event.Skip()

    def prepareResult(self):
        self.output = StringIO.StringIO(''.join(self.output)).readlines()
        self.errors = StringIO.StringIO(''.join(self.errors)).readlines()

    def OnCancelbtnButton(self, event):
        if not self.finished:
            self.detach()
            self.prepareResult()
            if self.modally:
                self.EndModal(wx.CANCEL)
        else:
            self.EndModal(wx.OK)

    def OnKillbtnButton(self, event):
        if not self.finished:
            self.prepareResult()
            self.kill()
            if self.modally:
                self.EndModal(wx.CANCEL)
        else:
            self.EndModal(wx.OK)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    #cmd = '''python.exe -c "for i in range(2049):print '*',"'''
    cmd = '''python.exe -c "print '*'*5000"'''
    #cmd = '''python.exe -c "import time; time.sleep(10)"'''
    if 1:
        modal = 1
        dlg = ProcessProgressDlg(None, cmd, 'Test', modal, autoClose=False)
        if modal:
            dlg.ShowModal()
        #print dlg.errors, dlg.output
        dlg.Destroy()
        app.MainLoop()
    else:
        class TestProcessRunner(ProcessRunner):
            def updateErrStream(self, stream, data):
                txt = ProcessRunner.updateErrStream(self, stream, data)
                if txt is not None: print 'error: %s'%txt

            def updateOutStream(self, stream, data):
                txt = ProcessRunner.updateOutStream(self, stream, data)
                if txt is not None: print 'output: %s'%txt

            def OnProcessEnded(self, event):
                ProcessRunnerMix.OnProcessEnded(self, event)
                # Test doesn't terminate, don't know why :(
                app.ExitMainLoop()

        tpr = TestProcessRunner()
        #cmd = 'cvs -H status'
        tpr.execute(cmd)
        app.MainLoop()
