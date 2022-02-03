from tools.DatasetCompiler import DatasetCompiler   
from tools.DataInterpreter import DataInterpreter

def initialize(existing=True):
    if existing==True:
        dataset_compiler=DatasetCompiler(existing=existing)
        data_interpreter=DataInterpreter(dataset_compiler.dataset)
    elif existing==False: 
        from tools.MappingDictionaryGetter import MappingDictionaryGetter   
        from tools.LinkGetter import LinkGetter
        link_getter=LinkGetter()
        dataset_compiler=DatasetCompiler(link_getter.links)
        data_interpreter=DataInterpreter(dataset_compiler.dataset)
    else:
        raise ValueError('Invalid input. Please specify existing as True or False')
    return data_interpreter
