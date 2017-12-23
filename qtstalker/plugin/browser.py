import os
import struct
from enigma import eConsoleAppContainer, getDesktop
from Components.VolumeControl import VolumeControl
import datasocket


class Browser:
	def __init__(self):
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

	def start(self):
		if not self.commandserver:
			size_w = getDesktop(0).size().width()
			size_h = getDesktop(0).size().height()
			self.commandserver = datasocket.CommandServer()
			datasocket.onCommandReceived.append(self.onCommandReceived)
			datasocket.onBrowserClosed.append(self.onBrowserClosed)
			container = eConsoleAppContainer()
			container.execute("export QT_QPA_PLATFORM=linuxfb; /usr/bin/stalker")

	def stop(self):
		if self.commandserver:
			self.commandserver = None

	def onCommandReceived(self, cmd, data):
		if cmd == 1000:
			for x in self.onMediaUrlChanged:
				x(data)
		elif cmd == 1001:
			for x in self.onStopPlaying:
				x()
		elif cmd == 1002:
			# pause
			for x in self.onPausePlaying:
				x()
		elif cmd == 1003:
			# resume
			for x in self.onResumePlaying:
				x()
		elif cmd == 1005:
			for x in self.onSkip:
				x(struct.unpack('!I', data))
		elif cmd == 1100:
			VolumeControl.instance and VolumeControl.instance.volUp()
		elif cmd == 1101:
			VolumeControl.instance and VolumeControl.instance.volDown()
		elif cmd == 1102:
			VolumeControl.instance and VolumeControl.instance.volMute()
		elif cmd == 1999:
			for x in self.onExit:
				x()

	def onBrowserClosed(self):
		self.commandserver = None
		for x in self.onExit:
			x()

	def sendCommand(self, cmd, data = ''):
		if self.commandserver is not None:
			self.commandserver.sendCommand(cmd, data)

	def sendUrl(self, url):
		self.sendCommand(1000, url)

	def StopMediaPlayback(self):
		self.sendCommand(5)

	def setPosition(self, dst_left, dst_top, dst_width, dst_height):
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
		if width > 720:
			dst_left = dst_left * 720 / width
			dst_width = dst_width * 720 / width
		if dst_left + dst_width > 720:
			dst_width = 720 - dst_left
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
			file = open('/proc/stb/vmpeg/0/dst_apply', 'w')
			file.write('00000001')
			file.close()
		except:
			return
