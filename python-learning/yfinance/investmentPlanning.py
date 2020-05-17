import math
import yfinance
import os
import time
import sqlite3
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def summarizeTickerMovement(tickerSymbol, startDate, endDate):
    data = yfinance.download(tickerSymbol,start=startDate,end=endDate,auto_adjust=True,prepost=True)
    data["Daily Movement"]=data["Close"]-data["Open"]
    data["Daily % Change"]=data["Daily Movement"]/data["Open"]
    summary = {}
    periodOpenPrice = data["Open"][0]
    periodClosePrice = data["Close"][len(data)-1]
    periodPriceMovement = periodClosePrice - periodOpenPrice
    periodPercentPriceMovement = periodPriceMovement / periodOpenPrice

    ###############################################################################
    # TODO:Calculate the mean & sd for daily moves during the period
    # TODO:Calculate the largest daily move during the period
    # TODO:Expand to use timeframes other than the default "1d"    
    ###############################################################################

    summary["Period Open Price"]=periodOpenPrice
    summary["Period Close Price"]=periodClosePrice
    summary["Period Percent Move"]=periodPercentPriceMovement
    summary["Period Price Movement"]=periodPriceMovement
    print(data)
    print(summary)

#summarizeTickerMovement("SPY","2020-01-01","2020-04-30")

def initializeDB(dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    #Check if Table Exitsts
    c.execute("SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = 'prices'")
    if c.fetchone()[0]==1:
        return
    #Create table
    c.execute("CREATE TABLE prices (TICKERSYMBOL text, TRADEDATE datetime, OPEN real, HIGH real, LOW real, CLOSE real, VOLUME real, DIVIDENDS real, SPLITS real,     PRIMARY KEY (TICKERSYMBOL, TRADEDATE))")
    conn.commit()
    

def dataDownload(tickerList,startDate,endDate):
    dataDownloaded={}
    for tick in tickerList:
        print("Starting dowload for " +tick)
        dataDownloaded[tick]=yfinance.Ticker(tick).history(start=startDate,end=endDate, auto_adjust=True, actions=True)
    print("All downloads complete!")
    return dataDownloaded

def insertTickerDataToDB(dbName,data):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    for ticker in data.keys():
        print("Starting insert for: "+ticker+"\n")
        for row in data[ticker].itertuples():
            oneRow = [str(ticker), str(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7])]
            c.execute("REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?,?)",oneRow)
            print(oneRow)
        print("Done with: "+ticker+"\n")
    conn.commit()
    print("Done inserting data for all tickers...")

def calculateTotalGrowth(principal,rate,years,payment,compounding=12):
    compoundingInterestOfPrincipal = principal*pow(1+rate/compounding,years*compounding)
    futureValueOfPayment = payment*((pow(1+rate/compounding,years*compounding)-1)/(rate/compounding))

    return compoundingInterestOfPrincipal+futureValueOfPayment

#print(calculateTotalGrowth(20000,.1,25,500,12))

def growthOfInvestment(dbName, tickerSymbol : str, initialInvestment, monthlyContribution,startDate,endDate):
    conn = sqlite3.connect(dbName)
    initializeDB(dbName)    
    #TODO: Check if tickerSymbol data is already in the DB, if not, call the download to get the data.

    insertTickerDataToDB(dbName,dataDownload([tickerSymbol],startDate,endDate))
    conn.row_factory=sqlite3.Row
    c = conn.cursor()
    ####################################################
    #Table: prices
    #Columns: TICKERSYMBOL, TRADEDATE, OPEN, HIGH, LOW, CLOSE, VOLUME, DIVIDENDS, SPLITS
    ####################################################
    tickerData = c.execute("Select TickerSymbol, TradeDate, Close, Dividends, Splits FROM prices WHERE TIckerSymbol = ? AND TradeDate >= ? and TradeDate <= ? ORDER BY TradeDate asc",(tickerSymbol,startDate,endDate))
    rowList = tickerData.fetchall()

    formattedInitialInvestment = '${:,.2f}'.format(initialInvestment)
    numberOfShares = initialInvestment/rowList[0]['CLOSE']

    print("Your initial investment of " + formattedInitialInvestment + " on " +startDate+" was worth "+"{:,.3f}".format(numberOfShares)+" shares of " +tickerSymbol)
    
    print(rowList[0].keys())
    currentMonth = rowList[0]['TRADEDATE'][5:7]
    previousMonth = rowList[0]['TRADEDATE'][5:7]
    for row in rowList:
        currentMonth = row['TRADEDATE'][5:7]
        if row['CLOSE'] is None:
            continue
        if row['SPLITS']>0:
            logging.debug(row['TRADEDATE']+" split of "+"{:,.3f}".format(row['SPLITS']) + " for a new total of "+"{:,.3f}".format(numberOfShares*row['SPLITS'])+ "shares")
            numberOfShares*=row['SPLITS']
        if row['DIVIDENDS']>0:
            logging.debug(row['TRADEDATE']+ " dividends of "+"${:,.2f}".format(row['DIVIDENDS'])+ " for each of your "+"{:,.3f}".format(numberOfShares)+" shares reinvested for "+"{:,.3f}".format((numberOfShares*row['DIVIDENDS'])/row['CLOSE'])+ " additional shares")
            numberOfShares+=(numberOfShares*float(row['DIVIDENDS']))/float(row['CLOSE'])
        if currentMonth != previousMonth:
            logging.debug(row['TRADEDATE'] + " adding monthly contribution of " +"${:,.2f}".format(monthlyContribution)+" worth "+"{:,.3f}".format(monthlyContribution/row['CLOSE'])+" shares")
            numberOfShares += monthlyContribution/row['CLOSE']
        previousMonth = currentMonth
    endValueOfInvestment = numberOfShares * rowList[len(rowList)-1]['CLOSE']
    print("By " + endDate+", your initial investment of " + formattedInitialInvestment + " and monthly payments of "+"${:,.2f}".format(monthlyContribution)+" will have grown to " + "{:,.3f}".format(numberOfShares) + " shares worth "+"${:,.2f}".format(endValueOfInvestment) )

    return endValueOfInvestment
    

    
testDBName = "tickerDataWithActions.db"
testTickerSymbol="AAPL"
testInitialInvestment = 1000
testMonthlyContribution = 100
testStartDate = "1970-01-01"
testEndDate = "2020-05-16"
growthOfInvestment(testDBName,testTickerSymbol,testInitialInvestment,testMonthlyContribution,testStartDate,testEndDate)