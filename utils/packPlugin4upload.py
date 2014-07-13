#!/usr/bin/env python
import os, glob
import zipfile


PROJECT = "geopunt4Qgis"
INCLUDEFILE = ["*.py", "*.txt", "*.qrc", "*.md", "*.gif", "*.jpg", "*.png", "*.html", "*.qm", "*.json", "*.xml" ] 
INCLUDEDIR = ["images","i18n","data","ext-libs"]

def makeList( src ):
  fileList = []    
  for idir in INCLUDEDIR:
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*","*" ))
  for incl in INCLUDEFILE: 
    fileList = fileList + glob.glob(os.path.join( src , incl )) 
  return fileList

def zipdir(path, zipf):
  files = makeList(path)
  for zfile in files: 
     sbase = os.path.dirname(path)
     arcName = zfile.replace( sbase ,"")
     zipf.write( zfile , arcName)

def main(src, target):
    if os.path.exists( target ):
       os.remove(target)
    zipf = zipfile.ZipFile( target , 'w')
    zipdir( src , zipf)
    print "zipped all deploy files in %s to %s" % ( src, target)
    zipf.close() 

if __name__ == '__main__':
    SOURCE = os.path.abspath( os.path.dirname( __file__ ) + "/.." )
    TARGET = os.path.join( SOURCE , "build/%s.zip" % PROJECT )
    main(SOURCE, TARGET)