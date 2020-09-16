# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsNetworkAccessManager
import urllib.request 


class settings(object):
    def __init__(self):
        self.s = QSettings()
        self._getProxySettings()

    def _getProxySettings(self):
        self.proxyEnabled = proxyHost = proxyPort = proxyUser = proxyPassword = None
        self.proxy = urllib.request.getproxies()

        self.proxyEnabled = int( self.s.value("geopunt4qgis/proxyOverwiteEnabled", 0) )

        if self.proxyEnabled:
            proxyUrl = self.s.value("geopunt4qgis/proxyUrl", "")
            if proxyUrl:
                proxyHost = proxyUrl.replace("http://", '').replace("https://", '')
                self.proxy = {'http':  'http://'+ proxyHost  ,
                              'https': 'https://'+ proxyHost }
            elif len(self.proxy) > 0:
                self.proxy = proxies
            else:
                qgsNetMan = QgsNetworkAccessManager.instance() 
                proxy = qgsNetMan.proxy().applicationProxy() 
                proxyHost =  proxy.hostName() 
                proxyPort = str( proxy.port()) 
                proxyUser =  proxy.user() 
                proxyPassword =  proxy.password()
                    
                if (proxyHost != '') & (proxyHost is not None) :
                    self.proxy = {'http': 'http://'+ proxyHost + ':' + proxyPort ,
                                  'https': 'https://'+ proxyHost + ':' + proxyPort}         