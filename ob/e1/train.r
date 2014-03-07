#!/usr/bin/Rscript 
print ("Section1: Clearing the environment and setting the working directory") 
rm(list=ls()) 
args <- commandArgs(trailingOnly = TRUE) 
if(length(args) < 2) 
{ 
  stop("Not enough arguments. Please supply 2 arguments.") 
} 
if((args[1]=="-d") == TRUE ) { 
   print ("Parameter check passed") 
}else{ 
   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train.r -d data/20140207") 
} 
setwd(args[2]) 

print ("Section2: Read in the target files") 
targetVector=read.csv("tBidGreaterThanAskInNext100.target", header=FALSE) 


print ("Section3: Read in the feature files") 
feature1=read.csv("fBidP0OfCurrentRow.feature", header=FALSE) 
feature2=read.csv("fLTPOfCurrentRow.feature", header=FALSE) 

print ("Section4: Creating the data frame") 
df = data.frame(tBidGreaterThanAskInNext100=targetVector$V2,fBidP0OfCurrentRow=feature1$V2,fLTPOfCurrentRow=feature2$V2)

print ("Section5: Running logistic regression") 
logistic.fit <- glm (tBidGreaterThanAskInNext100 ~ fBidP0OfCurrentRow+fLTPOfCurrentRow , data = df,family = binomial(link="logit") ) 

print ("Section6: Saving the model in directory ~/Downloads/src/data/20140207/ in file ob/e1/design.model") 
save(logistic.fit, file = "ob/e1/design.model")