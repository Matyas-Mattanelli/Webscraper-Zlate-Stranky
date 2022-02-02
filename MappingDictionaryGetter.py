#Running this file generates the dist_dict.json file which is the mapping dictionary for Prague districts 
#It is needed in Restaurant.py for generating a district based on an address
#No need to run it, the file has already been generated (but it is runnable if necessary)
import requests
from bs4 import BeautifulSoup
import json
import re

class MappingDictionaryGetter:
    """
    A class creating a mapping dictionary for Prague districts.

    ...

    Attributes
    ----------
    dist_dict : dict
        Mapping dictionary for Prague districts. Contains municipal districts as keys and administrative districts + cadastral areas as values

    Methods
    -------
    getMappingDict():
        A function to create the mapping dictionary. It sends a request to a wikipedia page and converts the acquired data into a dictionary

    cleanDict(dist_dict):
        A function to strip a raw mapping dictionary from unnecessary values.
    
    saveToJSON():
        A function to save the dictionary into a json file "dist_dict.json"

    """
    def __init__(self):
        """
        Constructs the dist_dict attribute by calling the getMappingDict function.

        Parameters
        ----------
        """
        self.dist_dict=self.getMappingDict()
    
    def getMappingDict(self):
        """
        A function to create the mapping dictionary. It sends a request to a wikipedia page and converts the acquired data into a dictionary

        Parameters
        ----------

        Returns
        -------
        dist_dict_final : dict
            Mapping dictionary for Prague districts
        """
        request=requests.get('https://cs.wikipedia.org/wiki/Administrativn%C3%AD_d%C4%9Blen%C3%AD_Prahy#Obvody_(1%E2%80%9310)') #Sending a request to the wikipedia page with Prague districts
        soup=BeautifulSoup(request.content,"html.parser") #Making a soup
        table=soup.find('table',{'class':'wikitable'}) #Extracting the table with municipal districts and their respective administrative districts and cadastral areas
        lines=table.find_all('tr') #Extracting the lines of the table (each line represents one municipal district)
        lines.pop(0) #First element is the header => not needed
        dist_dict={} #Making a dictionary with keys for each municipal district
        for line in lines:
            cells=line.find_all('td') #Each line has 3 cells (municipal district, administartive districts, cadastral areas)
            key=cells[0].find('a')['title'] #First cell always contains only one value - the municipal district - that will be our key
            demo_list=[] #List to temporarily store the values to
            for cell in cells[1:3]: #the second and third cell are the admin. districts and cadastral areas, respectively - values to map
                values=cell.find_all('a') #Extract all the values (multiple or one but still a list)
                for a in values: #Extract the title for each value
                    demo_list.append(a['title'])
            dist_dict[key]=demo_list
        dist_dict_final=self.cleanDict(dist_dict) #Clean the dictionary to keep only the useful values and increase the mapping speed and precision
        return dist_dict_final
    
    def cleanDict(self,dist_dict):
        """
        A function to strip a raw mapping dictionary from unnecessary values.

        Parameters
        ----------
        dist_dict : dict
            Raw mapping dictionary to be proccessed

        Returns
        -------
        dist_dict : dict
            Cleaned mapping dictionary
        """
        #Adjusting the values so its easier to search through them
        for key in dist_dict: 
            new_list=[]
            for value in dist_dict[key]:
                if re.search('\(',value): #Remove "(Praha)" if present
                    new_list.append(value[:value.index(" (")])
                elif re.search('-',value): #Remove "Praha-" if present
                    new_list.append(value[value.index("-")+1:])
                else: #If the above conditions are not met, the value does not need to be adjusted => return it
                    new_list.append(value)
            dist_dict[key]=new_list
        #Removing the municipal districts from the lists since they are the same as the keys
        for key in dist_dict:
            dist_dict[key].remove(key)
        return dist_dict

    def saveToJSON(self):
        """
        A function to save the dictionary into a json file "dist_dict.json"

        Parameters
        ----------

        Returns
        -------
        """
        with open('dist_dict.json', 'w') as outfile:
            json.dump(self.dist_dict, outfile)

dist_dict=MappingDictionaryGetter() #Generate the dictionary
dist_dict.saveToJSON() #Export it to a json file