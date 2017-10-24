#!/usr/bin/env python
'''
Created on Dec 3, 2015
@author: Dagomi
'''

import os
import gi
import psutil
import threading
from xml.etree import ElementTree
from urllib import urlopen 

#http://www.bok.net/dash/tears_of_steel/cleartext/stream.mpd
#http://localhost/dash/trik_audio_video/stream.mpd

gi.require_version('Gst', '1.0')
from gi.repository import  Gst, GObject, Gtk, GdkX11 , GstVideo


import matplotlib.pyplot as plt
import os
import gi
import psutil
import threading
from xml.etree import ElementTree
from urllib import urlopen 
from cmath import sqrt
import time
import numpy as np
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas



Gst.init(None)

#--- Select environment (True)/Simulation (False)
SELECTOR = False
#URLPRUEBAS = 'http://www.bok.net/dash/tears_of_steel/cleartext/stream.mpd'
URLPRUEBAS = 'http://localhost/IIM/videos_dash/MMSYS/stream.mpd'
# -- Varibles---
UPDATEAXES = True #Activa la actualizacion de los ejes X de las graficas
REGISTRO = 0 # Activa el registro de las variables monitorizadas ON = 1 ; OFF = 0
GRAPH = 1 # Activa el graficado en tiempo real
BUFFERSIZE =    6000000000
PREROLLBUFFER = 3000000000

class GTK_Main(object):
    
    def __init__(self):
                #ESTO
        
        self.xnuevo = 0
        self.prueba =[]
        self.indice = 0
        self.qindex = 0
        
        self.CPUGRAPH = []
        self.BUFFERGRAPH = []
        self.BATTERYGRAPH = []
        self.BWGRAPH = []
        self.QUALITYSHOWGRAPH = []
        self.SelectRepresentation = 0
        self.TIME = 0
        
        GObject.threads_init()
        self.VARIABLE_ESTADO_BATERIA_TEMPORAL = 0
        self.PLAY = 0
        self.indice = 0
        self.UI() # Launch the User Interface
        self.Dashplayer() # Launch the Gst Client
        
        
        
        if GRAPH == 1:
            self.Algorithm()
            self.graph()
        
    def graph (self):
        
        
        window2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window2.set_title("Graph in real time")
        window2.set_default_size(800 , 600)
        window2.connect("destroy", Gtk.main_quit, "WM destroy")
        window2.set_border_width(10)
        
        
        #window 1
        # first image setup
        self.fig = Figure()
        self.PARAMETERS = self.fig.add_subplot(211)
        
        self.BW_Q = self.fig.add_subplot(212)
        #show Grid
        self.PARAMETERS.grid(True)
        self.BW_Q.grid(True)
        #Labels
        
        
        self.PARAMETERS.set_ylabel('Percentage (%)')
        self.PARAMETERS.set_xlabel('Temporal evolution of measured samples')
        self.BW_Q.set_ylabel('Bandwidth (Kbps)')
        self.BW_Q.set_xlabel('Temporal evolution of measured samples')
        
        # set specific limits for X and Y axes
        #xlim(xmin=1)
        
        self.PARAMETERS.set_xbound(0, 20)
        self.PARAMETERS.set_ylim([0, 100])
        
        # and disable figure-wide autoscale
        self.PARAMETERS.set_autoscale_on(False)
        # generates first "empty" plots
        self.BW_Q.set_xlim(0, 50)
        self.BW_Q.set_ylim(0, 15000)
        
        
        self.l_CPUGRAPH, = self.PARAMETERS.plot([], self.CPUGRAPH, label='CPU')
        self.l_CPUGRAPH.set_linestyle('dashed')
        self.l_CPUGRAPH.set_linewidth(2)
        self.l_BUFFERGRAPH, = self.PARAMETERS.plot([], self.BUFFERGRAPH, label='Buffer')

        self.l_BUFFERGRAPH.set_linewidth(2)
        self.l_BATTERYGRAPH, = self.PARAMETERS.plot([], self.BATTERYGRAPH, label='Battery')
        self.l_BATTERYGRAPH.set_linestyle('dotted')
        self.l_BATTERYGRAPH.set_linewidth(3)
        self.l_BWGRAPH, = self.BW_Q.plot([], self.BWGRAPH, label='BW')
        self.l_QUALITYSHOWGRAPH, = self.BW_Q.plot([], self.QUALITYSHOWGRAPH, label='Quality')
        self.l_BWGRAPH.set_linewidth(2)
        self.l_BWGRAPH.set_linestyle('dashed')
        self.l_QUALITYSHOWGRAPH.set_linewidth(2)
        
        # add legend to plot
        self.PARAMETERS.legend()
        self.BW_Q.legend()
        # we bind the figure to the FigureCanvas, so that it will be
        # drawn using the specific backend graphic functions
        canvas = FigureCanvas(self.fig)
        # add that widget to the GTK+ main window
        window2.add(canvas)
        # explicit update the graph (speedup graph visualization)
        self.update_draw()
        # exec our "updated" funcion when GTK+ main loop is idle
        GObject.idle_add(self.update_draw)
        
        self.window_group.add_window(window2)
        window2.show_all()
        
    def UI (self):
        #UI
        self.window_group=Gtk.WindowGroup()
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("DASH Client by IIM (UPV)")
        window.set_default_size(800 , 600)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        window.set_border_width(10)
        
        # horizontal separator
        hseparator_scenario = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vseparator_sliders = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        vseparator_simulation = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 5)
        
        sliders = Gtk.HBox()
        vbox.pack_end(sliders, False, False, 10)
        
        table = Gtk.Table(7, 8, False)
        table.set_col_spacings(10)
        sliders.add(table)

        #Labels
        #Sliders
        label_top_left = Gtk.Label(label="Buffer Occupancy (%)" )
        label_top_right = Gtk.Label(label="Battery Level (%)")
        label_bottom_left = Gtk.Label(label="CPU Load (%)")
        label_bottom_right = Gtk.Label(label="Available Bandwidth (Kbs/s)")
        
        #Simulations
        self.label_Simulation = Gtk.Label(label="Simulation")
        self.label_Buffer_Sim = Gtk.Label(label="Buffer: 0 %")
        self.label_Buffer_Sim.set_alignment(xalign=0, yalign=0.5) 
        self.label_Battery_state_Sim = Gtk.Label(label="")
        self.label_Battery_state_Sim.set_alignment(xalign=0, yalign=0.5)
        self.label_Battery_Sim = Gtk.Label(label="Battery: 0 %")
        self.label_Battery_Sim.set_alignment(xalign=0, yalign=0.5)
        self.label_CPU_Sim = Gtk.Label(label="CPU: 0%")
        self.label_CPU_Sim.set_alignment(xalign=0, yalign=0.5)
        self.label_BW_Sim = Gtk.Label(label="BW: 0 Mb/s")
        self.label_BW_Sim.set_alignment(xalign=0, yalign=0.5)

        #Thresholds
        self.label_Thresholds = Gtk.Label(label="Thresholds")
        self.label_Thresholds_Buffer = Gtk.Label(label="Buffer (0-100) % :")
        self.label_Thresholds_Buffer.set_alignment(xalign=1, yalign=0.5) 
        self.label_Thresholds_Low_Battery = Gtk.Label(label="Low Battery (0-100) % :")
        self.label_Thresholds_Low_Battery.set_alignment(xalign=1, yalign=0.5)
        self.label_Thresholds_Very_Low_Battery = Gtk.Label(label="Very Low Battery (0-100) % :")
        self.label_Thresholds_Very_Low_Battery.set_alignment(xalign=1, yalign=0.5)
        self.label_Thresholds_CPU = Gtk.Label(label="CPU (0-100) % :")
        self.label_Thresholds_CPU.set_alignment(xalign=1, yalign=0.5)
        self.label_Mean = Gtk.Label(label="Segments for BW measurement :")
        self.label_Mean.set_alignment(xalign=1, yalign=0.5)
        
        #TextEntry
        self.bufferTreshold = Gtk.Entry()
        self.bufferTreshold.set_max_length(3)
        
        self.batteryLowTreshold = Gtk.Entry()
        self.batteryLowTreshold.set_max_length(3)
        
        self.batteryVeryLowTreshold = Gtk.Entry()
        self.batteryVeryLowTreshold.set_max_length(3)
        
        
        self.cpuTreshold = Gtk.Entry()
        self.cpuTreshold.set_max_length(3)
        
        self.MeanTreshold = Gtk.Entry()
        self.MeanTreshold.set_max_length(2)

        # in the grid:
        # attach the first label in the top left corner   (left_attach,right_attach,top_attach,bottom_attach)
        #separators
        table.attach(hseparator_scenario,           0, 8, 0, 1)
        table.attach(vseparator_sliders,            2, 3, 0, 7)
        table.attach(vseparator_simulation,         5, 6, 0, 7)
        table.attach(label_top_left,                0, 1, 1, 2)
        table.attach(label_top_right,               1, 2, 1, 2)
        table.attach(label_bottom_left,             0, 1, 4, 5)
        table.attach(label_bottom_right,            1, 2, 4, 5)
      
        #sliders / buttons
        table.attach(self.label_Simulation,         3, 4, 1, 2)        
        table.attach(self.label_Buffer_Sim,         3, 4, 2, 3)
        table.attach(self.label_Battery_Sim,        3, 4, 3, 4)
        table.attach(self.label_BW_Sim,             3, 4, 4, 5)
        table.attach(self.label_CPU_Sim,            3, 4, 5, 6)
        table.attach(self.label_Battery_state_Sim,  3, 4, 6, 7)
        
        
        
        #text entry for tresholds
        table.attach(self.label_Thresholds,         7, 8, 1, 2)        
        table.attach(self.bufferTreshold,           7, 8, 2, 3)
        table.attach(self.batteryLowTreshold,       7, 8, 3, 4)
        table.attach(self.batteryVeryLowTreshold,   7, 8, 4, 5)
        table.attach(self.cpuTreshold,               7, 8, 5, 6)
        table.attach(self.MeanTreshold,                7, 8, 6, 7)

        #labels tresholds
        table.attach(self.label_Thresholds_Buffer,            6, 7, 2, 3)
        table.attach(self.label_Thresholds_Low_Battery,       6, 7, 3, 4)
        table.attach(self.label_Thresholds_Very_Low_Battery,  6, 7, 4, 5)
        table.attach(self.label_Thresholds_CPU,       6, 7, 5, 6)
        table.attach(self.label_Mean,                 6, 7, 6, 7)
        
        
        #Togle button Power supply
        PowerSupplyButton = Gtk.CheckButton("Charger")
        PowerSupplyButton.connect("toggled", self.on_button_power_supply, "1")
        table.attach (PowerSupplyButton, 1, 2, 2, 3)

        #Slider 1 Buffer
        self.Buffer_Sim = Gtk.SpinButton()
        adjustmentBuffer = Gtk.Adjustment(0, 0, 100, 1, 10, 0) 
        self.Buffer_Sim.set_adjustment(adjustmentBuffer)
        table.attach(self.Buffer_Sim, 0, 1, 3, 4)
        self.Buffer_Sim.connect("value-changed", self.BufferChange)
   
        #Slider 2 CPU
        self.CPU_Sim = Gtk.SpinButton()
        adjustmentCPU = Gtk.Adjustment(0, 0, 100, 1, 10, 0) 
        self.CPU_Sim.set_adjustment(adjustmentCPU)
        table.attach(self.CPU_Sim, 0, 1, 5, 6)
        self.CPU_Sim.connect("value-changed", self.CPUChange)
         
        #Slider 3 BW
        self.BW_Sim = Gtk.SpinButton()
        adjustmentBW = Gtk.Adjustment(0, 0, 50000, 100, 10, 0) #1 Kbyte = bits 8192
        self.BW_Sim.set_adjustment(adjustmentBW)
        table.attach(self.BW_Sim, 1, 2,5,6)
        self.BW_Sim.connect("value-changed", self.BWChange)
        
        #Slider 4 Battery
        self.Battery_Sim = Gtk.SpinButton()
        adjustmentBatt = Gtk.Adjustment(0, 0, 100, 1, 10, 0) 
        self.Battery_Sim.set_adjustment(adjustmentBatt)
        table.attach(self.Battery_Sim, 1, 2, 3, 4)
        self.Battery_Sim.connect("value-changed", self.BatteryChange)
        
        #Entry
        self.inputMpdUrl = Gtk.Entry()
        hbox.add(self.inputMpdUrl)
        self.button_open = Gtk.Button("Open")
        hbox.pack_start(self.button_open, False, False, 0)
        self.button_open.connect("clicked", self.open_mpd)
        
        #Buttons
        self.button_pause = Gtk.Button("Pause")
        hbox.pack_start(self.button_pause, False, False, 0)
        self.button_pause.connect("clicked", self.play_pause)
        
        self.icon = Gtk.Button()
        hbox.pack_start(self.icon, False, False, 0)
        image = Gtk.Image()
        image.set_from_file("source/icon2.png")
        image.show()
        self.icon.add(image)
        self.icon.connect("clicked", self.on_info_clicked)
        
        
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        
        self.window_group.add_window(window)
        window.show_all()
    
    def Dashplayer (self):
        #Gstreamer
  
        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make("souphttpsrc", "http-src")
        self.dashdemuxer = Gst.ElementFactory.make("dashdemux", "dashdemux")
        
        self.videoqueue = Gst.ElementFactory.make("queue2", "video_queue")
        
        self.videoqueue.set_property ( "use-buffering", True)
        self.videoqueue.set_property ("max-size-buffers",0)
        self.videoqueue.set_property ("high-percent",  100)
        self.videoqueue.set_property ("low-percent",  10,)
        self.videoqueue.set_property ("max-size-time", BUFFERSIZE)
        
        self.videodemuxer = Gst.ElementFactory.make("qtdemux", "videodemuxer")
        self.videodecoder = Gst.ElementFactory.make ("h264parse","video_decoder")
        self.videoconvert = Gst.ElementFactory.make ("avdec_h264","video_convert")
        self.videosink = Gst.ElementFactory.make("autovideosink", "video_sink")

        self.audioqueue = Gst.ElementFactory.make("queue2", "audio_queue")
        self.audioqueue.set_property ( "use-buffering", True)
        self.audioqueue.set_property ("max-size-buffers",0)
        self.audioqueue.set_property ("high-percent",  100)
        self.audioqueue.set_property ("low-percent",  10,)
        self.audioqueue.set_property ("max-size-time", BUFFERSIZE)
        
        self.audiodemuxer = Gst.ElementFactory.make("qtdemux", "audio_demuxer")
        self.audiodecoder = Gst.ElementFactory.make("aacparse", "audio_decoder")
        self.audioconv = Gst.ElementFactory.make("faad", "audio_converter")
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        
        self.textoverlay = Gst.ElementFactory.make("textoverlay", "text")
 
        self.player.add(self.source)
        self.player.add(self.dashdemuxer)
        self.player.add(self.videodemuxer)
        self.player.add(self.audiodemuxer)
        self.player.add(self.videodecoder)
        self.player.add(self.audiodecoder)
        self.player.add(self.audioconv)
        self.player.add(self.audiosink)
        self.player.add(self.videosink)
        self.player.add(self.videoqueue)
        self.player.add(self.audioqueue)
        self.player.add(self.videoconvert)
        
        self.player.add(self.textoverlay)
        
        self.source.link(self.dashdemuxer)
        self.dashdemuxer.link(self.videodemuxer)
        self.dashdemuxer.link(self.audiodemuxer)
        
        self.videoqueue.link(self.videodecoder)
        
        #self.videodecoder.link(self.videoconvert)
        self.videodecoder.link(self.videoconvert)
        self.videoconvert.link(self.textoverlay)
        self.textoverlay.link(self.videosink)
        
        self.audioqueue.link(self.audiodecoder)
        self.audiodecoder.link(self.audioconv)
        self.audioconv.link(self.audiosink)
        
        #Handlers
        self.dashdemuxer.connect("pad-added",self.dashdemuxer_callback)
        self.videodemuxer.connect("pad-added",self.videodemuxer_callback)
        self.audiodemuxer.connect("pad-added",self.audiodemuxer_callback)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        
    def open_mpd(self, w):
        #self.environment()
        self.PLAY = 1
        if self.button_open.get_label() == "Play":
                self.player.set_state(Gst.State.PLAYING)
        #check button value 
        if self.button_open.get_label() == "Open":
            #self.filepath = URLPRUEBAS
            self.filepath = self.inputMpdUrl.get_text()
            if self.filepath.startswith("http://"):
                print ('Url OK')
                self.button_open.set_label("Play")
                self.player.get_by_name("http-src").set_property("location", self.filepath)
                self.loadTemplateTile() #Obtain MPD parameters
                self.player.set_state(Gst.State.PLAYING)
            else:
                print ('Input a valid url')
                self.player.set_state(Gst.State.READY)
                self.button_open.set_label("Open")
                    
        
    def play_pause(self, w):
        print ('Pause')
        self.player.set_state(Gst.State.PAUSED)
        
    def on_message(self, bus, message):

        t = message.type
        level = self.videoqueue.get_property("current-level-time")
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        
        if t == Gst.MessageType.BUFFERING:
            if level <= PREROLLBUFFER:
                    print ("Buffering... %d" % level)
                    self.player.set_state(Gst.State.PAUSED)
                   
            else:
                self.player.set_state(Gst.State.PLAYING)
            
    
    def on_sync_message(self, bus, message):
        
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            xid = self.movie_window.get_property('window').get_xid()
            imagesink.set_window_handle(xid)
            
# #         if message.structure is None:
# #             return False
#         
        if message.structure.get_name() == "prepare-xwindow-id":
            Gtk.gdk.threads_enter()
            Gtk.gdk.display_get_default().sync()
            win_id = self.movie_window.get_property('window').get_xid()
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(win_id)
            Gtk.gdk.threads_leave()
                
    def dashdemuxer_callback(self, demuxer, pad):
            print ('demuxer_call_bak')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "audio_00":
                qv_pad = self.videodemuxer.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "video_00":
                qa_pad = self.audiodemuxer.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')

    def videodemuxer_callback(self, demuxer, pad):
            print ('videodemuxer_callback')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "video_0":
                qv_pad = self.videoqueue.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "audio_0":
                qa_pad = self.audioqueue.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')
    
    def audiodemuxer_callback(self, demuxer, pad):
            print ('audiodemuxer_callback')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "video_0":
                qv_pad = self.videoqueue.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "audio_0":
                qa_pad = self.audioqueue.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')

    '''
    UI
    '''
    def on_button_power_supply(self, button, name):
        if SELECTOR:
            print ("environment Batt State")
            Battery = []
            Battery = self.environmentBattery()
            self.dashdemuxer.set_property("system-battery-state", int(str(Battery[1])))
            self.dashdemuxer.set_property("system-battery-charge", int(str(Battery[0])))
        else:
            #print ("Simulation Batt State") 
            if button.get_active():
                self.label_Battery_state_Sim.set_text("Power supply")
                self.VARIABLE_ESTADO_BATERIA_TEMPORAL = 1
            else:
                self.label_Battery_state_Sim.set_text("")
                self.VARIABLE_ESTADO_BATERIA_TEMPORAL = 0
                
    def BatteryChange(self, event):
        if SELECTOR:
            print ("environment Batt Level")
            Battery = []
            Battery = self.environmentBattery()
            self.SYSTEM_BATTERY_CHARGE = int(str(Battery[1]))
            
        else:
            self.label_Battery_Sim.set_text("Battery: " + str(int(self.Battery_Sim.get_value())) + "%")

    def BufferChange(self, event):
        if SELECTOR:
            print ("environment Buffer (not implemented yet)")
        else:
        
            '''
            0         Threshhold     100
            |------------|-----------|
                Danger        Optimal
             '''
            self.label_Buffer_Sim.set_text("Buffer: " + str(int(self.Buffer_Sim.get_value())) + "%")

                
    def CPUChange(self, event):
        if SELECTOR:
            print ("environment CPU Load ")
        else:
            #print ("Simulation CPU Load")
            self.label_CPU_Sim.set_text("CPU: " + str(int(self.CPU_Sim.get_value())) + "%" )

    def BWChange(self, event):    
        self.label_BW_Sim.set_text(("BW: %0.1f Mb/s") % (int(self.BW_Sim.get_value())*0.001))  
    
    '''
    I N F O | B U T T O N 
    '''
    
    
    def on_info_clicked(self, widget):
        print ("Info Button call back")

        # the textview
     
        window3 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window3.set_title("Contact Info")
        window3.set_default_size(400 , 300)
        window3.show_all()
        
        
        Info = Gtk.HBox()
               
        table = Gtk.Table(3, 3, False)
        table.set_col_spacings(10)
        Info.add(table)
        window3.add(Info)
        
        #Load Image from png (Logo)
        image = Gtk.Image()
        image.set_from_file("source/imagotipo_iim_con_letras.png")
        #Contact Text
        textview = Gtk.TextView()
        textbuffer = textview.get_buffer()
        # Load the file textview-basic.py into the text window
        infile = open("source/contactInfo.txt", "r")
        
        if infile:
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)
            
        l2 = Gtk.Label(label="Texto" )
#         textview.set_justification(Gtk.JUSTIFY_CENTER)

        # in the grid:
        # (left_attach,right_attach,top_attach,bottom_attach)
     
        table.attach(image,                1, 2, 0, 1)
        table.attach(textview,                0, 3, 1, 2)
        


        window3.show_all()
    def environmentBattery (self):
        BATT_NOW     =   "/sys/class/power_supply/BAT0/charge_now"
        BATT_FULL    =  "/sys/class/power_supply/BAT0/charge_full"
        BATT_STATUS  =     "/sys/class/power_supply/BAT0/status"    
    
        full = open(BATT_FULL, 'r')
        full_value = full.read()
        
        now = open(BATT_NOW, 'r')
        now_value = now.read()
        
        status = open(BATT_STATUS, 'r')
        status_value = status.read()
        
        if 'Charging' in  status_value:
            statusBattery = 'Charging'
        
        elif 'Discharging' in status_value:
            statusBattery = 'Discharging'
        
        elif 'Full' in status_value:
            statusBattery = ' Full '

        BatteryLoad = (int(now_value) / ( int(full_value)/100))

        full.close()
        now.close()
        status.close()
        
        return (BatteryLoad , statusBattery )
        
    

    def loadTemplateTile(self):
        ADAPTATIONSET = []
        self.BANDWITH_MPD = []
        #Load Xml
        manifestXmlTree = ElementTree.parse(urlopen(self.filepath))
        root = manifestXmlTree.getroot()
        tag = root.tag
        xmlns = tag.replace("MPD", "")
        PERIOD = root[0]
        
        for index in range (0,(len(PERIOD)),1):

            ADAPTATIONSET.append(PERIOD[index])
            ADAPTATIONSETATTRIB =(ADAPTATIONSET[index].attrib)
            if ADAPTATIONSETATTRIB["mimeType"] == "video/mp4":
                ADAPTATIONSET_VIDEO = ADAPTATIONSET[index]
                
        REPRESENTATION = (ADAPTATIONSET_VIDEO.findall( xmlns +"Representation"))
        
        for index in range (0,len(REPRESENTATION),1):
            REPRESENTATIONATTRIB = REPRESENTATION[index].attrib
            self.BANDWITH_MPD.append(REPRESENTATIONATTRIB['bandwidth'])
        print self.BANDWITH_MPD
        
    def Algorithm (self):
        
        threading.Timer(2.0, self.Algorithm).start()
        
        if self.PLAY == 1:
            if REGISTRO == 1 :
                self.registro("time", self.TIME)
                self.TIME = self.TIME + 1
        
        
        print ("--- Algoritmo ---")
        #Check threshold imputs 
        #CPU 
        if self.cpuTreshold.get_text() == "":
            MAX_CPU     = 85
            print "bufferTreshold is empty set as default: %s " %  MAX_CPU
        else:
            MAX_CPU = int(self.cpuTreshold.get_text())
            print "bufferTreshold set as : %s " %  MAX_CPU
        
        #BATT TH1    
        if self.batteryVeryLowTreshold.get_text() == "":
            VERY_LOW_BATT_LOAD = 5
            print "batteryVeryLowTreshold is empty as default: %s " %  VERY_LOW_BATT_LOAD 
        else:    
            VERY_LOW_BATT_LOAD = int(self.batteryVeryLowTreshold.get_text())   
            print "batteryVeryLowTreshold set as: %s " %  VERY_LOW_BATT_LOAD 
        
        #BATT TH2
        if self.batteryLowTreshold.get_text() == "":
            LOW_BATT_LOAD = 15
            print "batteryLowTreshold is empty as default: %s " %  LOW_BATT_LOAD 
        else:    
            LOW_BATT_LOAD = int(self.batteryLowTreshold.get_text())   
            print "batteryLowTreshold set as: %s " %  LOW_BATT_LOAD 
        
        #BUFF            
        if self.bufferTreshold.get_text() == "":
            MIN_BUFFER      = 50
            print "cpuTreshold is empty as default: %s " %  MIN_BUFFER   
        else:
            MIN_BUFFER = int(self.bufferTreshold.get_text())
            print "cpuTreshold set as: %s " %  MIN_BUFFER   
        
        
        #environment (at the momenr only simulated conditions)
        SYSTEMCPU   = int(self.CPU_Sim.get_value())
        SYSTEM_BATTERY_STATE = self.VARIABLE_ESTADO_BATERIA_TEMPORAL
        SYSTEM_BATTERY_CHARGE = int(self.Battery_Sim.get_value())
        SYSTEM_BUFFER = int(self.Buffer_Sim.get_value())
        printBaW =  (int(self.BW_Sim.get_value())*1024)
        if self.PLAY == 1:
            if REGISTRO == 1 :
                self.registro("BW", printBaW)
                self.registro("CPU", SYSTEMCPU)
                self.registro("Buffer", SYSTEM_BUFFER)
                self.registro("BatteryState", SYSTEM_BATTERY_STATE)
                self.registro("BatteryCharge", SYSTEM_BATTERY_CHARGE)
        
        if SYSTEMCPU > MAX_CPU :
            print ("System CPU overload")
            #Calidad minima
            if self.PLAY == 1:
                self.previousSegmentQuality()
#                 self.SelectRepresentation =  int(self.BANDWITH_MPD[0])
#                 self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                if self.PLAY == 1:
                    if REGISTRO == 1 :
                        self.registro("CPU_TH", 0)
        
        elif SYSTEMCPU <= MAX_CPU :
            print ("System CPU normal")
            #Uso normal del algoritmo
            if self.PLAY == 1:
                if REGISTRO == 1 :
                    self.registro("CPU_TH", 1)
            #Check Battery
            if SYSTEM_BATTERY_STATE == 0: #Uso de la Bateria
                print ("uso bateria")
                if SYSTEM_BATTERY_CHARGE <= LOW_BATT_LOAD: #Check battery low
                    print ("Bateria baja primer humbral")
                    #self.midleQuality()
                    self.previousSegmentQuality()
                    if SYSTEM_BATTERY_CHARGE <= VERY_LOW_BATT_LOAD: #Check Very Low batt
                            #usar text overlay
                            self.textOverlayFunction("Battery level below: %s" % VERY_LOW_BATT_LOAD )
                            print ("Bateria muy baja segundo humbral")
                            if self.PLAY == 1:
                                self.SelectRepresentation =  int(self.BANDWITH_MPD[0])
                                self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                    elif SYSTEM_BATTERY_CHARGE > VERY_LOW_BATT_LOAD:
                        self.textOverlayFunction("")
                        print ("Bateria normal")
                        self.previousSegmentQuality()

#                         if SYSTEM_BUFFER <= MIN_BUFFER :
#                             print ("Buffer bajo")
#                             self.previousSegmentQuality()
#                         elif SYSTEM_BUFFER > MIN_BUFFER:
#                             print ("Buffer OK")
#                             #selecciono la mejor calidad seun el BW
#                             self.nextSegmentQuality()
                elif SYSTEM_BATTERY_CHARGE > LOW_BATT_LOAD:
                        self.textOverlayFunction("")
                        print ("Bateria normal")
                                    #Rutina Buffer
                        if SYSTEM_BUFFER <= MIN_BUFFER :
                            print ("Buffer bajo")
                            #self.midleQuality()
                            self.previousSegmentQuality()
                        elif SYSTEM_BUFFER > MIN_BUFFER:
                            print ("Buffer OK")
                            #selecciono la mejor calidad seun el BW
                            self.nextSegmentQuality()
            
            elif SYSTEM_BATTERY_STATE == 1: #Uso del cargador
                print ("uso cargador")
                self.textOverlayFunction("")
                #Rutina Buffer
#                 if SYSTEM_BUFFER <= MIN_BUFFER :
#                     print ("Buffer bajo calidades pregresivamente:")
#                     #self.midleQuality()
#                     self.previousSegmentQuality()
#                 elif SYSTEM_BUFFER > MIN_BUFFER:
#                     print ("Buffer OK")
#                     #selecciono la mejor calidad seun el BW
#                     self.nextSegmentQuality()  
                    
                self.nextSegmentQuality()
 
    def nextSegmentQuality(self):
        if self.PLAY == 1:
            print ("nextSegmentQuality")
            #Select the best Quality in therms of BW
            #BW = (int(self.BW_Sim.get_value())*1024)
            
            self.prueba.insert(self.indice, (int(self.BW_Sim.get_value())*1024))
            print self.indice
            
            
            
            if self.MeanTreshold.get_text() == "":
                factor_amoritguado = 2
                print "Mean default: %s " %  factor_amoritguado 
            else:    
                factor_amoritguado = int(self.MeanTreshold.get_text())
                print "Mean set as: %s " %  factor_amoritguado 
                
            if (self.indice >= factor_amoritguado):
                self.indice = 0
                print self.prueba
                self.BW = float(sum(self.prueba))/len(self.prueba) if len(self.prueba) > 0 else float('nan')
                print ("MEAN %s ") % self.BW
                self.prueba = []
                self.indice = 0
    
                for i in range (0,len(self.BANDWITH_MPD),1):
                    if self.BW >= int(self.BANDWITH_MPD[i]):
                        action = "subo"
                        self.qindex = i
                        self.SelectRepresentation =  int(self.BANDWITH_MPD[i])
                        self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                    elif  self.BW < int(self.BANDWITH_MPD[0]):
                        action = "bajo"
                        self.SelectRepresentation =  int(self.BANDWITH_MPD[0])
                        self.qindex = 0
                        self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                
                print (" %s de calidad") % self.qindex
                if self.PLAY == 1:
                            if REGISTRO == 1 :
                                self.registro("Quality", self.qindex)
                                self.registro("QualityBW", self.SelectRepresentation)
                                self.registro("BW_amortiguado", self.BW)
            
                print self.SelectRepresentation
                self.indice = 0
            self.indice += 1
    
    def previousSegmentQuality(self):
        if self.PLAY == 1:
            print self.BANDWITH_MPD
            print ("previousSegmentQuality")
            print ("indice calidad %s " ) % self.indice
            calidadactual = self.qindex

            if calidadactual == 0 :
                
                self.SelectRepresentation =  int(self.BANDWITH_MPD[0])
                print self.SelectRepresentation
                self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                print ("ya estoy en la mas baja")
                self.registro("Quality", 0)
                self.registro("QualityBW", 0)
                self.registro("BW_amortiguado", self.BW)
            else:
                self.qindex = self.qindex - 1
                if self.qindex == 0:
                    self.SelectRepresentation =  int(self.BANDWITH_MPD[0])
                else:
                    print ("Desciendo a %s " ) % calidadactual
                    self.SelectRepresentation =  int(self.BANDWITH_MPD[self.qindex - 1])
                    print self.SelectRepresentation
                    self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
                    self.registro("Quality", self.qindex - 1)
                    self.registro("QualityBW", self.SelectRepresentation)
                    self.registro("BW_amortiguado", self.BW)
                    print (" %s de calidad") % self.qindex

        #Aqui llamo al demux
        #self.dashdemuxer.set_property("bw-sim", int(SelectRepresentation))   
    
    def textOverlayFunction (self, text):
            self.textoverlay.set_property("halignment", 0)
            self.textoverlay.set_property("valignment", 2)
            self.textoverlay.set_property("auto-resize", False)
            self.textoverlay.set_property("text", text)
            
#     def midleQuality (self):
#         if self.PLAY == 1:
#             print("Calidad media")
# 
#             self.SelectRepresentation =  int(self.BANDWITH_MPD[len(self.BANDWITH_MPD)/2]) 
#             print self.SelectRepresentation
#             if self.PLAY == 1:
#                         if REGISTRO == 1 :
#                             self.registro("Quality", 3)
#                             self.registro("QualityBW", self.SelectRepresentation)
#             self.dashdemuxer.set_property("bw-sim",self.SelectRepresentation)
    
    def registro (self, proceso, valor):
        
        outfile = open(proceso+'.txt', 'a') 
        outfile.write(str(valor)+';')
        outfile.close()
    def update_draw(self,*args):
        """Update the graph with current values"""
        # append new data to the datasets
        

        self.CPUGRAPH.append(int(self.CPU_Sim.get_value()))
        self.BUFFERGRAPH.append(int(self.Buffer_Sim.get_value()))
        self.BATTERYGRAPH.append(int(self.Battery_Sim.get_value()))
        self.BWGRAPH.append(int(self.BW_Sim.get_value()))
        
        self.QUALITYSHOWGRAPH.append(int(self.SelectRepresentation)/1024)
        # update lines data using the lists with new data
        self.l_CPUGRAPH.set_data(range(len(self.CPUGRAPH)), self.CPUGRAPH)
        self.l_BUFFERGRAPH.set_data(range(len(self.BUFFERGRAPH)), self.BUFFERGRAPH)
        self.l_BATTERYGRAPH.set_data(range(len(self.BATTERYGRAPH)), self.BATTERYGRAPH)
        self.l_BWGRAPH.set_data(range(len(self.BWGRAPH)), self.BWGRAPH)
        self.l_QUALITYSHOWGRAPH.set_data(range(len(self.QUALITYSHOWGRAPH)), self.QUALITYSHOWGRAPH)
        
        # force a redraw of the Figure
        self.fig.canvas.draw()
        #Update the X (time representation) every "n" seconds
        if UPDATEAXES:  
            self.xnuevo = self.xnuevo + 1 
            self.PARAMETERS.set_xbound(0, self.xnuevo)
            self.BW_Q.set_xlim(0, self.xnuevo)
        
        time.sleep(0.05)  
        return True

if __name__ == "__main__":
    GTK_Main()# run Python Class
    GObject.threads_init()
    Gtk.main()# run Ui