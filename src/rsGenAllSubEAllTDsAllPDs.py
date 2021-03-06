#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
src/rsGenForAllSubE.py -e ob/e/nsecur/24/ -a glmnet -td ob/data/ro/nsecur/20140203/ -dt 10 -pd ob/data/ro/nsecur/20140318/ -run real -sequence lp -targetClass binomial -tickSize 25000 -wt exp -g ob/generators/',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-dt',required=True,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No.  Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No.  Defaults to yes")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-skipTr',required=False,help="yes or no , If you want to regenerated tree then make this value no.  Defaults to yes")
parser.add_argument('-mpMearge',required=False,help="yes or no , If you want to separate model and prediction files then make this no .  Defaults to yes") 
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-t',required=True,help="TransactionCost")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument('-double',required=False,help='Double training of in model')
parser.add_argument('-treeUsed',required=False,help="To use tree in training")
parser.add_argument("-tTD",required=False,help="Number of days to be used for making tree")
parser.add_argument("-orderQty",required=True,help="Order qty ")
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.targetClass == None:
    args.targetClass = "binomial"
if args.tTD == None:
    args.tTD = args.dt
if args.t == None:
    args.t = "0.000015"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.skipT == None:
    args.skipT = "yes"
if args.mpMearge == None:
    args.mpMearge = "yes"
if args.dt == None:
    args.dt = "1"
if args.treeUsed == None:
    args.treeUsed = "no"                   
if(args.sequence == "dp"):
    import dp
if args.skipTr == None:
    args.skipTr = "yes" 

algo = rCodeGen.getAlgoName(args)

if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']
    
config = ConfigObj(args.e+"/design.ini")
targetAttributes = attribute.getTargetVariableKeys(config)
one_feature_attributes = attribute.getFeatureVariableKeys(config , targetAttributes.keys()[0])
lengthOfFeatures = len(one_feature_attributes)

allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td ,args.iT)
dataFolder = args.td
generatorsFolder = args.g
commandList = []

experimentFolder = args.e

# Seperate into 2 different list one for aGen and another for operateOnAttribute
for directories in allDataDirectories:
    commandList.append(["aGenForE.py","-e",experimentFolder,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
        
for chunkNum in range(0,len(commandList),int(args.nComputers)):
    lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
    utility.runCommandList(lSubGenList,args)
    print dp.printGroupStatus() 

entrylist = ""
exitlist = ""
for i in range(55,70,1):
    for j in range(50,i,1):
        exitlist = exitlist + str(j) + ";"
        entrylist = entrylist + str(i) + ";"
exitlist = exitlist[:-1]
entrylist = entrylist[:-1]          
'''

entrylist4 = ""
exitlist4 = ""
entrylist3 = ""
exitlist3 = ""
entrylist2 = ""
exitlist2 = ""
entrylist1 = ""
exitlist1 = ""

for entryCL2 in range(55,70,2):
    for entryCL1 in range(40,entryCL2,2):
        for exitCL2 in range(50,entryCL2,2):
            for exitCL1 in range(40,exitCL2,2):
                exitlist4 = exitlist4 + str(99) + ";"
                entrylist4 = entrylist4 + str(99) + ";"
                exitlist3 = exitlist3 + str(99) + ";"
                entrylist3 = entrylist3 + str(99) + ";"
                exitlist2 = exitlist2 + str(exitCL2) + ";"
                entrylist2 = entrylist2 + str(entryCL2) + ";"
                exitlist1 = exitlist1 + str(exitCL1) + ";"
                entrylist1 = entrylist1 + str(entryCL1) + ";"

exitlist4 = exitlist4[:-1]
entrylist4 = entrylist4[:-1]          
exitlist3 = exitlist3[:-1]
entrylist3 = entrylist3[:-1]          
exitlist2 = exitlist2[:-1]
entrylist2 = entrylist2[:-1]          
exitlist1 = exitlist1[:-1]
entrylist1 = entrylist1[:-1]          

'''
indexOfFeatures = 2
for algo in allAlgos:
    while indexOfFeatures <= lengthOfFeatures:
        lSubCombinationFolder = args.e+"/s/"+str(indexOfFeatures)+"c"
        designFiles = utility.list_files(lSubCombinationFolder)
        for designFile in designFiles:
            lExperimentFolderName = os.path.dirname(designFile) + "/"
            print lExperimentFolderName
            
            for wt in ['default']:
                lRCodeGenCommandList = []
                lMGenRCodeList = []
                lPGenRCodeList = []
                lTradingCommandList = [] 
                lTreeTrainingList = []
                for i in range(len(allDataDirectories)-int(args.dt)):
                    args.td = allDataDirectories[i]
                    predictionDirLastTD = allDataDirectories[i + int(args.dt) - 1]
                    predictionDirAfterLastTD = allDataDirectories[i + int(args.dt)]

                    lRCodeGenCommandList.append(["mRGenForE.py","-e",lExperimentFolderName,"-a",algo,"-targetClass",args.targetClass,"-skipM",args.skipM,"-td",args.td, "-dt" , \
                                                 args.dt , '-wt' , wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP ,'-double', args.double])
#                     lRCodeGenCommandList.append(["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",algo,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirLastTD , \
#                                                  "-dt" , args.dt , "-targetClass" , args.targetClass , '-wt' , wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-double', args.double])
                    lRCodeGenCommandList.append(["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",algo,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD ,\
                                                  "-dt" , args.dt , "-targetClass" , args.targetClass , '-wt' , wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-double', args.double])

                    dirName = args.td.replace('/ro/','/wf/')
                    if args.double:
                        scriptName = lExperimentFolderName+"/train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + wt + attribute.generateExtension() +"double.r"
                    else:
                        scriptName = lExperimentFolderName+"/train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + wt + attribute.generateExtension() +".r"
                    
                    trainingDataCorrespondingDateList = []    
                    trainingDataList = [] #";".join(allDataDirectories[i:i+ int(args.dt) ])
                    lCount = i
                    treeDataList = []
                    for trainDirs in allDataDirectories[i:i+ int(args.dt)]:
                        trainingDataList.append(trainDirs.replace('/ro/','/wf/'))  
                        
                    
                    try:
                        allDataDirectories[i+ int(args.tTD)]

                        for treeDirs in allDataDirectories[i:i+ int(args.tTD)]:
                            treeDataList.append(treeDirs.replace('/ro/','/wf/'))
                            if lCount-int(args.dt) > 0:
                                trainingDataCorrespondingDateList.append(allDataDirectories[lCount-int(args.dt)][-9:-1])
                            lCount = lCount + 1

                    except:
                        pass

                    trainingDataListString = ";".join(trainingDataList)
                    treeDataListString2 = ";".join(trainingDataCorrespondingDateList)
                    treeDataListString1 = ";".join(treeDataList)

                    lMGenRCodeList.append([scriptName,"-d",trainingDataListString])

                    if args.treeUsed.lower() == "yes":
                        if len(treeDataList) == len(trainingDataCorrespondingDateList):
                            lRCodeGenCommandList.append(["tRGenForE.py","-e",lExperimentFolderName,"-a",algo,"-targetClass",args.targetClass,"-skipT",args.skipTr,"-td",args.td, "-dt" , \
                                                     args.dt , '-wt' , wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-tTD",args.tTD,'-treeType',"1" ])                     
                            scriptName = lExperimentFolderName+"/traintree-td." + os.path.basename(os.path.abspath(args.td)) +"-tTD"+args.tTD+ "-dt." + args.dt + "-wt." + wt + attribute.generateExtension() +".r"
                            lTreeTrainingList.append([scriptName,'-d',treeDataListString1,'-p',treeDataListString2])

#                     dirName = predictionDirLastTD.replace('/ro/','/wf/')    
#                     scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  + \
#                                 os.path.basename(os.path.abspath(predictionDirLastTD)) + "-wt." + wt  + attribute.generateExtension() +".r"
#                     lPGenRCodeList.append([scriptName,"-d",dirName])

                    dirName = predictionDirAfterLastTD.replace('/ro/','/wf/') 
                    if args.double:
                        scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                                 os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + wt  + attribute.generateExtension() +"double.r"
                    else:
                        scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                                 os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + wt  + attribute.generateExtension() +".r"                         
                    lPGenRCodeList.append([scriptName,"-d",dirName])

                    if args.treeUsed.lower() == "no":
                        lTradingCommandList.append(["./ob/quality/tradeE7Optimized.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL",entrylist,"-exitCL",\
                                                    exitlist,"-orderQty",args.orderQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,\
                                                    '-tickSize',args.tickSize,'-wt',wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-double', args.double]) 
                    else:
                        lTradingCommandList.append(["./ob/quality/tradeE15/main.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL","60","-exitCL",\
                                                    "55","-orderQty","300",'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td ,"-tTD",args.tTD, "-pd",predictionDirAfterLastTD,\
                                                    '-tickSize',args.tickSize,'-wt',wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-treeType","1"]) 

#                    lTradingCommandList.append(["./ob/quality/tradeE12.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL1",entrylist1,"-exitCL1",exitlist1,"-entryCL2",entrylist2,"-exitCL2",exitlist2,"-entryCL3",entrylist3,"-exitCL3",exitlist3,"-entryCL4",entrylist4,"-exitCL4",exitlist4,"-orderQty","300",'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,'-tickSize',args.tickSize,'-wt',wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP]) 

                utility.runCommandList(lRCodeGenCommandList,args)
                print dp.printGroupStatus()
                totalModelsWhichCanBeScheduled = int(args.nComputers)
                for chunkNum in range(0,len(lMGenRCodeList),totalModelsWhichCanBeScheduled):
                    lSubModelList = lMGenRCodeList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
                    utility.runCommandList(lSubModelList,args)
                    print dp.printGroupStatus()
                
                utility.runCommandList(lPGenRCodeList,args)
                print dp.printGroupStatus()

                if args.treeUsed.lower() == "yes":
                    for chunkNum in range(0,len(lTreeTrainingList),totalModelsWhichCanBeScheduled):
                        lSubTreeList = lTreeTrainingList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
                        #utility.runCommandList(lSubTreeList,args)
                        #print dp.printGroupStatus()
                if args.treeUsed.lower() == "yes":
                    for chunkNum in range(0,len(lTradingCommandList),totalModelsWhichCanBeScheduled):
                        lSubTradingList = lTradingCommandList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
                        utility.runCommandList(lSubTradingList,args)
                        print dp.printGroupStatus() 
                else:
                    utility.runCommandList(lTradingCommandList,args)
                    print dp.printGroupStatus()
                     

                utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",dataFolder, "-dt" , str(args.dt) , '-nD' , str(args.nDays) , "-m" ,"ICICI_BANK_experiments" , "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        indexOfFeatures = indexOfFeatures + 1
    for i in range(len(allDataDirectories)-int(args.dt)):
        args.td = allDataDirectories[i]
        predictionDirLastTD = allDataDirectories[i + int(args.dt) - 1]
        predictionDirAfterLastTD = allDataDirectories[i + int(args.dt)]
#        utility.runCommand(["src/rsTradeBuySellMixMatch.py","-e",args.e,"-skipT",args.skipT,"-a",algo,"-entryCL", entrylist ,"-exitCL",exitlist,"-orderQty","300",'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,'-tickSize',args.tickSize,'-wt',wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)
#        print dp.printGroupStatus()
#    utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",dataFolder, "-dt" , str(args.dt) , '-nD' , str(args.nDays) , "-m" ,"LiveExperimentTestingInCurrentMonthsData" , "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
