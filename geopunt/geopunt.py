import urllib2, urllib, json

class geopunt:
  def __init__(self):
    self.locUrl = "http://loc.api.geopunt.be/geolocation/Location?"
    self.sugUrl = "http://loc.api.geopunt.be/geolocation/Suggestion?"

  def _createLocationUrl(self, q, c=1):
      geopuntUrl = self.locUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result


  def fetchLocation(self, q, c=1):
      url = self._createLocationUrl(q, c=1)
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      LocationResult = json.load(response)["LocationResult"]
      result = []
      for Loc in LocationResult:
	  adres = Loc["FormattedAddress"]
	  locType = Loc["LocationType"]
	  x, y = Loc["Location"]["X_Lambert72"], Loc["Location"]["Y_Lambert72"]
	  #bbx = Loc['BoundingBox']
	  #Lower = bbx['LowerLeft']['X_Lambert72']
	  #Left = bbx['LowerLeft']['Y_Lambert72']
	  #Upper = bbx['UpperRight']['X_Lambert72']
	  #Right = bbx['UpperRight']['Y_Lambert72']
	  result.append(  {'x':x, 'y':y, 'adres': adres,'type': locType} )
      return result
      
	
  def _createSuggestionUrl(self, q, c=5):
      geopuntUrl = self.sugUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result


  def fetchSuggestion(self, q, c=5):
      url = self._createSuggestionUrl(q,c)
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      suggestion = json.load(response)
      return suggestion["SuggestionResult"]

