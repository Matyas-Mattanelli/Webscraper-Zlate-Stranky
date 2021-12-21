import requests
from bs4 import BeautifulSoup
import re

class Restaurant:
    def __init__(self,link):
        self.soup=self.getSoup(link)
        self.name=self.getName(self.soup)
        self.district=self.getDistrict(self.soup)
        self.ratings=self.getRatings(self.soup)
        self.review_count=self.getReviewCount(self.soup)
        self.opening_hours=self.getOpeningHours(self.soup)
        self.opening_hours_span=self.openingHoursToSpan(self.opening_hours)
    
    def getSoup(self,link):
        request=requests.get(link)
        if request.status_code==200:
            soup=BeautifulSoup(request.content,'html.parser')
        else:
            print('Unsuccessful request')
        return soup

    def getName(self,soup):
        restaurant_name=soup.find('h1',{'itemprop':'name'}).text
        return restaurant_name

    def getDistrict(self,soup):
        address=soup.find('span',{'itemprop':'description'}).text
        district=re.search('Praha [0-9]{1,2}',address).group(0)
        return district

    def getRatings(self,soup):
        ratings=soup.find('span',{'itemprop':'ratingValue'}).text
        return float(ratings)

    def getReviewCount(self,soup):
        review_count=soup.find('span',{'itemprop':'reviewCount'}).text
        return int(review_count)

    def getOpeningHours(self,soup):
        table=soup.find('table',{'class':'table table-condensed'}).find_all('td')
        table_text=[]
        for i in table:
            if re.match('Dnes|\n',i.text):
                pass
            else:
                table_text.append(i.text)
        dict={}
        for i in range(0,len(table_text),2):
            dict[table_text[i]]=table_text[i+1]
        return dict

    def RangeToNumber(self,time_range):
        hours=[time_range.split()[i] for i in [0,2]] #splitting by space and disregarding "-"
        start_end=[] #empty list for converted starting and ending values
        for i in hours:
            if re.search(':',i): #if the string is not a whole hour, convert it
                splits=i.split(':')
                start_end.append(float(splits[0])+float(splits[1])/60)
            else:
                start_end.append(float(i))
        return round(start_end[1] - start_end[0],2)

    def openingHoursToSpan(self,opening_hours):
        span_dict={key:self.RangeToNumber(value) for (key,value) in opening_hours.items()}
        return span_dict


