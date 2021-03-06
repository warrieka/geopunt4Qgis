#\***************************************************************************
# geopunt4Qgis
# 
# 'Makefile for geopunt4Qgis, a QGIS plugin'
#                             -------------------
#        begin                : 2013-12-05
#        copyright            : (C) 2013 by Kay Warrie
#        email                : kaywarrie@gmail.com
# ***************************************************************************\
# 
#\***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and\or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************\

# CONFIGURATION
PROFILE=E:\work\devProfile

# translation
SOURCES = geopunt4qgis.py \
		  geopunt4QgisPoidialog.py \
		  geopunt4QgisAdresdialog.py \
		  geopunt4QgisAbout.py \
		  geopunt4QgisSettingsdialog.py \
		  geopunt4QgisBatchGeoCode.py \
		  geopunt4QgisGipod.py \
		  geopunt4QgisElevation.py \
		  geopunt4QgisDataCatalog.py \
		  geopunt4QgisParcel.py   \
		  tools/versionChecker.py

FORMS   = ui_geopunt4qgis.ui \
		  ui_geopunt4QgisPoi.ui \
		  ui_geopunt4QgisAbout.ui \
		  ui_geopunt4QgisSettings.ui  \
		  ui_geopunt4QgisBatchGeoCode.ui \
		  ui_geopunt4QgisGIPOD.ui \
		  ui_geopunt4QgisElevation.ui \
		  ui_geopunt4QgisDataCatalog.ui \
		  ui_geopunt4QgisParcel.ui

TRANSLATIONS = i18n\geopunt4qgis_en.ts i18n\geopunt4qgis_nl.ts

PLUGINNAME = geopunt4Qgis

PY_FILES = __init__.py tools geopunt mapTools \
		  geopunt4qgis.py \
		  geopunt4QgisAbout.py \
		  geopunt4QgisAdresdialog.py \
		  geopunt4QgisPoidialog.py \
		  geopunt4QgisSettingsdialog.py \
		  geopunt4QgisBatchGeoCode.py  \
		  geopunt4QgisGipod.py \
		  geopunt4QgisParcel.py \
		  geopunt4QgisElevation.py \
		  geopunt4QgisDataCatalog.py 

EXTRAS = images metadata.txt i18n data

UI_FILES = ui_geopunt4qgis.py ui_geopunt4QgisPoi.py ui_geopunt4QgisAbout.py \
ui_geopunt4QgisSettings.py ui_geopunt4QgisBatchGeoCode.py ui_geopunt4QgisGIPOD.py \
ui_geopunt4QgisElevation.py ui_geopunt4QgisDataCatalog.py ui_geopunt4QgisParcel.py

RESOURCE_FILES = resources_rc.py

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES) 

%_rc.py : %.qrc
	pyrcc5 -o  $*_rc.py  $<

%.py : %.ui
	pyuic5 --import-from=. -o $@ $<

# [KW]: extra command with my own python script, that I can also use on windows
# workflow testPlugin.py: pack -> extract at PROFILE -> start QGIS
runplugin: compile  
	python $(CURDIR)\script\testPlugin.py
	
run: deploy
	qgis --profiles-path $(PROFILE)

# The deploy  target only works on unix like operating system where
# [KW]: use "make runplugin" instead on windows
deploy: derase compile
	mkdir $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)
	cp -vfr $(PY_FILES) $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)
	cp -vf $(UI_FILES) $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)
	cp -vfr $(EXTRAS) $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)
	cp -vfr i18n $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME) -iname "*.pyc" -delete
	find $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -rf $(PROFILE)\profiles\default\python\plugins\$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http:\\plugins.qgis.org
# [KW]: replaced by my own python script, that I can use on windows
zip:
	python $(CURDIR)\script\packPlugin4upload.py


# Create a zip package of the plugin named $(PLUGINNAME).zip. 
# This requires use of git (your plugin development directory must be a 
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=v0.3
package: clean transclean dclean
	rm -f build\$(PLUGINNAME)-$(VERSION).zip
	git archive --prefix=$(PLUGINNAME)\ -o build\$(PLUGINNAME)-$(VERSION).zip $(VERSION)
	echo "Created package: $(PLUGINNAME)-$(VERSION).zip"

# transup
# update .ts translation files, compile to .qm and .mk to .html
# [KW]: added custom compile_translations for html
transup: 
	pylupdate5 Makefile
	lrelease i18n/*.ts
	script/compile_html_translations.sh

# transclean
# deletes all .qm (form .ts) and html (from .mk) files
transclean:
	rm -f i18n/*.qm
	rm -f i18n/*.html

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

