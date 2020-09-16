# -*- coding: utf-8 -*-
import json, sys, urllib.parse
from urllib.request import getproxies
import requests

class adresMatch(object):
  _gemUrl = "https://basisregisters.vlaanderen.be/api/v1/gemeenten/"
  _amUrl = "https://basisregisters.vlaanderen.be/api/v1/adresmatch"
  def __init__(self, timeout=15, proxies=None):
      self.timeout = timeout
      self.proxy = proxies if proxies else getproxies()

  def gemeenten(self, langcode="nl"):
      'Return all Flemish gemeenten (Municipalities), ylangcode= "nl", "fr", "de"' 
      data = urllib.parse.urlencode( {'Limit' : '2000' } )
      result = requests.get(self._gemUrl, params=data, timeout=self.timeout, 
                                          verify=False, proxies=self.proxy ).json()

      gemeenten = [{"Niscode": n['identificator']['objectId'], "Naam": n['gemeentenaam']['geografischeNaam']['spelling'] } 
                      for n in result["gemeenten"] 
                      if  n['gemeentenaam']['geografischeNaam']['taal'] == langcode
                      and n["gemeenteStatus"] ==  "inGebruik"]

      return sorted(gemeenten, key=lambda k: k['Naam']) 

  def findMatches(self, municipality="", niscode="", postalcode="", kadstreetcode="", 
                    rrstreetcode="", streetname="", housenr="", rrindex="", boxnr=""):
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
      
      result = requests.get(self._amUrl, params=data, timeout=self.timeout , 
                                        verify=False , proxies=self.proxy ).json()
      return result['adresMatches']
    
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
      
      result = requests.get(self._amUrl, params=data, timeout=self.timeout , 
                                            verify=False  , proxies=self.proxy ).json()
      return result['adresMatches']

    
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
