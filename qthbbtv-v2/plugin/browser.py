import os
import struct
from enigma import eConsoleAppContainer, getDesktop
from Components.VolumeControl import VolumeControl
import datasocket


class Browser:
	def __init__(self, urlcallback=None):
		self.onUrlChanged = []
		self.onUrlInfoChanged = []
		self.onMediaUrlChanged = []
		self.onExit = []
		self.onStopPlaying = []
		self.onPausePlaying = []
		self.onResumePlaying = []
		self.onSkip = []
		self.commandserver = None

	def connectedClients(self):
		return self.commandserver.connectedClients()

	def start(self, url):
		if not self.commandserver:
			size_w = getDesktop(0).size().width()
			size_h = getDesktop(0).size().height()
			self.commandserver = datasocket.CommandServer()
			datasocket.onCommandReceived.append(self.onCommandReceived)
			datasocket.onBrowserClosed.append(self.onBrowserClosed)
			container = eConsoleAppContainer()
			container.execute("export QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=linuxfb; /usr/bin/qthbbtv")
		self.sendUrl(url)

	def stop(self):
		if self.commandserver:
			self.commandserver = None

	def onCommandReceived(self, cmd, data):
		if cmd == 1000:
			for x in self.onMediaUrlChanged:
				x(data)
		elif cmd == 1001:
			for x in self.onExit:
				x()
		elif cmd == 1002:
			for x in self.onStopPlaying:
				x()
		elif cmd == 1003:
			# pause
			for x in self.onPausePlaying:
				x()
		elif cmd == 1004:
			# resume
			for x in self.onResumePlaying:
				x()
		elif cmd == 1005:
			x, y, w, h = struct.unpack('!IIII', data)
			self.setPosition(x, y, w, h, 1)
		elif cmd == 1006:
			for x in self.onSkip:
				x(struct.unpack('!I', data))
		elif cmd == 1007:
			VolumeControl.instance and VolumeControl.instance.volUp()
		elif cmd == 1008:
			VolumeControl.instance and VolumeControl.instance.volDown()
		elif cmd == 1009:
			VolumeControl.instance and VolumeControl.instance.volMute()

	def onBrowserClosed(self):
		self.commandserver = None
		for x in self.onExit:
			x()

	def sendCommand(self, cmd, data=''):
		if self.commandserver is not None:
			self.commandserver.sendCommand(cmd, data)

	def sendUrl(self, url):
		self.sendCommand(1, url)

	def showBrowser(self):
		self.sendCommand(2)

	def setServiceInfo(self, pmt, tsid, onid, ssid, chantype, chanid):
		self.sendCommand(3, struct.pack('!IIIIII', int(pmt), int(tsid), int(onid), int(ssid), int(chantype), int(chanid)))

	def sendAitData(self, ait):
		s = ''
		s = struct.pack('b', len(ait))
		for x in ait:
			s += struct.pack("II%ds" % (len(x[1]) + 1,), x[0], len(x[1]) + 1, x[1] + '\x00')
		self.sendCommand(4, s)

	def StopMediaPlayback(self):
		self.sendCommand(5)

	def setPosition(self, dst_left, dst_top, dst_width, dst_height, mode=0):
		width = 1280
		height = 720
		if width == -1:
			width = 1280
		if height == -1:
			height = 720
		if dst_width > 1280:
			dst_width = 1280
		if dst_height > 720:
			dst_height = 720
		if mode == 1:
			if width > 720:
				dst_left = dst_left * 720 / width
				dst_width = dst_width * 720 / width
		if dst_left + dst_width > 720:
			dst_width = 720 - dst_left
		if mode == 1:
			if height > 576:
				dst_top = dst_top * 576 / height
				dst_height = dst_height * 576 / height
		if dst_top + dst_height > 576:
			dst_height = 576 - dst_top
		try:
			file = open('/proc/stb/vmpeg/0/dst_left', 'w')
			file.write('%08X' % dst_left)
			file.close()
			file = open('/proc/stb/vmpeg/0/dst_top', 'w')
			file.write('%08X' % dst_top)
			file.close()
			file = open('/proc/stb/vmpeg/0/dst_width', 'w')
			file.write('%08X' % dst_width)
			file.close()
			file = open('/proc/stb/vmpeg/0/dst_height', 'w')
			file.write('%08X' % dst_height)
			file.close()
			if fileExists("/proc/stb/vmpeg/0/dst_apply"):
				file = open('/proc/stb/vmpeg/0/dst_apply', 'w')
				file.write('00000001')
				file.close()
		except:
			return
