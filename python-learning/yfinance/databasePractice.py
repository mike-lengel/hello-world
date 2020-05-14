import yfinance
import os
import time
import sqlite3
from datetime import datetime
import xlsxwriter

conn = sqlite3.connect("tickerDataWithoutPrePost.db")
c = conn.cursor()
#cur=c.execute("SELECT * from prices")

####################################################
#Table: prices
#Columns: TICKERSYMBOL, TRADEDATE, OPEN, HIGH, LOW, CLOSE, VOLUME
####################################################
#print(list(map(lambda x: x[0], cur.description)))

#query1 = c.execute("SELECT * FROM prices LIMIT 100")
#for row in query1:
#    print(row)

startDate = "2018-01-01"
endDate = "2019-12-31"
query2 = c.execute("SELECT l.TickerSymbol, start.tradeDate as startTradeDate,start.OPEN, end.tradeDate as endTradeDate, end.CLOSE, (end.CLOSE - start.OPEN) AS priceMovement, (end.CLOSE - start.OPEN)*100/start.OPEN AS perPriceMovement FROM (SELECT tickerSymbol, min(tradeDate) as tickerMinDate, max(tradeDate) as tickerMaxDate FROM prices WHERE tradeDate >= ? and tradeDate <=? GROUP BY tickerSymbol) AS l JOIN prices AS start ON l.TickerSymbol = start.TickerSymbol AND l.tickerMinDate = start.tradeDate JOIN prices as end ON l.TickerSymbol = end.TickerSymbol AND l.tickerMaxDate = end.tradeDate ORDER BY l.TickerSymbol ASC",(startDate,endDate))

print(list(map(lambda x: x[0], query2.description)))
for row in query2:
    print(row)

def createExcelWithPriceMoves(ticker,conn,startDate,endDate):
    c = conn.cursor()
    d = conn.cursor()
    e = conn.cursor()
    query = c.execute("SELECT TickerSymbol, TradeDate, Close, High, Low FROM prices WHERE TickerSymbol = ? AND TradeDate >= ? AND TradeDate <= ? ORDER BY TradeDate",(ticker,startDate,endDate))
    tempMax = list(d.execute("SELECT max(High) FROM prices WHERE TickerSymbol = ? AND TradeDate >= ? AND TradeDate <= ? ",(ticker,startDate,endDate)))
    maxValue = tempMax[0][0]
    print(maxValue)
    tempMin = list(e.execute("SELECT min(Low) FROM prices WHERE TickerSymbol = ? AND TradeDate >= ? AND TradeDate <= ? ",(ticker,startDate,endDate)))
    minValue = tempMin[0][0]
    print(minValue)
    excelFileName = "Stock Movement Summary - "+ticker+" from "+startDate+" to "+endDate+".xlsx"
    workbook = xlsxwriter.Workbook(excelFileName)
    worksheet = workbook.add_worksheet(ticker)

    worksheet.write_row("A1",["Price Movement for "+ticker+" from "+startDate+" to "+endDate])
    worksheet.write_row("A2",["Stock","Trade Date","Closing Price", "High", "Low"])
    lineNum = 3

    for row in query:
        worksheet.write_row("A"+str(lineNum),list(row))
        print("A"+str(lineNum)+str(list(row)))
        lineNum+=1

    chart1 = workbook.add_chart({'type':'line'})
    chart1.add_series({
        'categories' : '='+ticker+'!$B$3:$B$' + str(lineNum),
        'values' : '='+ticker+'!$C$3:$C$'+str(lineNum),
        'name' : '='+ticker+' Close'
        })
    chart1.add_series({
        'categories' : '='+ticker+'!$B$3:$B$' + str(lineNum),
        'values' : '='+ticker+'!$D$3:$D$'+str(lineNum),
        'name' : '='+ticker+' High'
        })
    chart1.add_series({
        'categories' : '='+ticker+'!$B$3:$B$' + str(lineNum),
        'values' : '='+ticker+'!$E$3:$E$'+str(lineNum),
        'name' : '='+ticker
        })    
    chart1.set_title({'name' : 'Movement of Ticker Price from '+startDate+' to '+endDate})
    chart1.set_x_axis({
        'name' : 'Trade Date',
        'date_axis' : True,
        'major_unit_type' : 'months',
        'minor_unit_type' : 'weeks'
        })
    chart1.set_y_axis({
        'name' : 'Price (USD)',
        'min' : minValue,
        'max' : maxValue
        })

    worksheet.insert_chart('F2',chart1,{
        'x_offset':25, 
        'x_scale' : 2,
        'y_offset' : 10,
        'y_scale' : 2
        
        })
    workbook.close()

createExcelWithPriceMoves("SPY",conn,startDate,endDate)

conn.close()
