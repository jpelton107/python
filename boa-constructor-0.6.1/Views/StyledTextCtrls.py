#-----------------------------------------------------------------------------
# Name:        StyledTextCtrls.py
# Purpose:     Mixin classes to extend wx.stc.StyledTextCtrl
#
# Author:      Riaan Booysen
#
# Created:     2000/04/26
# RCS-ID:      $Id: StyledTextCtrls.py,v 1.39 2007/07/02 15:01:16 riaan Exp $
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, re, keyword, string

import wx
import wx.stc

eols = {  wx.stc.STC_EOL_CRLF : '\r\n',
          wx.stc.STC_EOL_CR   : '\r',
          wx.stc.STC_EOL_LF   : '\n'}

import Preferences
from Utils import _

import methodparse
import STCStyleEditor

# from PythonWin from IDLE :)
_is_block_opener = re.compile(r':\s*(#.*)?$').search
_is_block_closer = re.compile(r'''
    \s*
    ( return
    | break
    | continue
    | raise
    | pass
    )
    \b
''', re.VERBOSE).match


def ver_tot(ma, mi, re):
    return ma*10000+mi*100+re

word_delim  = string.letters + string.digits + '_'
object_delim = word_delim + '.'

#---Utility mixins--------------------------------------------------------------

class FoldingStyledTextCtrlMix:
    def __init__(self, wId, margin):
        self.__fold_margin = margin
        if Preferences.edSTCFolding:
            self.SetProperty('fold', '1')
        self.SetMarginType(margin, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(margin, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(margin, True)
        self.SetMarginWidth(margin, Preferences.STCFoldingMarginWidth)

        markIdnt, markBorder, markCenter = Preferences.STCFoldingClose
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER, 
              markIdnt, markBorder, markCenter)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND, 
              wx.stc.STC_MARK_EMPTY, markBorder, markCenter)

        markIdnt, markBorder, markCenter = Preferences.STCFoldingOpen
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN, 
              markIdnt, markBorder, markCenter)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, 
              wx.stc.STC_MARK_EMPTY, markBorder, markCenter)

        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, 
              wx.stc.STC_MARK_BACKGROUND, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB, 
              wx.stc.STC_MARK_BACKGROUND, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL, 
              wx.stc.STC_MARK_BACKGROUND, "white", "black")

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == self.__fold_margin:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self, expanding=None):
        lineCount = self.GetLineCount()

        if expanding is None:
            expanding = True
    
            # find out if we are folding or unfolding
            for lineNum in range(lineCount):
                if self.GetFoldLevel(lineNum) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                    expanding = not self.GetFoldExpanded(lineNum)
                    break

        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
               (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == wx.stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1;

        return line

def idWord(line, piv, lineStart, leftDelim=word_delim, rightDelim=word_delim):
    if piv >= len(line):
        return 0, 0
    pivL = pivR = piv
    # Look left
    for pivL in range(piv, -1, -1):
        if not line[pivL] in leftDelim:
            pivL = pivL + 1
            break
    # Look right
    for pivR in range(piv + 1, len(line)):
        if not line[pivR] in rightDelim:
            break
    else:
        pivR = pivR+1

    return pivL + lineStart, pivR - pivL

class BrowseStyledTextCtrlMix:
    """ This class is to be mix-in with a wxStyledTextCtrl to add
        functionality for browsing the code.
    """
    def __init__(self, indicator=0):
        self.handCrs = 1
        self.stndCrs = 0

        self.IndicatorSetStyle(indicator, wx.stc.STC_INDIC_PLAIN)
        self.IndicatorSetForeground(indicator, wx.BLUE)
        self._indicator = indicator
        self.styleStart = 0
        self.styleLength = 0
        self.ctrlDown = False
        self.Bind(wx.EVT_MOTION, self.OnBrowseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnBrowseClick)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def doClearBrwsLn(self):
        self.styleStart, self.styleLength = \
            self.clearUnderline(self.styleStart, self.styleLength)

    def BrowseClick(self, word, line, lineNo, start, style):
        """Called when a link is clicked.
           Override to use, return True if click is swallowed """
        return False

    def StyleVeto(self, style):
        return False

    # XXX Setting the cursor irrevocably changes the cursor for the whole STC
    def underlineWord(self, start, length):
        #self.SetCursor(self.handCrs)
        self.SetLexer(wx.stc.STC_LEX_NULL)

        self.StartStyling(start, wx.stc.STC_INDICS_MASK)
        self.SetStyling(length, wx.stc.STC_INDIC0_MASK)
        return start, length

    def clearUnderline(self, start, length):
        #self.SetCursor(self.stndCrs)

        self.StartStyling(start, wx.stc.STC_INDICS_MASK)
        self.SetStyling(length, 0)
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.Refresh(False)
        return 0, 0

    def getBrowsableText(self, line, piv, lnStPs):
        return idWord(line, piv, lnStPs)

    def OnBrowseMotion(self, event):
        event.Skip()
        #check if words should be underlined
        if event.ControlDown():
            mp = event.GetPosition()
            pos = self.PositionFromPoint(wx.Point(mp.x, mp.y))

            stl = self.GetStyleAt(pos) & 31

            if self.StyleVeto(stl):
                if self.styleLength > 0:
                    self.styleStart, self.styleLength = \
                      self.clearUnderline(self.styleStart, self.styleLength)
                return

            lnNo = self.LineFromPosition(pos)
            lnStPs = self.PositionFromLine(lnNo)
            line = self.GetLine(lnNo)
            piv = pos - lnStPs
            start, length = self.getBrowsableText(line, piv, lnStPs)
            #mark new
            if length > 0 and self.styleStart != start:
                if self.styleLength > 0:
                    self.clearUnderline(self.styleStart, self.styleLength)
                self.styleStart,self.styleLength = \
                  self.underlineWord(start, length)
            #keep current
            elif self.styleStart == start: pass
            #delete previous
            elif self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)

        #clear any underlined words
        elif self.styleLength > 0:
            self.styleStart, self.styleLength = \
              self.clearUnderline(self.styleStart, self.styleLength)

    def getStyledWordElems(self, styleStart, styleLength):
        if styleLength > 0:
            lnNo = self.LineFromPosition(styleStart)
            lnStPs = self.PositionFromLine(lnNo)
            line = self.GetLine(lnNo)
            start = styleStart - lnStPs
            word = line[start:start+styleLength]
            return word, line, lnNo, start
        else:
            return '', 0, 0, 0

    def OnBrowseClick(self, event):
        word, line, lnNo, start = self.getStyledWordElems(self.styleStart, self.styleLength)
        if word:
            style = self.GetStyleAt(self.styleStart) & 31
            if self.BrowseClick(word, line, lnNo, start, style):
                return
        event.Skip()

    def OnKeyDown(self, event):
        if event.ControlDown(): self.ctrlDown = True
        event.Skip()

    def OnKeyUp(self, event):
        if self.ctrlDown and (not event.ControlDown()):
            self.ctrlDown = False
            if self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)
        event.Skip()

class CodeHelpStyledTextCtrlMix:
    def getCurrLineInfo(self):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.PositionFromLine(lnNo)
        return (pos, lnNo, lnStPs,
                self.GetCurLine()[0], pos - lnStPs - 1)

    def getFirstContinousBlock(self, docs):
        docs = docs.strip()
        res = []
        for line in docs.split('\n'):
            if line.strip():
                res.append(line)
            else:
                break
        return '\n'.join(res)


class AutoCompleteCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):
    """ Mixin that assists with code completion

        Users should implement:
        def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
            return ['list', 'of', 'options']
    """

    def __init__(self):
        self.AutoCompSetIgnoreCase(True)
        self.AutoCompSetCancelAtStart(False)

    def codeCompCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        start, length = idWord(line, piv, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        pivword = piv - startLine

        dot = word.rfind('.', 0, pivword+1)
        matchWord = word
        if dot != -1:
            rdot = word.find('.', pivword)
            if rdot != -1:
                matchWord = word[dot+1:rdot]
            else:
                matchWord = word[dot+1:]

            offset = pivword - dot
            rootWord = word[:dot]
        else:
            offset = pivword + 1
            rootWord = ''

        if not matchWord:
            offset = 0

        names = self.getCodeCompOptions(word, rootWord, matchWord, lnNo)

        # remove duplicates and sort
        unqNms = {}
        for name in names: unqNms[name] = None
        names = unqNms.keys()

        sortnames = [(name.upper(), name) for name in names]
        sortnames.sort()
        names = [n[1] for n in sortnames]

        # move _* names to the end of the list
        cnt = 0
        maxmoves = len(names)
        while cnt < maxmoves:
            if names[0] and names[0][0] == '_':
                names.append(names[0])
                del names[0]
                cnt = cnt + 1
            else:
                break

        if names:
            self.AutoCompShow(offset, ' '.join(names))
        #self.AutoCompSelect(matchWord)

class CallTipCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):
    """ Mixin that assists with code completion

        Users should implement:
            def getTipValue(word, lnNo):
                return 'Tip'
    """
    def __init__(self):
        self.lastCallTip = ''
        self.lastTipHilite = (0, 0)

        self.CallTipSetBackground(Preferences.STCCallTipBackColour)

    def getTipValue(self, word, lnNo):
        return ''

    def callTipCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        bracket = methodparse.matchbracket(line[:piv+1], '(')
        if bracket == -1 and self.CallTipActive():
            self.CallTipCancel()
            return

        cursBrktOffset = piv - bracket

        start, length = idWord(line, bracket-1, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        if word:
            tip = self.getTipValue(word, lnNo)
            if tip:
                # Minus offset of 1st bracket in the tip
                tipBrkt = tip.find('(')
                if tipBrkt != -1:
                    pos = pos - tipBrkt - 1
                else:
                    tipBrkt = 0

                # get the current parameter from source
                paramNo = len(methodparse.safesplitfields(\
                      line[bracket+1:piv+1]+'X', ','))
                if paramNo:
                    paramNo = paramNo - 1

                # get hilight & corresponding parameter from tip
                tipBrktEnd = tip.rfind(')')
                tip_param_str = tip[tipBrkt+1:tipBrktEnd]
                tip_params = methodparse.safesplitfields(\
                    tip_param_str, ',', ('(', '{'), (')', '}') )
                try:
                    hiliteStart = tipBrkt+1 + tip_param_str.find(tip_params[paramNo])
                except IndexError:
                    hilite = (0, 0)
                else:
                    hilite = (hiliteStart,
                              hiliteStart+len(tip_params[paramNo]))

                # don't update if active and unchanged
                if self.CallTipActive() and tip == self.lastCallTip and \
                      hilite == self.lastTipHilite:
                    return

                # close if active and changed
                if self.CallTipActive() and (tip != self.lastCallTip or \
                      hilite != self.lastTipHilite):
                    self.CallTipCancel()

                self.CallTipShow(pos - cursBrktOffset, tip)

                self.CallTipSetHighlight(hilite[0], hilite[1])
                self.lastCallTip = tip
                self.lastTipHilite = hilite

class DebuggingViewSTCMix:
    def __init__(self, debugMarkers):

        (self.brkPtMrk, self.tmpBrkPtMrk, self.disabledBrkPtMrk,
         self.stepPosMrk) = debugMarkers

        # XXX properly allocate the marker
        self.stepPosBackMrk = self.stepPosMrk + 1

        # Initialize breakpoints from file and running debugger
        # XXX Remote breakpoints should be stored in a local pickle
        filename = self.model.filename

        from Debugger.Breakpoint import bplist
        self.breaks = bplist.getFileBreakpoints(filename)
        self.tryLoadBreakpoints()

    def setupDebuggingMargin(self, symbolMrg):
        self.SetMarginType(symbolMrg, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginWidth(symbolMrg, Preferences.STCSymbolMarginWidth)
        self.SetMarginSensitive(symbolMrg, True)

        markIdnt, markBorder, markCenter = Preferences.STCBreakpointMarker
        self.MarkerDefine(self.brkPtMrk, markIdnt, markBorder, markCenter)

        markIdnt, markBorder, markCenter = Preferences.STCLinePointer
        self.MarkerDefine(self.stepPosMrk, markIdnt, markBorder, markCenter)

        markIdnt, markBorder, markCenter = Preferences.STCTmpBreakpointMarker
        self.MarkerDefine(self.tmpBrkPtMrk, markIdnt, markBorder, markCenter)

        markIdnt, markBorder, markCenter = Preferences.STCDisabledBreakpointMarker
        self.MarkerDefine(self.disabledBrkPtMrk, markIdnt, markBorder, markCenter)

        try:
            wx.stc.STC_MARK_BACKGROUND
        except:
            self.MarkerDefine(self.stepPosBackMrk, wx.stc.STC_MARK_EMPTY,
                              wx.Colour(255, 255, 255), wx.Colour(128, 128, 255))
        else:
            self.MarkerDefine(self.stepPosBackMrk, wx.stc.STC_MARK_BACKGROUND,
                              wx.Colour(255, 255, 255), wx.Colour(220, 220, 255))


    def setInitialBreakpoints(self):
        # Adds markers where the breakpoints are located.
        for mrk in (self.tmpBrkPtMrk, self.disabledBrkPtMrk, self.brkPtMrk):
            self.MarkerDeleteAll(mrk)
        for brk in self.breaks.listBreakpoints():
            self.setBreakMarker(brk)

    def setBreakMarker(self, brk):
        if brk['temporary']: mrk = self.tmpBrkPtMrk
        elif not brk['enabled']: mrk = self.disabledBrkPtMrk
        else: mrk = self.brkPtMrk
        lineno = brk['lineno'] - 1
        currMrk = self.MarkerGet(lineno) & (1 << mrk)
        if currMrk:
            self.MarkerDelete(lineno, mrk)
        self.MarkerAdd(lineno, mrk)

    def deleteBreakMarkers(self, lineNo):
        self.MarkerDelete(lineNo - 1, self.brkPtMrk)
        self.MarkerDelete(lineNo - 1, self.tmpBrkPtMrk)
        self.MarkerDelete(lineNo - 1, self.disabledBrkPtMrk)

    def deleteBreakPoint(self, lineNo):
        self.breaks.deleteBreakpoints(lineNo)
        debugger = self.model.editor.debugger
        if debugger:
            # Try to apply to the running debugger.
            debugger.deleteBreakpoints(self.model.filename, lineNo)
        self.deleteBreakMarkers(lineNo)

    def addBreakPoint(self, lineNo, temp=0, notify_debugger=1):
        filename = self.model.filename

        self.breaks.addBreakpoint(lineNo, temp)
        if notify_debugger:
            debugger = self.model.editor.debugger
            if debugger:
                # Try to apply to the running debugger.
                debugger.setBreakpoint(filename, lineNo, temp)
        if temp: mrk = self.tmpBrkPtMrk
        else: mrk = self.brkPtMrk
        self.MarkerAdd(lineNo - 1, mrk)

    def moveBreakpoint(self, bpt, delta):
        # remove
        index = (bpt.file, bpt.line)

        if index not in bpt.bplist.keys():
            return

        bpt.bplist[index].remove(bpt)
        if not bpt.bplist[index]:
            del bpt.bplist[index]

        del self.breaks[bpt.line]

        bpt.line = bpt.line + delta

        # re-add
        index = (bpt.file, bpt.line)
        if bpt.bplist.has_key(index):
            bpt.bplist[index].append(bpt)
        else:
            bpt.bplist[index] = [bpt]

        self.breaks[bpt.line] = bpt

    def tryLoadBreakpoints(self):
        import pickle
        fn = self.getBreakpointFilename()

        if fn:
            rval = self.breaks.loadBreakpoints(fn)
            if rval:
                self.setInitialBreakpoints()
        else:
            rval = None
        return rval

    def saveBreakpoints(self):
        # XXX This is not yet called automatically on saving a module,
        # should it be ?
        fn = self.getBreakpointFilename()
        if fn:
            self.breaks.saveBreakpoints(fn)

    def clearStepPos(self, lineNo):
        if lineNo < 0:
            lineNo = 0
        self.MarkerDelete(lineNo, self.stepPosMrk)
        self.MarkerDelete(lineNo, self.stepPosBackMrk)

    def setStepPos(self, lineNo):
        if lineNo < 0:
            lineNo = 0
        self.MarkerDeleteAll(self.stepPosMrk)
        self.MarkerAdd(lineNo, self.stepPosMrk)
        self.MarkerDeleteAll(self.stepPosBackMrk)
        self.MarkerAdd(lineNo, self.stepPosBackMrk)

        if self.breaks.hasBreakpoint(lineNo + 1):
            # Be sure all the breakpoints for this file are displayed.
            self.setInitialBreakpoints()
        self.MarkerDelete(lineNo, self.tmpBrkPtMrk)

    def getBreakpointFilename(self):
        try:
            return os.path.splitext(self.model.assertLocalFile())[0]+'.brk'
        except AssertionError:
            return ''

    def adjustBreakpoints(self, linesAdded, modType, evtPos):
        line = self.LineFromPosition(evtPos)#event.GetPosition())

        endline = self.GetLineCount()
        if self.breaks.hasBreakpoint(
              min(line, endline), max(line, endline)):

            changed = self.breaks.adjustBreakpoints(line, linesAdded)
            debugger = self.model.editor.debugger
            if debugger:
                # XXX also check that module has been imported
                # XXX this should apply; with or without breakpoint
                if debugger.running and \
                      not modType & wx.stc.STC_PERFORMED_UNDO:
                    wx.LogWarning(_('Adding or removing lines from the '
                                    'debugger will cause the source and the '
                                    'debugger to be out of sync.'
                                    '\nPlease undo this action.'))

                debugger.adjustBreakpoints(self.model.filename, line,
                      linesAdded)
            else:
                # bdb must still be updated
                import bdb

                bpList = bdb.Breakpoint.bplist
                filename = self.model.filename #canonic form, same as url form I think
                setBreaks = []

                # store reference and remove from (fn, ln) refed dict.
                for bpFile, bpLine in bpList.keys():
                    if bpFile == filename and bpLine > line:
                        setBreaks.append(bpList[bpFile, bpLine])
                        del bpList[bpFile, bpLine]

                # put old break at new place and renumber
                for brks in setBreaks:
                    for brk in brks:
                        brk.line = brk.line + linesAdded
                        # merge in moved breaks
                        if bpList.has_key((filename, brk.line)):
                            bpList[filename, brk.line].append(brk)
                        else:
                            bplist[filename, brk.line] = [brk]

    def OnSaveBreakPoints(self, event):
        self.saveBreakpoints()

    def OnLoadBreakPoints(self, event):
        self.tryLoadBreakpoints()

    def OnSetBreakPoint(self, event):
        line = self.LineFromPosition(self.GetCurrentPos()) + 1
        if self.breaks.hasBreakpoint(line):
            self.deleteBreakPoint(line)
        else:
            self.addBreakPoint(line)

    def OnMarginClick(self, event):
        lineClicked = self.LineFromPosition(event.GetPosition()) + 1
        if self.breaks.hasBreakpoint(lineClicked):
            self.deleteBreakPoint(lineClicked)
        else:
            self.addBreakPoint(lineClicked)


#---Language mixins-------------------------------------------------------------
class LanguageSTCMix:
    def __init__(self, wId, marginNumWidth, language, config):
        self.language = language
        (cfg, self.commonDefs, self.styleIdNames, self.styles, psgn, psg, olsgn,
              olsg, ds, self.lexer, self.keywords, bi) = \
              self.getSTCStyles(config, language)

        #self.SetEOLMode(wx.stc.STC_EOL_LF)
        #self.eol = '\n'
        self.SetBufferedDraw(Preferences.STCBufferedDraw)
        self.SetCaretPeriod(Preferences.STCCaretPeriod)

        self.SetViewWhiteSpace(Preferences.STCViewWhiteSpace)
        self.SetViewEOL(Preferences.STCViewEOL)

        self.SetIndent(Preferences.STCIndent)
        self.SetUseTabs(Preferences.STCUseTabs)
        self.SetTabWidth(Preferences.STCTabWidth)
        self.SetCaretPeriod(Preferences.STCCaretPeriod)
        #if Preferences.STCCaretPolicy:
        #    self.SetCaretPolicy(Preferences.STCCaretPolicy,
        #                        Preferences.STCCaretPolicySlop)

        self.SetEdgeMode(Preferences.STCEdgeMode)
        self.SetEdgeColumn(Preferences.STCEdgeColumnWidth)

        if marginNumWidth:
            self.SetMargins(1, 1)
            self.SetMarginType(marginNumWidth[0], wx.stc.STC_MARGIN_NUMBER)
            self.SetMarginWidth(marginNumWidth[0], marginNumWidth[1])

        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI, id=wId)

    def setStyles(self, commonOverride=None):
        commonDefs = {}
        commonDefs.update(self.commonDefs)
        if commonOverride is not None:
            commonDefs.update(commonOverride)

        STCStyleEditor.setSTCStyles(self, self.styles, self.styleIdNames,
              commonDefs, self.language, self.lexer, self.keywords)

    def getSTCStyles(self, config, language):
        """ Override to set values directly """
        return STCStyleEditor.initFromConfig(config, language)


    keymap={'euro': {226: chr(124), 69: chr(128), 81: chr(64), 77: chr(181),
                     48: chr(125), 337: chr(126), 50: chr(178), 51: chr(179),
                     55: chr(123), 56: chr(91), 57: chr(93), 219: chr(92),
                    },
            'swiss-german': {192: chr(93), 226: chr(92), 50: chr(64),
                             51: chr(35), 55: chr(124), 186: chr(91),
                             219: chr(96), 220: chr(123), 221: chr(126),
                             223: chr(125),
                            },
            'italian': {192: chr(64), 337: chr(93), 186: chr(91), 219: chr(123),
                        221: chr(125), 222: chr(35),
                       },
            'france': {226: chr(54), 48: chr(64), 337: chr(125), 50: chr(126),
                       51: chr(35), 52: chr(123), 53: chr(91), 54: chr(124),
                       55: chr(96), 56: chr(92), 219: chr(93),
                      },
           }
    def handleSpecialEuropeanKeys(self, event, countryKeymap='euro'):
        key = event.GetKeyCode()
        keymap = self.keymap[countryKeymap]
        if event.AltDown() and event.ControlDown() and keymap.has_key(key):
            currPos = self.GetCurrentPos()
            self.InsertText(currPos, keymap[key])
            self.SetCurrentPos(self.GetCurrentPos()+1)
            self.SetSelectionStart(self.GetCurrentPos())


stcConfigPath = os.path.join(Preferences.rcPath, 'stc-styles.rc.cfg')

class PythonStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId, margin):
        LanguageSTCMix.__init__(self, wId, margin, 'python', stcConfigPath)

        # XXX add 'with'. here or in stc config?
        self.keywords += ' yield None True False'

        self.setStyles()

    def grayout(self, do):
        if not Preferences.grayoutSource: return
        if do: f = {'backcol': '#EEF2FF'}
        else: f = None
        self.setStyles(f)

    def OnUpdateUI(self, event):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            try:
                charBefore = chr(self.GetCharAt(caretPos - 1))
            except ValueError:
                charBefore = ''
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and charBefore in "[]{}()" and styleBefore == 10:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            try:
                charAfter = chr(self.GetCharAt(caretPos))
            except ValueError:
                charAfter = ''
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and charAfter in "[]{}()" and styleAfter == 10:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            # self.Refresh(False)

    def doAutoIndent(self, prevline, pos):
        stripprevline = prevline.strip()
        if stripprevline:
            indent = prevline[:prevline.find(stripprevline)]
        else:
            try:
                indent = prevline.strip('\r\n', 1)
            except TypeError:
                indent = prevline
                while indent and indent[-1] in ('\r', '\n'):
                    indent = indent[:-1]

        if self.GetUseTabs():
            indtBlock = '\t'
        else:
            # XXX Why did I do this?
            indtBlock = self.GetTabWidth()*' '

        if _is_block_opener(prevline):
            indent = indent + indtBlock
        elif _is_block_closer(prevline):
            indent = indent[:-1*len(indtBlock)]

        self.BeginUndoAction()
        try:
            self.InsertText(pos, indent)
            self.GotoPos(pos + len(indent))
        finally:
            self.EndUndoAction()

class TextSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'text', stcConfigPath)
        self.setStyles()

## 1 :
## 2 : diff
## 3 : +++/---
## 4 : @
## 5 : -
## 6 : +
class DiffSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'diff', stcConfigPath)
        self.setStyles()

from types import IntType, SliceType, StringType
class STCLinesList:
    def __init__(self, STC):
        self.__STC = STC

    def _rememberPos(self):
        self.__pos = self.GetCurrentPos()

    def __getitem__(self, key):
        if type(key) is IntType:
            # XXX last char is garbage
            if key < len(self):
                return self.__STC.GetLine(key)
            else:
                raise IndexError
        elif type(key) is SliceType:
            res = []
            for idx in range(key.start, key.stop):
                res.append(self[idx])
            return res
        else:
            raise TypeError, _('%s not supported') % `type(key)`

    def __setitem__(self, key, value):
        stc = self.__STC
        if type(key) is IntType:
            assert type(value) is StringType
            if key < len(self):
                stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key))
                stc.ReplaceSelection(value)
            else:
                raise IndexError
        elif type(key) is SliceType:
            lines = eols[stc.GetEOLMode()].join(value)
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop))
            stc.ReplaceSelection(lines)
        else:
            raise TypeError, _('%s not supported') % `type(key)`

    def __delitem__(self, key):
        stc = self.__STC
        if type(key) is IntType:
            stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key)+1)
            stc.ReplaceSelection('')
        elif type(key) is SliceType:
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop)+1)
            stc.ReplaceSelection('')
        else:
            raise TypeError, _('%s not supported') % `type(key)`

    def __getattr__(self, name):
        if name == 'current':
            return self.__STC.GetCurrentLine()
        if name == 'count':
            return self.__STC.GetLineCount()
        if name == 'size':
            return self.__STC.GetTextLength()
        # dubious
        if name == 'line':
            return self.__STC.GetCurLine()[0]
        # dubious
        if name == 'pos':
            return self.__STC.GetCurrentPos()

        raise AttributeError, name

    def __len__(self):
        return self.__STC.GetLineCount()
