#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#####
# pyPlag
#
# Copyright 2012, erebos42 (https://github.com/erebos42/miscScripts)
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA, or see the FSF site: http://www.fsf.org.
#####

"""gui, to check via google if file is a plagiarism"""

# TODO:
# -  

import pyPlag
import webbrowser
import wx
import hashlib

appTitle = 'wxPlag'
appVersion = '0.1'
appAuthor = 'Christian Wichmann'
windowSize = wx.Size(800,600)

SCAN_BUTTON = wx.NewId()


class wxPlagFrame(wx.Frame):
    """main window of app"""
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self,parent,ID,title,pos=wx.DefaultPosition,size=windowSize)
        
        # build frame 
        self.textField = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.butadd = wx.Button(self, SCAN_BUTTON, "Scan text for plagiarism...")
        self.butadd.Bind(wx.EVT_BUTTON, self.onClick)
        
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2.Add(self.butadd, 1, wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textField, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        #self.sizer.Fit(self)
        
        self.textField.SetFocus()
        self.Show()
 
    def close(self, event):
        self.Destroy()
        
    def onClick(self, event):
        inputText = self.textField.GetValue().encode('utf-8')
        textHash = hashlib.md5(inputText).hexdigest()
        textfile = textHash + ".txt"
        htmlfile = textHash + ".html"
        fd = open(textfile, 'w')
        fd.write(inputText)
        fd.close()
        data = pyPlag.checkforplag_sentence(textfile)
        pyPlag.outputtohtml(htmlfile, data)
        webbrowser.open_new_tab(htmlfile)


class wxPlag(wx.App):
    """main app class"""
    def OnInit(self):
        self.frame = wxPlagFrame(None, -1, appTitle+' '+appVersion)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    wxPlag = wxPlag(0)
    wxPlag.MainLoop()

