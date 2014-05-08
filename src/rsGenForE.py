#!/usr/bin/python
import argparse,os
from datetime import datetime
import utility

parser = argparse.ArgumentParser(description='This program will do the 5 steps necessary to get the results for an experiment. \n \
The 5 steps are: \n \
1. Attribute generation  \n \
2. R code generation  \n \
3. R code running.  \n \
4. CMatrix generation  \n \
5. Doing the trading.   \n \
An e.g. command line >rsGenForE.py -e ob/e/8/ -td ob/data/ro/20140204/ -pd ob/data/ro/20140205/ -g ob/generators/ -run dry -sequence serial -targetClass multinomial -skipM Yes -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='dp/lp/serial')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
        
import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

if args.targetClass == None:
    args.targetClass = "binomial"
    print "Since no class of target variable is specified so taking binomial class of target variable"
# only run the set of programs if the trading results file does not exist

utility.runCommand(["aGenForE.py","-e",args.e,"-d",args.td,"-g",args.g,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)        
utility.runCommand(["aGenForE.py","-e",args.e,"-d",args.pd,"-g",args.g,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)        
utility.runCommand(["rGenForE.py","-e",args.e,"-a",algo,"-sequence",args.sequence,"-targetClass",args.targetClass,"-skipM",args.skipM,"-pd",args.pd,"-skipP",args.skipP],args.run,args.sequence)
utility.runCommand(["runAllRScriptsForE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)
if args.targetClass == "binomial" :
    utility.runCommand(["cMatrixGen.py","-d",args.pd,"-e",args.e,"-a",algo],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE3.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".55","-exitCL",".45"],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE3.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".90","-exitCL",".50"],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE3.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".60","-exitCL",".40"],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE3.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".50","-exitCL",".25"],args.run,args.sequence)
else:
    utility.runCommand(["./ob/quality/tradeE5.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".15","-exitCL",".00","-orderQty","500"],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE5.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".10","-exitCL",".00","-orderQty","500"],args.run,args.sequence)

