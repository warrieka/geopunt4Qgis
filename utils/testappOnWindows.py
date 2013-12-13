#!/usr/bin/env python
import os, shutil


def main():
  src = r'C:\projects\geopunt4Qgis'
  target = r'C:\Documents and Settings\sa64489\.qgis2\python\plugins\geopunt4Qgis'

  if os.path.exists(target):
    shutil.rmtree(target)
  shutil.copytree(src, target )
  os.startfile(r'C:\OSGeo4W\bin\qgis.bat')

if __name__ == '__main__':
     main()
