from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import eTimer, iPlayableService
import os
from enigma import fbClass, eRCInput
from browser import Browser
from enigma import fbClass, eRCInput, eServiceReference
import struct


browserinstance = None
g_session = None


class HbbTVWindow(Screen):
	skin = """
		<screen name="HbbTVWindow" position="0,0" size="1280,720" backgroundColor="transparent" flags="wfNoBorder" title="HbbTV Plugin">
		</screen>
		"""

	def __init__(self, session, url=None, pmt=0, tsid=0, onid=0, ssid=0, width=0, height=0, ait=None):
		Screen.__init__(self, session)

		global g_session
		g_session = session
		self._url = url
		self.closetimer = eTimer()
		self.closetimer.callback.append(self.stop_hbbtv_application)
		self.starttimer = eTimer()
		self.starttimer.callback.append(self.start_hbbtv_application)
		self.starttimer.start(100)
		self.mediatimer = eTimer()
		self.mediatimer.callback.append(self.mediatimercb)
		self.mediatimer.start(1000)
		self.count = 0
		self.ppos = 0
		self.llen = 0
		self.pmt = pmt
		self.tsid = tsid
		self.onid = onid
		self.ssid = ssid
		self.chantype = self.chanid = 0
		self.width = width
		self.height = height
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self.mediastate = 0
		self.ait = ait

		global browserinstance
		if not browserinstance:
			browserinstance = Browser()
		browserinstance.start('')

	def start_hbbtv_application(self):
		global browserinstance
		if browserinstance.connectedClients() == 0:
			self.count += 1
			if self.count > 50:
				self.close()
			return

		self.starttimer.stop()
		fbClass.getInstance().lock()
		eRCInput.getInstance().lock()

		browserinstance.onMediaUrlChanged.append(self.onMediaUrlChanged)
		browserinstance.onStopPlaying.append(self.onStopPlaying)
		browserinstance.onExit.append(self.onExit)
		browserinstance.onPausePlaying.append(self.onPausePlaying)
		browserinstance.onResumePlaying.append(self.onResumePlaying)
		browserinstance.onSkip.append(self.onSkip)

		browserinstance.sendAitData(self.ait)
		browserinstance.setServiceInfo(self.pmt, self.tsid, self.onid, self.ssid, self.chantype, self.chanid)
		browserinstance.sendUrl(self._url)
		browserinstance.showBrowser()

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
			iPlayableService.evStart: self.serviceStarted,
			iPlayableService.evStopped: self.serviceStopped,
			iPlayableService.evEOF: self.serviceEOF,
			iPlayableService.evGstreamerPlayStarted: self.serviceStarted
		})

	def serviceStarted(self):
		self.mediastate = 1

	def serviceEOF(self):
		self.serviceStopped()

	def serviceStopped(self):
		if self.mediastate == 1:
			global browserinstance
			browserinstance.StopMediaPlayback()
			self.mediastate = 0

	def stop_hbbtv_application(self):
		self.closetimer.stop()
		self.closetimer = None
		self.close()

	def onExit(self):
		file = open('/proc/stb/vmpeg/0/zorder', 'w')
		file.write('0')
		file.close()
		fbClass.getInstance().unlock()
		eRCInput.getInstance().unlock()
		global browserinstance
		browserinstance.onMediaUrlChanged.remove(self.onMediaUrlChanged)
		browserinstance.onStopPlaying.remove(self.onStopPlaying)
		browserinstance.onExit.remove(self.onExit)
		browserinstance.onPausePlaying.remove(self.onPausePlaying)
		browserinstance.onResumePlaying.remove(self.onResumePlaying)
		browserinstance.onSkip.remove(self.onSkip)
		browserinstance.setPosition(0, 0, self.width, self.height, 0)
		self.mediatimer.stop()
		global g_session
		g_session.nav.playService(self.lastservice)
		self.close()

	def onMediaUrlChanged(self, url):
		myreference = eServiceReference(4097, 0, url)
		global g_session
		g_session.nav.playService(myreference)
		self.mediastate = 0

	def onStopPlaying(self):
		global g_session
		g_session.nav.stopService()

	def onPausePlaying(self):
		global g_session
		service = g_session.nav.getCurrentService()
		if service is None:
			return False
		pauseable = service.pause()
		if pauseable is not None:
			pauseable.pause()

	def onResumePlaying(self):
		global g_session
		service = g_session.nav.getCurrentService()
		if service is None:
			return False
		pauseable = service.pause()
		if pauseable is not None:
			pauseable.unpause()

	def onSkip(self, val):
		if val is None:
			return
		self.doSeek(val[0] * 90)

	def mediatimercb(self):
		self.llen = 0
		self.ppos = 0
		if self.getCurrentLength() is not None:
			self.llen = self.getCurrentLength()
		if self.getCurrentPosition() is not None:
			self.ppos = self.getCurrentPosition()
		global browserinstance
		browserinstance.sendCommand(6, struct.pack('!II', self.pts_to_msec(self.llen), self.pts_to_msec(self.ppos)))

	def pts_to_msec(self, pts):
		return int(pts / 90)

	def getCurrentPosition(self):
		seek = self.getSeek()
		if seek is None:
			return
		r = seek.getPlayPosition()
		if r[0]:
			return
		return long(r[1])

	def getCurrentLength(self):
		seek = self.getSeek()
		if seek is None:
			return
		r = seek.getLength()
		if r[0]:
			return
		return long(r[1])

	def getSeek(self):
		global g_session
		service = g_session.nav.getCurrentService()
		if service is None:
			return
		seek = service.seek()
		if seek is None or not seek.isCurrentlySeekable():
			return
		return seek

	def doSeek(self, pts):
		seekable = self.getSeek()
		if seekable is None:
			return
		tenSec = 900000
		pts -= tenSec
		if pts >= tenSec:
			seekable.seekRelative(1, pts)
		else:
			seekable.seekTo(pts)
