from qgis.core import QgsBlockingNetworkRequest, QgsNetworkContentFetcher
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl
from urllib.parse import urlencode

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


def fetch_non_blocking(url, callback, onerror, params={}, contentType="application/json" ):
    """Performs a non-blocking “get” operation on the specified *url* 
    a callback function returns the response
    :param url: the url to fetch 
    :param callback: callback function on succes, returns conteny as string
    :param onerror: callback function on error, returns errormessage as string 
    :param params: a dict 
    :return: the created QgsNetworkContentFetcher
    """
    fetcher = QgsNetworkContentFetcher()
    fetcher.finished.connect(
        lambda: callback(fetcher.contentAsString()) if fetcher.reply().error() !=0 else onerror(fetcher.reply().errorString())
    )
    fullUrl = QUrl( url if len(params) == 0 else url +"?"+ urlencode(params) )
    request = QNetworkRequest( fullUrl )
    request.setRawHeader("Content-Type", contentType)
    fetcher.fetchContent(request)
    return fetcher
