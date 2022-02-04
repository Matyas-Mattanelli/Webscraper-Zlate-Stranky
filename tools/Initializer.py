import pandas as pd

from tools.DatasetCompiler import DatasetCompiler #Either loads an existing data set or generates a new one
from tools.DataInterpreter import DataInterpreter #Contains methods for interpreting the data set

from tools.GooglePlacesCompiler import GooglePlacesCompiler #Loads existing data set from zlatestranky and creates new data set from Places API
from tools.DataComparer import DataComparer #Contains methods for comparing data from zlatestranky.cz and from Google API

def initialize(existing=True):
    if existing==True: #Loads the existing data set
        dataset_compiler=DatasetCompiler(existing=existing)
        data_interpreter=DataInterpreter(dataset_compiler.dataset) 
        print('Data set successfully loaded')
    elif existing==False: #Generates a new data set which replaces the old one
        from tools.MappingDictionaryGetter import MappingDictionaryGetter #Compiles the mapping dictionary for Prague districts
        from tools.LinkGetter import LinkGetter #Acquires individual links for restaurants
        
        link_getter=LinkGetter()
        print(f'Successfully acquired links for {len(link_getter.links)} restaurants')
        
        dist_dict=MappingDictionaryGetter() #Generate the dictionary
        dist_dict.saveToJSON() #Export it to a json file
        print('Mapping dictionary successfully compiled and exported to a json file')
        
        dataset_compiler=DatasetCompiler(link_getter.links) #Compiles the data set from the links
        print('Data set successfully compiled')
        dataset_compiler.dumpToCSV() #Saves the new data set in .csv
        print('Data set successfully exported to csv')
        
        data_interpreter=DataInterpreter(dataset_compiler.dataset)
        print('Data set successfully loaded')
    else:
        raise ValueError('Invalid input. Please specify existing as True or False')
    return data_interpreter

def initializePlacesAPI(existing=True, API_KEY=None):
    if existing == True: #Loads the existing data set
        df_ZS=pd.read_csv('data/restaurants_zlatestranky.csv')
        df_API=pd.read_csv('data/restaurants_Places_API.csv')
        data_comparer = DataComparer(df_ZS, df_API)
        print('Data set successfully loaded')

    elif existing == False: #Generates a new data set which replaces the old one
        df_ZS=pd.read_csv('data/restaurants_zlatestranky.csv')
        print("Data from zlatestranky.cz successfully loaded")
        
        if type(API_KEY) == str:
            GP_compiler = GooglePlacesCompiler(df_ZS, API_KEY) #Compiles the data set (sends the API requests) based on the telephone numbers from zlatestranky.cz
            print('Data set successfully compiled')

            GP_compiler.dumpToCSV() #Saves the new data set in .csv
            print('Data set successfully exported to csv')

            df_API = GP_compiler.places_API_df

            data_comparer = DataComparer(df_ZS, df_API)
            print('Data set successfully loaded')
            
        else:
            raise ValueError('Invalid input. Please specify API_KEY as string')

    else:
        raise ValueError('Invalid input. Please specify existing as True or False')

    return data_comparer
