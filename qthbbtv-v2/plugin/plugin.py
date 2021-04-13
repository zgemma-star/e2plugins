from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from GlobalActions import globalActionMap
from Components.Label import Label, MultiColorLabel
from Components.Button import Button
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigPosition, getConfigListEntry, ConfigBoolean, ConfigInteger, ConfigText, ConfigSelection, configfile
from Components.Sources.StaticText import StaticText
from Components.Task import Task
from enigma import eTimer, eServiceReference, iPlayableService, iServiceInformation, getDesktop, eRCInput, eServiceCenter, fbClass
from Components.ServiceEventTracker import ServiceEventTracker
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.InfoBar import InfoBar
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarTeletextPlugin, InfoBarRedButton
from Screens.ChannelSelection import service_types_tv
from Screens.LocationBox import MovieLocationBox
import re
import os
import sys
import socket
import time
from Tools.Directories import fileExists, copyfile, pathExists, createDir
from Components.ServicePosition import ServicePosition
from Components.VolumeControl import VolumeControl
import urllib
import urllib2
from hbbtv import HbbTVWindow


class HBBTVParser(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.started = False
		from Components.ServiceEventTracker import ServiceEventTracker
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
		self.openUrl = False

	def serviceStarted(self):
		if self.started:
			return
		if InfoBar.instance:
			InfoBar.instance.onHBBTVActivation.append(self.onHBBTVActivation)
			self.started = True

	def onHBBTVActivation(self):
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		startUrl = info.getInfoString(iServiceInformation.sHBBTVUrl)
		width = info and info.getInfo(iServiceInformation.sVideoWidth) or -1
		height = info and info.getInfo(iServiceInformation.sVideoHeight) or -1
		pmt = info and info.getInfo(iServiceInformation.sPMTPID) or -1
		tsid = info and info.getInfo(iServiceInformation.sTSID) or -1
		onid = info and info.getInfo(iServiceInformation.sONID) or -1
		ssid = info and info.getInfo(iServiceInformation.sSID) or -1

		print 'URL %s' % (startUrl)
		print 'PMT %d TSID %d ONID %d SSID %d' % (pmt, tsid, onid, ssid)

		ait = info.getAITApplications()

		self.openUrl = startUrl
		if not self.openUrl:
			self.close()
			return
		self.session.open(HbbTVWindow, self.openUrl, pmt, tsid, onid, ssid, width, height, ait)


def autostart(reason, **kwargs):
	global globalinstance
	if 'session' in kwargs:
		HBBTVParser(kwargs['session'])


def Plugins(**kwargs):
	return PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart)
