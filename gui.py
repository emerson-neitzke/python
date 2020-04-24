import wx
import socket, ssl, pprint
import sys, time, os
import binascii
import struct
import fcntl
import threading

UDP_PORT = 4434
TCP_PORT = 4082

#variables
WIFI_HOST_IP = '192.168.1.112'
IP = WIFI_HOST_IP

class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(480,320))

        self.Centre()
        self.myVar = None
        self.count = 0
        self.sock_udp = 0
        self.socket_tcp = 0
        self.ip_addr = IP

#<thread>
        self.t1 = threading.Thread(target=self.th1,args=("thread 1 sendo executada",))
        self.t1.start()
#</thread>

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY, (0,0),(50,100),name="D1")
        self.SetBackgroundColour('gray')
#<timer>
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr_handler, self.timer)
#</timer>

#<button>
        self.toggleBtn = wx.Button(self, wx.ID_ANY, "Conectar", (150,20), (100,25))
        self.toggleBtn.Bind(wx.EVT_BUTTON, self.onToggle)
        self.button2 = wx.Button(self, wx.ID_ANY, "", (240,255), (120,20))
        self.button2.Bind(wx.EVT_BUTTON, self.button2_handler)
#</button>

#<label>
        self.Label1 = wx.StaticText(self, -1, "0", (150, 120))
#</label>

#<status bar>
        self.statusbar = self.CreateStatusBar(4)
        self.statusbar.SetStatusWidths([140, 100, 100, 140])
        self.statusbar.Show()
        self.statusbar.SetStatusText("")
#</status bar>

#<gauge>
        self.progress = wx.Gauge(self, -1, 100, (50,80), size=(220, 25))
#</gauge>

    def onToggle(self, event):
        btnLabel = self.toggleBtn.GetLabel()
        if btnLabel == "Conectar":
            print "starting timer..."
            self.timer.Start(1000)
            self.toggleBtn.SetLabel("Desconectar")
            self.anuncio_init()
            self.anuncio_open()
            self.tls_open()
        else:
            print "timer stopped!"
            self.timer.Stop()
            self.toggleBtn.SetLabel("Conectar")
            self.socket_tcp.close()

    def button2_handler(self, event):
        btnLabel = self.button2.GetLabel()
        return btnLabel

    def tmr_handler(self, event):
#       print "\nupdated: ",
#       print time.ctime()
        val = int(self.Label1.GetLabel())
        val = val + 1
        self.Label1.SetLabel(str(val))
        self.progress.SetValue(self.count)

        self.anuncio_broadcast()

        self.count +=1
        if self.count == 100:
            self.count = 0
            self.Label1.SetLabel("0")

    def anuncio_broadcast(self):
        ip  = bytearray(4)
        msg = bytearray(14)

        ip = [int(x) for x in self.ip_addr.split('.')]

        msg[0] = 0
        msg[1] = ord('L')
        msg[2] = ord('I')
        msg[3] = ord('F')
        msg[4] = ord('E')
        msg[5] = ord('S')
        msg[6] = ord('M')
        msg[7] = ord('T')
        msg[8] = ord('V')
        msg[9] = ord('X')
        msg[10:13] = ip
        msg[14:15] = struct.pack('>H', TCP_PORT)

        self.sock_udp.sendto(msg, ('<broadcast>', UDP_PORT))

    def anuncio_init(self):
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def anuncio_open(self):
        #self.statusbar.SetStatusText("ip:" + self.ip_addr +" | " + "udp Port:" + str(UDP_PORT) + " | " + "tcp Port:" + str(TCP_PORT))
        self.statusbar.SetStatusText("ip:" + self.ip_addr, 0)
        self.statusbar.SetStatusText("udp Port:" + str(UDP_PORT), 1)
        self.statusbar.SetStatusText("tcp Port:" + str(TCP_PORT), 2)
        self.statusbar.SetStatusText("seq. number:0", 3)
        self.sock_udp.bind((self.ip_addr, UDP_PORT))

    def tls_open(self):
        self.socket_tcp = socket.socket()
        self.socket_tcp.bind(('', TCP_PORT))
        self.socket_tcp.listen(5)
        self.th1 = threading.Thread(target=self.thread_inconnection,args=("thread inconnection sendo executada",1234))
        self.th1.start()

    def thread_client(self, arg):
        while True:

            time.sleep(1)

    def thread_inconnection(self, arg1, arg2):
        print arg1, arg2
        while True:
            newsocket, fromaddr = self.socket_tcp.accept()

            time.sleep(1)

    def th1(self, arg):
        while True:
            print arg
            time.sleep(1)
 
# Run the program
if __name__ == "__main__":
    app = wx.App()
    frame = MyForm().Show()
    app.MainLoop()

