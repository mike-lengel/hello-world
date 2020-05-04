nameList = ["Bob","Frank","George","Cassie","Erin","Anita"]
ageList = [24,43,51,25,37,62]

dictAgeName = {}
counter=0

for i in nameList:
    dictAgeName[i]=ageList[counter]
    counter+=1

print(dictAgeName)
