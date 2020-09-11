# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtWidgets import QMessageBox 
import urllib.request 


class settings(object):
    def __init__(self):
        self.s = QSettings()
        self._getProxySettings()


    def _getProxySettings(self):
        self.proxyEnabled = proxyHost = proxyPort = proxyUser = proxyPassword = None
        self.proxyUrl = ""
        self.proxyInfo = ""

        self.proxyEnabled = self.s.value("proxy/proxyEnabled", "")
        proxies = urllib.request.getproxies()
            
        qgsNetMan = QgsNetworkAccessManager.instance() 
        self.proxy = qgsNetMan.proxy().applicationProxy() 
        proxyHost =  self.proxy.hostName() 
        proxyPort = str( self.proxy.port()) 
        proxyUser =  self.proxy.user() 
        proxyPassword =  self.proxy.password()
            
        if (proxyHost != '') & (proxyHost is not None) & (len(proxies) == 0):
            self.proxyUrl = "http://"
            if proxyUser and proxyPassword:
                self.proxyUrl += proxyUser + ':' + proxyPassword + '@'
            self.proxyUrl += proxyHost + ':' + proxyPort

        if len(proxies) > 0 and 'http' in list(proxies.keys()):
           self.proxyUrl = proxies['http']
        if len(proxies) > 0 and 'https' in list(proxies.keys()):
           self.proxyUrl = proxies['https']
           
        self.proxyInfo = {"host": proxyHost, "port": proxyPort, 
                          "user": proxyUser, "pass": proxyPassword, "url": self.proxyUrl }
