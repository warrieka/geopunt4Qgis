import urllib2, urllib, json, sys, os.path, datetime
import xml.etree.ElementTree as ET

class metaError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


class MDdata:
    def __init__(self, metadataXML): 
        self.start = metadataXML.attrib["from"]
        self.to = metadataXML.attrib["to"]
        self.count = metadataXML[0].attrib["count"]
        self.records = []
        
        mds = metadataXML.findall("metadata")
        for md in mds:
           record = {}
           record['title'] = md.find('title').text
           record['abstract'] = md.find('abstract').text
           
           if md.find('geoBox') != None: 
             record['bounds'] = [float(i) for i in md.find('geoBox').text.split('|') ]
           else: record['bounds'] = None
           
           record['wms'] = self.findWMS( md )
           if len( record['wms'] ) > 0: record['hasWMS'] = True
           else: record['hasWMS'] = False
           
           geonet =  md.find('{http://www.fao.org/geonetwork}info')
           record['uuid'] = geonet.find('uuid').text
           
           self.records.append(record)
           
    def findWMS(self , node ):
        links =  "|".join( [ n.text for n in node.findall("link") ] ) 
        GetCapabilities=  [n for n in links.split('|') if ("request=GetCapabilities" in n) & ("service=wms" in n)]
        return GetCapabilities


class MDReader:
    def __init__(self, timeout=15, proxyUrl="", port="" ):
        self.timeout = timeout
        self.geoNetworkUrl = "https://metadata.geopunt.be/zoekdienst/srv/dut"

        self.inspireServiceTypes =  ["other","invoke","discovery","transformation","view"]
        self.inspireannex =  ["i","ii","iii"]

        if (proxyUrl <> "")  & proxyUrl.startswith("http://"):
            netLoc = proxyUrl.strip() + ":" + port
            proxy = urllib2.ProxyHandler({'http': netLoc })
            self.opener = urllib2.build_opener(proxy)
        else:
            self.opener = None

    def _createFindUrl(self, q="", c=20, start=1, to=20, themekey='',orgName='',inspiretheme='',inspireannex='', serviceType=''):
        geopuntUrl = self.geoNetworkUrl + "/q?fast=index&"
        data = {}
        data["any"] = "*" + unicode(q).encode('utf-8') + "*"
        data["hitsperpage"] = c
        data["from"] = start
        data["to"] = to

        if themekey: 
            if " " in themekey:
                data["themekey"] = '"' +  themekey.lower()  + '"'
            else: 
                data["themekey"] = themekey.lower()
        if orgName: 
            if " " in orgName:
                data["orgName"] = '"' +  orgName.lower() + '"' 
            else: 
                data["orgName"] = orgName.lower()
        if inspiretheme: 
            if " " in orgName:
                data["inspiretheme"] = '"' +  inspiretheme + '"' 
            else: 
                data["inspiretheme"] = inspiretheme
                
        if inspireannex and (inspireannex.lower() in self.inspireannex ) : 
            data["inspireannex"] = inspireannex.lower()
        if serviceType and (serviceType.lower()in self.inspireServiceTypes): 
            data["serviceType"] = serviceType.lower() 

        values = urllib.urlencode(data)
        result = geopuntUrl + values
        return result

    def list_GDI_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.GDI-Vlaanderen-trefwoorden&pKeyword=*" + unicode(q).encode('utf-8') +"*"
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            r= result.getroot()
            return [ n.find("value").text for n in  r[0].findall('keyword') ]

    def list_keywords(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=any" 
        if q:
            url= url + "&q=" + unicode(q).encode('utf-8') 
        
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = json.load(response)
            return result[1]

    def list_inspire_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.inspire-theme&pKeyword=*" + unicode(q).encode('utf-8') +"*"
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            r= result.getroot()
            return [ n.find("value").text for n in  r[0].findall('keyword') ]
    
    def list_orgnisations(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=orgName" 
        if q:
            url= url + "&q=" + unicode(q).encode('utf-8') 
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = json.load(response)
            return result[1]

    def search(self, q="", c=20, start=1, to=20, themekey='', orgName='', inspiretheme='', inspireannex='', serviceType='' ):
        url = self._createFindUrl( q, c, start, to, themekey, orgName, inspiretheme, inspireannex, serviceType )
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
                raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            resultXML = result.getroot()
            return  MDdata( resultXML )

        
def getWmsLayerNames( capability):
      responseWMS = urllib2.urlopen(capability, timeout=self.timeout)
      result = ET.parse(responseWMS)
      layerNames = [n.text for n in result.findall( ".//{http://www.opengis.net/wms}Layer/{http://www.opengis.net/wms}Name" )]
        