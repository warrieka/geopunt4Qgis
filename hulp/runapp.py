#!/usr/bin/env python
import os, shutil


def main():
  src = '/home/kay/projects/test'
  target = '/home/kay/.qgis2/python/plugins/testPod'
  
  if os.path.exists(target):
    shutil.rmtree(target)
  shutil.copytree(src, target )
  os.system('/usr/bin/qgis &')

if __name__ == '__main__':
     main()