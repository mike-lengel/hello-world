# Testing the urllib2 package to web crawl

import urllib.request
import sys

urlToRead = "http://www.zionlutheranoxford.org"
#Dummy url for while loop

crawledWebLinks = {}
#Dictionary with all of the weblinks crawled

print("Welcome to the web crawler.  This program has basic web crawling capabilities.  Please enjoy!")

while urlToRead != "q":
    try:
        urlToRead = input("Please enter the next URL to crawl (\'q\' to quit):\n")
        if urlToRead == "q":
            print("Ok, URL entry has ended.")
            break
        shortName = input("Please enter a key for that URL:\n")
        webFile = urllib.request.urlopen(urlToRead).read()
        crawledWebLinks[shortName] = webFile

    except:
        print("===============================\nUnexpected Error========================",sys.exc_info()[0])
        stopOrProceed = input("Do you wish to continue? (\'n\' to stop)\n")
        if stopOrProceed == "n":
            print("Ok.... stopping\n")
            break
        else:
            print("Ok... moving on\n")
            continue

for key in crawledWebLinks.keys():
    print("URL for "+str(key)+" contains a page with "+str(len(crawledWebLinks[key]))+" size html code.\n"+str(crawledWebLinks[key]))


        

