import requests
import json
import pandas as pd
import ast



class GooglePlacesCompiler:
    """
    A class compiling a data set from information available on Google Places API, given a dataframe of restaurants produced by DatasetCompiler.py.

    ...

    Attributes
    ----------
    list_of_results : list
        List containing the results of Places API query. Each member of a list is a dict.

    places_API_df : pd.DataFrame
        Dataframe containgn information on the restaurants

    Methods
    -------
    find_first_candidate(name, phone, coordinates, API_KEY)
        A function that 

    getListOfResults(restaurants_dataframe, API_KEY)
        A function that applies find_first_candidate on each row of given dataset.

    getDataFrame(list_of_results)
        A function that concerts list of results into Pandas DataFrame.

    """
    def __init__(self, restaurants_dataframe, API_KEY):
        """
        Constructs all the attributes given the parameters.

        Parameters
        ----------
        restaurants_dataframe : pd.DataFrame
            Dataframe of restaurants scraped from zlatestranky.cz, produced by DatasetCompiler.py.

        API_KEY : str
            Valid API_KEY generated on Google Cloud Platform (see https://console.cloud.google.com/apis/credentials), with Selected APIs containing Places API (see Key restrictions section).
        """
        self.list_of_results = self.getListOfResults(restaurants_dataframe, API_KEY)
        self.places_API_df = self.getDataFrame(self.list_of_results)

    def find_first_candidate(self, name, phone, coordinates, API_KEY):
        '''
        A function that takes information about a restaurant, makes a query to Google Places API and reurns thus obtained data in a dictionary.
        The steps are as follows:
        1) take dictionary of phones of restaurant and extract the first one, as well as coordinates, and saves them
        2) uses Find place to get first candidates ID
        3) use this ID to get Details
        4) return details as a dictionary 

        Parameters
        ----------
        name : str
            Name of restaurant

        phone : dict
            Dictionary of phone numbers

        coordinates : dict
            Dictionary of coordinates

        API_KEY : str
            Valid API_KEY generated on Google Cloud Platform (see __init__ for more info)                   

        Returns
        -------
        result : dict
            Dictionary containing name from zlatestranky.cz and information retrieved from Google Places API
        '''
        phone_list = []
        for i in phone:
            phone_list.append(phone[i])
        
        main_phone = phone_list[0] #extracting the main phone from dict

        if coordinates == None:
            result = {'ZS_name':name, 'name':None, 'formatted_address':None, 'location':None, 'rating':None, 'user_ratings_total':None, 'formatted_phone_number':None}
        else:
            latitude = coordinates['latitude']
            longitude = coordinates['longitude']

        place_request = requests.get(f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={main_phone}&inputtype=textquery&locationbias=circle:50@{latitude},{longitude}&fields=place_id&key={API_KEY}")
        place_dict = json.loads(place_request.text)

        if place_dict["candidates"] == []:
            result = {'ZS_name':name, 'name':None, 'formatted_address':None, 'location':None, 'rating':None, 'user_ratings_total':None, 'formatted_phone_number':None}
        else:
            iter_id = place_dict["candidates"][0]["place_id"]
            detail_request = requests.get(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={iter_id}&fields=name%2Cformatted_address%2Cgeometry%2Crating%2Cformatted_phone_number%2Cuser_ratings_total&key={API_KEY}")
            detail_dict = json.loads(detail_request.text)
            
            #saving the details
            result = {'ZS_name':name}

            try:
                result['name'] = detail_dict['result']['name']
            except KeyError:
                result['name'] = None

            try:
                result['formatted_address'] = detail_dict['result']['formatted_address']
            except KeyError:
                result['formatted_address'] = None

            try:
                result['location'] = detail_dict['result']['geometry']['location']
            except KeyError:
                result['location'] = None

            try:
                result['rating'] = detail_dict['result']['rating']
            except KeyError:
                result['rating'] = None

            try:
                result['user_ratings_total'] = detail_dict['result']['user_ratings_total']
            except KeyError:
                result['user_ratings_total'] = None

            try:
                result['formatted_phone_number'] = detail_dict['result']['formatted_phone_number']
            except KeyError:
                result['formatted_phone_number'] = None            

        return result

    def getListOfResults(self, restaurants_dataframe, API_KEY):
        """
        A function that applies find_first_candidate on each row of given dataset. The exception for the restaurant named "Céleste" was made, as it is an outlier with no information

        Parameters
        ----------
        restaurants_dataframe : pd.DataFrame
            Dataframe of restaurants scraped from zlatestranky.cz, produced by DatasetCompiler.py.

        API_KEY : str
            Valid API_KEY generated on Google Cloud Platform (see __init__ for more info)                   

        Returns
        -------
        list_of_results : list
            List containing the results of Places API query. Each member of a list is a dict.
        """
        zs_restaurants = restaurants_dataframe
        list_of_results = []
        for ind in zs_restaurants.index:
            if zs_restaurants["name"][ind] == "Céleste":
                celeste_exception = {'ZS_name':"Céleste", 'name':None, 'formatted_address':None, 'location':None, 'rating':None, 'user_ratings_total':None, 'formatted_phone_number':None}
                list_of_results.append(celeste_exception)
            else:
                iter_name = zs_restaurants["name"][ind]
                iter_phones = ast.literal_eval(zs_restaurants["phones"][ind])
                iter_coordinates = ast.literal_eval(zs_restaurants["coordinates"][ind])

                iter_result = self.find_first_candidate(iter_name, iter_phones, iter_coordinates, API_KEY)

                list_of_results.append(iter_result)
        return list_of_results

    def getDataFrame(self, list_of_results):
        """
        A function that converts list of results into Pandas DataFrame.

        Parameters
        ----------
        list_of_results : list
            List containing the results of Places API query. Each member of a list is a dict.

        Returns
        -------
        places_API_df : pd.DataFrame
            Dataframe containgn information on the restaurants
        """
        places_API_df = pd.DataFrame(list_of_results)
        return places_API_df
