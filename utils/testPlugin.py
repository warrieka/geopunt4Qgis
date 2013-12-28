#!/usr/bin/env python
"""
/***************************************************************************
testPlugin

"script to deploy and test a qgis plugin"
"workflow testPlugin.py: pack -> extract at QGISDIR -> start QGIS"
                            -------------------
       begin                : 2013-12-27
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
import os, shutil, zipfile, sys
import packPlugin4upload as pack

def removeExisting(target):
    if os.path.exists(target):
      print "removing: %s ->" % target
      shutil.rmtree(target)
      if not os.path.exists(target): 
	print "\t\t\t\t\t\t succes" 
      else:  
	raise Exception("could not remove: "+ target +", is qgis still running?")

def main(targetZip, project=None, qgis_exe=None):
  if sys.platform.startswith('win') : 
    home = os.environ["HOMEPATH"]
    # default: assume OSGeo4W is installed under C:\
    # try first variable qgis_exe then 32bit then 64bit
    if qgis_exe:
      run =  lambda: os.startfile(qgis_exe)
    elif os.path.exists( r'C:\OSGeo4W\bin\qgis.bat' ):
      run =  lambda: os.startfile(r'C:\OSGeo4W\bin\qgis.bat')
    elif os.path.exists( r'C:\OSGeo4W64\bin\qgis.bat' ): 
      run =  lambda: os.startfile(r'C:\OSGeo4W64\bin\qgis.bat')
    else:
      raise Exception("could not find a qgis executable")
  elif sys.platform.startswith('linux'): 
    home = os.environ["HOME"] 
    if qgis_exe:
      run =  lambda: os.system(qgis_exe + ' &')
    elif os.path.exists( '/usr/bin/qgis' ):
      run =  lambda: os.system('/usr/bin/qgis &')
    else:
      raise Exception("could not find a qgis executable")
  else:
    raise Exception('wrong os')
  
  targetDir = os.path.join( home , '.qgis2/python/plugins/' )
  
  if project:
     removeExisting(os.path.join(targetDir,project))
  
  zf = zipfile.ZipFile( targetZip )
  print "extracting from %s to: %s" % (targetZip, targetDir)
  zf.extractall( targetDir )
  zf.close()
  
  run()

if __name__ == '__main__':
    #commandline arguments
    if len(sys.argv) >= 2: QGISEXE = sys.argv[1]
    else: QGISEXE = None
    #settings are in packPlugin4upload
    PROJECT = pack.PROJECT
    SOURCE = os.path.abspath( os.path.dirname( __file__ ) + "/.." )
    TARGETZIP =  os.path.join( SOURCE , "build/%s.zip" % PROJECT )
    #pack first then extract to QGISDIR
    pack.main(SOURCE, TARGETZIP)
    main(TARGETZIP,PROJECT,QGISEXE)