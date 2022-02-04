import pandas as pd
import ast
import matplotlib.pyplot as plt

class DataComparer:
    '''
    
    '''

    def __init__(self, restaurants_zlatestranky, restaurants_Places_API):
        '''
        
        '''
        self.df_ZS = self.compareDatasets(restaurants_zlatestranky, restaurants_Places_API)["df_ZS"]
        self.df_API = self.compareDatasets(restaurants_zlatestranky, restaurants_Places_API)["df_API"]

    def compareDatasets(self, df_ZS, df_API):
        '''
        
        '''
        #adding empty column to df_ZS
        empty_list = []
        for i in df_ZS.index:
            empty_list.append(None)
        df_ZS["exact_match"] = empty_list

        #comparison loop
        for i in df_ZS.index:
            if df_ZS["name"][i] == "Céleste":  #assigns None in case of this outiler
                celeste_exception = None
                df_ZS.exact_match.iat[i] = celeste_exception

            elif pd.isna(df_API["name"][i]):   #assigns None is case of no resaurant found by Google API
                df_ZS.exact_match.iat[i] = None
                
            else:                              #assigns true in case of match and False in case of no match
                zs_phones_dict = ast.literal_eval(df_ZS["phones"][i])
                
                zs_phones_list = []
                for n in zs_phones_dict:
                    net_number = zs_phones_dict[n][5:]
                    zs_phones_list.append(net_number)

                if df_API["formatted_phone_number"][i] in zs_phones_list:
                    df_ZS.exact_match.iat[i] = True
                else:
                    df_ZS.exact_match.iat[i] = False

        df_API["exact_match"] = df_ZS["exact_match"]   
        
        dict_of_df = {"df_ZS": df_ZS, "df_API": df_API}
        return dict_of_df


    def summaryOfDatasets(self):
        '''
        
        '''
        print("Total restaurants found on zlatestranky.cz:", self.df_ZS.name.count())
        print("Restaurants found by Google API search querry for the phone numbers from zlatestranky:", self.df_ZS.exact_match.count())
        print("Out of that, the number of exactly matched phone numbers:", self.df_ZS.exact_match.sum())
        print("This leaves us with", self.df_ZS.exact_match.count() - self.df_ZS.exact_match.sum(), "restaurants found by Google API, not matching to respective restaurants from zs. and", self.df_ZS.name.count() - self.df_ZS.exact_match.count(), "restaurants, that could not be found at all based on the phone number from zs.")

    def plotReviews(self,outlier=5000):
        '''
        
        '''
        df_API_exact_match = self.df_API[self.df_API["exact_match"] == True]
        df_API_outlier = df_API_exact_match[df_API_exact_match["user_ratings_total"] < outlier]
        df_API_hist = df_API_outlier["user_ratings_total"]
        plt.hist(df_API_hist,color='red', bins=12)
        plt.title('Number of ratings')

    def plotRatings(self):
        '''
        
        '''
        plt.hist(self.df_API[self.df_API["exact_match"] == True]["rating"],color='green', bins=12)
        plt.title('Rating')

    def printRatingStatistics(self):
        '''
        
        '''
        #Number of restaurants with at least one review
        num_of_ratings = []
        for i in self.df_API[self.df_API["exact_match"] == True]["user_ratings_total"]:
            if (pd.isna(i) == False):
                num_of_ratings.append(True)
            else:
                num_of_ratings.append(False)

        print("Number of restaurants with at least one review:", num_of_ratings.count(True))

        #Highest number of reviews
        max_rev = self.df_API[self.df_API["exact_match"] == True]["user_ratings_total"].max()
        max_df = self.df_API[self.df_API["user_ratings_total"] == max_rev]
        max_name = max_df.iloc[0]["name"]
        max_address = max_df.iloc[0]["formatted_address"]

        print("Highest number of reviews:", max_rev, f"({max_name}, located at {max_address})")    

        #Mean average of available ratings
        mean_ratings = self.df_API[self.df_API["exact_match"] == True]["rating"].mean()

        print("Mean average of available ratings (rounded):", round(mean_ratings, 2))     

        #Lowest rating

        lowest_rating = self.df_API[self.df_API["exact_match"] == True]["rating"].min()
        df_exact_match = self.df_API[self.df_API["exact_match"] == True]
        num_of_lowest = df_exact_match[df_exact_match["rating"] == lowest_rating].count()["name"]
        lowest_name = df_exact_match[df_exact_match["rating"] == lowest_rating].iloc[0]["name"]
        lowest_address = df_exact_match[df_exact_match["rating"] == lowest_rating].iloc[0]["formatted_address"]
        if num_of_lowest == 1:
            print("Lowest rating:", lowest_rating, f"({lowest_name}, located at {lowest_address})")
        else:
            print("Lowest rating:", lowest_rating, f"({num_of_lowest} restaurants)")    

        #Highest rating

        highest_rating = self.df_API[self.df_API["exact_match"] == True]["rating"].max()
        df_exact_match = self.df_API[self.df_API["exact_match"] == True]
        num_of_highest = df_exact_match[df_exact_match["rating"] == highest_rating].count()["name"]
        highest_name = df_exact_match[df_exact_match["rating"] == highest_rating].iloc[0]["name"]
        highest_address = df_exact_match[df_exact_match["rating"] == highest_rating].iloc[0]["formatted_address"]
        if num_of_highest == 1:
            print("highest rating:", highest_rating, f"({highest_name}, located at {highest_address})")
        else:
            print("highest rating:", highest_rating, f"({num_of_highest} restaurants)")                       

