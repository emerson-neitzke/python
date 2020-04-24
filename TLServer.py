import wx
import socket, ssl, pprint
import sys, time, os
import binascii

PORT = 4080

#variables
r = 0
estado = 0
c = 0

class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "TLS Server", 
                                   size=(640,480))
 
        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
 
#		self.statusbar = self.CreateStatusBar()
        self.toggleBtn = wx.Button(panel, wx.ID_ANY, "Anuncio UDP")
#        self.toggleBtn = wx.Button(panel, wx.ID_ANY, "Config")
        self.toggleBtn.Bind(wx.EVT_BUTTON, self.onToggle)

 
    def onToggle(self, event):
        btnLabel = self.toggleBtn.GetLabel()
        if btnLabel == "Start":
            print "starting timer..."
	    wx.StaticText(panel, -1, "Waiting for connection...", (100, 10))
            self.timer.Start(1000)
            self.toggleBtn.SetLabel("Stop")
        else:
            print "timer stopped!"
            self.timer.Stop()
            self.toggleBtn.SetLabel("Start")
 
    def update(self, event):
        print "\nupdated: ",
        print time.ctime()
 
# Run the program
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()

