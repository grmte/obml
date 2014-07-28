#!/usr/bin/python
import argparse,os,multiprocessing
from datetime import timedelta
from datetime import datetime
import utility
import attribute

parser = argparse.ArgumentParser(description='This program will do the 5 steps necessary to get the results for an experiment. \n \
The 5 steps are: \n \
1. Attribute generation  \n \
2. R code generation  \n \
3. R code running.  \n \
4. CMatrix generation  \n \
5. Doing the trading.   \n \
src/rsGenForE.py -e ob/e/nsecur/32/ -dt 10 -td ob/data/ro/nsecur/20140620/ \
-targetClass binomial -wt default -run real -sequence lp -g ob/generators/ -tickSize 25000 -orderQty 500 -entryCL "57;57;58;58;60;60;65;65" -exitCL \
"45;50;45;50;45;50;45;50"', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='dp/lp/serial')
parser.add_argument('-a', required=False,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-pd', required=False,help='Prediction directory')
parser.add_argument('-dt',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No . Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No. Defaults to yes")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-t',required=False,help="TransactionCost")
parser.add_argument('-entryCL',required=False,help="Trade open position entry point separated by semicolon")
parser.add_argument('-exitCL',required=False,help="Trade close position point separated by semicolon")
parser.add_argument('-orderQty',required=False,help="Qty with which you want to trade")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
args = parser.parse_args()

if args.entryCL == None:
    args.entryCL = "90;75;60;55;55;65;65"
if args.exitCL == None:
    args.exitCL = "50;50;50;45;50;50;45"
if args.orderQty == None:
    args.orderQty = "500"
if args.t == None:
    args.t = "0.000015"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.skipT == None:
    args.skipT = "yes"
if args.dt == None:
    args.dt = "1"
if args.wt == None:
    args.wt = "default"
if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

if args.targetClass == None:
    args.targetClass = "binomial"
    print "Since no class of target variable is specified so taking binomial class of target variable"

if(args.sequence == "dp"):
    import dp

def scriptWrapperForFeatureGeneration(trainingDirectory):
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize],args.run,args.sequence)
        
if(args.sequence == "dp"):
    import aGenForE
    experimentFolder = args.e
    dataFolder = args.td
    generatorsFolder = args.g
    commandList = []
    lListofTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,args.td) 
    if args.pd is None:
        predictionDirectory = attribute.getListOfTrainingDirectoriesNames(2,lListofTrainingDirectories[-1])[-1]
    else:
        predictionDirectory = args.pd
    for trainingDirectory in lListofTrainingDirectories:
        commandList.extend(aGenForE.getCommandList(experimentFolder,trainingDirectory,generatorsFolder,args.tickSize))
    commandList.extend(aGenForE.getCommandList(experimentFolder,predictionDirectory,generatorsFolder,args.tickSize))
    # Seperate into 2 different list one for aGen and another for operateOnAttribute

    aGenList = []
    attribute.getGenerationCommands(commandList,aGenList)
    utility.runCommandList(aGenList,args)
    dp.printGroupStatus()

    operateOnAttributeList = []
    attribute.getOperationCommands(commandList,operateOnAttributeList)
    operateOnAttributeListAsPerPriority = attribute.getOperationCommandsInPriority(operateOnAttributeList)
    for i in operateOnAttributeListAsPerPriority:
        utility.runCommand(i,args.run,args.sequence)
        dp.printGroupStatus() 

else:
    lListOfTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,args.td) 
    lListOfTrainPredictDirectories = lListOfTrainingDirectories
    if args.pd is None:
        predictionDirectory = attribute.getListOfTrainingDirectoriesNames(2,lListOfTrainPredictDirectories[-1])[-1]
    else:
        predictionDirectory = args.pd
    lListOfTrainPredictDirectories.append(predictionDirectory)
    if args.sequence == 'lp':
        # to run it in local parallel mode
        pool = multiprocessing.Pool() # this will return the number of CPU's
        results = map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)
    else:
        results = map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)
        
utility.runCommand(["rGenForE.py","-e",args.e,"-a",algo,"-sequence",args.sequence,"-targetClass",args.targetClass,"-skipM",args.skipM,\
                    '-dt',args.dt,'-pd',predictionDirectory,"-td",args.td,"-skipP",args.skipP, '-wt' , args.wt],args.run,args.sequence)
utility.runCommand(["runAllRScriptsForE.py","-td",args.td,"-pd",predictionDirectory,"-dt",args.dt,"-e",args.e,"-a",algo,"-run",args.run,\
                     '-wt' , args.wt,"-sequence",args.sequence],args.run,args.sequence)
if args.targetClass == "multinomial" :
#    utility.runCommand(["cMatrixGen.py","-d",predictionDirectory,"-e",args.e,"-a",algo],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE5.py","-e",args.e,"-a",algo,"-entryCL",args.entryCL,"-exitCL",args.exitCL,"-orderQty",args.orderQty,"-skipT",args.skipT,\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirectory,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
else:
    utility.runCommand(["./ob/quality/tradeE7.py","-e",args.e,"-a",algo,"-entryCL",args.entryCL,"-exitCL",args.exitCL,"-orderQty",args.orderQty,"-skipT",args.skipT,\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirectory,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)


utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",args.td, "-dt" , str(args.dt) ,"-pd", predictionDirectory, "-m" , "FollowingExperimentResults" , "-f" , "1"],args.run,args.sequence)
