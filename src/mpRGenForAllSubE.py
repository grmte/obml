#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import utility
import attribute

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-s', required=True,help='Location of the folder containing all the sub experiments')
    parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
    parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
    parser.add_argument('-pd', required=True,help='Prediction directory')
    parser.add_argument('-td',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")
    parser.add_argument('-wt',required=True,help="default/exp , weight type to be given to different days")
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    args = parser.parse_args()

    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
    if args.skipM == None:
        args.skipM = "yes"
    if args.skipP == None:
        args.skipP = "yes"
                
    print "Using the experiment folder " + args.e
    
    print "Training files steps"
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    predictionDataDirectoryName = args.pd.replace('/ro/','/wf/')
    predictionDataDirectoryName = predictionDataDirectoryName + "/p/" + os.path.basename(os.path.dirname(args.e))
    if not os.path.exists(predictionDataDirectoryName):
        os.mkdir(predictionDataDirectoryName)
        
    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)

    args.s = args.s + "/"
    rProgName = "trainPredict"+ algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +\
     "-pd." + os.path.basename(os.path.abspath(args.pd)) +  "-wt." + args.wt+ attribute.generateExtension()  + "-For"+os.path.basename(os.path.dirname(args.s))+"SubE.r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')

    if(algo == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(algo == 'randomForest'):
        rScript.write('require (randomForest) \n')
    elif(algo == 'mda'):
        rScript.write('require (mda) \n')
    
    rCodeGen.ForSetUpChecksForTrainPredictTogather(rScript)
    rCodeGen.ToReadTargetFile(rScript,config)
    rCodeGen.ForWtVectorGeneration(rScript,args.wt.lower())
    for target in config['target']:
        rCodeGen.ToReadFeatureFiles(rScript,config,target,2)
        rCodeGen.ForSanityChecks(rScript,config,target)

    print "For prediction data set"
    configForPredictions = ConfigObj(args.e+"/design.ini")
    print "The config parameters that I am working with are"
    for target in configForPredictions['target']:
        feature_keys = configForPredictions['features-'+target].keys()
        features = configForPredictions['features-'+target]
        for key in feature_keys:
            new_key = key + "P"
            features[new_key] = features[key]
            del features[key]
        print configForPredictions 

        rCodeGen.ToReadFeatureFiles(rScript,configForPredictions,target,4)
        rCodeGen.ForSanityChecks(rScript,configForPredictions,target)
    
    designFiles = utility.list_files(args.s)

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for ' + designFile + '")\n')
        config = ConfigObj(designFile)
        configForPredictions = ConfigObj(designFile)
        #--------------MODEL--------------------
        for target in config['target']:
            feature_keys = configForPredictions['features-'+target].keys()
            features = configForPredictions['features-'+target]
            for key in feature_keys:
                new_key = key + "P"
                features[new_key] = features[key]
                del features[key]
            lModelGeneratedAfterTraining = os.path.dirname(designFile) + '/' + algo + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
            '-dt.' + args.dt + '-targetClass.' + args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  + '.model'
            if os.path.isfile(lModelGeneratedAfterTraining)and ( args.skipM.lower() == "yes" ):
                print "Model File " + lModelGeneratedAfterTraining + " already exists . So it will not be formed again . If you want to re-generate model then re-run with -skipM=No"
            else:
                rCodeGen.ToCreateDataFrameForTraining(rScript,config,target)
                rCodeGen.ForTraining(rScript,args,config,target)
                rCodeGen.saveTrainingModel(rScript,args,os.path.dirname(designFile),target)
        
        #--------------Prediction Part--------------------
            predictionFileName = predictionDataDirectoryName + "/" +  args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(designFile)) +\
                                 "-wt." + args.wt+ attribute.generateExtension()  +".predictions"
            if not os.path.isfile(predictionFileName) or ( args.skipP.lower() == "no" ):
                rCodeGen.ForPredictions(rScript,configForPredictions,args,designFile,target,4)
            else:
                print "Prediction File " + predictionFileName + "Already exists , not generating it again . If you want to generate it again then rerun it with -skipP no "
    rScript.write('rm(list=ls())')
    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)
    
if __name__ == "__main__":
    main()
