import sys, dataFile, os ,colNumberOfData, attribute, common
from collections import deque
from math import exp,sqrt

class ticks_values_to_be_stored(object):
    def __init__(self):
        self.MsgCode = ''
        self.OrderType = ''
        self.NewP = 0.0
        self.NewQ = 0
        self.Price = 0.0
        self.typeOfCase = False
        self.IntensityValue = 0.0

              
def updateCurrentTickAdditionToQueue( pCurrentTickObject, pPreviousTickObject , totalTradedQty , timeElapsed , l_first_time_elapsed , N , C , O):
    if O == 'T':
        if pPreviousTickObject != None:
            if  pCurrentTickObject.NewP == pPreviousTickObject.Price:
                pCurrentTickObject.typeOfCase = True
                totalTradedQty += pCurrentTickObject.NewQ
    else: 
        if O == 'N' or O == 'X' :   
            if pCurrentTickObject.MsgCode == O :
                if  pCurrentTickObject.OrderType.upper() == C:
                    pCurrentTickObject.typeOfCase = True
                    totalTradedQty += pCurrentTickObject.NewQ
            
    if timeElapsed != 0:
        if l_first_time_elapsed == False:
            pCurrentTickObject.IntensityValue = float(totalTradedQty) / timeElapsed
        else:
            pCurrentTickObject.IntensityValue = float(totalTradedQty) / N
    else:
        pCurrentTickObject.IntensityValue = totalTradedQty
    
    return  totalTradedQty   
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                           
def updateTickDeletionFromQueue(pObjectToBeDeleted , totalTradedQty ):

    if pObjectToBeDeleted.typeOfCase == True:
        totalTradedQty -= pObjectToBeDeleted.NewQ
    return totalTradedQty
     
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          
def extractAttributeFromDataMatrix(args):
    N = 5
    if args.n == None:
        N = 5
    else:
        N = int(args.n) 
    
    try:
        args.c
    except:
        print "Since -c has not been specified I cannot proceed"
        os._exit()

    try:
        args.o
    except:
        print "Since -o has not been specified I cannot proceed"
        os._exit()       

    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    numberOfRowsInLastNSecs = 0
    l_first_time_elapsed = False   
    queueOfValuesInLastNSecs = deque()
    timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp])
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    lengthOfDataMatrix = len(dataFile.matrix)
    totalTradedQty = 0
    lPreviousTickObject = None
    priceIndex = eval('colNumberOfData.'+args.c+'P0')
    if args.c == 'Ask':
        orderTypeToBeTracked = 'S'
    else:
        orderTypeToBeTracked = 'B'
    while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):

        lCurrentTickObject = ticks_values_to_be_stored()
        lCurrentDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
        timeOfCurrentRow = common.convertTimeStampFromStringToFloat(lCurrentDataRow[colNumberOfTimeStamp],args.cType)
        timeElapsed = timeOfCurrentRow - timeOfOldestRow
        if (timeElapsed < N):
            lCurrentTickObject.MsgCode = lCurrentDataRow[colNumberOfData.MsgCode]
            lCurrentTickObject.OrderType = lCurrentDataRow[colNumberOfData.OrderType]
            lCurrentTickObject.NewP = float(lCurrentDataRow[colNumberOfData.NewP])
            lCurrentTickObject.NewQ = int(lCurrentDataRow[colNumberOfData.NewQ])
            lCurrentTickObject.Price = float( lCurrentDataRow[priceIndex] )

            totalTradedQty = updateCurrentTickAdditionToQueue(lCurrentTickObject, lPreviousTickObject , totalTradedQty , timeElapsed , l_first_time_elapsed , N , orderTypeToBeTracked , args.o )

            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(lCurrentDataRow[colNumberOfTimeStamp])
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = str(lCurrentTickObject.IntensityValue) 
            
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = ";".join( map( str , [ timeElapsed , totalTradedQty , lCurrentTickObject.MsgCode ,\
                                                                                                          lCurrentTickObject.OrderType , lCurrentTickObject.NewP , lCurrentTickObject.NewQ ] ) )
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][3] = str(lCurrentTickObject.Price)
            queueOfValuesInLastNSecs.append([lCurrentTickObject,timeOfCurrentRow])
            lPreviousTickObject = lCurrentTickObject
            numberOfRowsInLastNSecs += 1   # Every append gets a +1 
            currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
            continue     # Since we are going back 1 row from current we cannot get data from current row
        
        else:
            l_first_time_elapsed = True
            # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
            while(timeElapsed >= N):
                if(len(queueOfValuesInLastNSecs) == 0):
                    timeOfOldestRow = timeOfCurrentRow
                    timeElapsed = 0
                    if(numberOfRowsInLastNSecs != 0):
                        print "Sanity check: This condition is not possible logically. numberOfRowsInLastNSecs should been 0. There has been an unknown error"
                        sys.exit(-1)
                else:   
                    oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
                    colValueInOldestElementInQueue = oldestElementInQueue[0]
                    totalTradedQty = updateTickDeletionFromQueue(colValueInOldestElementInQueue , totalTradedQty )
                    if len(queueOfValuesInLastNSecs) == 0:
                        timeElapsed = 0
                        timeOfOldestRow = timeOfCurrentRow
                    else:
                        timeOfOldestRow = queueOfValuesInLastNSecs[0][1]
                    numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
                    timeElapsed = timeOfCurrentRow - timeOfOldestRow
                    if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                        print "Sanity check: This condition is not possible logically. There has been an unknown error"
                        sys.exit(-1)
        
        print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)

    lNameOfFeaturePrinted = "fIntensityOfCol" + str(args.c) + "InOrder" + str(args.o) + "InLast" + str(args.n) + "Secs" 
    return [ "TimeStamp", lNameOfFeaturePrinted , "TimeElapsed" ,"totalQty", "MsgCode" , "Ordertype" ,"NewP","NewQ" ,"Price"
            ]
            