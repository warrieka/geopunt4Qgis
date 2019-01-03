# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse, json, sys
from .geopuntError import geopuntError

class adresMatch(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self._gemUrl = "https://basisregisters.vlaanderen.be/api/v1/gemeenten/"
      self._amUrl = "https://basisregisters.vlaanderen.be/api/v1/adresmatch?"
      if isinstance(proxyUrl, str)  and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)


  def gemeenten(self, niscode=""):
      "Return all Flemish gemeenten (Municipalities)" 
      data = urllib.parse.urlencode( {'Limit' : '2000' } )
      if not niscode:  url = self._gemUrl +"?"+ data
      else: url = self._gemUrl + str(niscode)
      response = self.opener.open(url,  timeout=self.timeout)
      result = json.load(response)
      gemeenten = [{"Niscode": n['identificator']['objectId'], "Naam": n['gemeentenaam']['geografischeNaam']['spelling'] } 
                                for n in result["gemeenten"]]
      return gemeenten

  def findMatches(self, municipality="", niscode="", postalcode="", kadstreetcode="", rrstreetcode="", streetname="", housenr="", rrindex="", boxnr=""):
      data = {}
      data["Gemeentenaam"] = municipality if municipality else ""
      data["Niscode"]      = niscode if niscode else ""
      data["Postcode"]     = postalcode if postalcode else ""
      data["KadStraatcode"]= kadstreetcode if kadstreetcode else ""
      data["RrStraatcode"] = rrstreetcode if rrstreetcode else ""
      data["Straatnaam"]   = streetname if streetname else ""
      data["Huisnummer"]   = housenr if housenr else ""
      data["Index"]        = rrindex if rrindex else ""
      data["Busnummer"]    = boxnr if boxnr else ""
      values = urllib.parse.urlencode(data)
      
      response = self.opener.open(self._amUrl + values, timeout=self.timeout)
      return json.load(response)['adresMatches']
    
  def findMatchFromSingleLine(self, adres):
      adr = [n.strip() for n in adres.split(",")]
      if len(adr) != 2: return []
      if len(adr[0].split() ) < 2: return []
      
      street = " ".join(adr[0].split()[:-1])
      housenr = adr[0].split()[-1]

      if len(adr[1].split()) ==2:
            post = adr[1].split()[0]
            muni = " ".join(adr[1].split()[1:])
      else:
            post = ""
            muni = adr[1]

      data = {}
      data["Gemeentenaam"] = muni
      data["Postcode"]     = post
      data["Straatnaam"]   = street
      data["Huisnummer"]   = housenr
      values = urllib.parse.urlencode(data)
      url = self._amUrl + values
      
      try:
         response = self.opener.open( url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ) )
      except:
         raise geopuntError( sys.exc_info()[1] )
      else:
         return json.load(response)['adresMatches']

    
  def findAdresSuggestions(self, single=None, municipality="", niscode="", postalcode="", kadstreetcode="", rrstreetcode="", streetname="", housenr="", rrindex="", boxnr="" ):
       if single is None:
            matches = self.findMatches(municipality, niscode, postalcode, kadstreetcode, rrstreetcode, streetname, housenr, rrindex, boxnr)
       else:
            matches = self.findMatchFromSingleLine(single)
       
       results = []          
       for match in matches:
            if "volledigAdres" in match.keys() and not 'busnummer' in match.keys():
                results.append( match['volledigAdres']['geografischeNaam']['spelling'] )
       return results
