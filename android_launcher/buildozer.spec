[app]
title = UKMLA Station
package.name = ukmla_station
package.domain = org.dr.ikrma
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 0.1
requirements = python3,kivy,speechrecognition,pygame,gtts
orientation = portrait
fullscreen = 1
android.permissions = RECORD_AUDIO,INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
