# -*- coding: utf-8 -*-
from PyQt4.QtCore import QSettings
import urllib

try:
   from qgis.core import QgsNetworkAccessManager
   hasNetworkManager = True
except ImportError:
   hasNetworkManager = False
import sys, os

class settings:
    def __init__(self):
        self.s = QSettings()
        self._getProxySettings()

    def _getProxySettings(self):
        self.proxyEnabled = self.proxyHost = self.proxyPort = self.proxyUser = self.proxyPassword = None
        self.proxyUrl = ""
        proxyEnabled = self.s.value("proxy/proxyEnabled", "")
        if proxyEnabled == 1 or proxyEnabled == "true":
            self.proxyEnabled = True
            self.proxy_type = self.s.value("proxy/proxyType", "")
            self.proxyHost = self.s.value("proxy/proxyHost", "" )
            self.proxyPort = self.s.value("proxy/proxyPort", "" )
            self.proxyUser = self.s.value("proxy/proxyUser", "" )
            self.proxyPassword = self.s.value("proxy/proxyPassword", "" )

            #https://github.com/nextgis/quickmapservices/blob/master/src/qgis_settings.py#L74L80
            if self.proxy_type == "DefaultProxy": 
               proxies = urllib.getproxies()
               if hasNetworkManager and len(proxies) == 0:
                  qgsNetMan = QgsNetworkAccessManager.instance() 
                  proxy = qgsNetMan.proxy().applicationProxy() 
                  self.proxyHost = proxy.hostName() 
                  self.proxyPort = str(proxy.port()) 
                  self.proxyUser = proxy.user() 
                  self.proxyPassword = proxy.password() 

               elif len(proxies) > 0 and 'http' in proxies.keys():
                  self.proxyUrl = proxies['http']
                  self.proxyUrlS = proxies['https']

            else:
               self.proxyUrl = "http://"
               if self.proxyUser and self.proxyPassword:
                   self.proxyUrl += self.proxyUser + ':' + self.proxyPassword + '@'
               self.proxyUrl += self.proxyHost + ':' + self.proxyPort
               self.proxyUrlS = self.proxyUrl.replace("http://", "https://")
