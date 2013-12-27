#!/usr/bin/env python
import os, shutil


def main():
  src = os.path.abspath( os.path.dirname( __file__ ) + "/.." )
  target = os.path.join( os.environ["HOME"], '.qgis2/python/plugins/geopunt4Qgis' )
  
  if os.path.exists(target):
    shutil.rmtree(target)
  shutil.copytree(src, target )
  os.system('/usr/bin/qgis &')

if __name__ == '__main__':
     main()