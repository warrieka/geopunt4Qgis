# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt
                                
"bibliotheek om geopunt in python te gebruiken"
                            -------------------
        begin                : 2013-12-05
        copyright            : (C) 2013 by Kay Warrie
        email                : kaywarrie@gmail.com
***************************************************************************/

/***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************/
"""
import urllib.request
from .Adres import Adres
from .basisregisters import adresMatch
from .capakey import capakey
from .elevation import elevation
from .gipod import gipod
from .perc import perc
from .Poi import Poi

def internet_on( proxyUrl="", timeout=15, testSite='http://loc.api.geopunt.be/v2/Suggestion' ):
    opener = None
    if isinstance(proxyUrl, str) and proxyUrl != "":
        if proxyUrl.startswith("https"): proxy = urllib.request.ProxyHandler({'https': proxyUrl})
        else: proxy = urllib.request.ProxyHandler({'http': proxyUrl})
        auth =   urllib.request.HTTPBasicAuthHandler()
        opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
    else: 
       proxy =  urllib.request.ProxyHandler()
       auth =   urllib.request.HTTPBasicAuthHandler()
       opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

    try:
        opener.open( testSite, timeout=timeout)
    except Exception as e:
        return False
    return True

