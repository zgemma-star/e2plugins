import os
import netifaces
import datetime
from enigma import iServiceInformation, eTimer, eConsoleAppContainer

from Components.ActionMap import NumberActionMap, ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubList, ConfigSubsection, ConfigYesNo, getConfigListEntry, ConfigInteger, ConfigText
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Sources.Boolean import Boolean
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from stalker import StalkerTVWindow

config.plugins.Stalker = ConfigSubsection()
config.plugins.Stalker.ntpurl = ConfigText(default = "")
config.plugins.Stalker.stalkermac = ConfigYesNo(default = False)
config.plugins.Stalker.showinextensions = ConfigYesNo(default = True)
config.plugins.Stalker.showinmenu = ConfigYesNo(default = False)
config.plugins.Stalker.autostart = ConfigYesNo(default = False)
config.plugins.Stalker.portalv2 = ConfigYesNo(default = False)
config.plugins.Stalker.preset = ConfigInteger(default = 0)
config.plugins.Stalker.presets = ConfigSubList()
NUMBER_OF_PRESETS = 6
for x in range(NUMBER_OF_PRESETS):
	preset = ConfigSubsection()
	preset.portal = ConfigText(default = "http://")
	config.plugins.Stalker.presets.append(preset)


class StalkerEdit(Screen, ConfigListScreen):
	skin = """
		<screen name="StalkerEdit" position="center,center" size="1010,410" title="StalkerEdit">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,50" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,50" font="Regular;24" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />

			<ePixmap pixmap="skin_default/buttons/green.png" position="150,0" size="140,50" alphatest="on" />
			<widget source="key_green" render="Label" position="150,0" zPosition="1" size="140,50" font="Regular;24" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />

			<ePixmap pixmap="skin_default/buttons/blue.png" position="300,0" size="140,50" alphatest="on" />
			<widget source="key_blue" render="Label" position="300,0" zPosition="1" size="140,50" font="Regular;24" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />

			<widget name="config" position="5,65" size="1000,500" itemHeight="32" font="Regular;28" zPosition="1" scrollbarMode="showOnDemand" />
			<widget source="mac" render="Label" position="680,0" size="320,40" zPosition="10" font="Regular;28" halign="left" valign="center" />
		</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, self.session)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

		self.loadPortals()
		self["mac"] = StaticText()
		self.setMac()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_blue"] = StaticText("USB")
		self.configfound = False

		self["actions"] = NumberActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"cancel": self.close,
			"red": self.close,
			"green": self.save,
			"blue": self.keyBlue,
		}, -2)

		self.setupTimer = eTimer()
		self.setupTimer.callback.append(self.setupCallback)
		self.setupTimer.start(1)

	def setupCallback(self):
		self.setupTimer.stop()
		parts = [ (r.tabbedDescription(), r.mountpoint, self.session) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False) if os.access(r.mountpoint, os.F_OK|os.R_OK) ]
		for p in parts:
			if p[1] == "/":
				continue
			for root, dirs, files in os.walk(p[1]):
				for f in files:
					self.path = os.path.join(root, f)
					if ".stalkerconfig" in self.path:
						self.configfound = True
						self["key_blue"].setText(_("Load Settings"))
						return					
					del dirs[:]

	def keyBlue(self):
		if self.configfound:
			self.session.openWithCallback(self.confirmationConfig, MessageBox, _("Install Stalker config?"))
		else:
			self.session.open(MessageBox, _("No stalker config file found"), MessageBox.TYPE_INFO, timeout=10)

	def setMac(self):
		addrs = netifaces.ifaddresses('eth0')
		if config.plugins.Stalker.stalkermac.value == True:
			if_mac = "00:1a:79" + str(addrs[netifaces.AF_LINK][0]['addr'][8:])
		else:
			if_mac = str(addrs[netifaces.AF_LINK][0]['addr'])
		self["mac"].setText(_("MAC: %s")% if_mac)

	def changedEntry(self):
		if self["config"].getCurrent()[1] == config.plugins.Stalker.stalkermac:
			self.setMac()

	def confirmationConfig(self, result):
		if result:
			data = open(self.path, "r").read()
			if len(data):
				data = data.split("\n")
				for x in data:
					y = x.split(" ")
					if len(y) == 2:
						if y[0] == "ntp":
							config.plugins.Stalker.ntpurl.value = y[1]
					if len(y) == 3:
						if y[0] == "portal":
							config.plugins.Stalker.presets[int(y[1])].portal.value = y[2]
							config.plugins.Stalker.presets[int(y[1])].save()
				config.plugins.Stalker.save()
				self.loadPortals()

	def loadPortals(self):
		self.list = []
		self.name = []
		for x in range(NUMBER_OF_PRESETS):
			self.name.append(ConfigText(default = config.plugins.Stalker.presets[x].portal.value, fixed_size = False))
			if config.plugins.Stalker.preset.value == x:
				self.list.append(getConfigListEntry(">> " + _("Portal URL") + (" %d" % (x + 1)), self.name[x]))
			else:
				self.list.append(getConfigListEntry(_("Portal URL") + (" %d" % (x + 1)), self.name[x]))
		self.list.append(getConfigListEntry(_("Start Stalker with enigma2 (Autostart)"), config.plugins.Stalker.autostart))
		self.list.append(getConfigListEntry(_("Use stalker mac"), config.plugins.Stalker.stalkermac))
		self.list.append(getConfigListEntry(_("New gen portal"), config.plugins.Stalker.portalv2))
		self.list.append(getConfigListEntry(_("Show Stalker in Extensions"), config.plugins.Stalker.showinextensions))
		self.list.append(getConfigListEntry(_("Show Stalker in Mainmenu"), config.plugins.Stalker.showinmenu))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def ok(self):
		if self["config"].getCurrentIndex() < NUMBER_OF_PRESETS:
			self.session.openWithCallback(self.confirmationResult, MessageBox, _("Set this portal as default?"))

	def confirmationResult(self, result):
		if result:
			config.plugins.Stalker.preset.value = self["config"].getCurrentIndex()
			for x in list(range(NUMBER_OF_PRESETS)):
				config.plugins.Stalker.presets[x].portal.value = self.name[x].value
				config.plugins.Stalker.presets[x].save()
			config.plugins.Stalker.save()
			self.loadPortals()

	def save(self):
		for x in range(NUMBER_OF_PRESETS):
			config.plugins.Stalker.presets[x].portal.value = self.name[x].value
			config.plugins.Stalker.presets[x].save()
		config.plugins.Stalker.save()
		self.close()

def setup(session, **kwargs):
	session.open(StalkerEdit)

def autostart(session, **kwargs):
	global g_timerinstance
	global g_session
	g_session = session
	g_timerinstance = eTimer()
	g_timerinstance.callback.append(timerCallback)
	g_timerinstance.start(1000)

def timerCallback():
	global g_timerinstance
	global g_session
	g_timerinstance.stop()
	left = open("/proc/stb/fb/dst_left", "r").read()
	width = open("/proc/stb/fb/dst_width", "r").read()
	top = open("/proc/stb/fb/dst_top", "r").read()
	height = open("/proc/stb/fb/dst_height", "r").read()

	if datetime.datetime.now().year < 2000:
		container = eConsoleAppContainer()
		if config.plugins.Stalker.ntpurl.value == "":
			container.execute("ntpd -p 0.europe.pool.ntp.org -q")
		else:
			container.execute("ntpd -p %s -q" % (config.plugins.Stalker.ntpurl.value))

	g_session.open(StalkerTVWindow, left, top, width, height)

def main(session, **kwargs):
	left = open("/proc/stb/fb/dst_left", "r").read()
	width = open("/proc/stb/fb/dst_width", "r").read()
	top = open("/proc/stb/fb/dst_top", "r").read()
	height = open("/proc/stb/fb/dst_height", "r").read()

	if datetime.datetime.now().year < 2000:
		container = eConsoleAppContainer()
		if config.plugins.Stalker.ntpurl.value == "":
			container.execute("ntpd -p 0.europe.pool.ntp.org -q")
		else:
			container.execute("ntpd -p %s -q" % (config.plugins.Stalker.ntpurl.value))

	session.open(StalkerTVWindow, left, top, width, height)

def startMenu(menuid):
	if menuid != "mainmenu":
		return []
	return [(_("Stalker"), main, "Stalker Plugin", 80)]

def Plugins(**kwargs):
	menus = []
	from enigma import getDesktop
	if getDesktop(0).size().width() <= 1280:
		stalker = "stalker_HD.png"
	else:
		stalker = "stalker_FHD.png"
	menus.append(PluginDescriptor(name=_("Stalker Setup"), description=_("Stalker Setup"), where=PluginDescriptor.WHERE_PLUGINMENU, icon=stalker, fnc=setup))
	if config.plugins.Stalker.showinextensions.value:
		menus.append(PluginDescriptor(name= _("Stalker"), description = _("Stalker"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, icon="", fnc = main))
	if config.plugins.Stalker.showinmenu.value:
		menus.append(PluginDescriptor(name=_("Stalker"), description = _("Stalker"), where = PluginDescriptor.WHERE_MENU, fnc = startMenu))
	if config.plugins.Stalker.autostart.value:
		menus.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart))
	return menus
