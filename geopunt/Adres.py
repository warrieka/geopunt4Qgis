import json
from urllib.parse import urlencode
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl

class Adres(object):
  def __init__(self):
      self.locUrl = "https://loc.geopunt.be/v4/Location"
      self.sugUrl = "https://loc.geopunt.be/v4/Suggestion"
      
  def fetchLocation(self, q: str, c=1):
      LocationResult = json.loads( fetch_blocking(self.locUrl, params={"q": q, "c": c} ) )
      return LocationResult["LocationResult"]

  def fetchSuggestion(self, q: str, c=5):
      suggestion =  json.loads( fetch_blocking(self.sugUrl, params={"q": q, "c": c} ) )
      return suggestion["SuggestionResult"]


def fetch_blocking(url, params={}, data=None, returnBytes=False):
    bnr = QgsBlockingNetworkRequest()
    if len(params) >0:
        url = url +"?"+ urlencode(params)
    if not data:
        respcode = bnr.get(QNetworkRequest( QUrl(url) ) )
    else:
        respcode = bnr.post(QNetworkRequest( QUrl(url) ) , data )
    if respcode == 0: 
        response = bnr.reply().content().data() 
        if returnBytes == False: 
            response = response.decode('utf-8') 
    else: 
        raise Exception( bnr.reply().errorString() )
    return response