from tkinter.messagebox import NO
import requests
from bs4 import BeautifulSoup
import re
import json

class Restaurant:
    """
    A class retrieving various attributes for a given restaurant from wwww.zlatestraky.cz

    ...

    Attributes
    ----------
    soup : A Beautiful Soup object
        A request converted into a Beautiful Soup object
    
    name : str or None
        The name of the restaurant
    
    district : str or None
        Restaurant's district

    ratings : float or None
        Average ratings of the restaurant

    review_count : int or None
        Number of reviews

    opening_hours : dict or None
        Opening hours on each day of the week

    opening_hours_span : dict or None
        The total opening time for each day of the week

    email_address : str or None
        The restaurant's email address

    phones : dict or None
        Phone nubers and their labels in a dictionary

    web_page : str or None
        Link for restaurant's own web page

    payment_methods : list or None
            List of available payment methods

    products : list or None
            List of available products

    services : list or None
            List of available services

    marks : list or None
            List of available marks

    coordinates : dict or None
            Dictionary of coordinates (latitude and longitude)

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

    getPhone(soup)
        A function to retrive the telephone numbers and their labels

    getWebPage(soup)
        A function to retrive a link for restaurant's own web page

    getPaymentMethods(soup)
        A function to retrive payment methods available in a restaurant

    getServicesMarksProducts(soup)
        This function extracts all children of the "Produkty+Služby+Značky" panel and puts them to one list

    getServicesSeparator(category)
        A function that accepts one of the three categories: 'Produkty', 'Služby', 'Značky', and picks the items from the list created by getServicesMarksProducts() between the specified category and the next one.

    getCoordinates(soup)
        A function to retrive coordinates of a restaurant    
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
        self.phones=self.getPhone(self.soup)
        self.web_page=self.getWebPage(self.soup)
        self.payment_methods=self.getPaymentMethods(self.soup)
        self.products=self.getServicesSeparator('Produkty')
        self.services=self.getServicesSeparator('Služby')
        self.marks=self.getServicesSeparator('Značky')
        self.coordinates=self.getCoordinates(self.soup)
    
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
        restaurant_name : str or None
            The name of the restaurant
        """
        if soup.find('h1',{'itemprop':'name'}) == None:
            restaurant_name = None
            return restaurant_name
        else:
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
        district : str or None
            The restaurant's district
        """
        if soup.find('span',{'itemprop':'description'}) == None:
            district = None
            return district
        else:
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
        ratings : float or None
            The restaurant's average ratings
        """
        if soup.find('span',{'itemprop':'ratingValue'}) == None:
            ratings = None
            return ratings
        else:
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
        review_count : int or None
            The number of reviews
        """
        if soup.find('span',{'itemprop':'reviewCount'}) == None:
            review_count = None
            return review_count
        else:
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
        dict : dict or None
            A dictionary containing the opening hours for each day of the week
        """
        if soup.find('table',{'class':'table table-condensed'}) == None:
            dict = None
            return dict
        else:
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
        opening_hours : dict or None
            Opening hours for each week day as a dictionary

        Returns
        -------
        span_dict : dict or None
            A dictionary of time spans
        """
        if opening_hours == None:
            span_dict = None
            return span_dict
        else:
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
        email_address : str or None
            The restaurant's email address
        """
        if soup.find('a', {'data-ta':'EmailClick'}) == None:
            email_address=None
            return email_address
        else:
            email_address=soup.find('a', {'data-ta':'EmailClick'}).text
            return email_address


    def getPhone(self,soup):
        """
        A function to retrive the telephone numbers and their labels

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        phones : dict or None
            Phone nubers and their labels in a dictionary
        """
        if soup.find('td', {'itemprop':'telephone'}).text == None:
            phones = None
            return phones
        else:
            telephone_numbers = []
            telephone_names = []

            #extracting telephone numbers:
            all_telephones = soup.find_all('td', {'itemprop':'telephone'})
            for i in all_telephones:
                telephone_numbers.append(i.text)

            #extracting telephone names:
            for i in telephone_numbers:
                telephone_names.append(soup.find('td', text=i).find_next_sibling('td').text)

            phones = {telephone_names[i]: telephone_numbers[i] for i in range(len(telephone_numbers))}

            return phones

    def getWebPage(self,soup):
        '''
        A function to retrive a link for restaurant's own web page

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        web_page : str or None
            Link for restaurant's own web page
        '''
        if soup.find('a', {'data-ta':'LinkClick'}) == None:
            web_page = None
            return web_page
        else:
            web_page = soup.find('a', {'data-ta':'LinkClick'})['href']
            return web_page

    def getPaymentMethods(self,soup):
        '''
        A function to retrive payment methods available in a restaurant

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        payment_methods : list or None
            List of available payment methods
        '''
        if soup.find('h2', text='Platební metody') == None:
            payment_methods = None
            return payment_methods
        else:
            payment_methods_raw = soup.find('h2', text='Platební metody').find_next_sibling('ul', {'class':'list-inline'}).find_all('li') #finding list of payment methods (wraped in <li><\li>)
            payment_methods = [] #empty list to be used in the next for loop

            for i in payment_methods_raw: #unwraping the <li>
                payment_methods.append(i.text)

            return payment_methods #list containing strings, representing individual payment methods

    def getServicesMarksProducts(self,soup):
        '''
        This function extracts all children of the "Produkty+Služby+Značky" panel and puts them to one list. This list is then used in the getServicesSeparator(). The function is not ment to be used on its own.

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        ServicesMarksProducts : list or None
            List containing all children of the "Produkty+Služby+Značky" panel
        '''
        if soup.find('div', {'class':'col-sm-12 tagcloud'}) == None:
            ServicesMarksProducts = None
        else:
            ServicesMarksProducts_raw = soup.find('div', {'class':'col-sm-12 tagcloud'}).find_all() #finding all children of the panel "Produkty+Služby+Značky"
            ServicesMarksProducts = []

            for i in ServicesMarksProducts_raw:
                ServicesMarksProducts.append(i.text)
            
            return ServicesMarksProducts


    def getServicesSeparator(self, category):
        '''
        A function that accepts one of the three categories: 'Produkty', 'Služby', 'Značky', and picks the items from the list created by getServicesMarksProducts() between the specified category and the next one.
        
        Parameters
        ----------
        category : 'Produkty' or 'Služby' or 'Značky'
            One of the three str objects specifing three categories. In case more categories are discovered, they will have to be addted manually.

        Returns
        -------
        items : list or None
            List containing items in the specified category
        '''
        ServicesMarksProducts = self.getServicesMarksProducts(self.soup)
        if ServicesMarksProducts == None:
             items = None
             return items
        else:
            try:
                ##defining the helper list of positions of categories
                services_index_list = []

                for i in ['Produkty', 'Služby', 'Značky']: #<-- in case of more categories, add here! (and also in the __init__)
                    if i in ServicesMarksProducts:
                        services_index_list.append(ServicesMarksProducts.index(i))   

                services_index_list.sort()

                ##selecting particular items
                if ServicesMarksProducts.index(category) == max(services_index_list):
                    items = ServicesMarksProducts[ServicesMarksProducts.index(category)+1:] #case when the given category is last in the ServicesMarksProducts list
                else:
                    items = ServicesMarksProducts[ServicesMarksProducts.index(category)+1:services_index_list[services_index_list.index(ServicesMarksProducts.index(category))+1]]
                    #when the given category is not last, subset the part of ServicesMarksProducts list between the given category and the next category
            
            except ValueError: #In case that retaurant does not have given category specified, None will return
                items = None
                return items

            else: #when the category is specified, the items will return
                return(items)

    def getCoordinates(self,soup):
        '''
        A function to retrive coordinates of a restaurant
        
        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        coordinates : dict or None
            Dictionary of coordinates (latitude and longitude)
        '''
        div_coordinates=soup.find('div',{'class':'map'})
        if div_coordinates == None:
            coordinates = None
            return coordinates
        else: 
            coordinates={}
            coordinates['latitude']=json.loads(div_coordinates['data-centerpoi'])['lat']
            coordinates['longitude']=json.loads(div_coordinates['data-centerpoi'])['lng']
            return coordinates