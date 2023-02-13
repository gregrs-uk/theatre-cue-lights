#!/usr/bin/python

import wx
import wx.lib.buttons
import serial
import time
import threading

device = 'SERIAL_PORT_HERE'
numChannels = 6
(button_width, button_height) = (100, 50)

chan = []  # empty array to hold channels


class Status(object):
    """A status represents one particular state that a channel can be in"""

    def __init__(self, label, colour):
        """Init status"""
        code = None
        self.label = label
        self.colour = colour


# create the statuses
reset = Status(label='Reset', colour='black')
standby = Status(label='Standby', colour='red')
ready = Status(label='Ready', colour='red')
go = Status(label='GO', colour='green')

statuses = []
code = 0
# give the statuses a number code in order from 0 upwards and add them to the array
for this_status in [reset, standby, ready, go]:
    this_status.code = code
    statuses.append(this_status)
    code += 1


class Channel(object):
    """An object for each channel that will hold the visual elements for that channel and control it"""

    button = []  # empty dict to hold buttons for this channel
    status = reset  # status reported by Arduino for this channel, default is reset

    def __init__(self, index):
        """Init channel with index and number"""
        self.index = index
        self.num = index + 1

    def write(self, status):
        """Write status over serial to the Arduino"""

        status = int(status)
        self.index = int(self.index)

        ser.write(b'^')  # packet start
        ser.write(str(self.index).encode())  # channel
        ser.write(str(status).encode())  # channel


# create an ID for status update events from the Arduino
EVT_STATUS_UPDATE_ID = wx.NewIdRef(count=1)


def EVT_STATUS_UPDATE(win, func):
    """Define status update event for communication from Arduino"""
    win.Connect(-1, -1, EVT_STATUS_UPDATE_ID, func)


class StatusUpdateEvent(wx.PyEvent):
    """Event which carries channel and status data for updates from Arduino"""

    def __init__(self, channel, status):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_STATUS_UPDATE_ID)
        self.channel = channel
        self.status = status


class SerialListener(threading.Thread):
    """Thread class which listens for serial communication from Arduino"""

    def __init__(self, notify_window):
        """Init thread class"""
        threading.Thread.__init__(self)
        self.notify_window = notify_window
        self.daemon = True  # end thread when main window is closed
        self.start()

    def run(self):
        """Run serial listener"""

        while True:
            # if ^ followed by two bytes are available
            first_byte = str(ser.read())
            first_byte = first_byte[1:4]
            if (ser.in_waiting >= 2 and first_byte == "'^'"):
                first_byte = str(ser.read())[2:3]
                # check for error notification
                if first_byte != 'E':
                    rxChannel = int(first_byte)  # convert ASCII to int
                    rxStatus = int(ser.read())  # convert ASCII to int
                    # if first byte is good
                    if (rxChannel >= 0 and rxChannel < numChannels):
                        pass
                        # if second byte is also good
                        if (rxStatus >= 0 and rxStatus < len(statuses)):
                            # send status update event
                            wx.PostEvent(self.notify_window,
                                         StatusUpdateEvent(rxChannel, rxStatus))
                        # if second byte is bad
                        else:
                            ser.write(b'^Estatus not understood\n')
                    # if first byte is bad
                    else:
                        ser.write(b'^Echannel not understood\n')


class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        # calculate size of frame needed
        frame_size = (((button_width + 5) * (numChannels + 1)) + 50,
                      ((button_height + 5) * 4) + 30
                      )
        wx.Frame.__init__(self, parent, id, title,
                          pos=wx.DefaultPosition, size=frame_size)
        self.panel = wx.Panel(self)

        # try opening serial connection
        self.OpenSerialConnection(device)

        # create Channel instance for each channel and add to chan array
        for i in range(0, numChannels):
            chan.append(Channel(i))

        self.CreateGrid()
        self.panel.SetSizer(self.grid)

        # set up event handler for any status updates from Arduino
        EVT_STATUS_UPDATE(self, self.OnStatusUpdate)
        # start serial listener thread
        self.listener = SerialListener(self)

    def OpenSerialConnection(self, _device):
        """Try opening a serial connection to the Arduino using specified port"""
        try:
            global ser
            ser = serial.Serial(_device, 9600)
        except serial.SerialException:
            print("Couldn't connect to Arduino on %s" % device)
            error_box = wx.MessageDialog(
                parent=None, message="Couldn't connect to Arduino on %s" % _device,
                caption='Error', style=wx.OK | wx.ICON_ERROR)
            # for some reason we might need to call ShowModal twice to make it appear
            error_box.ShowModal()
            error_box.ShowModal()
            error_box.Destroy()
            exit(1)

    def OnButton(self, event):
        """Runs when a single-channel status button is pressed"""
        event_object = event.GetEventObject()
        # get the relevant channel and status from the button and write
        temp = event_object.status.code
        temp = repr(temp).encode('utf-8')
        chan[event_object.channel].write(temp)

    def OnAllButton(self, event):
        """Runs when an all-channel status button is pressed"""
        event_object = event.GetEventObject()
        # get the relevant status from the button and write for each channel
        for this_channel in chan:

            byteTemp = str(event_object.status.code)
            this_channel.write(byteTemp.encode())

    def OnStatusUpdate(self, event):
        """Runs when status update event is received from serial listener thread"""
        update_chan = chan[event.channel]
        update_chan.status = statuses[event.status]
        update_chan.status_text.ChangeValue(update_chan.status.label)
        update_chan.status_text.SetForegroundColour(update_chan.status.colour)

    def CreateGrid(self):
        self.grid = wx.FlexGridSizer(
            rows=len(statuses) + 1, cols=numChannels + 1, vgap=5, hgap=5)
        self.grid.SetFlexibleDirection(wx.VERTICAL)

        # first row
        self.grid.Add(
            wx.StaticText(parent=self.panel, label='All channels'), flag=wx.ALIGN_CENTER)
        for this_channel in chan:
            # channel numbers
            self.grid.Add(
                wx.StaticText(parent=self.panel, label='Chan %d' %
                              this_channel.num),
                flag=wx.ALIGN_CENTER)

        # second row
        self.grid.Add((0, 0))  # empty cell on left second row
        for this_channel in chan:
            # channel status text
            this_channel.status_text = wx.TextCtrl(
                parent=self.panel, style=wx.TE_READONLY | wx.TE_RICH | wx.TE_CENTER)
            this_channel.status_text.ChangeValue(this_channel.status.label)
            this_channel.status_text.SetForegroundColour(
                this_channel.status.colour)
            self.grid.Add(this_channel.status_text)
            # create empty button array for this channel
            this_channel.button = []

        # empty array to hold all-channel status buttons
        self.all_button = []

        # status buttons
        n = 0
        for this_status in [reset, standby, go]:
            # create all-channel button for this status
            self.all_button.append(wx.lib.buttons.ThemedGenButton(
                parent=self.panel, label=this_status.label, size=(button_width, button_height)))
            self.all_button[n].SetForegroundColour(this_status.colour)
            # add the relevant status to the button object
            self.all_button[n].status = this_status
            # add button to GridSizer and bind function to it
            self.grid.Add(self.all_button[n])
            self.all_button[n].Bind(wx.EVT_BUTTON, self.OnAllButton)

            # button for each channel for this status
            for this_channel in chan:
                # create the button in this channel's button array
                this_channel.button.append(wx.lib.buttons.ThemedGenButton(
                    parent=self.panel, label=this_status.label, size=(button_width, button_height)))
                this_channel.button[n].SetForegroundColour(this_status.colour)
                # add the relevant channel and status to the button object
                this_channel.button[n].channel = this_channel.index
                this_channel.button[n].status = this_status
                # add button to GridSizer and bind function to it
                self.grid.Add(this_channel.button[n])
                this_channel.button[n].Bind(wx.EVT_BUTTON, self.OnButton)
            n += 1


class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, 'Cue lights')
        frame.Show(True)
        frame.Centre()
        return True


app = MyApp(0)
app.MainLoop()
