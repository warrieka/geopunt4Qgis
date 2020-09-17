# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsNetworkAccessManager
import urllib.request 


class settings(object):
    def __init__(self):
        self.s = QSettings()
        self.proxy = urllib.request.getproxies() #default system proxy
        self.proxyEnabled = int( self.s.value("geopunt4qgis/proxyOverwiteEnabled", 0) )

        if self.proxyEnabled:
            proxyUrl = self.s.value("geopunt4qgis/proxyUrl", "")
            if proxyUrl:
                proxyHost = proxyUrl.replace("http://", '').replace("https://", '')
                self.proxy = {'http':  'http://'+ proxyHost  ,
                              'https': 'https://'+ proxyHost }
        else:
            #check if a proxy is confiugured in qgis
            qgsNetMan = QgsNetworkAccessManager.instance() 
            proxy = qgsNetMan.proxy().applicationProxy() 
            proxyHost =  proxy.hostName() 
            proxyPort = str( proxy.port()) 
                
            if (proxyHost != '') & (proxyHost is not None) :
                self.proxy = {'http': 'http://{}:{}'.format( proxyHost, proxyPort if proxyPort else '') ,
                              'https': 'https://{}:{}'.format( proxyHost , proxyPort if proxyPort else '')}         