#Boa:WizardPage:wxWizardPage1

import wx
import wx.wizard

[wxID_WXWIZARDPAGE1] = [wx.NewId() for _init_ctrls in range(1)]

class wxWizardPage1(wx.wizard.WizardPage):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.wizard.WizardPage.__init__(self, bitmap=wx.NullBitmap, parent=prnt)
        self.SetSize(wx.Size(960, 692))
        self.SetClientSize(wx.Size(952, 665))
        self.SetPosition(wx.Point(88, 88))

    def __init__(self, parent):
        self._init_ctrls(parent)
