from qgis.core import QgsBlockingNetworkRequest, QgsNetworkContentFetcher
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl
from urllib.parse import urlencode
from typing import Callable

def getUrlData(url:str, params:dict={}, data:bytes=None, returnBytes=False, headers:dict={}) -> str:
    """Performs a blocking “get” operation on the specified *url* and returns the response,
    if *data* is given a "post" is performed. 
    :param url: the url to fetch 
    :param params: a dict 
    :param data: the data to post as bytes 
    :param returnBytes: return bytes instead of string if True
    :return: the response as a string
    """
    if params and len(params) >0:
        url = url +"?"+ urlencode(params)

    bnr = QgsBlockingNetworkRequest()
    request = QNetworkRequest( QUrl(url) )

    for k,v in headers.items():
        request.setRawHeader( k.encode(), v.encode())
    
    if not data:
        respcode = bnr.get( request )
    else:
        respcode = bnr.post( request , data )

    if respcode == 0: 
        response = bnr.reply().content().data() 
        if returnBytes == False: 
            response = response.decode('utf-8') 
    else: 
        raise Exception( bnr.reply().errorString() )
    return response


def fetch_non_blocking(url:str, callback:Callable, onerror:Callable, params:dict={}, 
                       contentType:str="application/json", headers:dict={}) -> QgsNetworkContentFetcher:
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
        lambda: callback(fetcher.contentAsString()) if fetcher.reply().error() !=0 
                                                    else onerror(fetcher.reply().errorString())
    )
    fullUrl = QUrl( url if len(params) == 0 else url +"?"+ urlencode(params) )
    request = QNetworkRequest( fullUrl )
    
    for k,v in headers.items():
        request.setRawHeader( k.encode(), v.encode())

    request.setHeader( QNetworkRequest.ContentTypeHeader , contentType)
    fetcher.fetchContent(request)
    return fetcher
