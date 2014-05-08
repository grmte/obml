#!/usr/bin/python
import argparse, glob
import utility
import multiprocessing  # read https://medium.com/building-things-on-the-internet/40e9b2b36148
from functools import partial

def parseCommandLine():
   parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>rRunForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
   parser.add_argument('-e', required=True,help='Directory of the experiment')
   parser.add_argument('-a', required=True,help='Algorithm name')
   parser.add_argument('-td', required=True,help='Training directory')
   parser.add_argument('-pd', required=True,help='Prediction directory')
   parser.add_argument('-run', required=True,help='Real or Dry')
   parser.add_argument('-sequence', required=True,help='lp (local parallel) / dp (distributed parallel) / Serial')
   parser.add_argument('-mpMearge',required=True,help="yes or no , If you want to separate model and prediction files then make this no")
   args = parser.parse_args()
   return args

def getTrainPredictCommandList(experimentFolder,algoName,trainFolder,predictFolder):
   commandList = list()
   # lets make a list of all the scripts that need to be run
   trainPredictScriptNames = glob.glob(experimentFolder+"/train-predict-"+algoName+"For*.r")
   trainDirName = trainFolder.replace('/ro/','/wf/')
   predictDirName = predictFolder.replace('/ro/','/wf/')
   for trainPredictScriptName in trainPredictScriptNames:
      commandList.append([trainPredictScriptName,"-td",trainDirName,"-pd",predictDirName])
   return commandList    

def getTrainCommandList(experimentFolder,algoName,trainFolder):
   commandList = list()
   # lets make a list of all the scripts that need to be run
   trainScriptNames = glob.glob(experimentFolder+"/train-"+algoName+"For*.r")
   dirName = trainFolder.replace('/ro/','/wf/')
   for trainScriptName in trainScriptNames:
      commandList.append([trainScriptName,"-d",dirName])
   return commandList

def getPredictCommandList(experimentFolder,algoName,predictFolder):
   commandList = list()
   # lets make a list of all the scripts that need to be run
   predictScriptNames = glob.glob(experimentFolder+"/predict-"+algoName+"For*.r")
   dirName = predictFolder.replace('/ro/','/wf/')      
   for predictScriptName in predictScriptNames:
      commandList.append([predictScriptName,"-d",dirName])
   return commandList
   
def wrapper(pCommandName): # we need this wrapper since pool.map has problems taking multiple arguments.
   utility.runCommand(pCommandName,args.run,args.sequence)

def main():
   global args
   args = parseCommandLine()
   experimentFolder = args.e
   trainDataFolder = args.td
   predictDataFolder = args.pd
   if args.mpMearge.lower() == "yes":
       commandList = getTrainPredictCommandList(experimentFolder,args.a,trainDataFolder,predictDataFolder)
       if args.sequence == 'lp':
          pool = multiprocessing.Pool() # this will return the number of CPU's
          results = pool.map(wrapper,commandList) # Calls trainWrapper function with each element of list trainScriptNames
       else:
          results = map(wrapper,commandList)           
   else: 
       commandList = getTrainCommandList(experimentFolder,args.a,trainDataFolder)
       if args.sequence == 'lp':
          # to run it in local parallel mode
          pool = multiprocessing.Pool() # this will return the number of CPU's
          results = pool.map(wrapper,commandList) # Calls trainWrapper function with each element of list trainScriptNames
       else:
          results = map(wrapper,commandList)
    
       commandList = getPredictCommandList(experimentFolder,args.a,predictDataFolder)
       if args.sequence == 'lp':
          # to run it in local parallel mode
          pool = multiprocessing.Pool() # this will return the number of CPU's
          results = pool.map(wrapper,commandList) # Calls trainWrapper function with each element of list trainScriptNames
       else:
          results = map(wrapper,commandList)
       
if __name__ == "__main__":
    main()

