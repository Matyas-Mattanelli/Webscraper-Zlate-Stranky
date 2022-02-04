from tools.DatasetCompiler import DatasetCompiler #Either loads an existing data set or generates a new one
from tools.DataInterpreter import DataInterpreter #Contains methods for interpreting the data set

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
        dataset_compiler.dumpToCSV()
        print('Data set successfully exported to csv')
        
        data_interpreter=DataInterpreter(dataset_compiler.dataset)
        print('Data set successfully loaded')
    else:
        raise ValueError('Invalid input. Please specify existing as True or False')
    return data_interpreter

def initializePlacesAPI(existing=True):
    if existing == True: 
        #wip

    elif existing == False:
        #wip
    else:
        raise ValueError('Invalid input. Please specify existing as True or False')
