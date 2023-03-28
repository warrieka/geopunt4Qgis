import json
from urllib.parse import urlencode
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl
from ..tools.web import fetch_non_blocking, getUrlData

class Adres(object):
  def __init__(self):
      self.locUrl = "https://geo.api.vlaanderen.be/geolocation/v4/Location"
      self.sugUrl = "https://geo.api.vlaanderen.be/geolocation/v4/Suggestion"
      
  def fetchLocation(self, q: str, c=1):
      LocationResult = json.loads( getUrlData(self.locUrl, params={"q": q, "c": c} ) )
      return LocationResult["LocationResult"]

  def fetchSuggestion(self, q: str, c=5):
      suggestion =  json.loads( getUrlData(self.sugUrl, params={"q": q, "c": c} ) )
      return suggestion["SuggestionResult"]


# def fetch_blocking(url, params={}, data=None, returnBytes=False):
#     bnr = QgsBlockingNetworkRequest()
#     if len(params) >0:
#         url = url +"?"+ urlencode(params)
#     if not data:
#         respcode = bnr.get(QNetworkRequest( QUrl(url) ) )
#     else:
#         respcode = bnr.post(QNetworkRequest( QUrl(url) ) , data )
#     if respcode == 0: 
#         response = bnr.reply().content().data() 
#         if returnBytes == False: 
#             response = response.decode('utf-8') 
#     else: 
#         raise Exception( bnr.reply().errorString() )
#     return response