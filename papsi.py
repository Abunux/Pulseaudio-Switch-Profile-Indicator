#!/usr/bin/env python3

# ---------------------------------------------------------------------
#     Pulse Audio Switch Profile Indicator (PASPI) - Extended version
# ---------------------------------------------------------------------
#
# A simple tray indicator to quickly change pulseaudio profile
# (for example, to switch easily on the HDMI when watching a movie)
#
# Works with more than one sound card
#
#
# Dependencies :
# --------------
# sudo apt-get install python3 libgtk-3-0 python-appindicator
#
# About :
# -------
# Inspired from : https://github.com/yktoo/indicator-sound-switcher/issues/3
# from the script of circuitbreaker303
#
# By Abunux
# abunux at gmail dot com
# Licence : Do whatever you want with this code
# Version : 0.1
# Started : 2015/02/11
# Last update : 2015/02/17
#
# Todo :
# ------
# - Maybe a config window to choose wich profile to display and set the icons
# - A nice set of icons
# - A way to handle the icon in case of several sound cards
# - Update the icon (done but removed) and the radio button in case of external change

import os, re
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib

# Pulseaudio part
# ---------------
# Parse the 'pacmd list-card' command to get all infos about the devices

class Profile:
	def __init__(self,infos):
		self.infos = infos
		self.get_profile()
		self.get_name()
		self.get_icons()

	def get_profile(self):
		r='(.*): (.*) \('
		m = re.search(r,self.infos)
		if m : 
			self.profile = m.group(1)

	def get_name(self):
		r = '(.*): (.*) \('
		m = re.search(r,self.infos)
		if m : 
			self.name = m.group(2)

	def set_icon(self, image):
		self.icon = image

	def get_icons(self):
		# You can change your icons here
		if "output:analog" in self.profile :
			self.set_icon('/usr/share/icons/gnome/scalable/devices/audio-speakers-symbolic.svg')
		elif "output:hdmi" in self.profile :
			self.set_icon('/usr/share/icons/gnome/scalable/devices/video-display-symbolic.svg')
		elif "off" in self.profile:
			self.set_icon('/usr/share/icons/gnome/scalable/actions/action-unavailable-symbolic.svg')
		else:
			self.set_icon('/usr/share/icons/gnome/scalable/devices/audio-speakers-symbolic.svg')

class SoundCard:
	def __init__(self,infos):
		self.infos = infos
		self.get_index()
		self.get_name()
		self.get_alsa_name()
		self.get_profiles()
		self.get_active()

	def get_index(self):
		for l in self.infos :
			if "index" in l :
				self.index = re.search(r'index: (\d)', l).group(1)
				break

	def get_name(self):
		for l in self.infos :
			if "name:" in l :
				self.name = re.search(r'name: \<(.*?)\>', l).group(1)
				break

	def get_alsa_name(self):
		for l in self.infos :
			if "alsa.card_name" in l :
				self.alsa_name = re.search(r'alsa.card_name = "(.*?)"', l).group(1)
				break

	def get_profiles(self):
		k=0
		while "profiles" not in self.infos[k]:
			k+=1
		istart = k+1
		while "active profile" not in self.infos[k]:
			k+=1
		iend = k
		self.profiles = []
		for l in self.infos[istart:iend] :
			self.profiles.append(Profile(l))

	def get_active(self):
		self.active = os.popen(r'pacmd list-cards|grep active\ profile|cut -d\  -f3-').readline()[1:-2]
		return self.active

	def set_profile(self, profile):
		for p in self.profiles :
			if profile == p.profile :
				os.system("pactl set-card-profile %s %s"%(self.name, profile))
				return 1
		print("Error : Profile %s not reconized"%(profile))
		return 0

class PA:
	def __init__(self):
		self.infos = []
		out = os.popen(r'pacmd list-cards').readlines()
		for l in out:
			self.infos.append(l.replace("\t",""))
		self.cards = []
		self.parse_infos()

	def parse_infos(self):
		list_index = []
		self.nbcards = 0
		for k in range(len(self.infos)):
			if "index" in self.infos[k]:
				list_index.append(k)
				self.nbcards+=1
		list_index.append(len(self.infos)-1)

		for k in range(self.nbcards):
			self.cards.append(SoundCard(self.infos[list_index[k]:list_index[k+1]]))

pa = PA()
card = pa.cards[0] # Default card is the 1st one


# Indicator part
# --------------
# The systray indicator

class Indicator:
	def __init__(self):
		active = card.get_active()
		for p in card.profiles:
			if p.profile == active :
				icon = p.icon
				break
		self.ind = appindicator.Indicator.new("Sound Switcher",icon,appindicator.IndicatorCategory.HARDWARE)
		self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
		self.menu = Gtk.Menu()

		if pa.nbcards == 1 :
			group = []
			for p in card.profiles:
				item = Gtk.RadioMenuItem.new_with_label(group, p.name)
				group = item.get_group()
				if card.get_active() == p.profile :
					item.set_active(True)
				item.set_tooltip_text(p.profile)
				item.connect("activate", self.change_mode,card,p)
				self.menu.append(item)

		else : # If more than one sound card, make a submenu
			for c in pa.cards:
				cardm = Gtk.Menu()
				group = []
				for p in c.profiles :
					itemp = Gtk.RadioMenuItem.new_with_label(group, p.name)
					group = itemp.get_group()
					if c.get_active() == p.profile :
						itemp.set_active(True)
					itemp.connect("activate", self.change_mode,c,p)
					cardm.append(itemp)
				item = Gtk.MenuItem(c.alsa_name)
				item.set_submenu(cardm)
				self.menu.append(item)

		item = Gtk.SeparatorMenuItem()
		self.menu.append(item)

		item = Gtk.MenuItem()
		item.set_label("Exit")
		item.connect("activate", self.quit)
		self.menu.append(item)

		self.menu.show_all()
		self.ind.set_menu(self.menu)

	def main(self):
		#~ GLib.timeout_add_seconds(1, self.check_update)
		Gtk.main()

	def change_mode(self, widget, c, p):
		if widget.get_active():
			c.set_profile(p.profile)
			self.ind.set_icon(p.icon)
			print(card.get_active())
			os.system('notify-send -i '+p.icon+ '"" "' +p.name+' activated"')

	#~ def check_update(self):
		#~ active=card.get_active()
		#~ for p in card.profiles :
			#~ if p.profile==active :
				#~ self.ind.set_icon(p.icon)
				#~ break
		#~ return True

	def quit(self, widget):
		Gtk.main_quit()

if __name__ == '__main__':
	indicator = Indicator();
	indicator.main();
