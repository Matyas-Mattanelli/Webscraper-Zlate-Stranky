import requests
from bs4 import BeautifulSoup
import time

class LinkGetter:
    """
    A class retrieving the link for each restaurant from the webpage www.zlatestranky.cz

    ...

    Attributes
    ----------
    links : list
        list of retrieved links

    Methods
    -------
    getLinks():
        A function to retrieve the links
    
    getRequestsFromAllPages():
        A function to get the requests from all available pages
    """
    def __init__(self):
        """
        Creates an object with an attribute self.links containing the retrieved links
        """
        self.links=[]
    
    def getLinks(self):
        """
        A function to retrieve the links 
        """
        request_list=self.getRequestsFromAllPages()
        soup_list=[]
        for request in request_list:
            soup_list.append(BeautifulSoup(request))
        titles_soup=[]
        for soup in soup_list:
            titles_soup.extend(soup.findall("h3"))
        links=[]
        for title in titles_soup:
            links.append(f'https://www.zlatestranky.cz{title.find("a")["href"]}')
        self.links=links
    
    def getRequestsFromAllPages():
        """
        A function to get the requests from all available pages 
        """
        request_list=[]
        i=1 #initializing the first iteration
        indicator=200 #initializing the while loop
        while indicator == 200:
            request=requests.get(f'https://www.zlatestranky.cz/firmy/rubrika/Restaurace/kraj/Hlavn%C3%AD%20m%C4%9Bsto%20Praha/{i}')
            indicator=request.status_code
            time.sleep(0.2)
            if indicator == 200:
                request_list.append(request.content)
                i += 1
            else:
                print(f'Successfuly requested {i-1} pages')
        return request_list

