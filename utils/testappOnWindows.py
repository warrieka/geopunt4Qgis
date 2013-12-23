#!/usr/bin/env python
import os, shutil, glob

prjname = "geopunt4Qgis"
source = os.path.abspath( os.path.basename( __file__ ) + "\\.." )
target = r'C:\OSGeo4W\apps\qgis\python\plugins\geopunt4Qgis'
includeFile = ["*.py", "*.txt", "*.qrc", "*.ui", "*.md","*.gif", "*.jpg", "*.png","*.html", "*.qm", "*.ts","*.json","*.xml" ] 
includeDir = ["images","i18n","data"]

def makeList( src ):
  fileList = []
  for incl in includeFile: 
    for idir in includeDir:
      fileList = fileList + glob.glob( os.path.join(  src , idir , incl ))
    fileList = fileList + glob.glob(os.path.join( src , incl )) 
  return fileList

def main():
  if os.path.exists(target):
    shutil.rmtree(target)
    
  files = makeList(source)
  os.mkdir( target ) 
  for dir in includeDir:
        os.mkdir( os.path.join( target , dir ) )
  for sfile in files:
      print sfile
      dname = os.path.basename(os.path.dirname(sfile))
      if dname in includeDir:
          tfile = os.path.join( target, dname, os.path.basename( sfile ) )
      else:
          tfile = os.path.join( target, os.path.basename( sfile ) )
      

      shutil.copy2( sfile, tfile )
  os.startfile(r'C:\OSGeo4W\bin\qgis.bat')

if __name__ == '__main__':
     main()
