from __future__ import absolute_import
import os
import struct
from enigma import eConsoleAppContainer, getDesktop
from Components.VolumeControl import VolumeControl
from Components.config import config
from . import datasocket
import six

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
		self.onGetPids = []
		self.onSetAudioPid = []
		self.commandserver = None
		self.urlsend = False

	def connectedClients(self):
		return self.commandserver.connectedClients()

	def start(self, portalv2):
		if not self.commandserver:
			size_w = getDesktop(0).size().width()
			size_h = getDesktop(0).size().height()
			self.commandserver = datasocket.CommandServer()
			datasocket.onCommandReceived.append(self.onCommandReceived)
			datasocket.onBrowserClosed.append(self.onBrowserClosed)
			arg = ""
			if portalv2:
				arg = " v2"
			container = eConsoleAppContainer()
			container.execute("export QT_QPA_FB_HIDECURSOR=1 QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=linuxfb:fb=/dev/fb/0; /usr/bin/stalker" + arg)

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
				x(struct.unpack("!I", data))
		elif cmd == 1006:
			for x in self.onGetPids:
				x()
		elif cmd == 1007:
			for x in self.onSetAudioPid:
				x(struct.unpack("!I", data))
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
		self.urlsend = False
		self.commandserver = None
		for x in self.onExit:
			x()

	def sendCommand(self, cmd, data = ''):
		if self.commandserver is not None:
			self.commandserver.sendCommand(cmd, six.ensure_binary(data))

	def sendUrl(self, url):
		self.sendCommand(1000, six.ensure_binary(url))

	def StopMediaPlayback(self):
		self.sendCommand(1002)
