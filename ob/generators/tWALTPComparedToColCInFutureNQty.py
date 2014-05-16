import os
import colNumberOfData
import dataFile

import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix(args):
   queueOfCellValueInFutureNLTQs = deque()
   totalOfFutureNRows = 0.0
   if args.n is None:
       print "-n has not been specified"
       os._exit(-1)
   totalOfFutureLTQQty = int(args.n)

   try:
      args.c 
   except:   
      print "-c has not been specified"
      os._exit(-1)

   colNumberOfAttribute = eval("colNumberOfData."+ args.c )
      
   lPipSize = 25000

   """ lets get the total of futureNrows"""
   futureLTQSum = 0
   currentRowIndex = 0
   lLastTradeIndex = 0
   lNoMoreTradesFound = 0
   currentLTPValue = 0.0
   currentLTQValue = 0
   WeightedLTPSum = 0.0
   totalLTPQty = totalOfFutureLTQQty
   while(futureLTQSum < totalOfFutureLTQQty):
      if dataFile.matrix[currentRowIndex][colNumberOfData.MsgCode].upper() == "T":
         currentLTPValue = float(dataFile.matrix[currentRowIndex][colNumberOfData.LTP])
         currentLTQValue = int(dataFile.matrix[currentRowIndex][colNumberOfData.NewQ])
         queueOfCellValueInFutureNLTQs.append( [ (currentLTPValue * currentLTQValue) , currentLTQValue , currentLTPValue , 0 ]  )
         futureLTQSum = futureLTQSum + currentLTQValue
         WeightedLTPSum = WeightedLTPSum + queueOfCellValueInFutureNLTQs[-1][0] 
      lLastTradeIndex = currentRowIndex
      currentRowIndex = currentRowIndex + 1
   if futureLTQSum > totalOfFutureLTQQty :
      currentLTQValueToBeUsed = currentLTQValue - ( futureLTQSum - totalOfFutureLTQQty ) 
      currentTickPriceToBeAdded  = currentLTPValue * currentLTQValueToBeUsed 
      LTQValueNotAdded = ( futureLTQSum - totalOfFutureLTQQty )
      WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
      queueOfCellValueInFutureNLTQs[-1] = [ currentTickPriceToBeAdded , currentLTQValueToBeUsed , currentLTPValue , LTQValueNotAdded ]

   currentRowCount = 0
   for dataRow in dataFile.matrix:
      sum = 0 
      currentPrice = float(dataFile.matrix[currentRowCount][colNumberOfAttribute])
      currentLTP = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])
      currentMsgCode = dataFile.matrix[currentRowCount][colNumberOfData.MsgCode]
      currentLTQ = int(dataFile.matrix[currentRowCount][colNumberOfData.NewQ])
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      
      if (dataFile.matrix[currentRowCount][colNumberOfData.MsgCode].upper() == "T") :
          lZerothElementOfQueue = queueOfCellValueInFutureNLTQs.popleft()
          WeightedLTPSum = WeightedLTPSum - lZerothElementOfQueue[0]
          LTQSubtracted = lZerothElementOfQueue[1]
          if len(queueOfCellValueInFutureNLTQs) != 0:
              LTQWhichCanBeAddedWithoutNewTradeMessage = queueOfCellValueInFutureNLTQs[-1][3]
              LTQAddedWithoutNewTradeMessage = min( LTQSubtracted , LTQWhichCanBeAddedWithoutNewTradeMessage)
              currentTickPriceToBeAdded = ( LTQAddedWithoutNewTradeMessage * queueOfCellValueInFutureNLTQs[-1][2] ) + queueOfCellValueInFutureNLTQs[-1][0]
              LTQValueNotAddedInLastElementOfQueue = queueOfCellValueInFutureNLTQs[-1][3] - LTQAddedWithoutNewTradeMessage
              WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
              queueOfCellValueInFutureNLTQs[-1][0] =  currentTickPriceToBeAdded
              queueOfCellValueInFutureNLTQs[-1][1] = queueOfCellValueInFutureNLTQs[-1][1] + LTQAddedWithoutNewTradeMessage
              queueOfCellValueInFutureNLTQs[-1][3] = LTQValueNotAddedInLastElementOfQueue
          else:
              LTQAddedWithoutNewTradeMessage = 0
          if LTQSubtracted >  LTQAddedWithoutNewTradeMessage:
              LTQToBeAddedFromNewTrade = LTQSubtracted - LTQAddedWithoutNewTradeMessage
              if (lNoMoreTradesFound == 0):
                  startIndexToFindNextTrade = lLastTradeIndex + 1
                  while( startIndexToFindNextTrade < len(dataFile.matrix)):
                     if dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.MsgCode].upper() == "T":
                        lLastTradeIndex = startIndexToFindNextTrade 
                        futureLTPValue = float(dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.LTP])
                        futureLTQValue = int(dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.NewQ])
                        queueOfCellValueInFutureNLTQs.append( [ (futureLTPValue * futureLTQValue) , futureLTQValue , futureLTPValue , 0 ]  )
                        LTQToBeAddedFromNewTrade = LTQToBeAddedFromNewTrade - futureLTQValue
                        WeightedLTPSum = WeightedLTPSum + queueOfCellValueInFutureNLTQs[-1][0] 
                        
                        if LTQToBeAddedFromNewTrade <= 0 :
                            if LTQToBeAddedFromNewTrade < 0 :
                                LTQValueToBeUsed = futureLTQValue + LTQToBeAddedFromNewTrade
                                currentTickPriceToBeAdded  = LTQValueToBeUsed * futureLTPValue 
                                LTQValueNotAdded = -1 * LTQToBeAddedFromNewTrade
                                WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
                                queueOfCellValueInFutureNLTQs[-1] = [ currentTickPriceToBeAdded , LTQValueToBeUsed , futureLTPValue , LTQValueNotAdded ]
                               
                            break
                     startIndexToFindNextTrade = startIndexToFindNextTrade + 1
                  if startIndexToFindNextTrade == len(dataFile.matrix):
                     if LTQToBeAddedFromNewTrade > 0 :
                         totalLTPQty = totalLTPQty - LTQToBeAddedFromNewTrade 
                     lNoMoreTradesFound = 1
              else:
                  totalLTPQty = totalLTPQty - LTQToBeAddedFromNewTrade 
          for ele in queueOfCellValueInFutureNLTQs:
              sum =  sum + (ele[1]*ele[2]) 
              if (ele[1]*ele[2] != ele[0]):
                  print "Error in Code"
                  os.exit(-1)
      
      if sum != 0 and sum != WeightedLTPSum :
          print "Error in Code"
          os.exit(-1)
      if totalLTPQty != 0:
          WALTPOfFutureNQty = WeightedLTPSum / totalLTPQty


      if args.c == "BidP0":
          if WALTPOfFutureNQty >= (currentPrice + lPipSize):
              lClassOfTargetVariable = 1
          else:
              lClassOfTargetVariable = 0
      else:
          if WALTPOfFutureNQty <= (currentPrice - lPipSize):
              lClassOfTargetVariable = 1
          else:
              lClassOfTargetVariable = 0

      attribute.aList[currentRowCount][1] = lClassOfTargetVariable
      attribute.aList[currentRowCount][2] = currentPrice
      attribute.aList[currentRowCount][3] = ";".join([ str(WALTPOfFutureNQty) , str(currentLTP) , str(currentLTQ) ,\
                                                       str(currentMsgCode) , str(WeightedLTPSum) , str(totalLTPQty)
                                                        ])

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 
         
   lNameOfTarget = "tWALTPComparedToCol" + str(args.c) + "InFuture" + str(args.n) + "Qty" 
   return ["TimeStamp",lNameOfTarget,args.c,"WALTPWithWtAsLTQForFuture"+args.n+"LTQQty","CurrentLTP","CurrentLTQ","CurrentMsgCode",\
           "WeightedLTPSum" , "totalLTPQtys"]
