import wx
import socket, ssl, pprint
import sys, time, os
import binascii
import struct
import fcntl
import threading
import random

UDP_PORT = 4434
TCP_PORT = 4082

#variables
WIFI_HOST_IP = '192.168.1.101'
IP = WIFI_HOST_IP

class LeftPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        self.text = parent.GetParent().rightPanel.texto
        
        button1 = wx.Button(self, -1, '+', (10, 10))
        button2 = wx.Button(self, -1, '-', (10, 60))
        self.Bind(wx.EVT_BUTTON, self.OnPlus, id=button1.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnMinus, id=button2.GetId())

    def OnPlus(self, event):
        value = int(self.text.GetLabel())
        value = value + 1
        self.text.SetLabel(str(value))
        
    def OnMinus(self, event):
        value = int(self.text.GetLabel())
        value = value - 1
        self.text.SetLabel(str(value))

class RightPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.texto = wx.StaticText(self, -1, '0', (40, 60))        

class Communicate(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(280, 200))

        panel = wx.Panel(self, -1)

        self.rightPanel = RightPanel(panel, -1)
        leftPanel = LeftPanel(panel, -1)
        hbox = wx.BoxSizer()
        hbox.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(hbox)

        self.tmr_timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr1_handler, self.tmr_timer1)
        self.tmr_timer1.Start(1000)

        self.textum = GetParent().rightPanel.texto

        self.Centre()
        self.Show(True)
        
    def tmr1_handler(self, event):
        value = int(self.text.GetLabel())
        value = value + 1
        self.textum.SetLabel(str(value))
 
# Run the program
app = wx.App()
Communicate(None, -1, 'widgets communicate')
app.MainLoop()

