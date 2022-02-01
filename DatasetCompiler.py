from Restaurant import Restaurant
import pandas as pd
import ast

class DatasetCompiler:
    """
    A class compiling a data set given a link or a list of links for each restaurant. If a data set already exits, it can be loaded.

    ...

    Attributes
    ----------
    dataset : pd.DataFrame
        Data set either compiled from the given links or loaded from an existing file
    
    links : list or str
        Either a list of strings for each restaurant or a string containing a link for a single restaurant
    
    list_of_restaurants : list
        List of Restaurant objects created from the links

    Methods
    -------
    getListOfRestaurants(links):
        A function creating a list or Restaurant objects given the links
    
    getDataset(list_of_restaurants):
        A function to compile a data set given a list of Restaurant objects

    dumpToCSV(file_name='restaurants_zlatestranky.csv'):
        A function to export the compiled data set to a csv file named "file_name"

    readExistingDataset(file_name):
        A function to read an existing data set from a csv file named "file_name". It also converts strings to Python objects.

    """
    def __init__(self,links=None,existing=False,file_name='restaurants_zlatestranky.csv'):
        """
        Constructs all the attributes given the parameters. If existing=False, compiles a new data set. Otherwise, reads an existing one based on file_name

        Parameters
        ----------
        links : list or str
            Either a list of links for each restaurant or a string containing a link for a single restaurant

        existing : bool
            A boolean indicating whether an existing data set should be loaded or a new one should be compiled. Defaults to False

        file_name : str
            Name of the file to read in case existing=True. Defaults to "restaurants_zlatestranky.csv"
        """
        if existing:
            self.dataset=self.readExistingDataset(file_name)
        else:
            if links:
                self.links=links
                self.list_of_restaurants=self.getListOfRestaurants(self.links)
                self.dataset=self.getDataset(self.list_of_restaurants)
            else:
                print('Please either provide the links or set the "existing" parameter to True')

    def getListOfRestaurants(self,links):
        """
        A function creating a list or Restaurant objects given the links

        Parameters
        ----------
        links : str
            Either a list of links for each restaurant or a string containing a link for a single restaurant

        Returns
        -------
        list_of_restaurants : list
            List of Restaurant objects created from the links
        """
        list_of_restaurants=[]
        if type(links)==type(''):
            links=[links] #In case of a single string we convert it to a list
        for link in links:
            list_of_restaurants.append(Restaurant(link))
        return list_of_restaurants

    def getDataset(self,list_of_restaurants):
        """
        A function to compile a data set given a list of Restaurant objects

        Parameters
        ----------
        list_of_restaurants : list
            List of Restaurant objects created from the links

        Returns
        -------
        df : pd.DataFrame
            Data set compiled from the list of Restaurant objects
        """
        attributes=list(list_of_restaurants[0].__dict__.keys()) #Attributes are the same accross instances => need to get them only once.
        attributes.remove('soup')
        attributes.remove('dist_dict')  #We disregard soup and dist_dict since we do not need them in the data set
        restaurants_list_of_dicts=[] #Making a list of dictionaries to be able to transform it into a pd.DataFrame 
        for restaurant in list_of_restaurants:
            restaurant_dict={} #Dictionary for each restaurant
            for attribute in attributes: #Add each attribute to the dictionary
                restaurant_dict[attribute]=getattr(restaurant,attribute)
            restaurants_list_of_dicts.append(restaurant_dict)
        df=pd.DataFrame(restaurants_list_of_dicts)
        return df

    def dumpToCSV(self,file_name='restaurants_zlatestranky.csv'):
        """
        A function to export the compiled data set to a csv file named file_name

        Parameters
        ----------
        file_name : str
            Desired name of the exported csv file

        Returns
        -------

        """
        self.dataset.to_csv(file_name)

    def readExistingDataset(self,file_name):
        """
        A function to read an existing data set from a csv file. It also converts strings to Python objects.

        Parameters
        ----------
        file_name : str
            Name of the file to read

        Returns
        -------
        df : pd.DataFrame
            Data set read from the file named file_name
        """
        df=pd.read_csv(file_name,index_col=0)
        #Dictionaries and lists are read from csv as strings=> we need to convert them back
        for column in ['opening_hours','opening_hours_span','phones','payment_methods','products','services','marks','coordinates']:
            for idx in df.index:
                try:
                    df.at[idx,column]=ast.literal_eval(df.at[idx,column])  
                except ValueError:
                    pass #In case there is NaN, ast.literal_eval throws an error => we will pass since we do not need to convert NaNs anyway
        return df