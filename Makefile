# CONFIGURATION
PROFILENAME=devProfile
QGISBIN=C:\OSGeo4W\bin\qgis-ltr-bin.exe
PROFILEPATH=$(APPDATA)\QGIS\QGIS3
PROFILE=$(PROFILEPATH)\profiles\${PROFILENAME}

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

run: deploy
	$(QGISBIN) --profiles-path $(PROFILEPATH) --profile $(PROFILENAME)

# The deploy  target only works on unix like operating system where
# [KW]: use "make runplugin" instead on windows
deploy: derase compile
	mkdir   $(PROFILE)\python\plugins\$(PLUGINNAME)
	cp -vfr $(PY_FILES) $(PROFILE)\python\plugins\$(PLUGINNAME)
	cp -vf  $(UI_FILES) $(PROFILE)\python\plugins\$(PLUGINNAME)
	cp -vf  $(RESOURCE_FILES) $(PROFILE)\python\plugins\$(PLUGINNAME)
	cp -vfr $(EXTRAS) $(PROFILE)\python\plugins\$(PLUGINNAME)
	cp -vfr i18n $(PROFILE)\python\plugins\$(PLUGINNAME)

# The derase deletes deployed plugin
derase:
	rm -rf $(PROFILE)\python\plugins\$(PLUGINNAME)

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

