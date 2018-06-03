#!/usr/bin/env python
from __future__ import print_function
import os, glob
import zipfile

PROJECT = "geopunt4Qgis"
INCLUDEFILE = ["*.py", "*.txt", "*.qrc", "*.md", "*.gif", "*.jpg", "*.png", "*.html", "*.qm", "*.json", "*.xml" ] 
INCLUDEDIR = ["images","i18n","data","tools","geopunt","mapTools"]

def makeList( src ):
  fileList = []    
  for idir in INCLUDEDIR:
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*","*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*","*","*" ))
    fileList = fileList + glob.glob( os.path.join(  src , idir , "*","*","*","*","*" ))
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
    if not os.path.exists( os.path.dirname(target) ):
        os.mkdir( os.path.dirname(target) )
    with zipfile.ZipFile( target , mode='w') as zipf:
        zipdir( src , zipf)
        
if __name__ == '__main__':
    SOURCE = os.path.dirname( os.path.dirname(os.path.realpath(__file__)) )
    TARGET = os.path.join( SOURCE , "build" , "{}.zip".format( PROJECT ) )
    main(SOURCE, TARGET)
