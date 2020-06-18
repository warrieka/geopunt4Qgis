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
        self.proxyUrl = None

        self.proxyEnabled = self.s.value("proxy/proxyEnabled", "")
        self.proxy_type = "DefaultProxy"
        proxies = urllib.request.getproxies()
        if len(proxies) == 0:
            qgsNetMan = QgsNetworkAccessManager.instance() 
            self.proxy = qgsNetMan.proxy().applicationProxy() 
            proxyHost =  self.proxy.hostName() 
            proxyPort = str( self.proxy.port()) 
            proxyUser =  self.proxy.user() 
            proxyPassword =  self.proxy.password()
            
            if proxyHost:
                self.proxyUrl = "http://"
                if proxyUser and proxyPassword:
                    self.proxyUrl += proxyUser + ':' + proxyPassword + '@'
                self.proxyUrl += proxyHost + ':' + proxyPort
                self.proxyUrlS = self.proxyUrl.replace("http://", "https://")

        if len(proxies) > 0 and 'http' in list(proxies.keys()):
           self.proxyUrl = proxies['http']
        if len(proxies) > 0 and 'https' in list(proxies.keys()):
           self.proxyUrl = proxies['https']

