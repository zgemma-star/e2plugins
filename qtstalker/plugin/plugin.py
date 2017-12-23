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
from Components.config import config, ConfigSubsection, ConfigPosition, getConfigListEntry, ConfigBoolean, ConfigInteger, ConfigText, ConfigSelection, configfile, NoSave
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
import re, os, sys, socket, time
from Tools.Directories import fileExists, copyfile, pathExists, createDir
from Components.ServicePosition import ServicePosition
from Components.VolumeControl import VolumeControl
import urllib
import urllib2
import netifaces
from stalker import StalkerTVWindow

config.misc.stalker = ConfigSubsection()
config.misc.stalker.portal = ConfigText(default = 'http://')

class StalkerEdit(Screen, ConfigListScreen):
	skin = """
		<screen name="StalkerEdit" position="center,center" size="710,450" title="StalkerEdit">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />

			<ePixmap pixmap="skin_default/buttons/green.png" position="150,0" size="140,40" alphatest="on" />
			<widget source="key_green" render="Label" position="150,0" zPosition="1" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />

			<widget name="config" position="5,50" size="700,250" zPosition="1" scrollbarMode="showOnDemand" />
			<widget source="mac" render="Label" position="300,0" size="400,40" zPosition="10" font="Regular;24" halign="left" valign="center" />
		</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, self.session)

		self.list = []
		ConfigListScreen.__init__(self, self.list,session = self.session)

		self.urlConfigEntry = NoSave(ConfigText(default = config.misc.stalker.portal.value, visible_width = 50, fixed_size = False))
		self.urlEntry = getConfigListEntry(_("Portal url"), self.urlConfigEntry)
		self.list.append(self.urlEntry)

		addrs = netifaces.ifaddresses('eth0')
		if_mac = addrs[netifaces.AF_LINK][0]['addr']
		self["mac"] = StaticText()
		self["mac"].setText(_("MAC: ") + if_mac)

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		self["actions"] = NumberActionMap(["SetupActions" , "ColorActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"cancel": self.close,
			"red": self.close,
			"green": self.ok,
		}, -2)

	def ok(self):
		config.misc.stalker.portal.value = self.urlConfigEntry.value
		config.misc.stalker.save()
		self.close()

def setup(session, **kwargs):
	session.open(StalkerEdit)

def main(session, **kwargs):
	service = session.nav.getCurrentService()
	info = service and service.info()
	width = info and info.getInfo(iServiceInformation.sVideoWidth) or -1
	height = info and info.getInfo(iServiceInformation.sVideoHeight) or -1
	session.open(StalkerTVWindow, width, height)

def Plugins(**kwargs):
	menus = []
	menus.append(PluginDescriptor(name='Stalker', description='Stalker Plugin', where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='', fnc=main))
	menus.append(PluginDescriptor(name='Stalker Setup', description='Stalker Setup', where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='', fnc=setup))
	menus.append(PluginDescriptor(name='Stalker Setup', description='Stalker Setup', where=PluginDescriptor.WHERE_PLUGINMENU, icon='stalker.png', fnc=setup))
	return menus
