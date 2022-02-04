import pandas as pd
import ast
import matplotlib.pyplot as plt

class DataComparer:
    '''
    
    '''

    def __init__(self, restaurants_zlatestranky, restaurants_Places_API):
        '''
        
        '''
        self.df_ZS = restaurants_zlatestranky
        self.df_API = restaurants_Places_API


    def summary_of_datasets(self):
        '''
        
        '''
        print("Total restaurants found on zlatestranky.cz:", self.df_ZS.name.count())
        print("Restaurants found by Google API search querry for the phone numbers from zlatestranky:", self.df_ZS.exact_match.count())
        print("Out of that, the number of exactly matched phone numbers:", self.df_ZS.exact_match.sum())
        print("This leaves us with", self.df_ZS.exact_match.count() - self.df_ZS.exact_match.sum(), "restaurants found by Google API, not matching to respective restaurants from zs. and", self.df_ZS.name.count() - self.df_ZS.exact_match.count(), "restaurants, that could not be found at all based on the phone number from zs.")

    def plot_reviews(self, outlier=5000):
        '''
        
        '''
        self.df_API[self.df_API["exact_match"] == True]["user_ratings_total"]
        plt.hist(self.df_API[self.df_API["exact_match"] == True][self.df_API["user_ratings_total"] < outlier]["user_ratings_total"],color='red', bins=12)
        plt.title('Number of ratings')