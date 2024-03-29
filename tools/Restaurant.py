from audioop import add
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

    address : str or None
        The address of the restaurant
    
    dist_dict : dict
        Mapping dictionary for districts

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

    getAdress(soup)
        A function to retrieve the address of the restaurant

    getMappingDictionary():
        A function to load the prepared dictionary with municipal districts as keys and their respective administrative districts and cadastral areas as values

    mappingDistrict(address):
        A function to map administrative districts or cadastral areas to their municipal district based on a whole address. If the district cannot be mapped, it is derived from the zip code.
    
    getDistrictFromPraha_XX(praha_xx)
        A function to map administrative district or municipal district to municipal district

    getDistrict(address)
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
        self.address=self.getAddress(self.soup)
        self.dist_dict=self.getMappingDictionary()
        self.district=self.getDistrict(self.address)
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
        else:
            restaurant_name=soup.find('h1',{'itemprop':'name'}).text
        return restaurant_name

    def getAddress(self,soup):
        """
        A function to retrieve the address of the restaurant

        Parameters
        ----------
        soup : A Beautiful Soup object
            A Beatiful Soup object created from the request sent to the restaurants page

        Returns
        -------
        address : str or None
            The addres of the restaurant
        """
        if soup.find('span',{'itemprop':'description'}) == None:
            address = None
        else:
            address_full=soup.find('span',{'itemprop':'description'}).text
            address = re.search('.+?(?=okres)',address_full).group(0)
        return address

    def getMappingDictionary(self):
        """
        A function to load the prepared dictionary with municipal districts as keys and their respective administrative districts and cadastral areas as values

        Parameters
        ----------

        Returns
        -------
        dist_dict : dict
            Mapping dictionary for districts
        """
        with open('data\\dist_dict.json') as json_file:
            dist_dict = json.load(json_file)
        return dist_dict

    def mappingDistrict(self, address):
        """
        A function to map administrative districts or cadastral areas to their municipal district based on a whole address. If the district cannot be mapped, it is derived from the zip code.

        Parameters
        ----------
        address: str
            A string containing the address

        Returns
        -------
        district : str
            District based on the given address
        """
        indic=False
        for key in self.dist_dict: #For each munipal district
            for value in self.dist_dict[key]: #Take each administartive district/cadastral area a look for them in the address string
                if value in address: #If found, save it and break the loop
                    district=key
                    indic=True #Tool to break the outside loop as well
                    break
            if indic: #break the outside loop if the district has been found
                break
        try:
            return district
        except UnboundLocalError: #In case the district is still not found (district variable has not been generated), try to get it from the zip code
            try:
                zip_code=re.search('[0-9]{3} [0-9]{2}',address).group(0) #Extract the zip code from the address
                if zip_code[1]=='0': #Special case for Praha 10
                    value='10'
                else:
                    value=zip_code[1]
                district='Praha '+value
                return district
            except AttributeError: #If the zip code is not in the address, return "Not found"
                return 'Not found'

    def getDistrictFromPraha_XX(self, praha_xx):
        """
        A function to map administrative district or municipal district to municipal district

        Parameters
        ----------
        praha_xx: str
            A string containing the municipal/administartive district in format Praha XX

        Returns
        -------
        district : str
            Municipal district derived from the input
        """
        if praha_xx in self.dist_dict.keys(): #In case the municipal district (Praha 1-10) was already extracted, return it
            district=praha_xx
        else: #If not, search through the mapping dictionary
            for key in self.dist_dict:
                if praha_xx in self.dist_dict[key]:
                    district=key
                    break
        return district

    def getDistrict(self,address):
        """
        A function to retrive the restaurant's district

        Parameters
        ----------
        address : str
            Restaurant's address

        Returns
        -------
        district : str or None
            The restaurant's municipal district
        """
        if address == None:
            district = None
        else:
            search_dist=re.search('Praha [0-9]{1,2}',address) #Firstly, try to find a Praha xx
            if search_dist: #If found, map it to the municipal district
                if search_dist.group(0)=='Praha 31': #Very special case of one restaurant with Praha 310 in the beginning of the address => resolved by brute force
                    district='Praha 1'
                else:
                    district=self.getDistrictFromPraha_XX(search_dist.group(0)) #Find district based on Praha XX
            else: #If not found, feed the whole address to the mapping function
                district=self.mappingDistrict(address)
        return district
            #value=re.search('Praha[ ]{0,1}[0-9]{0,2}',address).group(0).strip()
            #if value=='Praha':
                #words=re.split('\W+',address)
                #district=self.mappingDistrict(words)
            #elif value=='Praha 31': #For a very special case of one of the Starbucks, had to be resolved by brute force
                #district='Praha 1'
            #else:
                #district=self.mappingDistrict(value)
            #return district

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
        else:
            ratings=float(soup.find('span',{'itemprop':'ratingValue'}).text)
        return ratings

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
        else:
            review_count=int(soup.find('span',{'itemprop':'reviewCount'}).text)
        return review_count

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
        #elif self.name == 'Restaurace HOOTERS Vodičkova': #this elif is only temporary solution..to be removed
        #    dict = {'Po': '11 - 23', 'Út': '11 - 23', 'St': '11 - 23', 'Čt': '11 - 01', 'Pá': '11 - 01', 'So': '11 - 01', 'Ne': '11 - 23'}
        #    return dict
        else:
            table=soup.find('table',{'class':'table table-condensed'}).find_all('td')
            table_text=[]
            for i in table:
                if re.match('Dnes|\n',i.text):
                    pass
                elif i.text == 'zavřeno':
                    table_text.append(None)
                elif i.text == 'nonstop':
                    table_text.append('0 - 24')
                else:
                    table_text.append(i.text)
            #dict={}             #these 4 lines to be removed
            #for i in range(0,len(table_text),2):
            #    dict[table_text[i]]=table_text[i+1]
            #return dict

            week_days = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
            dict = {'Po':None, 'Út':None, 'St':None, 'Čt':None, 'Pá':None, 'So':None, 'Ne':None}
            for i in table_text:
                if i in week_days:
                    if table_text.index(i)+3 < len(table_text):
                        if table_text[table_text.index(i)+2] in week_days:
                            dict[i]=table_text[table_text.index(i)+1]
                        elif table_text[table_text.index(i)+3] in week_days:
                            dict[i]=[table_text[table_text.index(i)+1], table_text[table_text.index(i)+2]]
                        else:
                            raise IndexError('Unexpected number of cells in the Opening hours table :(')
                    else:
                        if len(table_text)-table_text.index(i) == 2:
                            dict[i]=table_text[table_text.index(i)+1]
                        elif len(table_text)-table_text.index(i) == 3:
                            dict[i]=[table_text[table_text.index(i)+1], table_text[table_text.index(i)+2]]
                else:
                    pass

        return dict

    def rangeToNumber(self,time_range):
        """
        A function to convert a string containing a time range into a number

        Parameters
        ----------
        time_range : str or None
            A time range as a string

        Returns
        -------
        span : float or None
            A number representing the time span of the given time range
        """
        if time_range == None:
            span=None
        else:
            hours=[time_range.split()[i] for i in [0,2]] #splitting by space and disregarding "-"
            start_end=[] #empty list for converted starting and ending values
            for i in hours:
                if re.search(':',i): #if the string is not a whole hour, convert it
                    splits=i.split(':')
                    start_end.append(float(splits[0])+float(splits[1])/60)
                else:
                    start_end.append(float(i))
            span=round(start_end[1] - start_end[0],2)
        return span

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
        else:
            span_dict = {'Po':None, 'Út':None, 'St':None, 'Čt':None, 'Pá':None, 'So':None, 'Ne':None}
            week_days = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
            for i in week_days:
                if opening_hours[i] == None:
                    span_dict[i] = None
                elif type(opening_hours[i]) == list:
                    multiple_spans = []
                    for n in opening_hours[i]:
                        multiple_spans.append(self.rangeToNumber(n))
                    
                    span_dict[i] = sum(multiple_spans) 
                else:    
                    span_dict[i]=self.rangeToNumber(opening_hours[i])

        return span_dict        

        #if opening_hours == None:
        #    span_dict = None
        #    return span_dict
        #else:
        #    span_dict={key:self.rangeToNumber(value) for (key,value) in opening_hours.items()}
        #    return span_dict

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
        if soup.find('td', {'itemprop':'telephone'}) == None:
            phones = None
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
        else: 
            coordinates={}
            coordinates['latitude']=json.loads(div_coordinates['data-centerpoi'])['lat']
            coordinates['longitude']=json.loads(div_coordinates['data-centerpoi'])['lng']
        return coordinates