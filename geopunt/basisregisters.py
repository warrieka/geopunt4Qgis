import json
from ..tools.web import getUrlData


class adresMatch(object):
  def __init__(self):
      self._gemUrl = "https://api.basisregisters.vlaanderen.be/v1/gemeenten/"
      self._amUrl = "https://api.basisregisters.vlaanderen.be/v1/adresmatch"

  def gemeenten(self, langcode="nl", step=500, stop=1500):
      'Return all Flemish gemeenten (Municipalities), langcode= "nl", "fr", "de"' 
      
      gemeenten = []
      data = {'limit' : step , 'offset': 0}
      
      while data['offset'] <= stop:
            result = json.loads( getUrlData(self._gemUrl, params=data ) )
            
            data['offset'] += step

            if len(result["gemeenten"]) == 0:
                break

            gemeenten += [{"Niscode": n['identificator']['objectId'], 
                              "Naam": n['gemeentenaam']['geografischeNaam']['spelling'] } 
                      for n in result["gemeenten"] 
                      if  n['gemeentenaam']['geografischeNaam']['taal'] == langcode
                      and n["gemeenteStatus"].lower() != "gehistoreerd"]

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

      try:
        result = json.loads( getUrlData(self._amUrl, params=data) )
      except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return []

      return [ n for n in result['adresMatches'] if not "adresStatus" in n.keys() or n["adresStatus"].lower() != "gehistoreerd" ]
    
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
      
      try:
        result = json.loads( getUrlData( self._amUrl, params=data ) )
      except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")  
        return []

      return [ n for n in result['adresMatches'] 
                if not "adresStatus" in n.keys() or n["adresStatus"].lower() != "gehistoreerd" ]

    
  def findAdresSuggestions(self, single=None, municipality="", niscode="", postalcode="", 
                kadstreetcode="", rrstreetcode="", streetname="", housenr="", rrindex="", boxnr="" ):
       if single is None:
            matches = self.findMatches(municipality, niscode, postalcode, 
                       kadstreetcode, rrstreetcode, streetname, housenr, rrindex, boxnr)
       else:
            matches = self.findMatchFromSingleLine(single)
       
       results = []          
       for match in matches:
            if ("volledigAdres" in match.keys() and not 'busnummer' in match.keys() 
                and ("adresStatus" not in match.keys() or match["adresStatus"].lower() != "gehistoreerd")):
                results.append( match['volledigAdres']['geografischeNaam']['spelling'] )
       return results
