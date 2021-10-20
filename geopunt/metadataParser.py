import urllib.parse
from ..tools import getUrlData
import xml.etree.ElementTree as ET

class MDdata(object):
    def __init__(self, metadataXML):
        self.count = 0 if not metadataXML else int( metadataXML.attrib["numberOfRecordsMatched"] ) 
        self.records = []

        if not metadataXML: return
        
        mds = metadataXML.findall("{http://www.opengis.net/cat/csw/2.0.2}Record")
        for md in mds:
           record = {}
           if md.find("{http://purl.org/dc/elements/1.1/}identifier") == None or not md.find("{http://purl.org/dc/elements/1.1/}identifier").text: 
               continue 
           record['uuid'] = md.find("{http://purl.org/dc/elements/1.1/}identifier").text
           record['title'] = md.find('{http://purl.org/dc/elements/1.1/}title').text

           description = md.find('{http://purl.org/dc/elements/1.1/}description')
           if (description != None):
              record['abstract'] = description.text if description.text != None else ''
           else: record['abstract'] = ''

           bbox = md.find('{http://www.opengis.net/ows}BoundingBox')
           if (bbox != None): 
               LowerCorner = md.find('{http://www.opengis.net/ows}LowerCorner')
               UpperCorner = md.find('{http://www.opengis.net/ows}UpperCorner')
               if LowerCorner and UpperCorner: 
                   record['geoBox'] = [float(n) for n in LowerCorner.text.split(" ")] + [float(n) for n in UpperCorner.text.split(" ")]
               else:
                   record['geoBox'] = [3.1, 50.6, 7.4, 53.6]
           else: 
               record['geoBox'] = [3.1, 50.6, 7.4, 53.6]
           
           record['wms']  = self._findWXS( md, "OGC:WMS" )
           record['wfs']  = self._findWXS( md, "OGC:WFS" )
           record['wcs']  = self._findWXS( md, "OGC:WCS" )
           record['wmts'] = self._findWXS( md, "OGC:WMTS")
           record['download'] = self._findDownloads( md )
           self.records.append(record)
           
    def _findWXS(self , node, protocol= None ):
        links = [n for n in node.findall("{http://purl.org/dc/elements/1.1/}URI") 
                            if "protocol" in n.attrib and n.attrib["protocol"] == protocol] 
        if len(links) == 0: return ("","")

        name = links[0].attrib["name"] if "name" in links[0].attrib else links[0].text
        return (name, links[0].text)

    def _findDownloads(self , node):
        links = [n for n in node.findall("{http://purl.org/dc/elements/1.1/}URI") 
                         if "protocol" in n.attrib and "DOWNLOAD" in n.attrib["protocol"].upper() ] 
        if len(links) == 0: return  ('','')

        name = links[0].attrib["name"] if "name" in links[0].attrib else links[0].text
        return (name, links[0].text)


class MDReader(object):
    def __init__(self ):
        self.geoNetworkUrl = "https://metadata.vlaanderen.be/srv/dut/csw"
        self.dataTypes = [["Dataset", "dataset"],["Dienst","service"],
                  ["ObjectenCatalogus",'featureCatalog'],["Datasetserie",'series']]
        
    def _createFindUrl(self, q="", start=0, maxRecords=100, orgName='', dataType=''): 
        url = self.geoNetworkUrl 
        data = {}
        
        #escape '-sign's in CQL 
        q = q.replace("'", "''")
        orgName = orgName.replace("'", "''")
        
        #make CQL query
        CQLparts = []
        
        if len(q.strip()) > 0: 
            CQLparts.append(" AnyText LIKE '%" + q + "%' ")
        if orgName: 
            CQLparts.append(" OrganisationName = '" + orgName + "' ")
        if dataType: 
            CQLparts.append(" type = '" + dataType + "' ")

        CQL = "(" + " AND ".join(CQLparts) + ")"

        data["request"] = "GetRecords"
        data["service"] = "CSW"
        data["version"] = "2.0.2"
        data["elementsetname"] = "full"
        data["typenames"] = "gmd:MD_Metadata"
        data["RESULTTYPE"] = "results"
        data["constraintLanguage"] = "CQL_TEXT"
        data["constraint_language_version"] = "1.1.0"          
        data["maxRecords"] = maxRecords
        data["startPosition"] = start
        data["constraint"] = CQL
                
        values = urllib.parse.urlencode(data)

        return url +"?"+ values
          
    def list_suggestionKeyword(self):
        url = self.geoNetworkUrl + "?request=GetDomain&service=CSW&version=2.0.2&PropertyName=title"
        response = getUrlData(url )
        result   = ET.fromstring( response )
        val1 = [ n.text for n in result.findall('.//{http://www.opengis.net/cat/csw/2.0.2}Value') ]
        return val1

    def list_organisations(self):
        url = self.geoNetworkUrl + '?request=GetDomain&service=CSW&version=2.0.2&PropertyName=OrganisationName'
        response = getUrlData(url )
        result   = ET.fromstring( response )
        organisations = [ n.text for n in result.findall('.//{http://www.opengis.net/cat/csw/2.0.2}Value') ]
        organisations.sort()
        return organisations

    def search(self, q="", start=0, step=100, orgName='', dataType=''):
        url = self._createFindUrl( q, start, step, orgName, dataType)
        response = getUrlData(url )
        result   = ET.fromstring( response )
        return result

    def searchAll(self, q="", orgName='', dataType=''):
        start= 1
        step = 100
        result = self.search(q, start, step, orgName, dataType)
        searchResult = result.find(".//{http://www.opengis.net/cat/csw/2.0.2}SearchResults")
        if not searchResult: 
            return
        count = int( searchResult.attrib["numberOfRecordsMatched"] )
        start += step
        while (start) <= count: 
           result = self.search(q, start, step, orgName, dataType)
           mds= result.findall(".//{http://www.opengis.net/cat/csw/2.0.2}Record")
           for md in mds: 
               searchResult.append( md )
           start += step
           
        return searchResult


class metaError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

      
def getWmsLayerNames( url=''):
    if (not "request=GetCapabilities" in url.lower()) or (not "service=wms" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.3.0&service=wms"
    else:
      capability = url
        
    response = getUrlData(capability )
    result = ET.fromstring(response)
    layers =  result.findall( ".//{http://www.opengis.net/wms}Layer" ) + result.findall( ".//Layer" ) 
    layerNames=[]

    for lyr in layers:
      name= lyr.find("{http://www.opengis.net/wms}Name")
      if name is None: name= lyr.find("Name")
      title = lyr.find("{http://www.opengis.net/wms}Title")
      if title is None: title = lyr.find("Title")
      style = lyr.find("{http://www.opengis.net/wms}Style/{http://www.opengis.net/wms}Name")
      if ( name != None) and ( title != None ):
         if style == None: layerNames.append(( name.text, title.text, ''))
         else: layerNames.append(( name.text, title.text, style.text))

    return layerNames

def getWFSLayerNames( url):
    if (not "request=GetCapabilities" in url.lower()) or (not "service=wfs" in url.lower()):
        capability = url.split("?")[0] + "?request=GetCapabilities&version=1.0.0&service=wfs"
    else: 
        capability = url
        
    response = getUrlData(capability )
    result = ET.fromstring(response)
    layers =  result.findall( ".//{http://www.opengis.net/wfs}FeatureType" )
    layerNames=[]

    for lyr in layers:
        name= lyr.find("{http://www.opengis.net/wfs}Name")
        title = lyr.find("{http://www.opengis.net/wfs}Title")
        srs = lyr.find("{http://www.opengis.net/wfs}SRS")
        if ( name != None) and ( title != None ):
            if srs == None: layerNames.append(( name.text, title.text, 'EPSG:31370'))
            else: layerNames.append(( name.text, title.text, srs.text))

    return layerNames

def getWMTSlayersNames( url):
    if (not "request=getcapabilities" in url.lower()) or (not "service=wmts" in url.lower()):
        capability = url.split("?")[0] + "?service=WMTS&request=Getcapabilities"
    else:
        capability = url
            
    response = getUrlData(capability )
    result = ET.fromstring(response)

    content = result.find( "{http://www.opengis.net/wmts/1.0}Contents" )
    layers =  content.findall( "{http://www.opengis.net/wmts/1.0}Layer" )
    layerNames = []

    matrixSets = content.findall("{http://www.opengis.net/wmts/1.0}TileMatrixSet")

    for lyr in layers:
        name= lyr.find("{http://www.opengis.net/ows/1.1}Identifier")
        title = lyr.find("{http://www.opengis.net/ows/1.1}Title")
        matrix = lyr.find("{http://www.opengis.net/wmts/1.0}TileMatrixSetLink/{http://www.opengis.net/wmts/1.0}TileMatrixSet")
        format = lyr.find("{http://www.opengis.net/wmts/1.0}Format")

        srsList = [ n.find("{http://www.opengis.net/ows/1.1}SupportedCRS").text
                    for n in matrixSets if n.find("{http://www.opengis.net/ows/1.1}Identifier").text == matrix.text]

        if srsList: srs =  "EPSG:"+ srsList[0].split(':')[-1]
        else: srs = ""

        if ( name != None) and ( title != None ) and ( matrix != None ) and ( format != None ):
              layerNames.append(( name.text, title.text, matrix.text, format.text, srs ))

    return layerNames

def getWCSlayerNames( url):
    wcsNS = "http://www.opengis.net/wcs/1.1"

    if (not "request=getcapabilities" in url.lower()) or (not "service=wcs" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.1.0&service=wcs"
    else:
      capability = url

    response = getUrlData(capability )

    if 'xmlns:wcs="http://www.opengis.net/wcs/1.1.1"' in response:
        wcsNS = "http://www.opengis.net/wcs/1.1.1"

    result = ET.fromstring(response)
    content = result.find( "{%s}Contents" % wcsNS)
    layers =  content.findall( "{%s}CoverageSummary" % wcsNS)
    layerNames = []

    for lyr in layers:
       Identifier= lyr.find("{%s}Identifier" % wcsNS)
       title = lyr.find("{http://www.opengis.net/ows/1.1}Title")

       DescribeCoverage = url.split("?")[0] + "?request=DescribeCoverage&version=1.1.0&service=wcs&Identifiers=" + Identifier.text
       response = getUrlData(DescribeCoverage)
       resultDC = ET.fromstring(response)
       CoverageDescription = resultDC.find( "{%s}CoverageDescription" % wcsNS)
       Identifier = CoverageDescription.find("{%s}Identifier" % wcsNS)
       formats =  CoverageDescription.findall( "{%s}SupportedFormat" % wcsNS)
       if [n.text for n in formats if 'tiff' in n.text.lower()] :
          format = [n.text for n in formats if 'tiff' in n.text.lower()][0]
       elif formats: format = formats[0].text.split(";")[0]
       else: format = "image/tiff"

       if ( Identifier != None) and (title != None):
            layerNames.append(( Identifier.text, title.text, format ))

    return layerNames

def makeWFSuri( url, name='', srsname="EPSG:31370", version='1.0.0', bbox=None ):
    params = {  'SERVICE': 'WFS',
                'VERSION': version ,
                'REQUEST': 'GetFeature',
                'TYPENAME': name,
                'SRSNAME': srsname }
    if bbox: params['BBOX'] = ",".join([str(s) for s in bbox])

    uri = url.split('?')[0] + '?' + urllib.parse.unquote( urllib.parse.urlencode(params) )

    return uri

def makeWMTSuri( url, layer, tileMatrixSet, srsname="EPSG:3857", styles='', format='image/png' ):
    params = {  'tileMatrixSet': tileMatrixSet,
                'styles': styles,
                'format': format ,
                'layers': layer,
                'crs': srsname,
                'url': url.split('?')[0]  + '?service=WMTS'}

    uri = urllib.parse.unquote( urllib.parse.urlencode(params)  )
    return uri

def makeWCSuri( url, layer,srsname="EPSG:31370", format="GeoTIFF" ):
    """ cache=PreferNetwork
        crs=EPSG:28992
        format=GeoTIFF
        identifier=dank:altr_a04_gi_bodemC
        url=http://geodata.rivm.nl/geoserver/wcs?version%3D1.0.0%26"""
    params = {  'cache': 'PreferNetwork',
                'format': format ,
                'identifier': layer,
                'crs': srsname,
                'url': url.split('?')[0]  } #+ '?version%3D1.0.0%26'

    uri = urllib.parse.unquote( urllib.parse.urlencode(params)  )
    return uri

def xmlIsEmpty(xml_file, gmlException=True):
    """test if a xml file contais data
    
    :param xml_file: a path to a xml file. 
    :param gmlException: also return if gmlException
    
    return: True if empty else False
    """
    try:
        tree = ET.parse(xml_file)  
        root = tree.getroot()
        if gmlException and "ExceptionReport" in root.tag:
            return True
        
        return not len(root)
    except:
        return True