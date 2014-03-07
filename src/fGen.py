#!/usr/bin/python
import os
import sys
import importlib

import dataFile
import fGenArgs
import feature

sys.path.append(os.path.dirname(fGenArgs.args.m))
import colNumberOfData

user_module = importlib.import_module(os.path.basename(fGenArgs.args.m))

def main():
   dataFile.getDataIntoMatrix(fGenArgs.args.d)
   feature.initVector()
   user_module.extractFeatureFromDataMatrix()
   feature.writeToFile(os.path.basename(fGenArgs.args.m))

if __name__ == "__main__":
    main()
