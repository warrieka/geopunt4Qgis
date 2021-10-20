import os, urllib.request
import xml.etree.ElementTree as ET
import configparser as cfg

class versionChecker(object):
    def __init__(self, timeout=3, proxyUrl="" ):
        self.timeout = timeout
        self.url = 'http://plugins.qgis.org/plugins/plugins.xml?qgis=3.0'
        self.ini = os.path.join( os.path.dirname( os.path.dirname(__file__)), "metadata.txt")
        if (isinstance(proxyUrl, str) or isinstance(proxyUrl, str)) & proxyUrl.startswith("http://"):
            proxy = urllib.request.ProxyHandler({'http': proxyUrl })
            auth = urllib.request.HTTPBasicAuthHandler()
            self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
        else:
            self.opener = None
        
    def  getCurrentversion(self ):
         config = cfg.ConfigParser()
         config.read( self.ini )
         return config.get('general','version')
       
    def findLatestVersion(self, experimental=False):
        try:
          if experimental: expTag = 'True'
          else: expTag = 'False'

          if self.opener:
            response= self.opener.open( self.url , timeout=self.timeout)
          else:
            response= urllib.request.urlopen( self.url ,timeout=self.timeout)
          
          pluginsXML = ET.parse(response)
          root = pluginsXML.getroot()
          plugins= root.findall("pyqgis_plugin")
          gp4q= [ n for n in plugins if (n.attrib["name"] == "geopunt4Qgis") and (n.find('experimental').text== expTag)]
          if len( gp4q ) == 0: return '0'
          gp4qVersion = gp4q[0].attrib['version']
          return gp4qVersion
        except:
          return '0'
        
    def isUptoDate(self):
        cur = self.getCurrentversion()
        latest = self.findLatestVersion(False)
        if cur < latest: 
           return False
        else:
           return True
