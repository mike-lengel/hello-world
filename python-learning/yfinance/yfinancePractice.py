import yfinance
import os
import time
import sqlite3
from datetime import datetime

""" data = yfinance.download(tickers = "SPY DIA QQQ", period = "max", interval="1d", group_by = 'ticker', auto_adjust=True)

#print(str(data))

spy=yfinance.Ticker("SPY")
options = spy.options

for chain in options:
    print("Getting option chains for: ")
    print(chain)
    print(spy.option_chain(chain))
    
print(spy.option_chain(options[0])[1]) """

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

    #Create table
    c.execute("CREATE TABLE prices (TICKERSYMBOL text, TRADEDATE datetime, OPEN real, HIGH real, LOW real, CLOSE real, VOLUME real, PRIMARY KEY (TICKERSYMBOL, TRADEDATE))")
    conn.commit()
    

def dataDownload(tickerList,startDate,endDate):
    dataDownloaded={}
    for tick in tickerList:
        print("Starting dowload for " +tick)
        dataDownloaded[tick]=yfinance.download(tick,start=startDate,end=endDate, auto_adjust=True,prepost=True)
    print("All downloads complete!")
    return dataDownloaded

def insertTickerDataToDB(dbName,data):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    for ticker in data.keys():
        print("Starting insert for: "+ticker+"\n")
        for row in data[ticker].itertuples():
            oneRow = [str(ticker), str(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])]
            c.execute("INSERT INTO prices VALUES (?,?,?,?,?,?,?)",oneRow)
            print(oneRow)
        print("Done with: "+ticker+"\n")
    conn.commit()
    print("Done inserting data for all tickers...")


dbName = "tickerData.db"
startDate = "2000-01-01"
endDate = "2020-05-06"
tickerList = ["AAPL","AMZN","BABA","BIDU","C","CMG","CSCO","DIS","EEM","EWW","EWZ","FB","FXI","GDX","GDXJ","GLD","GOOG","GS","IBM","IWM","MSFT","NFLX","SBUX","SLV","SNAP","TLT","TSLA","TWTR","USO","UVXY","VIX","XLE","XLU","XOP","JNUG","NOBL","SPHD","VOO","KO","F","BA","PTON","ROKU","SQ","AAL","ADNT","AMD","AVGO","BYND","CAT","COF","DD","DE","GM","GOOGL","HD","JPM","LOW","M","MCD","MMM","NVDA","ORCL","PG","QCOM","SHOP","TGT","UBER","V","VFC","WMT","X","XOM"]
#tickerList = ["SPY","DIA","QQQ"]

#initializeDB(dbName)
d = dataDownload(tickerList,startDate,endDate)
insertTickerDataToDB(dbName,d)

