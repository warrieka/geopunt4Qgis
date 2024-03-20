import urllib.parse, json
from ..tools.web import getUrlData
import xml.etree.ElementTree as ET

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
        capability = url.split("?")[0] + "?request=GetCapabilities&version=2.0.0&service=wfs"
    else: 
        capability = url
        
    response = getUrlData(capability )
    result = ET.fromstring(response)
    version = '1.0.0'
    if 'version' in result.attrib:
        version = result.attrib['version'] 
       
    wfs_ns= {'wfs': 'http://www.opengis.net/wfs/2.0' if version.startswith('2.0.') 
                                                     else 'http://www.opengis.net/wfs' } 
    layers = result.findall( ".//wfs:FeatureType" , wfs_ns)
    layerNames=[]

    for lyr in layers:
        name= lyr.find("wfs:Name", wfs_ns)
        title = lyr.find("wfs:Title", wfs_ns)
        srs = lyr.find("wfs:SRS", wfs_ns)
        if ( name != None) and ( title != None ):
            if srs == None: layerNames.append(( name.text, title.text, 'EPSG:31370'))
            else: layerNames.append(( name.text, title.text, srs.text))

    return (layerNames, version)

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

def get_ogc_api_collections( url):
    resp = getUrlData( url +'/collections', params={'f': 'application/json'} )
    collections = json.loads(resp)
    lyrNames = [(c['id'] , c['title'] , c['description'])
        for c in collections["collections"]
    ]
    return lyrNames

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

def makeWCSuri( url, layer, srsname="EPSG:31370", format="GeoTIFF" ):
    params = {  'cache': 'PreferNetwork',
                'format': format ,
                'identifier': layer,
                'crs': srsname,
                'url': url.split('?')[0]  } #+ '?version%3D1.0.0%26'

    uri = urllib.parse.unquote( urllib.parse.urlencode(params)  )
    return uri

def makeOGCAPIuri( url, name='', srsname="EPSG:31370", version='1.0.0', bbox=None ):
    params = {'TYPENAME': name}
    uri = url.split('?')[0] + '?' + urllib.parse.unquote( urllib.parse.urlencode(params) )
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