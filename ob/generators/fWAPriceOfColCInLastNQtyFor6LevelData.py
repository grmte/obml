"""
This can generate features like:
1. fWAPriceOfColAskInLast100Qty
2. fWAPriceOfColBidInLast10000Qty
"""
import dataFile, os, colNumberOfData, attribute, common

def extractAttributeFromDataMatrix(args):
   try:
      args.n
   except:   
      print "Since -n has not been specified I cannot proceed"
      os._exit(-1)

   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit(-1)
   list_of_price_array = [ eval('colNumberOfData.'+args.c+'P1') , eval('colNumberOfData.'+args.c+'P2') ,\
                           eval('colNumberOfData.'+args.c+'P3') , eval('colNumberOfData.'+args.c+'P4') , eval('colNumberOfData.'+args.c+'P5')  ]
   list_of_qty_array = [ eval('colNumberOfData.'+args.c+'Q1') , eval('colNumberOfData.'+args.c+'Q2') ,\
                           eval('colNumberOfData.'+args.c+'Q3') , eval('colNumberOfData.'+args.c+'Q4') , eval('colNumberOfData.'+args.c+'Q5')  ]
   currentRowCount = 0
   qtyForCalculatingWeightedAverage = float(args.n)
   levelOfDataAvailable = 4
   for dataRow in dataFile.matrix:
      qSum = 0
      totalPrice = 0
      totalPriceAtThisLevel = 0
      i = 0
      while(i <= levelOfDataAvailable and qSum < qtyForCalculatingWeightedAverage):
         priceAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_price_array[i]])
         qtyAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_qty_array[i]])
         qSum += qtyAtThisLevel
         if(qSum > qtyForCalculatingWeightedAverage):
            qtyToUseAtThisLevel = qtyAtThisLevel - (qSum - qtyForCalculatingWeightedAverage)
            totalPriceAtThisLevel = qtyToUseAtThisLevel * priceAtThisLevel
         else:
            totalPriceAtThisLevel = qtyAtThisLevel * priceAtThisLevel
         
         totalPrice += totalPriceAtThisLevel
         i = i + 1
         
      if(qSum < qtyForCalculatingWeightedAverage): # This implies that the current row does not have enough qty to fill our requirement.
         qtyToUseAtThisLevel =  qtyForCalculatingWeightedAverage - qSum
         totalPriceAtThisLevel = qtyToUseAtThisLevel * priceAtThisLevel
         totalPrice += totalPriceAtThisLevel

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      attribute.aList[currentRowCount][1] = float(totalPrice)/qtyForCalculatingWeightedAverage

      currentRowCount += 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)
   
   lNameOfFeaturePrinted = "fWAPriceOfCol" + args.c + "InLast" + str(args.n) + "Qty"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]

