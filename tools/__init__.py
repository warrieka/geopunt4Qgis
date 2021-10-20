from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl
import urllib.parse

def getUrlData(url, params={}, data=None, returnBytes=False):
    """Performs a blocking “get” operation on the specified *url* and returns the response,
    if *data* is given a "post" is performed. 
    :param url: the url to fetch 
    :param params: a dict 
    :param data: the data to post as bytes 
    :param returnBytes: return bytes instead of string if True
    :return: the response as a string
    """
    bnr = QgsBlockingNetworkRequest()
    
    if len(params) >0:
        url = url +"?"+ urllib.parse.urlencode(params)
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

