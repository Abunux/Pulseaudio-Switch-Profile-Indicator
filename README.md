# Pulseaudio Switch Profile Indicator (PASPI)

A simple tray indicator to quickly change pulseaudio profile
(for example, to switch easily to HDMI when watching a movie).

 Works with more than one sound card.

![alt tag](https://cloud.githubusercontent.com/assets/11058053/6246189/70adf2f4-b766-11e4-8e33-3020d753433c.png)

Dependencies :
--------------
sudo apt-get install python3 libgtk-3-0 python-appindicator

About :
-------
Inspired from : https://github.com/yktoo/indicator-sound-switcher/issues/3
from the script of circuitbreaker303 (for the pulseaudio part), and from http://blog.alex-rudenko.com/2014/08/31/extending-your-ubuntu-desktop-with-custom-indicator-applets-using-python3/ for the indicator part.

By Abunux

abunux at gmail dot com

Licence : WTFPL

Version : 0.1

Started : 2015/02/11

Last update : 2015/02/17

Todo :
------
- Maybe a config window to choose wich profile to display and set the icons
- A nice set of icons
- A way to handle the icon in case of several sound cards
- Update the icon (done but removed) and the radio button in case of external change
