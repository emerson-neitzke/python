#=======================================================================================
#
#                 		Python TLS Server 
#
#=======================================================================================
# Main File           : wxform.py
# Inicio Projeto      : 
# Version             : 
# Compiler            : gcc
# Desenvolvimento     : emerson.goulart@lifemed.com.br
#
# Description         : 
#
#=======================================================================================
#
# Instalacao Windows
# 1 - instalar python-2.7.16.amd64;
# 2 - instalar wxpython(https://pypi.org/project/wxPython/) usando o comando 'pip install wxPython';
# 3*- adicionar o arquivo executavel do python e a pasta /Python27/Script nas variaveis de ambiente windows;
# 4 - rodar o teste clicando no atalho 'Rodar - Teste Wi-Fi';
# 5 - para parar o teste executar o atalho 'Parar - Teste-Wi-fi';
#
# 3* - Acessar PaineldeControle/Sistema/ConfiguracoesAvancadasdoSistema/VariaveisdeAmbiente
#      Em Variaveis do Sistema clicar em Path e, em seguida em Editar
#      Na tela que abrir clique em novo e, no campo em branco que aparecer cole o caminho da pasta Python27(C:\Python27)
#      Repetir e adicionar a pasta Scripts(C:\Python27\Scripts)
#      Reiniciar o micro
#
# Todos os arquivos necessarios se encontram em 'C:/Python'
# 
# Scripts
#
# Prompt Syntax:
#
# Executar script:
# runserv.bat <row> <col>
# runserv.bat 2 2     //server rodando no ip da rede com 2x2 instancias
#
# Parar:
# stopserv.bat
#
#
# <runserv.bat>
#
# @echo off
# echo Este batch funciona em Windows somente
# echo Python TLS Multiclient Server v1.0
# echo emerson.goulart@lifemed.com.br
# rem IP_GET
# for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %ComputerName% ^| findstr [') do set NetworkIP=%%a
# echo Server IP: %NetworkIP%
# echo Running...
#
# rem set ip=%1
# set row=%1
# set col=%2
#
# set /a x=0
# set /a y=0
# set /a i=0
#
# rem set /a size=%row% * %col%
# rem echo %size%
#
# for /L %%r in (1,1,%row%) do call :calc_y %%r
# goto :eof
#
# :calc_y
# set /a temp=%1
# set /a y=((%temp% - 1) * 220) + 20
# rem echo %y%
#
# for /L %%c in (1,1,%col%) do call :calc_x %%c
# set /a x=0
# goto :eof
#
# :calc_x
# set /a temp=%1
# set /a i=%i% + 1
# set /a x=((%temp% - 1) * 328) + 20
# rem echo %x%
# rem echo %i%
#
# rem start python wxform.py %i% %ip% %x% %y%
# start python wxform.py %i% %NetworkIP% %x% %y%
#
# rem goto :eof
#
# </runserv.bat>
#
# <stopserv.bat>
#
# @echo off
# Taskkill /IM python.exe /F
#
# </stopserv.bat>
#
#
# Instalacao Linux
# 1 - Baixar o arquivo "wxPython-4.0.2-cp27-cp27mu-linux_x86_64.whl" em https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04/
#
# 2 - Executar o comando: 
#	sudo pip install wxPython-4.0.2-cp27-cp27mu-linux_x86_64.whl 
#
#
# Script
#
# <run.sh>
#
# !/bin/bash
# ip=$1
# row=$2
# col=$3
# x=0
# y=0
# i=0
#
# for((r=1;r<=row;r+=1));
# do
#	y=$((r-1))
#	y=$((y*220))
#	y=$((y+20))
#	if [ "$y" -gt 440 ]; then
#		y=$((y-9))
#	fi
#	for((c=1;c<=col;c+=1));
#	do
#		i=$((i+1))
#		x=$((c-1))
#		x=$((x*328))
#		x=$((x+20))
#		python wxform.py $i $ip $x $y &done
#!		echo $i
#!		echo $x
#!		echo $y
#	done
#	x=0
#done
#
# </run.sh>
# 
# Executar script:
# ./run.sh <ip> <row> <col>
# $ sudo ./run.sh 10.42.0.1 2 2		//server rodando no ip 10.42.0.1 com 2x2 instancias
#
#=======================================================================================
# 15/01/2020    gerada versao 1.01
#               - implementado suporte a mensagem 12h(Modcom requisita status dos 
#		  ponteiros do datalogger do LifeView);
#
#=======================================================================================

VERSION = "1.01"

from datetime import datetime
import wx
import socket, ssl, pprint
import sys, time, os
import binascii
import struct
import fcntl
import threading
import random
import re
import sys

UDP_PORT = 4434
TCP_PORT = 4082

recv = ""
recv2 = ""
medicine1 = ""
medicine2 = ""
fluxo1 = ""
fluxo2 = ""
status_bar = ""
pan1_color = ""
pan2_color = ""
datalog_canal1 = ""
datalog_canal2 = ""
stat_equipament1 = "Equipamento Desconectado"
stat_equipament2 = "Equipamento Desconectado"
unidade1 = ""
unidade2 = ""
ip_addr = "127.0.0.1"
power = ""
infusion_mod = ""
tipo_de_paciente = "Adulto"
ttconnect = ""
thoras = 0
tmin = 0
tsec = 0
ttsec = 0

status_dl_1 = 0x01
status_dl_2 = 0x01
reg_number_dl_1 = 0xE4
reg_number_dl_2 = 0xF0

os.system('clear')
#os.system('cls')

#variables
#WIFI_HOST_IP = '192.168.1.106'

WIFI_HOST_IP = str(sys.argv[2])

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

class BottonPanel(wx.Panel):
    def __init__(self, parent, id, posxy, sizexy):
        wx.Panel.__init__(self, parent, id, pos=posxy, size=sizexy, style=wx.NO_BORDER)
        self.SetBackgroundColour((179, 179, 179))
        button = wx.Button(self, -1, '+', (10, 10))

class StatusPanel(wx.Panel):
    def __init__(self, parent, id, posxy, sizexy, caption):
        wx.Panel.__init__(self, parent, id, pos=posxy, size=sizexy, style=wx.SUNKEN_BORDER)
        self.device = wx.StaticText(self, -1, caption, (15, 63))
        #self.tconnect = wx.StaticText(self, 1, "00:00:00", (8, 72))
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.device.SetFont(self.font)
        #self.tconnect.SetFont(self.font)

class StatusBar(wx.Panel):
    def __init__(self, parent, id, posxy, sizexy, caption):
        wx.Panel.__init__(self, parent, id, pos=posxy, size=sizexy, style=wx.SUNKEN_BORDER)
        self.tipo_paciente = wx.StaticText(self, -1, caption, (115, 3))
        self.tconnect = wx.StaticText(self, -1, "", (170, 3))
        self.power = wx.StaticText(self, -1, "", (25, 3))
        self.modo_infusao = wx.StaticText(self, -1, "VOL", (230, 3))
        self.font = wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.tipo_paciente.SetFont(self.font)
        self.power.SetFont(self.font)
        self.modo_infusao.SetFont(self.font)
        self.tconnect.SetFont(self.font)

class CanalPanel(wx.Panel):
    def __init__(self, parent, id, posxy, sizexy, color):
        wx.Panel.__init__(self, parent, id, pos=posxy, size=sizexy, style=wx.SUNKEN_BORDER)
        #self.SetBackgroundColour(color)
        self.dev_status = wx.StaticText(self, -1, "Equipamento Desconectado", (50, 25))
        self.nome_med = wx.StaticText(self, -1, "", (2, 2))
        self.tempo_restante = wx.StaticText(self, -1, "", (185, 12))
        self.fluxo = wx.StaticText(self, -1, "", (100, 25))
        self.unidade = wx.StaticText(self, -1, "", (100, 44))
        self.font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.tempo_restante.SetFont(self.font)
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.nome_med.SetFont(self.font)
        self.font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.fluxo.SetFont(self.font)
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.unidade.SetFont(self.font)
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.dev_status.SetFont(self.font)

        self.nome_medicamento = wx.StaticText(self, -1, "", (12, 30))

class cstruct:
        var_i = 0
        var_f = 0.0
        var_str = ""

class pump(wx.Panel):
    def __init__(self, parent, id, posxy, caption):
        wx.Panel.__init__(self, parent, id, pos=posxy, size=(317,159), style=wx.SUNKEN_BORDER)
        self.status = StatusPanel(self, -1, (0,0), (50,155),caption)
        self.status_bar = StatusBar(self, -1, (50,0), (264,20),tipo_de_paciente)
        self.canal1 = CanalPanel(self, -1, (50,20), (264,67), '#3c60f2')
        self.canal2 = CanalPanel(self, -1, (50,88), (264,67), '#c97406')

#<main_class>
class MyForm(wx.Frame):
     def __init__(self):
        #wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(650,280), style = wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(324,218), style = wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        #wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(327,212), style = wx.CAPTION)
        panel = wx.Panel(self, -1)

        self.counter = 0
        obj = cstruct()
        obj.var_i = 50

        self.ip_addr = IP
        self.tcp_port = random.randint(1000, 65000)

        #self.d1 = pump(panel, -1, (3,0), "01")
        self.d1 = pump(panel, -1, (3,0), str(sys.argv[1]))
        #self.d2 = pump(panel, -1, (326,0), "02")   #instancia dispositivo 2
#<button>
        #self.btn_conectar = wx.Button(panel, -1, 'Conectar', (4,163), (318,25))
        #self.btn_conectar.Bind(wx.EVT_BUTTON, self.onToggle)
#</button>

#<statusbar>
        self.statusbar = self.CreateStatusBar(3)
        self.statusbar.SetStatusWidths([175, 75, 75])
        self.statusbar.Show()
        self.statusbar.SetStatusText("Status")
#</statusbar>

        self.lbl1 = panel.GetParent().statusbar
        self.tempo = panel.GetParent().d1.canal1.tempo_restante
        self.tempo2 = panel.GetParent().d1.canal2.tempo_restante
        self.medic1 = panel.GetParent().d1.canal1.nome_med
        self.medic2 = panel.GetParent().d1.canal2.nome_med
        self.flux1 = panel.GetParent().d1.canal1.fluxo
        self.flux2 = panel.GetParent().d1.canal2.fluxo
        self.pan_canal1 = panel.GetParent().d1.canal1
        self.pan_canal2 = panel.GetParent().d1.canal2
        self.status_equipamento1 = panel.GetParent().d1.canal1.dev_status
        self.status_equipamento2 = panel.GetParent().d1.canal2.dev_status
        self.unidade1 = panel.GetParent().d1.canal1.unidade
        self.unidade2 = panel.GetParent().d1.canal2.unidade
        self.power = panel.GetParent().d1.status_bar.power
        self.modo = panel.GetParent().d1.status_bar.modo_infusao
        self.tipo_pacient = panel.GetParent().d1.status_bar.tipo_paciente
        self.ttime_connect = panel.GetParent().d1.status_bar.tconnect

        #self.lbl = panel.CanalPanel.GetParent()
        #self.lbl2.SetLabel("Tetratodoxina")
        #self.lbl3.SetLabel("Zyclon")
        #self.lbl3.SetLabel("Peridrociclopentanofenantreno")
        #self.lbl3.SetLabel("Tetranitrato de Pentaritritol")
        #print self.lbl1
        #print self.lbl2

#<timer broadcast>
        self.tmr_broadcast = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr1_broadcast_handler, self.tmr_broadcast)
#</timer broadcast>

#<timer visualizacao>
        self.tmr_visualiza = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr_visualiza_handler, self.tmr_visualiza)
#</timer visualizacao>

#<timer watchdog>
        self.tmr_watchdog = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr_watchdog_handler, self.tmr_watchdog)
#</timer watchdog>

#<timer tempo conexao>
        self.tmr_ttconnect = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmr_visual_tconnect_handler, self.tmr_ttconnect)
#</timer tempo conexao>

#<udp>
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_udp.bind((self.ip_addr, UDP_PORT))
#</udp>

#<tcp>
        self.socket_tcp = socket.socket()
        self.socket_tcp.bind(('', self.tcp_port))
        self.socket_tcp.listen(1)
#</tcp>

        self.threadStopped = False
        self.threadClientConnected = False
        self.watchdog_timeout = 0
        self.th1 = threading.Thread(target=self.thread_inconnection,args=("thread inconnection sendo executada",1234,self.tempo))
        self.th1.start()

        self.tmr_broadcast.Start(500)
        self.tmr_visualiza.Start(500)
        self.tmr_watchdog.Start(1000)

        self.x = int(sys.argv[3])
        self.y = int(sys.argv[4])

        #frame.SetTitle("TCH0123456")

        #self.Centre()
        #if int(sys.argv[1]) > 0 and int(sys.argv[1]) <= 3:
        #    self.SetPosition(wx.Point(100 + (int(sys.argv[1]) - 1) * 328, 100))
        #elif int(sys.argv[1]) > 3:
        #    self.SetPosition(wx.Point(100 + (int(sys.argv[1]) - 4) * 328, 312))
        self.SetPosition(wx.Point(self.x, self.y))
        #self.SetTitle("TCH16080079")
        self.Show(True)

# testBit()
     def testBit(self, int_type, offset):
        mask = 1 << offset
        return(int_type & mask)

# setBit()
     def setBit(self, int_type, offset):
        mask = 1 << offset
        return(int_type | mask)

# clearBit()
     def clearBit(self, int_type, offset):
        mask = ~(1 << offset)
        return(int_type & mask)

# toggleBit()
     def toggleBit(self, int_type, offset):
        mask = 1 << offset
        return(int_type ^ mask)

#calcula CRC_CCITT 16 bits
     def calcula_crc16(self, data, tamanho):
        crc_16 = 0
        current = 0

        crc_16 = (data[0] * 256) + data[1]
        current += 2

        for i in range(0, tamanho - 2):
          for j in range(7, -1, -1):
            if not self.testBit(crc_16, 15):
              crc_16 = (crc_16 << 1) & 0xFFFF
              if self.testBit(data[current], j):
                crc_16 = self.setBit(crc_16, 0)
              else:
                crc_16 = self.clearBit(crc_16, 0)
              continue
 
            crc_16 = (crc_16 << 1) & 0xFFFF
            if self.testBit(data[current], j):
                crc_16 = self.setBit(crc_16, 0)
            else:
                crc_16 = self.clearBit(crc_16, 0)
            crc_16 = (crc_16 ^ 0x1021) & 0xFFFF

          current += 1

        for x in range(0, 16):
            if not self.testBit(crc_16, 15):
                crc_16 = (crc_16 << 1) & 0xFFFF
                continue

            crc_16 = (crc_16 << 1) & 0xFFFF
            crc_16 = (crc_16 ^ 0x1021) & 0xFFFF

        return crc_16

#button
     def onToggle(self, event):
        btnLabel = self.btn_conectar.GetLabel()
        if btnLabel == "Conectar":
            print "starting timer..."
            self.tmr_broadcast.Start(500)
            self.tmr_visualiza.Start(500)
            self.btn_conectar.SetLabel("Desconectar")
            self.threadStopped = False
        else:
            print "timer stopped!"
            print "thread stopped!"
            self.tmr_broadcast.Stop()
            self.tmr_visualiza.Stop()
            self.threadStopped = True
            self.btn_conectar.SetLabel("Conectar")

     def tmr1_broadcast_handler(self, event):
        if not self.threadClientConnected:
            self.anuncio_broadcast()

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
        msg[14:15] = struct.pack('>H', self.tcp_port)

        try:
            self.sock_udp.sendto(msg, ('<broadcast>', UDP_PORT))
        except:
            print "Socekt Error...broadcast"

     #Timer de visualizacao	
     def tmr_visualiza_handler(self, event):
        self.tempo.SetLabel(recv)
        self.tempo2.SetLabel(recv2)
        self.medic1.SetLabel(medicine1)
        self.medic2.SetLabel(medicine2)
        self.flux1.SetLabel(str(fluxo1))
        self.flux2.SetLabel(str(fluxo2))
        self.statusbar.SetStatusText(ip_addr, 0)
        self.statusbar.SetStatusText(datalog_canal1, 1)
        self.statusbar.SetStatusText(datalog_canal2, 2)
        self.pan_canal1.SetBackgroundColour(pan1_color)
        self.pan_canal2.SetBackgroundColour(pan2_color)
        self.status_equipamento1.SetLabel(stat_equipament1)
        self.status_equipamento2.SetLabel(stat_equipament2)
        self.unidade1.SetLabel(unidade1)
        self.unidade2.SetLabel(unidade2)
        self.power.SetLabel(power)
        self.modo.SetLabel(infusion_mod)
        self.tipo_pacient.SetLabel(tipo_de_paciente)
        self.ttime_connect.SetLabel(ttconnect)

     def tmr_watchdog_handler(self, event):
        global stat_equipament1, stat_equipament2
        global recv, recv2, medicine1, medicine2, fluxo1, fluxo2, status_bar, pan1_color, pan2_color
        global datalog_canal1, datalog_canal2, unidade1, unidade2, ip_addr, tipo_de_paciente, ttconnect
        self.watchdog_timeout +=1
        if self.watchdog_timeout == 20 and self.threadClientConnected:
            self.watchdog_timeout = 0
            self.threadClientConnected = False
            self.SetTitle("")
            stat_equipament1 = "Equipamento Desconectado"
            stat_equipament2 = "Equipamento Desconectado"
            recv = ""
            recv2 = ""
            medicine1 = ""
            medicine2 = ""
            fluxo1 = ""
            fluxo2 = ""
            ip_addr = "127.0.0.1"
            datalog_canal1 = ""
            datalog_canal2 = ""
            pan1_color = ""
            pan2_color = ""
            unidade1 = ""
            unidade2 = ""
            tipo_de_paciente = "Adulto"
            ttconnect = ""
            self.tmr_ttconnect.Stop()

        elif self.watchdog_timeout == 20:
            self.watchdog_timeout = 0

     def tmr_visual_tconnect_handler(self, event):
         global ttconnect, thoras, tmin, tsec, ttsec
         if self.threadClientConnected:
             ttsec += 1
             tsec = ttsec
             thoras = tsec / 3600
             tsec = tsec % 3600
             tmin = tsec / 60
             tsec = tsec % 60

             thoras = format(thoras, '02d')
             tmin = format(tmin, '02d')
             tsec = format(tsec, '02d')

             ttconnect = str(thoras) + ":" + str(tmin) + ":" + str(tsec)

#<thread_inconnection>
     def thread_inconnection(self, arg1, arg2, arg3):
        global ip_addr,stat_equipament1, stat_equipament2, ttsec 
        self.id = 0
        self.error = False
        self.init = True
        print arg1

        #print "Aguardando..." + str(sys.argv[1])
        #time.sleep(int(sys.argv[1]) * 2)

        while not self.threadStopped:
            try:
                newsocket, fromaddr = self.socket_tcp.accept()
                print "Bind Socket"
            except:
                self.error = True
                print "Bind exception..."

            try:
                connstream = ssl.wrap_socket(newsocket, certfile = "server.cert", keyfile = "server.key",server_side=True)
            except:
                self.error = True
                print "Socket exception..."

            self.watchdog_timeout = 0

            print "Client connected,", fromaddr
            ip_addr = ""
            temp = ""
            ip_addr = str(fromaddr)
            ip_addr = re.sub(r'[(|)|,]',r'', ip_addr)
            ip_addr = re.sub(r'[\']',r'', ip_addr)

            self.id += 1

            try:
                self.cyph = (connstream.cipher())
                #self.cert = (pprint.pformat(connstream.getpeercert()))
            except:
                self.error = True
                print "Cipher Error..."

            try:
                self.cert = connstream.getpeercert()
            except:
                self.error = True
                print "Cert Error..."

            if not self.error:
                print "cypher: ", self.cyph
                print "cert: ", self.cert

                self.th_client = threading.Thread(target=self.thread_client,args=("thread client " + str(sys.argv[1]) + " sendo executada:",connstream, self.id, 0))
                self.th_client.start()

                self.threadClientConnected = True

                print "\n"
                print "Client " + str(sys.argv[1]) + " Connected...", ip_addr
                print "\n"

                #time.sleep(1)
                #self.envia_auth_required(connstream)

                stat_equipament1 = ""
                stat_equipament2 = ""

                ttsec = 0
                self.tmr_ttconnect.Start(1000)

                while self.threadClientConnected:
                    time.sleep(1)

                print "Client " + str(sys.argv[1]) + " disconnected...", ip_addr
            else:
                self.error = False
                time.sleep(1)
#</thread_inconnection>

#<thread_client>
     def thread_client(self, arg1, conn, cid, init):
        global recv, recv2, medicine1, medicine2, fluxo1, fluxo2, status_bar, pan1_color, pan2_color
        global datalog_canal1, datalog_canal2, unidade1, unidade2, power, infusion_mod, tipo_de_paciente
        self.estado = init
        self.s = bytearray(368)
        self.ack = bytearray(8)
        self.s = "";

        print arg1, cid

        #time.sleep(15);
        self.envia_auth_required(conn)

        #while not self.threadStopped:
        while self.threadClientConnected:
            try:
                self.data = conn.read()
            except:
                print "Read Error..."

            self.watchdog_timeout = 0

            if self.estado == 0:
               #AUTH_REQUEST
               #todo: tratar resposta do desafio aqui

               #AUTH_RESPONSE
               auth_response = bytearray(2)
               auth_response[0] = 03
               auth_response[1] = 01     #ACCEPTED
               conn.write(auth_response)
               time.sleep(1)

               #SYNCHRONIZE(date,time) date/time do sistema
               sync_response = bytearray(8)
	       now = datetime.now()
               sync_response[0] = 04
               sync_response[1] = now.hour
               sync_response[2] = now.minute
               sync_response[3] = now.second
               sync_response[4] = now.day
               sync_response[5] = now.month
               sync_response[6] = (now.year / 256)
               sync_response[7] = (now.year % 256)
               conn.write(sync_response)
               self.estado +=1

            elif self.estado == 1:
               #check PING/disconnecting
               if len(self.data) == 1:
                   if self.data == chr(0x05):
                       print "Rx PING:", "%02X" % ord(self.data)
                       conn.write(chr(0x0C))  #PONG
                   elif self.data == chr(0x06):
                       print "Cliente desconectado pelo usuario"
                       self.threadClientConnected = False

               #ack
               elif len(self.data) > 1 and self.data[2] == chr(0x00) or self.data[2] == chr(0x02):
                   self.envia_ack(conn, self.data)

                   if self.data[2] == chr(0x00):
                      self.str_serial = ""
                      for i in range(14):
                          self.str_serial += self.data[18 + i]

                      self.SetTitle(self.str_serial)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

#<converte segundos>
                   if self.data[2] == chr(0x02):
                      self.tsec = (int(ord(self.data[190])) * 16777216) + (int(ord(self.data[189])) * 65536) + (int(ord(self.data[188])) * 256) + int(ord(self.data[187]))
                      self.sec_total = self.tsec

                      self.thor = self.tsec / 3600
                      self.tsec = self.tsec % 3600
                      self.tmin = self.tsec / 60
                      self.tsec = self.tsec % 60

                      self.thor = format(self.thor, '02d')
                      self.tmin = format(self.tmin, '02d')
                      self.tsec = format(self.tsec, '02d')

                      self.time = str(self.thor) + ":" + str(self.tmin) + ":" + str(self.tsec)
#</converte segundos>

#<fluxo>
                      self.temp_fluxo = ""
                      self.temp_fluxo = (int(ord(self.data[115])) * 16777216) + (int(ord(self.data[114])) * 65536) + (int(ord(self.data[113])) * 256) + int(ord(self.data[112]))
#</fluxo>

#<medicamento>
                      self.str_temp = ""
                      for x in range(7):
                          self.str_temp += self.data[x + 37]

                      if self.data[31] == chr(0x01):
                          recv = self.time
                          medicine1 = re.sub('([^\s\w]|_)+', '', self.str_temp)
                          x = str(struct.unpack('f',struct.pack('i',self.temp_fluxo)))
                          fluxo1 = re.sub(r'[(|)|,]',r'', x)
                          fluxo1 = round(float(fluxo1), 2)
                          if self.data[34] == chr(60):
                              pan1_color = "yellow"
                          else:
                              pan1_color = ""

                          if self.data[33] == chr(0):
                              unidade1 = "ml/h"
                          else:
                              unidade1 = ""

                      elif self.data[31] == chr(0x02):
                          recv2 = self.time
                          medicine2 = re.sub('([^\s\w]|_)+', '', self.str_temp)
                          x = str(struct.unpack('f',struct.pack('i',self.temp_fluxo)))
                          fluxo2 = re.sub(r'[(|)|,]',r'', x)
                          fluxo2 = round(float(fluxo2), 2)
                          if self.data[34] == chr(60):
                              pan2_color = "yellow"
                          else:
                              pan2_color = ""

                          if self.data[33] == chr(0):
                              unidade2 = "ml/h"
                          else:
                              unidade2 = ""

                      #print "Tipo de paciente:", int(self.data[32])

                      #if self.data[32] == chr(0):
                      #    tipo_de_paciente = "Neonatal"
                      #elif self.data[32] == chr(1):
                      #    tipo_de_paciente = "Adulto"
                      #elif self.data[32] == chr(2):       
                      #    tipo_de_paciente = "Pediatrico"

                      #print "\n"
                      #print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                      
		      #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                      self.s = ""
#</medicamento>

               elif len(self.data) > 1 and self.data[2] == chr(0x01):
                   self.envia_ack(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   if (int(ord(self.data[72])) & int(0x02)) == int(0x02):
                      power = "AC"    
                   else:
                      power = ""

                   if int(ord(self.data[52])) == 0:
                      infusion_mod = "VOL"
                   elif int(ord(self.data[52])) == 1:    
                      infusion_mod = "DOSE"
                   elif int(ord(self.data[52])) == 2:
                      infusion_mod = "DERS"

                   print "\n"
                   print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s

		   #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

#<Datalogger>
               elif len(self.data) > 1 and self.data[2] == chr(0x03):
                   self.envia_ack(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   self.reg = int(ord(self.data[33]) * 256) + int(ord(self.data[32]))
                   self.cod = int(ord(self.data[41]))
                   self.datalog = str(self.reg) + ":" + str(self.cod)

                   if self.data[17] == chr(0x01):
                       if self.cod == 34:
                          pan1_color = "red"
                       elif self.cod == 9:
                          pan1_color = ""

                       datalog_canal1 = self.datalog

                   elif self.data[17] == chr(0x02):
                       if self.cod == 34:
                          pan2_color = "red"
                       elif self.cod == 9:
                          pan2_color = ""

                       datalog_canal2 = self.datalog

                   print "\n"
                   #if self.data[17] == chr(0x02): 
                   print "packet :", p, ", datalogger :", "canal :", ord(self.data[17]),", reg:", self.reg, ",IP:", ip_addr, "=>", self.s
                   #print "packet :", p, ", message :", ord(self.data[2]), "canal :", ord(self.data[17]),",reg:", self.reg, ",IP:", ip_addr, "=>", self.s
		   #print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""
#</Datalogger>

               elif len(self.data) > 1 and self.data[2] == chr(0x0E):
                   self.envia_ackex_info_leito_atual(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   print "\n"
                   print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

               elif len(self.data) > 1 and self.data[2] == chr(0x0B):
                   self.envia_ackex_plus_envia_infra64(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   print "\n"
                   print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

               elif len(self.data) > 1 and self.data[2] == chr(0x0D):
                   self.envia_ackex_status_troca_alocacao(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   print "\n"
                   print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

               elif len(self.data) > 1 and self.data[2] == chr(0x0F):
                   self.envia_smart_code(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   print "\n"
                   print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   #print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

               elif len(self.data) > 1 and self.data[2] == chr(0x12):
                   self.envia_status_ponteiros_datalogger(conn, self.data)

                   p = int(ord(self.data[6]) * 256) + int(ord(self.data[5]))

                   for x in range(len(self.data)):
                      c = "%02X" % ord(self.data[x])
                      self.s += c

                   print "\n"
                   #print "packet :", p, ", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   print "packet :", p, "canal :", ord(self.data[17]),", message :", ord(self.data[2]), ",IP:", ip_addr, "=>", self.s
                   self.s = ""

            #time.sleep(1)
#</thread_client>

     def envia_auth_required(self, connstream):
        desafio = bytearray(6)
        desafio[0] = 01
        desafio[1] = 04
        desafio[2] = 12
        desafio[3] = 34
        desafio[4] = 56
        desafio[5] = 78
        connstream.write(desafio)

     def envia_ack(self, connstream, data):
        ack = bytearray(8)
    
        if len(data) == 1:
            return False
        else:
          ack[0] = 0xAA
          ack[1] = 0x55
          ack[2] = 0xF0
          ack[3] = ord(data[5])
          ack[4] = ord(data[6])
          ack[5] = ord(data[7])
          ack[6] = ord(data[8])
          ack[7] = 0xFF

          connstream.write(ack)

     def envia_ackex_status_troca_alocacao(self, connstream, data):
           temp = bytearray(17)
           BsdBuf = bytearray(17)

           BsdBuf[0]= 0xaa
           BsdBuf[1]= 0x55
           BsdBuf[2]= 0xfd
           BsdBuf[3]= 0x0b
           BsdBuf[4]= 0x00
           BsdBuf[5]= data[5]
           BsdBuf[6]= data[6]
           BsdBuf[7]= data[7]
           BsdBuf[8]= data[8]
           BsdBuf[9]= data[17]
           BsdBuf[10]= data[18]
           BsdBuf[11]= data[19]
           BsdBuf[12]= data[20]
           BsdBuf[13]= 0x00
           BsdBuf[14]= 0x00
           BsdBuf[15]= 0x00
           BsdBuf[16]= 0xff

           size = (BsdBuf[4] * 256) + BsdBuf[3]

           for x in range(size):
                temp[x] = BsdBuf[x + 3]

           crc_16b = self.calcula_crc16(temp, size)

           BsdBuf[14]= crc_16b % 256
           BsdBuf[15]= crc_16b / 256

           connstream.write(BsdBuf)

#<envia_status_ponteiros_datalogger>
     def envia_status_ponteiros_datalogger(self, connstream, data):
	   global status_dl_1, status_dl_2 
	   global reg_number_dl_1, reg_number_dl_2
           temp = bytearray(37)
           BsdBuf = bytearray(37)

           BsdBuf[0]= 0xaa
           BsdBuf[1]= 0x55
           BsdBuf[2]= 0xf2
           BsdBuf[3]= 0x1f
           BsdBuf[4]= 0x00
           BsdBuf[5]= data[5]
           BsdBuf[6]= data[6]
           BsdBuf[7]= data[7]
           BsdBuf[8]= data[8]
	   BsdBuf[9]= status_dl_1
           BsdBuf[10]= reg_number_dl_1 % 256
           BsdBuf[11]= reg_number_dl_1 / 256
	   BsdBuf[12]= status_dl_2
           BsdBuf[13]= reg_number_dl_2 % 256
           BsdBuf[14]= reg_number_dl_2 / 256
	   BsdBuf[15]= 0
           BsdBuf[16]= 0x00
           BsdBuf[17]= 0x00
           BsdBuf[18]= 0x00
           BsdBuf[19]= 0x00
           BsdBuf[20]= 0x00
           BsdBuf[21]= 0x00
           BsdBuf[22]= 0x00
           BsdBuf[23]= 0x00
           BsdBuf[24]= 0x00
           BsdBuf[25]= 0x00
           BsdBuf[26]= 0x00
           BsdBuf[27]= 0x00
           BsdBuf[28]= 0x00
           BsdBuf[29]= 0x00
           BsdBuf[30]= 0x00
           BsdBuf[31]= 0x00
           BsdBuf[32]= 0x00
           BsdBuf[33]= 0x00
           BsdBuf[34]= 0x00
           BsdBuf[35]= 0x00
           BsdBuf[36]= 0xff

           size = (BsdBuf[4] * 256) + BsdBuf[3]

           for x in range(size):
                temp[x] = BsdBuf[x + 3]

           crc_16b = self.calcula_crc16(temp, size)

           BsdBuf[34]= crc_16b % 256
           BsdBuf[35]= crc_16b / 256

	   status_dl_1 = 0
           status_dl_2 = 0

           connstream.write(BsdBuf)

#</envia_status_ponteiros_datalogger>

#<envia_smart_code>

#000TCH17050080	920ebf59db12e8c0e0ac31243c3a
#000TCH16080079	920ebf59db12e8c0e0ac3124333a
#000LFT16050119	920ebf59db12e8c0e0ac31253b3a

     def envia_smart_code(self, connstream, data):
           temp = bytearray(42)
           BsdBuf = bytearray(42)

           BsdBuf[0]= 0xaa
           BsdBuf[1]= 0x55
           BsdBuf[2]= 0xf1
           BsdBuf[3]= 0x24
           BsdBuf[4]= 0x00
           BsdBuf[5]= data[5]
           BsdBuf[6]= data[6]
           BsdBuf[7]= data[7]
           BsdBuf[8]= data[8]
           BsdBuf[9]= 0x1c
           BsdBuf[10]= 0x00
           BsdBuf[11]= '9'
           BsdBuf[12]= '2'
           BsdBuf[13]= '0'
           BsdBuf[14]= 'e'
           BsdBuf[15]= 'b'           
           BsdBuf[16]= 'f'
           BsdBuf[17]= '5'
           BsdBuf[18]= '9'
           BsdBuf[19]= 'd'
           BsdBuf[20]= 'b'
           BsdBuf[21]= '1'
           BsdBuf[22]= '2'           
           BsdBuf[23]= 'e'
           BsdBuf[24]= '8'
           BsdBuf[25]= 'c'
           BsdBuf[26]= '0'
           BsdBuf[27]= 'e'
           BsdBuf[28]= '0'
           BsdBuf[29]= 'a'
           BsdBuf[30]= 'c'
           BsdBuf[31]= '3'
           BsdBuf[32]= '1'
           BsdBuf[33]= '2'
           BsdBuf[34]= '4'
           BsdBuf[35]= '3'
           BsdBuf[36]= '3'
           BsdBuf[37]= '3'
           BsdBuf[38]= 'a'
           BsdBuf[39]= 0x00
           BsdBuf[40]= 0x00
           BsdBuf[41]= 0xff

           size = (BsdBuf[4] * 256) + BsdBuf[3]

           for x in range(size):
                temp[x] = BsdBuf[x + 3]

           crc_16b = self.calcula_crc16(temp, size)

           BsdBuf[39]= crc_16b % 256
           BsdBuf[40]= crc_16b / 256

           connstream.write(BsdBuf)
#</envia_smart_code>

     def envia_ackex_plus_envia_infra64(self, connstream, data):
           temp = bytearray(804)
           BsdBuf = bytearray(804)

           BsdBuf[0]= 0xaa
           BsdBuf[1]= 0x55
           BsdBuf[2]= 0xfb
           BsdBuf[3]= 0x01e
           BsdBuf[4]= 0x03
           BsdBuf[5]= data[5]   #0x083
           BsdBuf[6]= data[6]   #0x00
           BsdBuf[7]= data[7]   #0x00
           BsdBuf[8]= data[8]   #0x00
           BsdBuf[9]= 0x01
           BsdBuf[10]= 0x01
           BsdBuf[11]= 0x00
           BsdBuf[12]= 0x00
           BsdBuf[13]= 0x00
           BsdBuf[14]= 0x55
           BsdBuf[15]= 0x54
           BsdBuf[16]= 0x49
           BsdBuf[17]= 0x00
           BsdBuf[18]= 0x00
           BsdBuf[19]= 0x00
           BsdBuf[20]= 0x00
           BsdBuf[21]= 0x00
           BsdBuf[22]= 0x00
           BsdBuf[23]= 0x00
           BsdBuf[24]= 0x00
           BsdBuf[25]= 0x00
           BsdBuf[26]= 0x00
           BsdBuf[27]= 0x00
           BsdBuf[28]= 0x00
           BsdBuf[29]= 0x00
           BsdBuf[30]= 0x00
           BsdBuf[31]= 0x00
           BsdBuf[32]= 0x40
           BsdBuf[33]= 0x01
           BsdBuf[34]= 0x00
           BsdBuf[35]= 0x00
           BsdBuf[36]= 0x00
           BsdBuf[37]= 0x30
           BsdBuf[38]= 0x31
           BsdBuf[39]= 0x00
           BsdBuf[40]= 0x00
           BsdBuf[41]= 0x00
           BsdBuf[42]= 0x00
           BsdBuf[43]= 0x00
           BsdBuf[44]= 0x00
           BsdBuf[45]= 0x02
           BsdBuf[46]= 0x00
           BsdBuf[47]= 0x00
           BsdBuf[48]= 0x00
           BsdBuf[49]= 0x30
           BsdBuf[50]= 0x32
           BsdBuf[51]= 0x00
           BsdBuf[52]= 0x00
           BsdBuf[53]= 0x00
           BsdBuf[54]= 0x00
           BsdBuf[55]= 0x00
           BsdBuf[56]= 0x00
           BsdBuf[57]= 0x05
           BsdBuf[58]= 0x00
           BsdBuf[59]= 0x00
           BsdBuf[60]= 0x00
           BsdBuf[61]= 0x30
           BsdBuf[62]= 0x33
           BsdBuf[63]= 0x00
           BsdBuf[64]= 0x00
           BsdBuf[65]= 0x00
           BsdBuf[66]= 0x00
           BsdBuf[67]= 0x00
           BsdBuf[68]= 0x00
           BsdBuf[69]= 0x06
           BsdBuf[70]= 0x00
           BsdBuf[71]= 0x00
           BsdBuf[72]= 0x00
           BsdBuf[73]= 0x30
           BsdBuf[74]= 0x34
           BsdBuf[75]= 0x00
           BsdBuf[76]= 0x00
           BsdBuf[77]= 0x00
           BsdBuf[78]= 0x00
           BsdBuf[79]= 0x00
           BsdBuf[80]= 0x00
           BsdBuf[81]= 0x07
           BsdBuf[82]= 0x00
           BsdBuf[83]= 0x00
           BsdBuf[84]= 0x00
           BsdBuf[85]= 0x30
           BsdBuf[86]= 0x35
           BsdBuf[87]= 0x00
           BsdBuf[88]= 0x00
           BsdBuf[89]= 0x00
           BsdBuf[90]= 0x00
           BsdBuf[91]= 0x00
           BsdBuf[92]= 0x00
           BsdBuf[93]= 0x03
           BsdBuf[94]= 0x00
           BsdBuf[95]= 0x00
           BsdBuf[96]= 0x00
           BsdBuf[97]= 0x30
           BsdBuf[98]= 0x36
           BsdBuf[99]= 0x00
           BsdBuf[100]= 0x00
           BsdBuf[101]= 0x00
           BsdBuf[102]= 0x00
           BsdBuf[103]= 0x00
           BsdBuf[104]= 0x00
           BsdBuf[105]= 0x04
           BsdBuf[106]= 0x00
           BsdBuf[107]= 0x00
           BsdBuf[108]= 0x00
           BsdBuf[109]= 0x30
           BsdBuf[110]= 0x37
           BsdBuf[111]= 0x00
           BsdBuf[112]= 0x00
           BsdBuf[113]= 0x00
           BsdBuf[114]= 0x00
           BsdBuf[115]= 0x00
           BsdBuf[116]= 0x00
           BsdBuf[117]= 0x08
           BsdBuf[118]= 0x00
           BsdBuf[119]= 0x00
           BsdBuf[120]= 0x00
           BsdBuf[121]= 0x30
           BsdBuf[122]= 0x38
           BsdBuf[123]= 0x00
           BsdBuf[124]= 0x00
           BsdBuf[125]= 0x00
           BsdBuf[126]= 0x00
           BsdBuf[127]= 0x00
           BsdBuf[128]= 0x00
           BsdBuf[129]= 0x09
           BsdBuf[130]= 0x00
           BsdBuf[131]= 0x00
           BsdBuf[132]= 0x00
           BsdBuf[133]= 0x30
           BsdBuf[134]= 0x39
           BsdBuf[135]= 0x00
           BsdBuf[136]= 0x00
           BsdBuf[137]= 0x00
           BsdBuf[138]= 0x00
           BsdBuf[139]= 0x00
           BsdBuf[140]= 0x00
           BsdBuf[141]= 0x0a
           BsdBuf[142]= 0x00
           BsdBuf[143]= 0x00
           BsdBuf[144]= 0x00
           BsdBuf[145]= 0x31
           BsdBuf[146]= 0x30
           BsdBuf[147]= 0x00
           BsdBuf[148]= 0x00
           BsdBuf[149]= 0x00
           BsdBuf[150]= 0x00
           BsdBuf[151]= 0x00
           BsdBuf[152]= 0x00
           BsdBuf[153]= 0x0b
           BsdBuf[154]= 0x00
           BsdBuf[155]= 0x00
           BsdBuf[156]= 0x00
           BsdBuf[157]= 0x31
           BsdBuf[158]= 0x31
           BsdBuf[159]= 0x00
           BsdBuf[160]= 0x00
           BsdBuf[161]= 0x00
           BsdBuf[162]= 0x00
           BsdBuf[163]= 0x00
           BsdBuf[164]= 0x00
           BsdBuf[165]= 0x0c
           BsdBuf[166]= 0x00
           BsdBuf[167]= 0x00
           BsdBuf[168]= 0x00
           BsdBuf[169]= 0x31
           BsdBuf[170]= 0x32
           BsdBuf[171]= 0x00
           BsdBuf[172]= 0x00
           BsdBuf[173]= 0x00
           BsdBuf[174]= 0x00
           BsdBuf[175]= 0x00
           BsdBuf[176]= 0x00
           BsdBuf[177]= 0x0e
           BsdBuf[178]= 0x00
           BsdBuf[179]= 0x00
           BsdBuf[180]= 0x00
           BsdBuf[181]= 0x31
           BsdBuf[182]= 0x33
           BsdBuf[183]= 0x00
           BsdBuf[184]= 0x00
           BsdBuf[185]= 0x00
           BsdBuf[186]= 0x00
           BsdBuf[187]= 0x00
           BsdBuf[188]= 0x00
           BsdBuf[189]= 0x0d
           BsdBuf[190]= 0x00
           BsdBuf[191]= 0x00
           BsdBuf[192]= 0x00
           BsdBuf[193]= 0x31
           BsdBuf[194]= 0x34
           BsdBuf[195]= 0x00
           BsdBuf[196]= 0x00
           BsdBuf[197]= 0x00
           BsdBuf[198]= 0x00
           BsdBuf[199]= 0x00
           BsdBuf[200]= 0x00
           BsdBuf[201]= 0x0f
           BsdBuf[202]= 0x00
           BsdBuf[203]= 0x00
           BsdBuf[204]= 0x00
           BsdBuf[205]= 0x31
           BsdBuf[206]= 0x35
           BsdBuf[207]= 0x00
           BsdBuf[208]= 0x00
           BsdBuf[209]= 0x00
           BsdBuf[210]= 0x00
           BsdBuf[211]= 0x00
           BsdBuf[212]= 0x00
           BsdBuf[213]= 0x010
           BsdBuf[214]= 0x00
           BsdBuf[215]= 0x00
           BsdBuf[216]= 0x00
           BsdBuf[217]= 0x31
           BsdBuf[218]= 0x36
           BsdBuf[219]= 0x00
           BsdBuf[220]= 0x00
           BsdBuf[221]= 0x00
           BsdBuf[222]= 0x00
           BsdBuf[223]= 0x00
           BsdBuf[224]= 0x00
           BsdBuf[225]= 0x011
           BsdBuf[226]= 0x00
           BsdBuf[227]= 0x00
           BsdBuf[228]= 0x00
           BsdBuf[229]= 0x31
           BsdBuf[230]= 0x37
           BsdBuf[231]= 0x00
           BsdBuf[232]= 0x00
           BsdBuf[233]= 0x00
           BsdBuf[234]= 0x00
           BsdBuf[235]= 0x00
           BsdBuf[236]= 0x00
           BsdBuf[237]= 0x012
           BsdBuf[238]= 0x00
           BsdBuf[239]= 0x00
           BsdBuf[240]= 0x00
           BsdBuf[241]= 0x31
           BsdBuf[242]= 0x38
           BsdBuf[243]= 0x00
           BsdBuf[244]= 0x00
           BsdBuf[245]= 0x00
           BsdBuf[246]= 0x00
           BsdBuf[247]= 0x00
           BsdBuf[248]= 0x00
           BsdBuf[249]= 0x013
           BsdBuf[250]= 0x00
           BsdBuf[251]= 0x00
           BsdBuf[252]= 0x00
           BsdBuf[253]= 0x31
           BsdBuf[254]= 0x39
           BsdBuf[255]= 0x00
           BsdBuf[256]= 0x00
           BsdBuf[257]= 0x00
           BsdBuf[258]= 0x00
           BsdBuf[259]= 0x00
           BsdBuf[260]= 0x00
           BsdBuf[261]= 0x014
           BsdBuf[262]= 0x00
           BsdBuf[263]= 0x00
           BsdBuf[264]= 0x00
           BsdBuf[265]= 0x32
           BsdBuf[266]= 0x30
           BsdBuf[267]= 0x00
           BsdBuf[268]= 0x00
           BsdBuf[269]= 0x00
           BsdBuf[270]= 0x00
           BsdBuf[271]= 0x00
           BsdBuf[272]= 0x00
           BsdBuf[273]= 0x015
           BsdBuf[274]= 0x00
           BsdBuf[275]= 0x00
           BsdBuf[276]= 0x00
           BsdBuf[277]= 0x32
           BsdBuf[278]= 0x31
           BsdBuf[279]= 0x00
           BsdBuf[280]= 0x00
           BsdBuf[281]= 0x00
           BsdBuf[282]= 0x00
           BsdBuf[283]= 0x00
           BsdBuf[284]= 0x00
           BsdBuf[285]= 0x016
           BsdBuf[286]= 0x00
           BsdBuf[287]= 0x00
           BsdBuf[288]= 0x00
           BsdBuf[289]= 0x32
           BsdBuf[290]= 0x32
           BsdBuf[291]= 0x00
           BsdBuf[292]= 0x00
           BsdBuf[293]= 0x00
           BsdBuf[294]= 0x00
           BsdBuf[295]= 0x00
           BsdBuf[296]= 0x00
           BsdBuf[297]= 0x017
           BsdBuf[298]= 0x00
           BsdBuf[299]= 0x00
           BsdBuf[300]= 0x00
           BsdBuf[301]= 0x32
           BsdBuf[302]= 0x33
           BsdBuf[303]= 0x00
           BsdBuf[304]= 0x00
           BsdBuf[305]= 0x00
           BsdBuf[306]= 0x00
           BsdBuf[307]= 0x00
           BsdBuf[308]= 0x00
           BsdBuf[309]= 0x018
           BsdBuf[310]= 0x00
           BsdBuf[311]= 0x00
           BsdBuf[312]= 0x00
           BsdBuf[313]= 0x32
           BsdBuf[314]= 0x34
           BsdBuf[315]= 0x00
           BsdBuf[316]= 0x00
           BsdBuf[317]= 0x00
           BsdBuf[318]= 0x00
           BsdBuf[319]= 0x00
           BsdBuf[320]= 0x00
           BsdBuf[321]= 0x019
           BsdBuf[322]= 0x00
           BsdBuf[323]= 0x00
           BsdBuf[324]= 0x00
           BsdBuf[325]= 0x32
           BsdBuf[326]= 0x35
           BsdBuf[327]= 0x00
           BsdBuf[328]= 0x00
           BsdBuf[329]= 0x00
           BsdBuf[330]= 0x00
           BsdBuf[331]= 0x00
           BsdBuf[332]= 0x00
           BsdBuf[333]= 0x01a
           BsdBuf[334]= 0x00
           BsdBuf[335]= 0x00
           BsdBuf[336]= 0x00
           BsdBuf[337]= 0x32
           BsdBuf[338]= 0x36
           BsdBuf[339]= 0x00
           BsdBuf[340]= 0x00
           BsdBuf[341]= 0x00
           BsdBuf[342]= 0x00
           BsdBuf[343]= 0x00
           BsdBuf[344]= 0x00
           BsdBuf[345]= 0x01b
           BsdBuf[346]= 0x00
           BsdBuf[347]= 0x00
           BsdBuf[348]= 0x00
           BsdBuf[349]= 0x32
           BsdBuf[350]= 0x37
           BsdBuf[351]= 0x00
           BsdBuf[352]= 0x00
           BsdBuf[353]= 0x00
           BsdBuf[354]= 0x00
           BsdBuf[355]= 0x00
           BsdBuf[356]= 0x00
           BsdBuf[357]= 0x01d
           BsdBuf[358]= 0x00
           BsdBuf[359]= 0x00
           BsdBuf[360]= 0x00
           BsdBuf[361]= 0x32
           BsdBuf[362]= 0x38
           BsdBuf[363]= 0x00
           BsdBuf[364]= 0x00
           BsdBuf[365]= 0x00
           BsdBuf[366]= 0x00
           BsdBuf[367]= 0x00
           BsdBuf[368]= 0x00
           BsdBuf[369]= 0x01c
           BsdBuf[370]= 0x00
           BsdBuf[371]= 0x00
           BsdBuf[372]= 0x00
           BsdBuf[373]= 0x32
           BsdBuf[374]= 0x39
           BsdBuf[375]= 0x00
           BsdBuf[376]= 0x00
           BsdBuf[377]= 0x00
           BsdBuf[378]= 0x00
           BsdBuf[379]= 0x00
           BsdBuf[380]= 0x00
           BsdBuf[381]= 0x01e
           BsdBuf[382]= 0x00
           BsdBuf[383]= 0x00
           BsdBuf[384]= 0x00
           BsdBuf[385]= 0x33
           BsdBuf[386]= 0x30
           BsdBuf[387]= 0x00
           BsdBuf[388]= 0x00
           BsdBuf[389]= 0x00
           BsdBuf[390]= 0x00
           BsdBuf[391]= 0x00
           BsdBuf[392]= 0x00
           BsdBuf[393]= 0x01f
           BsdBuf[394]= 0x00
           BsdBuf[395]= 0x00
           BsdBuf[396]= 0x00
           BsdBuf[397]= 0x33
           BsdBuf[398]= 0x31
           BsdBuf[399]= 0x00
           BsdBuf[400]= 0x00
           BsdBuf[401]= 0x00
           BsdBuf[402]= 0x00
           BsdBuf[403]= 0x00
           BsdBuf[404]= 0x00
           BsdBuf[405]= 0x20
           BsdBuf[406]= 0x00
           BsdBuf[407]= 0x00
           BsdBuf[408]= 0x00
           BsdBuf[409]= 0x33
           BsdBuf[410]= 0x32
           BsdBuf[411]= 0x00
           BsdBuf[412]= 0x00
           BsdBuf[413]= 0x00
           BsdBuf[414]= 0x00
           BsdBuf[415]= 0x00
           BsdBuf[416]= 0x00
           BsdBuf[417]= 0x21
           BsdBuf[418]= 0x00
           BsdBuf[419]= 0x00
           BsdBuf[420]= 0x00
           BsdBuf[421]= 0x33
           BsdBuf[422]= 0x33
           BsdBuf[423]= 0x00
           BsdBuf[424]= 0x00
           BsdBuf[425]= 0x00
           BsdBuf[426]= 0x00
           BsdBuf[427]= 0x00
           BsdBuf[428]= 0x00
           BsdBuf[429]= 0x22
           BsdBuf[430]= 0x00
           BsdBuf[431]= 0x00
           BsdBuf[432]= 0x00
           BsdBuf[433]= 0x33
           BsdBuf[434]= 0x34
           BsdBuf[435]= 0x00
           BsdBuf[436]= 0x00
           BsdBuf[437]= 0x00
           BsdBuf[438]= 0x00
           BsdBuf[439]= 0x00
           BsdBuf[440]= 0x00
           BsdBuf[441]= 0x23
           BsdBuf[442]= 0x00
           BsdBuf[443]= 0x00
           BsdBuf[444]= 0x00
           BsdBuf[445]= 0x33
           BsdBuf[446]= 0x35
           BsdBuf[447]= 0x00
           BsdBuf[448]= 0x00
           BsdBuf[449]= 0x00
           BsdBuf[450]= 0x00
           BsdBuf[451]= 0x00
           BsdBuf[452]= 0x00
           BsdBuf[453]= 0x24
           BsdBuf[454]= 0x00
           BsdBuf[455]= 0x00
           BsdBuf[456]= 0x00
           BsdBuf[457]= 0x33
           BsdBuf[458]= 0x36
           BsdBuf[459]= 0x00
           BsdBuf[460]= 0x00
           BsdBuf[461]= 0x00
           BsdBuf[462]= 0x00
           BsdBuf[463]= 0x00
           BsdBuf[464]= 0x00
           BsdBuf[465]= 0x25
           BsdBuf[466]= 0x00
           BsdBuf[467]= 0x00
           BsdBuf[468]= 0x00
           BsdBuf[469]= 0x33
           BsdBuf[470]= 0x37
           BsdBuf[471]= 0x00
           BsdBuf[472]= 0x00
           BsdBuf[473]= 0x00
           BsdBuf[474]= 0x00
           BsdBuf[475]= 0x00
           BsdBuf[476]= 0x00
           BsdBuf[477]= 0x26
           BsdBuf[478]= 0x00
           BsdBuf[479]= 0x00
           BsdBuf[480]= 0x00
           BsdBuf[481]= 0x33
           BsdBuf[482]= 0x38
           BsdBuf[483]= 0x00
           BsdBuf[484]= 0x00
           BsdBuf[485]= 0x00
           BsdBuf[486]= 0x00
           BsdBuf[487]= 0x00
           BsdBuf[488]= 0x00
           BsdBuf[489]= 0x27
           BsdBuf[490]= 0x00
           BsdBuf[491]= 0x00
           BsdBuf[492]= 0x00
           BsdBuf[493]= 0x33
           BsdBuf[494]= 0x39
           BsdBuf[495]= 0x00
           BsdBuf[496]= 0x00
           BsdBuf[497]= 0x00
           BsdBuf[498]= 0x00
           BsdBuf[499]= 0x00
           BsdBuf[500]= 0x00
           BsdBuf[501]= 0x28
           BsdBuf[502]= 0x00
           BsdBuf[503]= 0x00
           BsdBuf[504]= 0x00
           BsdBuf[505]= 0x34
           BsdBuf[506]= 0x30
           BsdBuf[507]= 0x00
           BsdBuf[508]= 0x00
           BsdBuf[509]= 0x00
           BsdBuf[510]= 0x00
           BsdBuf[511]= 0x00
           BsdBuf[512]= 0x00
           BsdBuf[513]= 0x29
           BsdBuf[514]= 0x00
           BsdBuf[515]= 0x00
           BsdBuf[516]= 0x00
           BsdBuf[517]= 0x34
           BsdBuf[518]= 0x31
           BsdBuf[519]= 0x00
           BsdBuf[520]= 0x00
           BsdBuf[521]= 0x00
           BsdBuf[522]= 0x00
           BsdBuf[523]= 0x00
           BsdBuf[524]= 0x00
           BsdBuf[525]= 0x2a
           BsdBuf[526]= 0x00
           BsdBuf[527]= 0x00
           BsdBuf[528]= 0x00
           BsdBuf[529]= 0x34
           BsdBuf[530]= 0x32
           BsdBuf[531]= 0x00
           BsdBuf[532]= 0x00
           BsdBuf[533]= 0x00
           BsdBuf[534]= 0x00
           BsdBuf[535]= 0x00
           BsdBuf[536]= 0x00
           BsdBuf[537]= 0x2b
           BsdBuf[538]= 0x00
           BsdBuf[539]= 0x00
           BsdBuf[540]= 0x00
           BsdBuf[541]= 0x34
           BsdBuf[542]= 0x33
           BsdBuf[543]= 0x00
           BsdBuf[544]= 0x00
           BsdBuf[545]= 0x00
           BsdBuf[546]= 0x00
           BsdBuf[547]= 0x00
           BsdBuf[548]= 0x00
           BsdBuf[549]= 0x2c
           BsdBuf[550]= 0x00
           BsdBuf[551]= 0x00
           BsdBuf[552]= 0x00
           BsdBuf[553]= 0x34
           BsdBuf[554]= 0x34
           BsdBuf[555]= 0x00
           BsdBuf[556]= 0x00
           BsdBuf[557]= 0x00
           BsdBuf[558]= 0x00
           BsdBuf[559]= 0x00
           BsdBuf[560]= 0x00
           BsdBuf[561]= 0x2d
           BsdBuf[562]= 0x00
           BsdBuf[563]= 0x00
           BsdBuf[564]= 0x00
           BsdBuf[565]= 0x34
           BsdBuf[566]= 0x35
           BsdBuf[567]= 0x00
           BsdBuf[568]= 0x00
           BsdBuf[569]= 0x00
           BsdBuf[570]= 0x00
           BsdBuf[571]= 0x00
           BsdBuf[572]= 0x00
           BsdBuf[573]= 0x2e
           BsdBuf[574]= 0x00
           BsdBuf[575]= 0x00
           BsdBuf[576]= 0x00
           BsdBuf[577]= 0x34
           BsdBuf[578]= 0x36
           BsdBuf[579]= 0x00
           BsdBuf[580]= 0x00
           BsdBuf[581]= 0x00
           BsdBuf[582]= 0x00
           BsdBuf[583]= 0x00
           BsdBuf[584]= 0x00
           BsdBuf[585]= 0x2f
           BsdBuf[586]= 0x00
           BsdBuf[587]= 0x00
           BsdBuf[588]= 0x00
           BsdBuf[589]= 0x34
           BsdBuf[590]= 0x37
           BsdBuf[591]= 0x00
           BsdBuf[592]= 0x00
           BsdBuf[593]= 0x00
           BsdBuf[594]= 0x00
           BsdBuf[595]= 0x00
           BsdBuf[596]= 0x00
           BsdBuf[597]= 0x30
           BsdBuf[598]= 0x00
           BsdBuf[599]= 0x00
           BsdBuf[600]= 0x00
           BsdBuf[601]= 0x34
           BsdBuf[602]= 0x38
           BsdBuf[603]= 0x00
           BsdBuf[604]= 0x00
           BsdBuf[605]= 0x00
           BsdBuf[606]= 0x00
           BsdBuf[607]= 0x00
           BsdBuf[608]= 0x00
           BsdBuf[609]= 0x31
           BsdBuf[610]= 0x00
           BsdBuf[611]= 0x00
           BsdBuf[612]= 0x00
           BsdBuf[613]= 0x34
           BsdBuf[614]= 0x39
           BsdBuf[615]= 0x00
           BsdBuf[616]= 0x00
           BsdBuf[617]= 0x00
           BsdBuf[618]= 0x00
           BsdBuf[619]= 0x00
           BsdBuf[620]= 0x00
           BsdBuf[621]= 0x32
           BsdBuf[622]= 0x00
           BsdBuf[623]= 0x00
           BsdBuf[624]= 0x00
           BsdBuf[625]= 0x35
           BsdBuf[626]= 0x30
           BsdBuf[627]= 0x00
           BsdBuf[628]= 0x00
           BsdBuf[629]= 0x00
           BsdBuf[630]= 0x00
           BsdBuf[631]= 0x00
           BsdBuf[632]= 0x00
           BsdBuf[633]= 0x33
           BsdBuf[634]= 0x00
           BsdBuf[635]= 0x00
           BsdBuf[636]= 0x00
           BsdBuf[637]= 0x35
           BsdBuf[638]= 0x31
           BsdBuf[639]= 0x00
           BsdBuf[640]= 0x00
           BsdBuf[641]= 0x00
           BsdBuf[642]= 0x00
           BsdBuf[643]= 0x00
           BsdBuf[644]= 0x00
           BsdBuf[645]= 0x34
           BsdBuf[646]= 0x00
           BsdBuf[647]= 0x00
           BsdBuf[648]= 0x00
           BsdBuf[649]= 0x35
           BsdBuf[650]= 0x32
           BsdBuf[651]= 0x00
           BsdBuf[652]= 0x00
           BsdBuf[653]= 0x00
           BsdBuf[654]= 0x00
           BsdBuf[655]= 0x00
           BsdBuf[656]= 0x00
           BsdBuf[657]= 0x35
           BsdBuf[658]= 0x00
           BsdBuf[659]= 0x00
           BsdBuf[660]= 0x00
           BsdBuf[661]= 0x35
           BsdBuf[662]= 0x33
           BsdBuf[663]= 0x00
           BsdBuf[664]= 0x00
           BsdBuf[665]= 0x00
           BsdBuf[666]= 0x00
           BsdBuf[667]= 0x00
           BsdBuf[668]= 0x00
           BsdBuf[669]= 0x36
           BsdBuf[670]= 0x00
           BsdBuf[671]= 0x00
           BsdBuf[672]= 0x00
           BsdBuf[673]= 0x35
           BsdBuf[674]= 0x34
           BsdBuf[675]= 0x00
           BsdBuf[676]= 0x00
           BsdBuf[677]= 0x00
           BsdBuf[678]= 0x00
           BsdBuf[679]= 0x00
           BsdBuf[680]= 0x00
           BsdBuf[681]= 0x37
           BsdBuf[682]= 0x00
           BsdBuf[683]= 0x00
           BsdBuf[684]= 0x00
           BsdBuf[685]= 0x35
           BsdBuf[686]= 0x35
           BsdBuf[687]= 0x00
           BsdBuf[688]= 0x00
           BsdBuf[689]= 0x00
           BsdBuf[690]= 0x00
           BsdBuf[691]= 0x00
           BsdBuf[692]= 0x00
           BsdBuf[693]= 0x38
           BsdBuf[694]= 0x00
           BsdBuf[695]= 0x00
           BsdBuf[696]= 0x00
           BsdBuf[697]= 0x35
           BsdBuf[698]= 0x36
           BsdBuf[699]= 0x00
           BsdBuf[700]= 0x00
           BsdBuf[701]= 0x00
           BsdBuf[702]= 0x00
           BsdBuf[703]= 0x00
           BsdBuf[704]= 0x00
           BsdBuf[705]= 0x39
           BsdBuf[706]= 0x00
           BsdBuf[707]= 0x00
           BsdBuf[708]= 0x00
           BsdBuf[709]= 0x35
           BsdBuf[710]= 0x37
           BsdBuf[711]= 0x00
           BsdBuf[712]= 0x00
           BsdBuf[713]= 0x00
           BsdBuf[714]= 0x00
           BsdBuf[715]= 0x00
           BsdBuf[716]= 0x00
           BsdBuf[717]= 0x3a
           BsdBuf[718]= 0x00
           BsdBuf[719]= 0x00
           BsdBuf[720]= 0x00
           BsdBuf[721]= 0x35
           BsdBuf[722]= 0x38
           BsdBuf[723]= 0x00
           BsdBuf[724]= 0x00
           BsdBuf[725]= 0x00
           BsdBuf[726]= 0x00
           BsdBuf[727]= 0x00
           BsdBuf[728]= 0x00
           BsdBuf[729]= 0x3b
           BsdBuf[730]= 0x00
           BsdBuf[731]= 0x00
           BsdBuf[732]= 0x00
           BsdBuf[733]= 0x35
           BsdBuf[734]= 0x39
           BsdBuf[735]= 0x00
           BsdBuf[736]= 0x00
           BsdBuf[737]= 0x00
           BsdBuf[738]= 0x00
           BsdBuf[739]= 0x00
           BsdBuf[740]= 0x00
           BsdBuf[741]= 0x3c
           BsdBuf[742]= 0x00
           BsdBuf[743]= 0x00
           BsdBuf[744]= 0x00
           BsdBuf[745]= 0x36
           BsdBuf[746]= 0x30
           BsdBuf[747]= 0x00
           BsdBuf[748]= 0x00
           BsdBuf[749]= 0x00
           BsdBuf[750]= 0x00
           BsdBuf[751]= 0x00
           BsdBuf[752]= 0x00
           BsdBuf[753]= 0x3d
           BsdBuf[754]= 0x00
           BsdBuf[755]= 0x00
           BsdBuf[756]= 0x00
           BsdBuf[757]= 0x36
           BsdBuf[758]= 0x31
           BsdBuf[759]= 0x00
           BsdBuf[760]= 0x00
           BsdBuf[761]= 0x00
           BsdBuf[762]= 0x00
           BsdBuf[763]= 0x00
           BsdBuf[764]= 0x00
           BsdBuf[765]= 0x3e
           BsdBuf[766]= 0x00
           BsdBuf[767]= 0x00
           BsdBuf[768]= 0x00
           BsdBuf[769]= 0x36
           BsdBuf[770]= 0x32
           BsdBuf[771]= 0x00
           BsdBuf[772]= 0x00
           BsdBuf[773]= 0x00
           BsdBuf[774]= 0x00
           BsdBuf[775]= 0x00
           BsdBuf[776]= 0x00
           BsdBuf[777]= 0x3f
           BsdBuf[778]= 0x00
           BsdBuf[779]= 0x00
           BsdBuf[780]= 0x00
           BsdBuf[781]= 0x36
           BsdBuf[782]= 0x33
           BsdBuf[783]= 0x00
           BsdBuf[784]= 0x00
           BsdBuf[785]= 0x00
           BsdBuf[786]= 0x00
           BsdBuf[787]= 0x00
           BsdBuf[788]= 0x00
           BsdBuf[789]= 0x40
           BsdBuf[790]= 0x00
           BsdBuf[791]= 0x00
           BsdBuf[792]= 0x00
           BsdBuf[793]= 0x36
           BsdBuf[794]= 0x34
           BsdBuf[795]= 0x00
           BsdBuf[796]= 0x00
           BsdBuf[797]= 0x00
           BsdBuf[798]= 0x00
           BsdBuf[799]= 0x00
           BsdBuf[800]= 0x00
           BsdBuf[801]= 0x6e
           BsdBuf[802]= 0x7c
           BsdBuf[803]= 0xff

           size = (BsdBuf[4] * 256) + BsdBuf[3]

           for x in range(size):
                temp[x] = BsdBuf[x + 3]

           crc_16b = self.calcula_crc16(temp, size)

           BsdBuf[801]= crc_16b % 256
           BsdBuf[802]= crc_16b / 256

           connstream.write(BsdBuf)

     def envia_ackex_info_leito_atual(self, connstream, data):
           temp = bytearray(234)
           BsdBuf = bytearray(234)

           BsdBuf[0] = 0xAA
           BsdBuf[1] = 0x55
           BsdBuf[2] = 0xfe
           BsdBuf[3] = 0xe4
           BsdBuf[4] = 0x00
           BsdBuf[5] = data[5]  #0x0c
           BsdBuf[6] = data[6]  #0x00
           BsdBuf[7] = data[7]  #0x00
           BsdBuf[8] = data[8]  #0x00
           BsdBuf[9] = 0x01
           BsdBuf[10]= 0x00
           BsdBuf[11]= 0x00
           BsdBuf[12]= 0x00
           BsdBuf[13]= '0'
           BsdBuf[14]= '1'
           BsdBuf[15]= 0x00
           BsdBuf[16]= 0x00
           BsdBuf[17]= 0x00
           BsdBuf[18]= 0x00
           BsdBuf[19]= 0x00
           BsdBuf[20]= 0x00
           BsdBuf[21]= 0x01
           BsdBuf[22]= 0x00
           BsdBuf[23]= 0x00
           BsdBuf[24]= 0x00
           BsdBuf[25]= 'U'
           BsdBuf[26]= 'T'
           BsdBuf[27]= 'I'
           BsdBuf[28]= 0x00
           BsdBuf[29]= 0x00
           BsdBuf[30]= 0x00
           BsdBuf[31]= 0x00
           BsdBuf[32]= 0x00
           BsdBuf[33]= 0x00
           BsdBuf[34]= 0x00
           BsdBuf[35]= 0x00
           BsdBuf[36]= 0x00
           BsdBuf[37]= 0x00
           BsdBuf[38]= 0x00
           BsdBuf[39]= 0x00
           BsdBuf[40]= 0x00
           BsdBuf[41]= 0x00
           BsdBuf[42]= 0x00
           BsdBuf[43]= '0'
           BsdBuf[44]= '1'
           BsdBuf[45]= '5'
           BsdBuf[46]= '9'
           BsdBuf[47]= '3'
           BsdBuf[48]= '5'
           BsdBuf[49]= '7'
           BsdBuf[50]= 0x00
           BsdBuf[51]= 0x00
           BsdBuf[52]= 0x00
           BsdBuf[53]= 0x00
           BsdBuf[54]= 0x00
           BsdBuf[55]= 0x00
           BsdBuf[56]= 0x00
           BsdBuf[57]= 0x00
           BsdBuf[58]= 0x00
           BsdBuf[59]= 0x00
           BsdBuf[60]= 0x00
           BsdBuf[61]= 0x00
           BsdBuf[62]= 0x00
           BsdBuf[63]= 0x00
           BsdBuf[64]= 0x00
           BsdBuf[65]= 0x00
           BsdBuf[66]= 0x00
           BsdBuf[67]= 0x00
           BsdBuf[68]= 0x00
           BsdBuf[69]= 0x00
           BsdBuf[70]= 0x00
           BsdBuf[71]= 0x00
           BsdBuf[72]= 0x00
           BsdBuf[73]= 0x00
           BsdBuf[74]= 0x00
           BsdBuf[75]= 0x00
           BsdBuf[76]= 0x00
           BsdBuf[77]= 0x00
           BsdBuf[78]= 0x00
           BsdBuf[79]= 0x00
           BsdBuf[80]= 0x00
           BsdBuf[81]= 0x00
           BsdBuf[82]= 0x00
           BsdBuf[83]= 0x00
           BsdBuf[84]= 0x00
           BsdBuf[85]= 0x00
           BsdBuf[86]= 0x00
           BsdBuf[87]= 0x00
           BsdBuf[88]= 0x00
           BsdBuf[89]= 0x00
           BsdBuf[90]= 0x00
           BsdBuf[91]= 0x00
           BsdBuf[92]= 0x00
           BsdBuf[93]= 'E'
           BsdBuf[94]= 'm'
           BsdBuf[95]= 'e'
           BsdBuf[96]= 'r'
           BsdBuf[97]= 's'
           BsdBuf[98]= 'o'
           BsdBuf[99]= 'n'
           BsdBuf[100]= ' '
           BsdBuf[101]= 'N'
           BsdBuf[102]= 'e'
           BsdBuf[103]= 'i'
           BsdBuf[104]= 't'
           BsdBuf[105]= 'z'
           BsdBuf[106]= 'k'
           BsdBuf[107]= 'e'
           BsdBuf[108]= 0x00
           BsdBuf[109]= 0x00
           BsdBuf[110]= 0x00
           BsdBuf[111]= 0x00
           BsdBuf[112]= 0x00
           BsdBuf[113]= 0x00
           BsdBuf[114]= 0x00
           BsdBuf[115]= 0x00
           BsdBuf[116]= 0x00
           BsdBuf[117]= 0x00
           BsdBuf[118]= 0x00
           BsdBuf[119]= 0x00
           BsdBuf[120]= 0x00
           BsdBuf[121]= 0x00
           BsdBuf[122]= 0x00
           BsdBuf[123]= 0x00
           BsdBuf[124]= 0x00
           BsdBuf[125]= 0x00
           BsdBuf[126]= 0x00
           BsdBuf[127]= 0x00
           BsdBuf[128]= 0x00
           BsdBuf[129]= 0x00
           BsdBuf[130]= 0x00
           BsdBuf[131]= 0x00
           BsdBuf[132]= 0x00
           BsdBuf[133]= 0x00
           BsdBuf[134]= 0x00
           BsdBuf[135]= 0x00
           BsdBuf[136]= 0x00
           BsdBuf[137]= 0x00
           BsdBuf[138]= 0x00
           BsdBuf[139]= 0x00
           BsdBuf[140]= 0x00
           BsdBuf[141]= 0x00
           BsdBuf[142]= 0x00
           BsdBuf[143]= 'M'
           BsdBuf[144]= 0x0a
           BsdBuf[145]= 0x0a
           BsdBuf[146]= 0xe1
           BsdBuf[147]= 0x07
           BsdBuf[148]= 0x00
           BsdBuf[149]= 0x00
           BsdBuf[150]= 0x00
           BsdBuf[151]= 0x00
           BsdBuf[152]= 0x00
           BsdBuf[153]= 0x00
           BsdBuf[154]= 0x00
           BsdBuf[155]= 0x00
           BsdBuf[156]= 0x00
           BsdBuf[157]= 0x00
           BsdBuf[158]= 0x00
           BsdBuf[159]= 0x00
           BsdBuf[160]= 0x00
           BsdBuf[161]= 0x00
           BsdBuf[162]= 0x00
           BsdBuf[163]= 0x00
           BsdBuf[164]= 0x00
           BsdBuf[165]= 0x00
           BsdBuf[166]= 0x00
           BsdBuf[167]= 0x00
           BsdBuf[168]= 0x00
           BsdBuf[169]= 0x00
           BsdBuf[170]= 0x00
           BsdBuf[171]= 0x00
           BsdBuf[172]= 0x00
           BsdBuf[173]= 0x00
           BsdBuf[174]= 0x00
           BsdBuf[175]= 0x00
           BsdBuf[176]= 0x00
           BsdBuf[177]= 0x00
           BsdBuf[178]= 0x00
           BsdBuf[179]= 0x00
           BsdBuf[180]= 0x00
           BsdBuf[181]= 0x00
           BsdBuf[182]= 0x00
           BsdBuf[183]= 0x00
           BsdBuf[184]= 0x00
           BsdBuf[185]= 0x00
           BsdBuf[186]= 0x00
           BsdBuf[187]= 0x00
           BsdBuf[188]= 0x00
           BsdBuf[189]= 0x00
           BsdBuf[190]= 0x00
           BsdBuf[191]= 0x00
           BsdBuf[192]= 0x00
           BsdBuf[193]= 0x00
           BsdBuf[194]= 0x00
           BsdBuf[195]= 0x00
           BsdBuf[196]= 0x00
           BsdBuf[197]= 0x00
           BsdBuf[198]= 0x00
           BsdBuf[199]= 0x00
           BsdBuf[200]= 0x00
           BsdBuf[201]= 0x00
           BsdBuf[202]= 0x00
           BsdBuf[203]= 0x00
           BsdBuf[204]= 0x00
           BsdBuf[205]= 0x00
           BsdBuf[206]= 0x00
           BsdBuf[207]= 0x00
           BsdBuf[208]= 0x00
           BsdBuf[209]= 0x00
           BsdBuf[210]= 0x00
           BsdBuf[211]= 0x00
           BsdBuf[212]= 0x00
           BsdBuf[213]= 0x00
           BsdBuf[214]= 0x00
           BsdBuf[215]= 0x00
           BsdBuf[216]= 0x00
           BsdBuf[217]= 0x00
           BsdBuf[218]= 0x00
           BsdBuf[219]= 0x00
           BsdBuf[220]= 0x00
           BsdBuf[221]= 0x00
           BsdBuf[222]= 0x00
           BsdBuf[223]= 0x00
           BsdBuf[224]= 0x00
           BsdBuf[225]= 0x00
           BsdBuf[226]= 0x00
           BsdBuf[227]= 0x00
           BsdBuf[228]= 0x00
           BsdBuf[229]= 0x00
           BsdBuf[230]= 0x00
           BsdBuf[231]= 0x9a
           BsdBuf[232]= 0x73
           BsdBuf[233]= 0xff

           size = (BsdBuf[4] * 256) + BsdBuf[3]

           for x in range(size):
                temp[x] = BsdBuf[x + 3]

           crc_16b = self.calcula_crc16(temp, size)

           BsdBuf[231]= crc_16b % 256
           BsdBuf[232]= crc_16b / 256

           connstream.write(BsdBuf)
#</main_class>
 
# Run the program
if __name__ == "__main__":
    app = wx.App()
    frame = MyForm().Show()
    app.MainLoop()

