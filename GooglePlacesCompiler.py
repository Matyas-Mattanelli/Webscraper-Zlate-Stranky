import requests
import json
import pickle #not needed(?)
import pandas as pd
import ast



class GooglePlacesCompiler:
    """
    A class compiling a data set from information available on Google Places API, given a dataframe of restaurants produced by DatasetCompiler.py.

    ...

    Attributes
    ----------
    dasda : asdasd
        Aasdasd.

    Methods
    -------
    adsfsdasd(asdasd):
        Asdasd.

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
        self.restaurants_dataframe = restaurants_dataframe
        self.MY_API_KEY = API_KEY

