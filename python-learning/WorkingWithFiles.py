import urllib.request
import sys
import csv
import zipfile
import os

fileName = "python-learning\FY2020_50_County_rev.csv"
lineNum = 0
listOfLists = []

with open(fileName,'r') as csvfile:
    lineReader = csv.reader(csvfile, delimiter = ",", quotechar = "\"")
    for row in lineReader:
        lineNum+=1

        if lineNum==1:
            print("Skipping the header row")
            continue #skips to next iteration of "for" loop

        rent50_0 = row[1]
        rent50_1 = row[2]
        rent50_2 = row[3]
        rent50_3 = row[4]
        rent50_4 = row[5]
        areaName = row[8]
        countyName = row[11]
        cityName = row[12]
        population = row[13]
        housingUnits = row[14]
        stateAbbr = row[15]

        oneResultRow = [stateAbbr, areaName, countyName, cityName, int(rent50_0), int(rent50_1), int(rent50_2), int(rent50_3), int(rent50_4), int(population), int(housingUnits)]
        listOfLists.append(oneResultRow)

        print(stateAbbr+","+areaName+","+countyName+","+cityName+","+str(rent50_0)+","+str(rent50_1)+","+str(rent50_2)+","+str(rent50_3)+","+str(rent50_4)+","+str(population)+","+str(housingUnits))

    print("Done with file.")
    print("We have information from " + str(len(listOfLists))+" municipalities")

listOfListsSortedByPopulation = sorted(listOfLists, key=lambda x:x[8], reverse=True)

print(listOfListsSortedByPopulation[:9])

import xlsxwriter

excelFileName = "python-learning\FY2020_Median_Rent.xlsx"

workbook = xlsxwriter.Workbook(excelFileName)
worksheet = workbook.add_worksheet("All Data")

worksheet.write_row("A1",["State","AreaName","CountyName","Municipality","Median_0","Median_1","Median_2","Median_3","Median_4","Population","HU"])

for rowNum in range(len(listOfListsSortedByPopulation)):
    oneRowToWrite = listOfListsSortedByPopulation[rowNum]
    worksheet.write_row("A"+str(rowNum+2), oneRowToWrite)

workbook.close()


