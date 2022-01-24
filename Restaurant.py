import requests
from bs4 import BeautifulSoup
import re

class Restaurant:
    """
    A class retrieving various attributes for a given restaurant from wwww.zlatestraky.cz

    ...

    Attributes
    ----------
    soup : A Beautiful Soup object
        A request converted into a Beautiful Soup object
    
    name : str
        The name of the restaurant
    
    district : str
        Restaurant's district

    ratings : float
        Average ratings of the restaurant

    review_count : int
        Number of reviews

    opening_hours : dict
        Opening hours on each day of the week

    opening_hours_span : dict
        The total opening time for each day of the week

    email_address : str
        The restaurant's email address

    Methods
    -------
    getSoup():
        A function to send a request and convert it into a Beautiful Soup object
    
    getName(soup):
        A function to retrieve the name of the restaurant

    getDirstrict(soup)
        A function to retrive the restaurant's district
    
    getRatings(soup)
        A function to retrieve the ratings
    
    getReviewCount(soup)
        A function to retrieve the number of reviews

    getOpeningHours(soup)
        A function to retrieve the opening hours and put them into a dictionary

    rangeToNumber(time_range)
        A function to convert a string containing a time range into a number

    openingHoursToSpan(opening_hours)
        A function to convert the opening hours into a number

    getEmail(soup)
        A function to retrive the email address    
    """
    def __init__(self,link):
        """
        Constructs all the necessary attributes for the restaurant.

        Parameters
        ----------
            link : str
                link to the restaurants page
        """
        self.soup=self.getSoup(link)
        self.name=self.getName(self.soup)
        self.district=self.getDistrict(self.soup)
        self.ratings=self.getRatings(self.soup)
        self.review_count=self.getReviewCount(self.soup)
        self.opening_hours=self.getOpeningHours(self.soup)
        self.opening_hours_span=self.openingHoursToSpan(self.opening_hours)
        self.email_address=self.getEmail(self.soup)
    
    def getSoup(self,link):
        """
        A function to send a request and convert it into a Beautiful Soup object

        Parameters
        ----------
        link : str
            link to the restaurants page

        Returns
        -------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page
        """
        request=requests.get(link)
        if request.status_code==200:
            soup=BeautifulSoup(request.content,'html.parser')
        else:
            print('Unsuccessful request')
        return soup

    def getName(self,soup):
        """
        A function to retrieve the name of the restaurant

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        restaurant_name : str
            The name of the restaurant
        """
        restaurant_name=soup.find('h1',{'itemprop':'name'}).text
        return restaurant_name

    def getDistrict(self,soup):
        """
        A function to retrive the restaurant's district

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        district : str
            The restaurant's district
        """
        address=soup.find('span',{'itemprop':'description'}).text
        district=re.search('Praha [0-9]{1,2}',address).group(0)
        return district

    def getRatings(self,soup):
        """
        A function to retrive the ratings

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        ratings : float
            The restaurant's average ratings
        """
        ratings=soup.find('span',{'itemprop':'ratingValue'}).text
        return float(ratings)

    def getReviewCount(self,soup):
        """
        A function to retrive the number of reviews

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        review_count : int
            The number of reviews
        """
        review_count=soup.find('span',{'itemprop':'reviewCount'}).text
        return int(review_count)

    def getOpeningHours(self,soup):
        """
        A function to retrieve the opening hours and put them into a dictionary

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        dict : dict
            A dictionary containing the opening hours for each day of the week
        """
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

    def rangeToNumber(self,time_range):
        """
        A function to convert a string containing a time range into a number

        Parameters
        ----------
        time_range : str
            A time range as a string

        Returns
        -------
        number : float
            A number representing the time span of the given time range
        """
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
        """
        A function to convert the opening hours into a number

        Parameters
        ----------
        opening_hours : dict
            Opening hours for each week day as a dictionary

        Returns
        -------
        span_dict : dictionary
            A dictionary of time spans
        """
        span_dict={key:self.rangeToNumber(value) for (key,value) in opening_hours.items()}
        return span_dict

    def getEmail(self,soup):
        """
        A function to retrive the email address

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        email : str
            The restaurant's email address
        """
        email_address=soup.find('a', {'data-ta':'EmailClick'}).text
        return email_address



