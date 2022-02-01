import requests
from bs4 import BeautifulSoup
import json

#Sending a request
request=requests.get('https://cs.wikipedia.org/wiki/Administrativn%C3%AD_d%C4%9Blen%C3%AD_Prahy#Obvody_(1%E2%80%9310)')

#Extracting the desired part
soup=BeautifulSoup(request.content)
table=soup.find('table',{'class':'wikitable'}) #Extracting the table
lines=table.find_all('tr') #Extracting the lines of the table
lines.pop(0) #First element is the header => not needed

#Making a dictionary with keys for each municipal district
dist_dict={}
for line in lines:
    cells=line.find_all('td') #Each line has 3 cells (municipal district, administartive districts, cadastral areas)
    key=cells[0].find('a')['title'] #First cell always contains only one value - the municipal district - that will be our key
    demo_list=[] #List to temporarily store the values to
    for cell in cells[1:3]: #the second and third cell are the admin. districts and cadastral areas - values to map
        values=cell.find_all('a') #Extract all the values (multiple or one but still a list)
        for a in values: #Extract the title for each value
            demo_list.append(a['title'])
    dist_dict[key]=demo_list

#Adjusting the names so its easier to search through them
for key in dist_dict:
    new_list=[]
    for value in dist_dict[key]:
        if re.search('\(',value): #Remove (Praha) if present
            new_list.append(value[:value.index(" (")])
        elif re.search('-',value): #Remove Praha- if present
            new_list.append(value[value.index("-")+1:])
        else:
            new_list.append(value)
    dist_dict[key]=new_list

#Removing the municipal districts from the lists since they are the same as the keys
for key in dist_dict:
    dist_dict[key].remove(key)

#Save the result for future use (dump the dict to json and export it to json file)
with open('dist_dict.json', 'w') as outfile:
    json.dump(dist_dict, outfile)